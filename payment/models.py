from django.db import models
from django.conf import settings
from core.models import WishlistItem
import uuid


class Payment(models.Model):
    PAYMENT_STATUS_CHOICES = [
        ('PENDING', 'در انتظار'),
        ('COMPLETED', 'تکمیل شده'),
        ('FAILED', 'ناموفق'),
        ('CANCELLED', 'لغو شده'),
    ]

    PAYMENT_TYPE_CHOICES = [
        ('CONTRIBUTION', 'کمک مالی'),
        ('WALLET_CHARGE', 'شارژ کیف پول'),
        ('PURCHASE', 'خرید'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='payments')
    amount = models.DecimalField(max_digits=12, decimal_places=2)  # ریال
    type = models.CharField(max_length=20, choices=PAYMENT_TYPE_CHOICES)
    status = models.CharField(
        max_length=20, choices=PAYMENT_STATUS_CHOICES, default='PENDING')
    description = models.TextField(blank=True)

    # Zarinpal fields
    authority = models.CharField(max_length=50, blank=True, null=True)
    ref_id = models.CharField(max_length=50, blank=True, null=True)

    # Related fields
    wishlist_item = models.ForeignKey(
        WishlistItem, on_delete=models.CASCADE, blank=True, null=True)
    is_anonymous = models.BooleanField(default=False)

    # Metadata
    order_id = models.CharField(max_length=100, unique=True)
    callback_url = models.URLField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Payment {self.order_id} - {self.amount} ریال"


class Transaction(models.Model):
    TRANSACTION_TYPE_CHOICES = [
        ('CHARGE', 'شارژ'),
        ('CONTRIBUTION', 'کمک'),
        ('PURCHASE', 'خرید'),
        ('REFUND', 'بازپرداخت'),
    ]

    TRANSACTION_STATUS_CHOICES = [
        ('PENDING', 'در انتظار'),
        ('COMPLETED', 'تکمیل شده'),
        ('FAILED', 'ناموفق'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='transactions')
    payment = models.ForeignKey(
        Payment, on_delete=models.CASCADE, related_name='transactions', blank=True, null=True)

    amount = models.DecimalField(max_digits=12, decimal_places=2)
    type = models.CharField(max_length=20, choices=TRANSACTION_TYPE_CHOICES)
    status = models.CharField(
        max_length=20, choices=TRANSACTION_STATUS_CHOICES, default='PENDING')
    description = models.TextField()

    # For contributions
    wishlist_item = models.ForeignKey(
        WishlistItem, on_delete=models.CASCADE, blank=True, null=True)
    is_anonymous = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Transaction {self.id} - {self.type} - {self.amount} ریال"


class WalletBalance(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='wallet')
    balance = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Wallet {self.user.username} - {self.balance} ریال"

    def add_balance(self, amount):
        """افزودن موجودی به کیف پول"""
        self.balance += amount
        self.save()

    def subtract_balance(self, amount):
        """کم کردن موجودی از کیف پول"""
        if self.balance >= amount:
            self.balance -= amount
            self.save()
            return True
        return False


class ContributionRecord(models.Model):
    """رکورد کمک‌های مالی به آیتم‌های لیست آرزو"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    contributor = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='payment_contributions')
    wishlist_item = models.ForeignKey(
        WishlistItem, on_delete=models.CASCADE, related_name='payment_contributions')
    transaction = models.OneToOneField(
        Transaction, on_delete=models.CASCADE, related_name='contribution_record')

    amount = models.DecimalField(max_digits=12, decimal_places=2)
    is_anonymous = models.BooleanField(default=False)
    message = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        contributor_name = "ناشناس" if self.is_anonymous else self.contributor.username
        return f"{contributor_name} - {self.amount} ریال برای {self.wishlist_item.title}"
