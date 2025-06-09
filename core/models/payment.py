from django.db import models
from django.conf import settings


class PaymentGateway(models.Model):
    """Model for payment gateway configurations"""
    GATEWAY_TYPES = [
        ('ZARINPAL', 'ZarinPal'),
        ('IDPAY', 'IDPay'),
        ('NEXTPAY', 'NextPay'),
    ]

    name = models.CharField(max_length=50)
    gateway_type = models.CharField(max_length=20, choices=GATEWAY_TYPES)
    is_active = models.BooleanField(default=True)
    merchant_id = models.CharField(max_length=100)
    api_key = models.CharField(max_length=100)
    callback_url = models.URLField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.get_gateway_type_display()} - {self.name}"


class Transaction(models.Model):
    """Model for tracking all financial transactions"""
    TRANSACTION_TYPES = [
        ('WALLET_CHARGE', 'Wallet Charge'),
        ('WALLET_WITHDRAW', 'Wallet Withdrawal'),
        ('PLAN_PURCHASE', 'Plan Purchase'),
        ('CONTRIBUTION', 'Contribution'),
        ('REFUND', 'Refund'),
    ]

    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('SUCCESS', 'Successful'),
        ('FAILED', 'Failed'),
        ('REFUNDED', 'Refunded'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='transactions'
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_type = models.CharField(
        max_length=20, choices=TRANSACTION_TYPES)
    payment_method = models.CharField(
        max_length=20,
        choices=[('WALLET', 'Wallet'), ('ONLINE', 'Online Gateway')]
    )
    gateway = models.ForeignKey(
        PaymentGateway,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    reference_id = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} - {self.amount} - {self.transaction_type}"
