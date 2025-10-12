from decimal import Decimal
import uuid

from django.apps import apps
from django.db.models import Sum
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.conf import settings
from django.template import loader
from django.shortcuts import render, redirect
from django.views.generic import TemplateView
from django.http import JsonResponse
from django.utils import timezone

from .forms import ContactForm, StartInvestmentForm, PLAN_RULES
from .models import Contact, Investment


# ---------- Static pages ----------
class HomeView(TemplateView):
    template_name = "index.html"


class OverviewView(TemplateView):
    template_name = "trading.html"


class AboutView(TemplateView):
    template_name = "about.html"


class FaqView(TemplateView):
    template_name = "faq.html"


class PlansView(TemplateView):
    template_name = "trading.html"


# ---------- Contact ----------
def contact(request):
    success_message = None
    if request.method == "POST":
        form = ContactForm(request.POST)
        if form.is_valid():
            message_body = form.cleaned_data["message"]
            name = form.cleaned_data["name"]
            email = form.cleaned_data["email"]
            subject = form.cleaned_data["subject"]

            Contact.objects.create(
                message=message_body, name=name, email=email, subject=subject
            )

            html_message = loader.render_to_string(
                "contact_email.html",
                {"name": name, "email": email, "subject": subject, "message": message_body},
            )

            send_mail(
                f"New Contact: {subject}",
                f"Name: {name}\nEmail: {email}\n\n{message_body}",
                settings.EMAIL_HOST_USER,
                ["badguybadguy79@gmail.com"],
                fail_silently=True,
                html_message=html_message,
            )
            success_message = "Form submitted successfully!"
    else:
        form = ContactForm()

    return render(request, "contact.html", {"form": form, "success_message": success_message})


# ---------- Generic helpers ----------
def _field_names(Model):
    return {f.name for f in Model._meta.get_fields() if hasattr(f, "attname")}


def _auto_amount_field(Model, preferred=None):
    names = _field_names(Model)
    for cand in [preferred, "amount", "amount_usd", "usd_amount", "value", "total"]:
        if cand and cand in names:
            return cand
    return None


def _auto_asset_field(Model):
    names = _field_names(Model)
    for cand in ("asset", "symbol", "currency", "coin", "token"):
        if cand in names:
            return cand
    return None


def _first_name(names, *candidates):
    for c in candidates:
        if c in names:
            return c
    return None


def _apply_filters(Model, qs, filters):
    """
    Safely apply filters across heterogeneous models.
     - If model has `status`, use `status__iexact` for strings
     - If it doesn't, map `status` to boolean `is_approved` when present
    """
    if not filters:
        return qs

    names = _field_names(Model)
    mapped = {}
    for key, val in (filters or {}).items():
        if key in names:
            mapped[key] = val
            continue
        if key == "status" and "status" not in names and "is_approved" in names:
            if isinstance(val, bool):
                mapped["is_approved"] = val
            else:
                s = str(val).strip().lower()
                truthy = {"approved", "posted", "success", "successful", "paid", "active", "completed"}
                falsy = {"pending", "processing", "awaiting", "failed", "declined", "rejected"}
                if s in truthy:
                    mapped["is_approved"] = True
                elif s in falsy:
                    mapped["is_approved"] = False

    for k, v in mapped.items():
        qs = qs.filter(**{k: v})

    if "status" in names and "status" in (filters or {}):
        val = filters["status"]
        if isinstance(val, str):
            qs = qs.filter(status__iexact=val.strip())
        else:
            qs = qs.filter(status=val)

    return qs


def _sum_amount_for_model(Model, user, filters=None, amount_field=None):
    amt_field = _auto_amount_field(Model, preferred=amount_field)
    if not amt_field:
        return Decimal("0")
    qs = Model.objects.filter(user=user)
    qs = _apply_filters(Model, qs, filters)
    agg = qs.aggregate(total=Sum(amt_field))
    return agg["total"] or Decimal("0")


# ---------- Deposit helpers ----------
def _iter_deposit_models():
    """Find models that look like deposits."""
    for Model in apps.get_models():
        name = Model.__name__.lower()
        if "deposit" not in name or "withdraw" in name:
            continue
        names = _field_names(Model)
        if "user" not in names:
            continue
        if not _auto_amount_field(Model):
            continue
        yield Model


