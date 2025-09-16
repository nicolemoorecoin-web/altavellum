from django.contrib import admin
from .models import Deposit, Withdrawal, Investment
from .models import PaymentAddress

# --- reusable actions -------------------------------------------------
def _mark_status(value):
    def action(modeladmin, request, queryset):
        queryset.update(status=value)
    action.__name__ = f"mark_{value}"
    action.short_description = f"Mark selected as {value}"
    return action

mark_completed = _mark_status("completed")
mark_pending   = _mark_status("pending")
mark_failed    = _mark_status("failed")


# --- Deposit ----------------------------------------------------------
@admin.register(Deposit)
class DepositAdmin(admin.ModelAdmin):
    list_display       = ("reference", "user", "method", "asset", "amount_usd", "status", "created_at")
    list_filter        = ("status", "method", "asset")
    search_fields      = ("reference", "user__username", "asset", "notes")
    ordering           = ("-created_at",)
    date_hierarchy     = "created_at"
    list_select_related = ("user",)
    readonly_fields    = ("reference", "created_at")
    actions            = (mark_completed, mark_pending, mark_failed)


# --- Withdrawal -------------------------------------------------------
@admin.register(Withdrawal)
class WithdrawalAdmin(admin.ModelAdmin):
    list_display        = ("reference", "user", "asset", "amount_usd", "status", "created_at")
    list_filter         = ("status", "asset")
    search_fields       = ("reference", "user__username", "asset", "notes")
    ordering            = ("-created_at",)
    date_hierarchy      = "created_at"
    list_select_related = ("user",)
    readonly_fields     = ("reference", "created_at")
    actions             = (mark_completed, mark_pending, mark_failed)

# --- Investment -------------------------------------------------------
@admin.register(Investment)
class InvestmentAdmin(admin.ModelAdmin):
    list_display       = ("reference", "user", "plan", "amount_usd", "profit_usd", "status", "created_at")
    list_filter        = ("status", "plan")
    search_fields      = ("reference", "user__username", "plan", "notes")
    ordering           = ("-created_at",)
    date_hierarchy     = "created_at"
    list_select_related = ("user",)
    readonly_fields    = ("reference", "created_at")
    actions            = (mark_completed, mark_pending, mark_failed)

    
@admin.register(PaymentAddress)
class PaymentAddressAdmin(admin.ModelAdmin):
    list_display = ("asset", "network", "address", "is_active", "updated_at")
    list_filter  = ("asset", "network", "is_active")
    search_fields = ("address",)
    ordering = ("asset", "network")