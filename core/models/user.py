from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _

class User(AbstractUser):
    """Custom User model with wallet functionality"""
    wallet_balance = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        help_text=_('User\'s current wallet balance')
    )
    phone_number = models.CharField(
        max_length=20,
        blank=True,
        help_text=_('User\'s phone number for notifications')
    )
    birthdate = models.DateField(
        null=True,
        blank=True,
        help_text=_('User\'s birthdate for birthday reminders')
    )
    notification_preferences = models.JSONField(
        default=dict,
        help_text=_('User\'s notification preferences')
    )
    avatar = models.ImageField(
        upload_to='avatars/',
        null=True,
        blank=True
    )
    is_verified = models.BooleanField(
        default=False,
        help_text=_('Whether the user\'s email/phone is verified')
    )

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')

    def add_to_wallet(self, amount):
        """Add money to user's wallet"""
        self.wallet_balance += amount
        self.save(update_fields=['wallet_balance'])

    def deduct_from_wallet(self, amount):
        """Deduct money from user's wallet"""
        if self.wallet_balance >= amount:
            self.wallet_balance -= amount
            self.save(update_fields=['wallet_balance'])
            return True
        return False

    def has_sufficient_balance(self, amount):
        """Check if user has sufficient balance"""
        return self.wallet_balance >= amount
