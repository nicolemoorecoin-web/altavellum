# dashboard/home/views.py
from decimal import Decimal

from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.shortcuts import render, redirect
from django.utils.timezone import localtime
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse
from collections import defaultdict
import json


from dashboard.app.models import (
    Deposit,
    Withdrawal,
    Investment,
    PaymentAddress,   # <-- for admin-managed addresses
)

# statuses that count as “done”
CREDIT_STATUSES = ("completed", "success", "paid")
DEBIT_STATUSES  = ("completed", "success", "paid", "approved")


ASSET_NAME  = {"BTC": "Bitcoin", "ETH": "Ethereum", "USDT": "Tether"}
ASSET_COLOR = {"BTC": "#D08B2F", "ETH": "#3862F5", "USDT": "#1FA386"}


def _sum(qs, field):
    return qs.aggregate(s=Sum(field))["s"] or Decimal("0.00")

def _norm_asset(val: str) -> str:
    """Map free-text asset values to a stable symbol."""
    s = (val or "").strip().upper()
    if s.startswith("BTC"): return "BTC"
    if s.startswith("ETH"): return "ETH"
    if "USDT" in s or "TETHER" in s: return "USDT"
    return s or "USDT"

@require_http_methods(["GET", "POST"])
def logout_and_home(request):
    logout(request)
    return redirect(request.GET.get("next") or "home")


# ---------------- Dashboard ----------------

@login_required
def index(request):
    u = request.user

    dep_done = Deposit.objects.filter(user=u, status__in=CREDIT_STATUSES)
    wdr_done = Withdrawal.objects.filter(user=u, status__in=DEBIT_STATUSES)
    inv_done = Investment.objects.filter(user=u, status__in=CREDIT_STATUSES)

    deposit_total    = _sum(dep_done, "amount_usd")
    withdrawal_total = _sum(wdr_done, "amount_usd")
    profit_total     = _sum(inv_done, "profit_usd")
    balance          = deposit_total + profit_total - withdrawal_total

    # --- net USD by asset (deposits - withdrawals)
    dep_by_asset = defaultdict(Decimal)
    for r in dep_done.values("asset").annotate(total=Sum("amount_usd")):
        dep_by_asset[_norm_asset(r["asset"])] += r["total"]

    wdr_by_asset = defaultdict(Decimal)
    for r in wdr_done.values("asset").annotate(total=Sum("amount_usd")):
        wdr_by_asset[_norm_asset(r["asset"])] += r["total"]

    net_by_asset = {}
    for sym in set(dep_by_asset) | set(wdr_by_asset):
        amt = dep_by_asset.get(sym, Decimal("0")) - wdr_by_asset.get(sym, Decimal("0"))
        if amt > 0:
            net_by_asset[sym] = amt

    total_usd = sum(net_by_asset.values()) or Decimal("0")

    # Chart arrays
    ordered = sorted(net_by_asset.items(), key=lambda kv: float(kv[1]), reverse=True)
    alloc_symbols = [sym for sym, _ in ordered]
    alloc_labels  = [ASSET_NAME.get(sym, sym) for sym in alloc_symbols]
    alloc_values  = ([round(float(v / total_usd * 100), 2) for _, v in ordered] if total_usd > 0 else [])
    alloc_colors  = [ASSET_COLOR.get(sym, "#888888") for sym in alloc_symbols]

    # Currency cards
    currency_rows = [
        {"symbol": sym, "name": ASSET_NAME.get(sym, sym), "usd": amt}
        for sym, amt in ordered
    ]

    ctx = {
        "segment": "index",
        "balance": balance,
        # card numbers (keep multiple keys for old templates)
        "deposit_total": deposit_total,
        "deposits": deposit_total,
        "profit_total": profit_total,
        "profit": profit_total,
        "total_deposit": deposit_total,
        "total_profit": profit_total,
        # allocation / balances
        "alloc_labels_json": json.dumps(alloc_labels),
        "alloc_values_json": json.dumps(alloc_values),
        "alloc_colors_json": json.dumps(alloc_colors),
        "currency_rows": currency_rows,
    }
    return render(request, "home/dashboard2.html", ctx)