def _sum_all_deposits(user):
    """Sum all deposits; prefer approved, else all."""
    total = Decimal("0")
    for Model in _iter_deposit_models():
        approved = _sum_amount_for_model(Model, user, {"status": "approved"})
        total += approved if approved > 0 else _sum_amount_for_model(Model, user, None)
    return total


def _assets_from_all_deposits(user):
    """Merge balances per asset from all deposit-like models."""
    combined = {}
    for Model in _iter_deposit_models():
        amt_field = _auto_amount_field(Model)
        asset_field = _auto_asset_field(Model)
        if not amt_field or not asset_field:
            continue

        base_qs = Model.objects.filter(user=user)
        qs = _apply_filters(Model, base_qs, {"status": "approved"})
        rows = qs.values(asset_field).annotate(total=Sum(amt_field)).order_by("-total")
        if not rows or all((r["total"] or 0) == 0 for r in rows):
            rows = base_qs.values(asset_field).annotate(total=Sum(amt_field)).order_by("-total")

        for r in rows:
            sym = (r.get(asset_field) or "").upper().strip()
            if not sym:
                continue
            usd = float(r.get("total") or 0)
            combined[sym] = combined.get(sym, 0.0) + usd
    return combined


def _currency_rows(profit_total: Decimal, user):
    rows = [{"symbol": "PROFITS USD", "usd": float(profit_total or 0)}]
    for sym, usd in sorted(_assets_from_all_deposits(user).items(), key=lambda kv: kv[1], reverse=True):
        rows.append({"symbol": sym, "usd": float(usd)})
    return rows


def _addr_map_from_admin():
    """
    Pull active deposit addresses from admin (major.PaymentAddress).
    Returns: {"BTC": {"network": "...", "address": "..."}, ...}
    """
    try:
        PaymentAddress = apps.get_model("major", "PaymentAddress")
    except LookupError:
        return {}

    addr_map = {}
    qs = PaymentAddress.objects.filter(is_active=True).order_by("-is_primary", "asset", "network")
    for pa in qs:
        key = (pa.asset or "").upper().strip()
        if key and key not in addr_map:  # one per asset for the picker
            addr_map[key] = {"network": pa.network or "", "address": pa.address or ""}
    return addr_map


def _collect_recent_deposits(user, limit=25):
    rows = []
    for Model in _iter_deposit_models():
        amt_field = _auto_amount_field(Model)
        asset_field = _auto_asset_field(Model)
        names = _field_names(Model)
        qs = Model.objects.filter(user=user)
        qs = qs.order_by("-created_at") if "created_at" in names else qs.order_by("-id")
        for obj in qs[:limit]:
            rows.append({
                "reference": getattr(obj, "reference", f"{Model.__name__} #{obj.pk}"),
                "asset": getattr(obj, asset_field, None),
                "amount_usd": getattr(obj, amt_field, None),
                "status": getattr(obj, "status", "pending"),
                "created_at": getattr(obj, "created_at", None),
            })
    rows.sort(key=lambda r: r.get("created_at") or 0, reverse=True)
    return rows[:limit]


# ---------- Withdrawal helpers ----------
def _get_withdrawal_model():
    """Find a Withdrawal model reliably."""
    # Try common locations first
    for label, name in [("major", "Withdrawal"), ("app", "Withdrawal")]:
        try:
            return apps.get_model(label, name)
        except LookupError:
            pass

    # Fallback: heuristic search
    for Model in apps.get_models():
        if "withdraw" in Model.__name__.lower():
            if "user" in _field_names(Model) and _auto_amount_field(Model):
                return Model
    raise LookupError("No Withdrawal model found")


def _iter_withdrawal_models():
    """Iterator for all withdrawal-like models (usually just one)."""
    yielded = False
    for label, name in [("major", "Withdrawal"), ("app", "Withdrawal")]:
        try:
            Model = apps.get_model(label, name)
            if "user" in _field_names(Model) and _auto_amount_field(Model):
                yielded = True
                yield Model
        except LookupError:
            pass
    if not yielded:
        for Model in apps.get_models():
            n = Model.__name__.lower()
            if "withdraw" in n and "user" in _field_names(Model) and _auto_amount_field(Model):
                yield Model


def _sum_all_withdrawals(user, status=None):
    """
    Sum withdrawals. If status is provided, it's mapped via _apply_filters
    (so 'completed', 'approved', 'paid', etc. all work).
    """
    total = Decimal("0")
    for Model in _iter_withdrawal_models():
        filters = {"status": status} if status else None
        total += _sum_amount_for_model(Model, user, filters)
    return total


