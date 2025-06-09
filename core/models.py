from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator
from decimal import Decimal
from .models.categorization import Category, Tag

class User(AbstractUser):
    """Extended user model for additional functionality"""
    phone_number = models.CharField(max_length=15, blank=True)
    bio = models.TextField(blank=True)
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    wallet_balance = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00'))]
    )

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')

    def check_subscription_limits(self):
        """Check if user has reached their subscription limits"""
        try:
            subscription = self.subscription
            if not subscription.is_active:
                return False
            
            current_wishlists = self.wishlists.count()
            if current_wishlists >= subscription.plan.max_wishlists:
                return False
                
            return True
        except UserSubscription.DoesNotExist:
            return False

    def can_add_images(self):
        """Check if user's plan allows adding images"""
        try:
            return self.subscription.is_active and self.subscription.plan.can_add_images
        except UserSubscription.DoesNotExist:
            return False

    def can_receive_contributions(self):
        """Check if user's plan allows receiving contributions"""
        try:
            return self.subscription.is_active and self.subscription.plan.can_receive_contributions
        except UserSubscription.DoesNotExist:
            return False

class WishList(models.Model):
    """Model for user wishlists"""
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='wishlists')
    occasion_date = models.DateField(null=True, blank=True)
    is_public = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.owner.username}'s {self.title}"

class WishListItem(models.Model):
    """Model for items within a wishlist"""
    STATUS_CHOICES = [
        ('AVAILABLE', 'Available'),
        ('IN_PROGRESS', 'In Progress'),
        ('FULFILLED', 'Fulfilled')
    ]

    wishlist = models.ForeignKey(WishList, on_delete=models.CASCADE, related_name='items')
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    product_url = models.URLField(blank=True)
    image = models.ImageField(upload_to='wishlist_items/', null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='AVAILABLE')
    priority = models.PositiveSmallIntegerField(default=1)
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='items'
    )
    tags = models.ManyToManyField(Tag, blank=True, related_name='items')
    price_history = models.JSONField(default=list, blank=True)
    similar_items = models.ManyToManyField(
        'self',
        blank=True,
        symmetrical=False,
        related_name='related_items'
    )
    is_reserved = models.BooleanField(default=False)
    reserved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reserved_items'
    )
    reserved_until = models.DateTimeField(null=True, blank=True)
    external_ids = models.JSONField(
        default=dict,
        blank=True,
        help_text='Store IDs from external services (Amazon, etc.)'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['priority', '-created_at']

    def __str__(self):
        return f"{self.name} - {self.wishlist.title}"

class Contribution(models.Model):
    """Model for tracking contributions to wishlist items"""
    item = models.ForeignKey(WishListItem, on_delete=models.CASCADE, related_name='contributions')
    contributor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='contributions')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    message = models.TextField(blank=True)
    is_anonymous = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Contribution to {self.item.name} by {self.contributor.username if not self.is_anonymous else 'Anonymous'}"

class Notification(models.Model):
    """Model for user notifications"""
    NOTIFICATION_TYPES = [
        ('CONTRIBUTION', 'New Contribution'),
        ('WISHLIST_SHARE', 'Wishlist Shared'),
        ('ITEM_FULFILLED', 'Item Fulfilled'),
        ('OCCASION_REMINDER', 'Occasion Reminder'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

class Plan(models.Model):
    """Model for subscription plans"""
    PLAN_TYPES = [
        ('FREE', 'Free'),
        ('BASIC', 'Basic'),
        ('PREMIUM', 'Premium'),
        ('BUSINESS', 'Business'),
    ]
    
    DURATION_TYPES = [
        ('MONTHLY', 'Monthly'),
        ('YEARLY', 'Yearly'),
        ('LIFETIME', 'Lifetime'),
    ]

    name = models.CharField(max_length=50)
    type = models.CharField(max_length=20, choices=PLAN_TYPES)
    duration_type = models.CharField(
        max_length=20,
        choices=DURATION_TYPES,
        default='MONTHLY'
    )
    monthly_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text='Monthly price for the plan'
    )
    yearly_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text='Yearly price (usually discounted)'
    )
    lifetime_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text='One-time lifetime price'
    )
    max_wishlists = models.IntegerField(default=1)
    max_items_per_list = models.IntegerField(default=10)
    can_add_images = models.BooleanField(default=False)
    can_receive_contributions = models.BooleanField(default=False)
    priority_support = models.BooleanField(default=False)
    description = models.TextField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def get_price(self, duration_type):
        if duration_type == 'MONTHLY':
            return self.monthly_price
        elif duration_type == 'YEARLY':
            return self.yearly_price
        elif duration_type == 'LIFETIME':
            return self.lifetime_price
        return None

    def __str__(self):
        return f"{self.name} - {self.price}"

class UserSubscription(models.Model):
    """Model for user subscriptions"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='subscription')
    plan = models.ForeignKey(Plan, on_delete=models.PROTECT)
    start_date = models.DateTimeField(auto_now_add=True)
    end_date = models.DateTimeField()
    is_active = models.BooleanField(default=True)
    auto_renew = models.BooleanField(default=False)
    payment_id = models.CharField(max_length=100, blank=True)  # For payment gateway reference
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}'s {self.plan.name} subscription"

class PaymentHistory(models.Model):
    """Model for subscription payment history"""
    PAYMENT_STATUS = [
        ('PENDING', 'Pending'),
        ('SUCCESS', 'Success'),
        ('FAILED', 'Failed'),
        ('REFUNDED', 'Refunded'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='payments')
    subscription = models.ForeignKey(UserSubscription, on_delete=models.SET_NULL, null=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=PAYMENT_STATUS)
    payment_method = models.CharField(max_length=50)
    transaction_id = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username}'s payment - {self.amount}"
