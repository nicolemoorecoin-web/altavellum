from decimal import Decimal
from django.conf import settings
from django.db import models
from django.utils.crypto import get_random_string
from django.db import IntegrityError


def make_ref(prefix: str) -> str:
    return f"{prefix}-{get_random_string(8).upper()}"

STATUS = [
    ("pending", "Pending"),
    ("processing", "Processing"),
    ("completed", "Completed"),
    ("failed", "Failed"),
    ("rejected", "Rejected"),
]


class BaseTx(models.Model):
    user        = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="%(class)ss",
    )
    # 👇 make it optional/hidden in forms; still unique in DB
    reference   = models.CharField(max_length=32, unique=True, blank=True, editable=False)
    amount_usd  = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
    status      = models.CharField(max_length=12, choices=STATUS, default="pending")
    notes       = models.TextField(blank=True)
    created_at  = models.DateTimeField(auto_now_add=True)

    class Meta:
        abstract  = True
        ordering  = ("-created_at",)

    def __str__(self):
        return f"{self.__class__.__name__} {self.reference or '(new)'} (${self.amount_usd})"

    def save(self, *args, **kwargs):
        """
        Auto-generate a unique reference on first save using the subclass'
        new_ref() if present (DEP/WDR/INV). Retries a couple times on race.
        """
        if not self.reference:
            gen = getattr(self.__class__, "new_ref", None)
            prefix_ref = gen() if callable(gen) else f"{self.__class__.__name__[:3].upper()}-{get_random_string(8).upper()}"
            self.reference = prefix_ref

        # Rare chance of collision? Retry a couple of times.
        for _ in range(2):
            try:
                return super().save(*args, **kwargs)
            except IntegrityError:
                self.reference = (getattr(self.__class__, "new_ref", None) or (lambda: f"{self.__class__.__name__[:3].upper()}-{get_random_string(8).upper()}"))()
        # final attempt (will raise if still colliding)
        return super().save(*args, **kwargs)


class Deposit(BaseTx):
    method = models.CharField(max_length=50, blank=True)     # e.g. “Crypto”
    asset = models.CharField(max_length=50, blank=True)      # e.g. “USDT”
    network = models.CharField(max_length=50, blank=True)    # e.g. “TRC-20”

    @staticmethod
    def new_ref(): return make_ref("DEP")


class Withdrawal(BaseTx):
    asset = models.CharField(max_length=50, blank=True)
    network = models.CharField(max_length=50, blank=True)
    address = models.CharField(max_length=120, blank=True)

    @staticmethod
    def new_ref(): return make_ref("WDR")


class Investment(BaseTx):
    # amount_usd = principal invested
    plan = models.CharField(max_length=60, blank=True)
    profit_usd = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))

    @staticmethod
    def new_ref(): return make_ref("INV")

    # --- add below your Investment model ---
class PaymentAddress(models.Model):
    ASSET_CHOICES = [
        ("BTC", "Bitcoin"),
        ("ETH", "Ethereum"),
        ("USDT", "Tether"),
    ]
    NETWORK_CHOICES = [
        ("Bitcoin", "Bitcoin"),
        ("ERC-20", "ERC-20"),
        ("TRC-20", "TRC-20"),
    ]

    asset   = models.CharField(max_length=10, choices=ASSET_CHOICES)
    network = models.CharField(max_length=20, choices=NETWORK_CHOICES, blank=True)
    address = models.CharField(max_length=200, unique=True)
    is_active = models.BooleanField(default=True)
    label   = models.CharField(max_length=50, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = (("asset", "network"),)
        ordering = ("asset", "network")

    def __str__(self):
        return f"{self.get_asset_display()} {self.network} • {self.address[:8]}…"