@login_required
def investments(request):
    qs = Investment.objects.filter(user=request.user).order_by("-created_at")
    return render(request, "home/investments.html", {"object_list": qs})


@login_required
def invest(request):
    return investments(request)


@login_required
def plans(request):
    return render(request, "home/plans.html", {})


# --------------- Deposit page ----------------

@login_required
def deposit(request):
    """
    GET  -> show balance + recent deposits + addresses from admin
    POST -> create a Deposit row and redirect
    """
    u = request.user

    if request.method == "POST":
        amt_str = (request.POST.get("amount_usd") or "").strip()
        method  = (request.POST.get("method") or "Crypto").strip()
        asset   = (request.POST.get("asset") or "").strip()
        network = (request.POST.get("network") or "").strip()
        notes   = (request.POST.get("notes") or "").strip()

        try:
            amount = Decimal(amt_str)
        except Exception:
            amount = Decimal("0")

        if amount <= 0:
            messages.error(request, "Enter a valid amount (minimum $20).")
        else:
            Deposit.objects.create(
                user=u,
                reference=Deposit.new_ref(),
                amount_usd=amount,
                method=method,
                asset=asset,
                network=network,
                notes=notes,
                status="pending",
            )
            messages.success(request, "Deposit submitted. It will appear below.")
            return redirect("deposit")

    dep_done = Deposit.objects.filter(user=u, status__in=CREDIT_STATUSES)
    inv_done = Investment.objects.filter(user=u, status__in=CREDIT_STATUSES)
    wdr_done = Withdrawal.objects.filter(user=u, status__in=DEBIT_STATUSES)
    balance  = _sum(dep_done, "amount_usd") + _sum(inv_done, "profit_usd") - _sum(wdr_done, "amount_usd")

    # build {"BTC":{"address":"...","network":"..."}, ...} from admin
    addr_map = {}
    for row in PaymentAddress.objects.filter(is_active=True):
        addr_map[row.asset] = {"address": row.address, "network": row.network}

    recent = Deposit.objects.filter(user=u).order_by("-created_at")[:20]

    ctx = {
        "balance_usd": balance,
        "balance": balance,
        "object_list": recent,
        "addr_map": addr_map,
    }
    return render(request, "home/deposit.html", ctx)


@login_required
def withdraw(request):
    u = request.user

    # ----- create a request
    if request.method == "POST":
        method = request.POST.get("method", "crypto")
        amount = Decimal(request.POST.get("amount_in_USD") or request.POST.get("amount_usd") or "0").quantize(Decimal("0.01"))

        if method == "crypto":
            asset   = request.POST.get("cryptocurrency") or request.POST.get("asset") or ""
            network = request.POST.get("network") or ""
            address = request.POST.get("wallet_address") or ""
            w = Withdrawal(
                user=u,
                reference=Withdrawal.new_ref(),
                amount_usd=amount,
                asset=asset,
                network=network,
                address=address,
                status="pending",
                notes=request.POST.get("notes", ""),
            )
            w.save()
            payload = {
                "reference": w.reference,
                "method": "Crypto",
                "amount_in_USD": float(w.amount_usd),
                "asset": w.asset,
                "network": w.network,
                "wallet_address": w.address,
                "status": w.status,
                "created_at": w.created_at.isoformat(),
            }
        else:
            # Bank payout: store details in notes + address holds account number
            bank_name = request.POST.get("bank_name", "")
            account_name = request.POST.get("account_name", "")
            account_number = request.POST.get("account_number", "")
            swift = request.POST.get("swift_code", "")
            note = f"Bank: {bank_name}; Holder: {account_name}; Account: {account_number}; SWIFT/Routing: {swift}"
            w = Withdrawal(
                user=u,
                reference=Withdrawal.new_ref(),
                amount_usd=amount,
                asset="BANK",
                network="",
                address=account_number,
                status="pending",
                notes=note,
            )
            w.save()
            payload = {
                "reference": w.reference,
                "method": "Bank",
                "amount_in_USD": float(w.amount_usd),
                "bank_name": bank_name,
                "account_number": account_number,
                "status": w.status,
                "created_at": w.created_at.isoformat(),
            }

        # AJAX? return JSON so the page updates without reload
        if request.headers.get("x-requested-with") == "XMLHttpRequest":
            return JsonResponse(payload, status=201)

        messages.success(request, f"Withdrawal request {w.reference} created.")
        return redirect("withdraw")

    # ----- GET: page data
    object_list = Withdrawal.objects.filter(user=u).order_by("-created_at")

    deposit_total    = _sum(Deposit.objects.filter(user=u, status__in=CREDIT_STATUSES), "amount_usd")
    profit_total     = _sum(Investment.objects.filter(user=u, status__in=CREDIT_STATUSES), "profit_usd")
    withdrawn_total  = _sum(Withdrawal.objects.filter(user=u, status__in=DEBIT_STATUSES), "amount_usd")
    balance          = deposit_total + profit_total - withdrawn_total
    pending_total    = _sum(Withdrawal.objects.filter(user=u).exclude(status__in=DEBIT_STATUSES), "amount_usd")

    ctx = {
        "object_list": object_list,
        "balance_usd": balance,
        "pending_withdrawals_total": pending_total,
    }
    return render(request, "home/withdraw.html", ctx)