def _withdrawal_rows(user, limit=50):
    """Build rows for the history table safely (no getattr with None)."""
    try:
        W = _get_withdrawal_model()
    except LookupError:
        return []

    names = _field_names(W)
    amount_f = _auto_amount_field(W)
    addr_f = _first_name(names, "wallet_address", "address", "destination", "to_address")
    method_f = _first_name(names, "method", "type")
    ref_f = _first_name(names, "reference", "ref", "code", "tx_ref")
    status_f = _first_name(names, "status", "state")
    created_f = "created_at" if "created_at" in names else None

    qs = W.objects.filter(user=user)
    qs = qs.order_by(f"-{created_f}") if created_f else qs.order_by("-id")

    rows = []
    for o in qs[:limit]:
        rows.append({
            "reference": getattr(o, ref_f) if ref_f else f"WD-{o.pk}",
            "method": getattr(o, method_f) if method_f else "Crypto",
            "amount_usd": getattr(o, amount_f) if amount_f else Decimal("0"),
            "address": getattr(o, addr_f) if addr_f else "",
            "status": getattr(o, status_f) if status_f else "Pending",
            "created_at": getattr(o, created_f) if created_f else None,
        })
    return rows


# ---------- Dashboard ----------
@login_required
def user_home(request):
    user = request.user

    # totals
    profit_total = Decimal("0")
    try:
        ProfitModel = apps.get_model("major", "Profit")
        profit_total = _sum_amount_for_model(ProfitModel, user, {"status": "posted"})
    except Exception:
        profit_total = Decimal("0")

    deposit_total = _sum_all_deposits(user)

    # Subtract COMPLETED withdrawals from overall balance
    withdrawals_completed = _sum_all_withdrawals(user, status="completed")

    # Available account balance (used sitewide)
    balance = (profit_total or Decimal("0")) + (deposit_total or Decimal("0")) - (withdrawals_completed or Decimal("0"))

    # Capital allocation: Profit vs Deposits (deposits are gross; pie is just composition)
    base = float(max(balance, 0))
    if base > 0:
        # Use gross deposits + profits to show composition percentages
        gross = float((profit_total or 0) + (deposit_total or 0))
        p_pct = round(float(profit_total) / gross * 100.0, 2) if gross else 0.0
        d_pct = round(100.0 - p_pct, 2) if gross else 0.0
    else:
        p_pct = d_pct = 0.0

    ctx = {
        "balance": balance,
        "balance_btc": None,
        "profit_total": profit_total,
        "deposit_total": deposit_total,
        "currency_rows": _currency_rows(profit_total, user),
        "alloc_labels_json": ["Profit", "Deposits"],
        "alloc_values_json": [p_pct, d_pct],
        "alloc_colors_json": ["#f59e0b", "#10b981"],
    }
    return render(request, "home/dashboard2.html", ctx)


# ---------- Deposit page ----------
@login_required
def deposit(request):
    user = request.user

    # Totals for the ribbon (match dashboard math)
    profit_total = Decimal("0")
    try:
        ProfitModel = apps.get_model("major", "Profit")
        profit_total = _sum_amount_for_model(ProfitModel, user, {"status": "posted"})
    except Exception:
        pass
    deposit_total = _sum_all_deposits(user)
    withdrawals_completed = _sum_all_withdrawals(user, status="completed")
    balance = (profit_total or Decimal("0")) + (deposit_total or Decimal("0")) - (withdrawals_completed or Decimal("0"))

    addr_map = _addr_map_from_admin()

    if request.method == "POST":
        # If you have a concrete Deposit model, create it here.
        messages.success(request, "Deposit submitted. Waiting for confirmation.")
        return redirect("deposit")

    ctx = {
        "balance_usd": f"{balance:,.2f}",
        "balance_btc": None,
        "addr_map": addr_map,
        "object_list": _collect_recent_deposits(user),
    }
    return render(request, "home/deposit.html", ctx)


