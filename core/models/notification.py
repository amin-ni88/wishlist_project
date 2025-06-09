from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _


class NotificationPreference(models.Model):
    """Model for user notification preferences"""
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notification_preferences'
    )

    # Email notifications
    email_contribution = models.BooleanField(
        default=True,
        help_text=_('Receive email notifications for new contributions')
    )
    email_wishlist_invite = models.BooleanField(
        default=True,
        help_text=_('Receive email notifications for wishlist invitations')
    )
    email_subscription = models.BooleanField(
        default=True,
        help_text=_('Receive email notifications for subscription updates')
    )
    email_price_changes = models.BooleanField(
        default=True,
        help_text=_('Receive email notifications for price changes')
    )

    # Push notifications (for future use)
    push_enabled = models.BooleanField(default=False)
    push_token = models.CharField(max_length=255, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Notification preferences for {self.user.username}"


class Notification(models.Model):
    """Model for storing notifications"""
    NOTIFICATION_TYPES = [
        ('CONTRIBUTION', _('New Contribution')),
        ('WISHLIST_SHARE', _('Wishlist Shared')),
        ('ITEM_FULFILLED', _('Item Fulfilled')),
        ('SUBSCRIPTION_EXPIRY', _('Subscription Expiring')),
        ('PRICE_CHANGE', _('Price Change')),
        ('OCCASION_REMINDER', _('Occasion Reminder')),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notifications'
    )
    type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    title = models.CharField(max_length=200)
    message = models.TextField()
    data = models.JSONField(
        default=dict,
        help_text=_('Additional data for the notification')
    )
    is_read = models.BooleanField(default=False)
    is_email_sent = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.pk:  # New notification
            # Get user's notification preferences
            prefs = NotificationPreference.objects.get_or_create(
                user=self.user
            )[0]

            # Check if email should be sent
            should_send_email = False
            if self.type == 'CONTRIBUTION' and prefs.email_contribution:
                should_send_email = True
            elif self.type == 'WISHLIST_SHARE' and prefs.email_wishlist_invite:
                should_send_email = True
            elif self.type == 'SUBSCRIPTION_EXPIRY' and prefs.email_subscription:
                should_send_email = True
            elif self.type == 'PRICE_CHANGE' and prefs.email_price_changes:
                should_send_email = True

            # Send email notification
            if should_send_email:
                from core.tasks.notifications import send_email_notification
                template_name = self.type.lower()
                send_email_notification.delay(
                    user_id=self.user.id,
                    subject=self.title,
                    template_name=template_name,
                    context={'notification': self, **self.data}
                )
                self.is_email_sent = True

        super().save(*args, **kwargs)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['type', '-created_at'])
        ]

    def __str__(self):
        return f"{self.type} notification for {self.user.username}"