@login_required
def edit_profile(request):
    return render(request, "home/profile.html", {})


@login_required
def chart(request):
    return render(request, "home/charts.html", {})


# --------------- Transactions ---------------

@login_required
def transactions(request):
    """Unified list the template expects."""
    u = request.user
    rows = []

    for d in Deposit.objects.filter(user=u).order_by("-created_at"):
        rows.append({
            "reference": d.reference,
            "category": "deposit",
            "method": getattr(d, "method", "Crypto"),
            "asset": getattr(d, "asset", "") or "",
            "amount": d.amount_usd,
            "status": d.status,
            "date": localtime(d.created_at),
            "notes": getattr(d, "notes", "") or "",
            "flow": "in",
            "network": getattr(d, "network", "") or "",
            "cryptocurrency": getattr(d, "asset", "") or "",
            "plan": "",
        })

    for w in Withdrawal.objects.filter(user=u).order_by("-created_at"):
        rows.append({
            "reference": w.reference,
            "category": "withdrawal",
            "method": getattr(w, "method", "Crypto"),
            "asset": getattr(w, "asset", "") or "",
            "amount": w.amount_usd,
            "status": w.status,
            "date": localtime(w.created_at),
            "notes": getattr(w, "notes", "") or "",
            "flow": "out",
            "network": getattr(w, "network", "") or "",
            "cryptocurrency": getattr(w, "asset", "") or "",
            "plan": "",
        })

    for i in Investment.objects.filter(user=u).order_by("-created_at"):
        profit = getattr(i, "profit_usd", Decimal("0.00")) or Decimal("0.00")
        if profit != 0:
            rows.append({
                "reference": i.reference,
                "category": "investment",
                "method": "Profit",
                "asset": getattr(i, "plan", "") or "Plan",
                "amount": profit,
                "status": i.status,
                "date": localtime(i.created_at),
                "notes": getattr(i, "notes", "") or "",
                "flow": "in",
                "network": "",
                "cryptocurrency": "",
                "plan": getattr(i, "plan", "") or "",
            })

    inflows  = _sum(Deposit.objects.filter(user=u, status__in=CREDIT_STATUSES), "amount_usd") \
             + _sum(Investment.objects.filter(user=u, status__in=CREDIT_STATUSES), "profit_usd")
    outflows = _sum(Withdrawal.objects.filter(user=u, status__in=DEBIT_STATUSES), "amount_usd")
    totals = {"inflows": inflows, "outflows": outflows, "net": inflows - outflows}

    rows.sort(key=lambda r: r["date"], reverse=True)
    return render(request, "home/transactions.html", {"object_list": rows, "totals": totals})