# ---------- Withdraw page (with receipt + live numbers) ----------
@login_required
def withdraw(request):
    user = request.user

    # Base balance: profits + deposits - completed withdraws
    profit_total = Decimal("0")
    try:
        ProfitModel = apps.get_model("major", "Profit")
        profit_total = _sum_amount_for_model(ProfitModel, user, {"status": "posted"})
    except Exception:
        pass
    deposit_total = _sum_all_deposits(user)
    withdrawals_completed = _sum_all_withdrawals(user, status="completed")

    base_balance = (profit_total or Decimal("0")) + (deposit_total or Decimal("0")) - (withdrawals_completed or Decimal("0"))

    # Pending total (affects withdrawable-now)
    pending_total = _sum_all_withdrawals(user, status="pending") + _sum_all_withdrawals(user, status="processing") + _sum_all_withdrawals(user, status="awaiting")

    if request.method == "POST":
        # Create a withdrawal row and return a receipt JSON
        try:
            W = _get_withdrawal_model()
        except LookupError:
            # Fallback: just show a message and reload
            messages.error(request, "Withdrawal model not found.")
            return redirect("withdraw")

        names = _field_names(W)
        amount_f = _auto_amount_field(W) or "amount_usd"
        addr_f = _first_name(names, "wallet_address", "address", "destination", "to_address")
        method_f = _first_name(names, "method", "type")
        network_f = _first_name(names, "network", "chain")
        asset_f = _first_name(names, "asset", "cryptocurrency", "symbol", "coin", "token")
        ref_f = _first_name(names, "reference", "ref", "code", "tx_ref")
        status_f = _first_name(names, "status", "state")

        # Pull values from POST (your form field names)
        method = (request.POST.get("method") or "crypto").lower()
        amount_str = request.POST.get("amount_in_USD") or request.POST.get("amount") or "0"
        try:
            amount_val = Decimal(amount_str)
        except Exception:
            amount_val = Decimal("0")

        wallet = request.POST.get("wallet_address") or request.POST.get("address") or ""
        network = request.POST.get("network") or ""
        asset = request.POST.get("cryptocurrency") or request.POST.get("asset") or "USDT"

        # Create object
        o = W()
        setattr(o, "user", user)
        if amount_f:
            setattr(o, amount_f, amount_val)
        if addr_f:
            setattr(o, addr_f, wallet)
        if method_f:
            setattr(o, method_f, "Crypto" if method == "crypto" else "Bank")
        if network_f:
            setattr(o, network_f, network)
        if asset_f:
            setattr(o, asset_f, asset)
        if status_f:
            setattr(o, status_f, "pending")
        if ref_f:
            setattr(o, ref_f, f"WD-{uuid.uuid4().hex[:8].upper()}")
        # created_at usually auto_now_add; if the model lacks it, it's fine.
        o.save()

        # Build JSON receipt for the modal
        receipt = {
            "reference": getattr(o, ref_f) if ref_f else f"WD-{o.pk}",
            "method": getattr(o, method_f) if method_f else "Crypto",
            "amount_in_USD": str(amount_val),
            "wallet_address": wallet if method == "crypto" else "",
            "asset": asset if method == "crypto" else "",
            "network": network if method == "crypto" else "",
            "account_number": "" if method == "crypto" else request.POST.get("account_number", ""),
            "bank_name": "" if method == "crypto" else request.POST.get("bank_name", ""),
            "status": getattr(o, status_f) if status_f else "Pending",
            "created_at": timezone.localtime(getattr(o, "created_at", timezone.now())).isoformat(),
        }

        return JsonResponse(receipt, status=201)

    # GET: render page
    ctx = {
        "balance_usd": f"{(base_balance - pending_total):,.2f}" if base_balance > 0 else "0.00",
        "pending_withdrawals_total": f"{pending_total:,.2f}",
        "object_list": _withdrawal_rows(user),
    }
    return render(request, "home/withdraw.html", ctx)


# ---------- Investments ----------
@login_required
def invest_start(request):
    plan_key = request.GET.get("plan") or request.POST.get("plan")
    if plan_key not in PLAN_RULES:
        messages.error(request, "Please choose a valid plan.")
        return redirect("plans")

    if request.method == "POST":
        form = StartInvestmentForm(plan_key, request.POST)
        if form.is_valid():
            Investment.objects.create(
                user=request.user,
                plan=form.cleaned_data["plan"],
                amount=form.cleaned_data["amount"],
            )
            messages.success(request, "Investment created. Pending funding/activation.")
            return redirect("user-home")
    else:
        form = StartInvestmentForm(plan_key)

    ctx = {"plan_key": plan_key, "rules": PLAN_RULES[plan_key], "form": form}
    return render(request, "invest/start.html", ctx)
