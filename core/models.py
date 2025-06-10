from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator, MaxValueValidator
from decimal import Decimal
import uuid
from django.utils import timezone


class User(AbstractUser):
    """Extended user model with wallet and profile features"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    profile_image = models.ImageField(
        upload_to='profiles/', blank=True, null=True)
    bio = models.TextField(max_length=500, blank=True)
    birth_date = models.DateField(blank=True, null=True)
    wallet_balance = models.DecimalField(
        max_digits=12, decimal_places=2, default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00'))]
    )
    is_verified = models.BooleanField(default=False)
    verification_token = models.CharField(
        max_length=100, blank=True, null=True)

    # Privacy Settings
    profile_visibility = models.CharField(
        max_length=20,
        choices=[
            ('PUBLIC', 'عمومی'),
            ('FRIENDS', 'دوستان'),
            ('PRIVATE', 'خصوصی'),
        ],
        default='PUBLIC'
    )

    # Social Features
    followers = models.ManyToManyField(
        'self', through='UserFollow', symmetrical=False,
        related_name='following', blank=True
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('کاربر')
        verbose_name_plural = _('کاربران')

    def __str__(self):
        return f"{self.get_full_name() or self.username}"

    @property
    def available_balance(self):
        """Calculate available balance excluding pending transactions"""
        pending_amount = self.wallet_transactions.filter(
            status='PENDING'
        ).aggregate(
            total=models.Sum('amount')
        )['total'] or Decimal('0.00')
        return self.wallet_balance - pending_amount


class UserFollow(models.Model):
    """Follow relationship between users"""
    follower = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='following_set')
    followed = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='followers_set')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['follower', 'followed']
        verbose_name = _('دنبال کردن')
        verbose_name_plural = _('دنبال کردن‌ها')


class Category(models.Model):
    """Categories for wishlist items"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    name_en = models.CharField(max_length=100, blank=True)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, blank=True)
    color = models.CharField(max_length=7, default='#6366f1')
    parent = models.ForeignKey(
        'self', on_delete=models.CASCADE, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    sort_order = models.PositiveIntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['sort_order', 'name']
        verbose_name = _('دسته‌بندی')
        verbose_name_plural = _('دسته‌بندی‌ها')

    def __str__(self):
        return self.name


class Tag(models.Model):
    """Tags for wishlist items"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=50, unique=True)
    color = models.CharField(max_length=7, default='#64748b')
    usage_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-usage_count', 'name']
        verbose_name = _('برچسب')
        verbose_name_plural = _('برچسب‌ها')

    def __str__(self):
        return self.name


class Occasion(models.Model):
    """Special occasions/events"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    icon = models.CharField(max_length=50, blank=True)
    color = models.CharField(max_length=7, default='#f59e0b')
    is_recurring = models.BooleanField(default=False)
    sort_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['sort_order', 'name']
        verbose_name = _('مناسبت')
        verbose_name_plural = _('مناسبت‌ها')

    def __str__(self):
        return self.name


class Wishlist(models.Model):
    """Main wishlist model"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    slug = models.SlugField(max_length=100, unique=True, blank=True)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    owner = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='wishlists')
    occasion = models.ForeignKey(
        Occasion, on_delete=models.SET_NULL, null=True, blank=True)
    occasion_date = models.DateField(null=True, blank=True)

    # Privacy & Sharing
    visibility = models.CharField(
        max_length=20,
        choices=[
            ('PUBLIC', 'عمومی'),
            ('UNLISTED', 'با لینک'),
            ('FRIENDS', 'دوستان'),
            ('PRIVATE', 'خصوصی'),
        ],
        default='PUBLIC'
    )
    allow_contributions = models.BooleanField(default=True)
    allow_anonymous_contributions = models.BooleanField(default=True)

    # Design & Appearance
    cover_image = models.ImageField(
        upload_to='wishlists/', blank=True, null=True)
    theme_color = models.CharField(max_length=7, default='#6366f1')

    # Status
    is_active = models.BooleanField(default=True)
    is_completed = models.BooleanField(default=False)
    completion_date = models.DateTimeField(null=True, blank=True)

    # Stats
    view_count = models.PositiveIntegerField(default=0)
    share_count = models.PositiveIntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['owner', 'is_active']),
            models.Index(fields=['visibility', 'is_active']),
        ]
        verbose_name = _('لیست آرزو')
        verbose_name_plural = _('لیست‌های آرزو')

    def __str__(self):
        return f"{self.title} - {self.owner.get_full_name() or self.owner.username}"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = str(uuid.uuid4())[:10].lower()
        super().save(*args, **kwargs)

    @property
    def total_value(self):
        return self.items.aggregate(
            total=models.Sum('price')
        )['total'] or Decimal('0.00')

    @property
    def total_contributed(self):
        return self.items.aggregate(
            total=models.Sum('contributed_amount')
        )['total'] or Decimal('0.00')

    @property
    def completion_percentage(self):
        if self.total_value == 0:
            return 0
        return round((self.total_contributed / self.total_value) * 100, 2)


class WishlistItem(models.Model):
    """Items in a wishlist"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    wishlist = models.ForeignKey(
        Wishlist, on_delete=models.CASCADE, related_name='items')
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=12, decimal_places=2)
    contributed_amount = models.DecimalField(
        max_digits=12, decimal_places=2, default=Decimal('0.00')
    )

    # Product Details
    product_url = models.URLField(blank=True)
    image = models.ImageField(upload_to='items/', blank=True, null=True)
    brand = models.CharField(max_length=100, blank=True)
    model = models.CharField(max_length=100, blank=True)

    # Classification
    category = models.ForeignKey(
        Category, on_delete=models.SET_NULL, null=True, blank=True)
    tags = models.ManyToManyField(Tag, blank=True)

    # Priority & Status
    priority = models.PositiveSmallIntegerField(
        default=3,
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="1=کم، 5=زیاد"
    )
    status = models.CharField(
        max_length=20,
        choices=[
            ('ACTIVE', 'فعال'),
            ('RESERVED', 'رزرو شده'),
            ('PURCHASED', 'خریداری شده'),
            ('RECEIVED', 'دریافت شده'),
            ('CANCELLED', 'لغو شده'),
        ],
        default='ACTIVE'
    )

    # Purchase Details
    purchased_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='purchased_items'
    )
    purchased_at = models.DateTimeField(null=True, blank=True)
    purchase_notes = models.TextField(blank=True)

    # Metadata
    external_ids = models.JSONField(default=dict, blank=True)
    sort_order = models.PositiveIntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['sort_order', '-priority', '-created_at']
        indexes = [
            models.Index(fields=['wishlist', 'status']),
            models.Index(fields=['status', 'priority']),
        ]
        verbose_name = _('آیتم آرزو')
        verbose_name_plural = _('آیتم‌های آرزو')

    def __str__(self):
        return f"{self.name} - {self.wishlist.title}"

    @property
    def remaining_amount(self):
        return max(Decimal('0.00'), self.price - self.contributed_amount)

    @property
    def completion_percentage(self):
        if self.price == 0:
            return 0
        return min(100, round((self.contributed_amount / self.price) * 100, 2))

    @property
    def is_fully_funded(self):
        return self.contributed_amount >= self.price


class WalletTransaction(models.Model):
    """Wallet transactions for users"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='wallet_transactions')
    transaction_type = models.CharField(
        max_length=20,
        choices=[
            ('DEPOSIT', 'واریز'),
            ('WITHDRAW', 'برداشت'),
            ('CONTRIBUTION', 'کمک'),
            ('REFUND', 'بازگشت وجه'),
            ('PURCHASE', 'خرید'),
            ('BONUS', 'جایزه'),
        ]
    )
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    status = models.CharField(
        max_length=20,
        choices=[
            ('PENDING', 'در انتظار'),
            ('COMPLETED', 'تکمیل شده'),
            ('FAILED', 'ناموفق'),
            ('CANCELLED', 'لغو شده'),
        ],
        default='PENDING'
    )

    # Related Objects
    related_item = models.ForeignKey(
        WishlistItem, on_delete=models.SET_NULL, null=True, blank=True
    )
    related_contribution = models.ForeignKey(
        'Contribution', on_delete=models.SET_NULL, null=True, blank=True
    )

    # Payment Details
    payment_method = models.CharField(max_length=50, blank=True)
    transaction_id = models.CharField(max_length=100, blank=True)
    reference_number = models.CharField(max_length=100, blank=True)

    # Description & Notes
    description = models.CharField(max_length=200)
    notes = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['transaction_type', 'status']),
        ]
        verbose_name = _('تراکنش کیف پول')
        verbose_name_plural = _('تراکنش‌های کیف پول')

    def __str__(self):
        return f"{self.user.username} - {self.get_transaction_type_display()} - {self.amount}"


class Contribution(models.Model):
    """Contributions to wishlist items"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    item = models.ForeignKey(
        WishlistItem, on_delete=models.CASCADE, related_name='contributions')
    contributor = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name='contributions'
    )
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    message = models.TextField(blank=True)
    is_anonymous = models.BooleanField(default=False)

    # Guest Contribution Support
    guest_name = models.CharField(max_length=100, blank=True)
    guest_email = models.EmailField(blank=True)

    # Status & Payment
    status = models.CharField(
        max_length=20,
        choices=[
            ('PENDING', 'در انتظار'),
            ('COMPLETED', 'تکمیل شده'),
            ('FAILED', 'ناموفق'),
            ('REFUNDED', 'بازگشت داده شده'),
        ],
        default='PENDING'
    )
    wallet_transaction = models.OneToOneField(
        WalletTransaction, on_delete=models.SET_NULL, null=True, blank=True
    )

    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['item', 'status']),
            models.Index(fields=['contributor', 'status']),
        ]
        verbose_name = _('کمک')
        verbose_name_plural = _('کمک‌ها')

    def __str__(self):
        contributor_name = self.guest_name or (
            self.contributor.get_full_name() if self.contributor else 'ناشناس'
        )
        return f"{contributor_name} - {self.amount} - {self.item.name}"


class SubscriptionPlan(models.Model):
    """Subscription plans for premium features"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    name_en = models.CharField(max_length=100, blank=True)
    description = models.TextField()

    # Pricing
    monthly_price = models.DecimalField(max_digits=10, decimal_places=2)
    yearly_price = models.DecimalField(max_digits=10, decimal_places=2)
    yearly_discount_percentage = models.PositiveIntegerField(default=0)

    # Features & Limits
    max_wishlists = models.PositiveIntegerField(default=5)
    max_items_per_wishlist = models.PositiveIntegerField(default=50)
    max_image_uploads = models.PositiveIntegerField(default=100)
    can_use_custom_domains = models.BooleanField(default=False)
    can_export_data = models.BooleanField(default=False)
    priority_support = models.BooleanField(default=False)
    advanced_analytics = models.BooleanField(default=False)

    # Display
    color = models.CharField(max_length=7, default='#6366f1')
    sort_order = models.PositiveIntegerField(default=0)
    is_popular = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['sort_order', 'monthly_price']
        verbose_name = _('طرح اشتراک')
        verbose_name_plural = _('طرح‌های اشتراک')

    def __str__(self):
        return self.name


class UserSubscription(models.Model):
    """User subscription to plans"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name='subscription')
    plan = models.ForeignKey(SubscriptionPlan, on_delete=models.PROTECT)

    # Subscription Details
    is_active = models.BooleanField(default=True)
    start_date = models.DateTimeField(auto_now_add=True)
    end_date = models.DateTimeField()
    auto_renew = models.BooleanField(default=True)

    # Payment Info
    payment_method = models.CharField(max_length=50, blank=True)
    last_payment_date = models.DateTimeField(null=True, blank=True)
    next_payment_date = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('اشتراک کاربر')
        verbose_name_plural = _('اشتراک‌های کاربران')

    def __str__(self):
        return f"{self.user.username} - {self.plan.name}"

    @property
    def is_expired(self):
        return timezone.now() > self.end_date

    @property
    def days_remaining(self):
        if self.is_expired:
            return 0
        return (self.end_date - timezone.now()).days


class Notification(models.Model):
    """User notifications"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='notifications')
    title = models.CharField(max_length=200, default='اعلان')
    message = models.TextField()
    notification_type = models.CharField(
        max_length=30,
        choices=[
            ('CONTRIBUTION', 'کمک جدید'),
            ('WISHLIST_COMPLETE', 'تکمیل لیست آرزو'),
            ('ITEM_PURCHASED', 'خرید آیتم'),
            ('FOLLOWER_NEW', 'دنبال‌کننده جدید'),
            ('OCCASION_REMINDER', 'یادآوری مناسبت'),
            ('SUBSCRIPTION_EXPIRY', 'انقضای اشتراک'),
            ('SYSTEM', 'سیستم'),
        ],
        default='SYSTEM'
    )

    # Related Objects
    related_wishlist = models.ForeignKey(
        Wishlist, on_delete=models.CASCADE, null=True, blank=True
    )
    related_item = models.ForeignKey(
        WishlistItem, on_delete=models.CASCADE, null=True, blank=True
    )
    related_user = models.ForeignKey(
        User, on_delete=models.CASCADE, null=True, blank=True,
        related_name='triggered_notifications'
    )

    # Status
    is_read = models.BooleanField(default=False)
    is_sent = models.BooleanField(default=False)

    # Delivery Channels
    send_push = models.BooleanField(default=True)
    send_email = models.BooleanField(default=False)
    send_sms = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    read_at = models.DateTimeField(null=True, blank=True)
    sent_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'is_read']),
            models.Index(fields=['notification_type', 'is_sent']),
        ]
        verbose_name = _('اعلان')
        verbose_name_plural = _('اعلان‌ها')

    def __str__(self):
        return f"{self.user.username} - {self.title}"


class WishlistShare(models.Model):
    """مدل اشتراک‌گذاری لیست آرزو"""
    SHARE_TYPE_CHOICES = [
        ('PUBLIC', 'عمومی'),
        ('PRIVATE', 'خصوصی'),
        ('FRIENDS', 'دوستان'),
        ('LINK', 'با لینک'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    wishlist = models.ForeignKey(
        Wishlist, on_delete=models.CASCADE, related_name='shares')
    shared_by = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='shared_wishlists')
    share_type = models.CharField(
        max_length=20, choices=SHARE_TYPE_CHOICES, default='PRIVATE')

    # لینک اشتراک‌گذاری
    share_token = models.CharField(max_length=64, unique=True, blank=True)
    expires_at = models.DateTimeField(null=True, blank=True)

    # تنظیمات اشتراک‌گذاری
    allow_contributions = models.BooleanField(default=True)
    allow_comments = models.BooleanField(default=True)
    show_progress = models.BooleanField(default=True)

    # آمار
    view_count = models.PositiveIntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['wishlist', 'shared_by']

    def save(self, *args, **kwargs):
        if not self.share_token:
            self.share_token = self.generate_share_token()
        super().save(*args, **kwargs)

    def generate_share_token(self):
        """تولید توکن منحصر به فرد برای اشتراک‌گذاری"""
        import secrets
        return secrets.token_urlsafe(32)

    def get_share_url(self):
        """دریافت URL اشتراک‌گذاری"""
        from django.conf import settings
        base_url = getattr(settings, 'FRONTEND_BASE_URL',
                           'http://localhost:3000')
        return f"{base_url}/shared/wishlist/{self.share_token}"

    def is_expired(self):
        """بررسی انقضای لینک اشتراک‌گذاری"""
        if not self.expires_at:
            return False
        from django.utils import timezone
        return timezone.now() > self.expires_at

    def __str__(self):
        return f"Share: {self.wishlist.title} by {self.shared_by.username}"


class WishlistInvitation(models.Model):
    """مدل دعوت دوستان برای کمک مالی"""
    STATUS_CHOICES = [
        ('PENDING', 'در انتظار'),
        ('ACCEPTED', 'پذیرفته شده'),
        ('DECLINED', 'رد شده'),
        ('EXPIRED', 'منقضی شده'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    wishlist_item = models.ForeignKey(
        WishlistItem, on_delete=models.CASCADE, related_name='invitations')
    invited_by = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='sent_invitations')

    # اطلاعات دعوت‌شده
    invited_email = models.EmailField()
    invited_phone = models.CharField(max_length=15, blank=True)
    invited_name = models.CharField(max_length=100, blank=True)

    # پیام دعوت
    message = models.TextField(blank=True)
    suggested_amount = models.DecimalField(
        max_digits=12, decimal_places=2, null=True, blank=True)

    # وضعیت
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default='PENDING')
    invitation_token = models.CharField(max_length=64, unique=True)

    # زمان‌ها
    sent_at = models.DateTimeField(auto_now_add=True)
    responded_at = models.DateTimeField(null=True, blank=True)
    expires_at = models.DateTimeField()

    def save(self, *args, **kwargs):
        if not self.invitation_token:
            self.invitation_token = self.generate_invitation_token()
        if not self.expires_at:
            from django.utils import timezone
            from datetime import timedelta
            self.expires_at = timezone.now() + timedelta(days=7)  # 7 روز اعتبار
        super().save(*args, **kwargs)

    def generate_invitation_token(self):
        """تولید توکن دعوت"""
        import secrets
        return secrets.token_urlsafe(32)

    def get_invitation_url(self):
        """دریافت URL دعوت"""
        from django.conf import settings
        base_url = getattr(settings, 'FRONTEND_BASE_URL',
                           'http://localhost:3000')
        return f"{base_url}/invitation/{self.invitation_token}"

    def is_expired(self):
        """بررسی انقضای دعوت"""
        from django.utils import timezone
        return timezone.now() > self.expires_at

    def accept_invitation(self):
        """پذیرش دعوت"""
        if self.is_expired():
            return False, "دعوت منقضی شده است"

        self.status = 'ACCEPTED'
        from django.utils import timezone
        self.responded_at = timezone.now()
        self.save()
        return True, "دعوت پذیرفته شد"

    def decline_invitation(self):
        """رد دعوت"""
        self.status = 'DECLINED'
        from django.utils import timezone
        self.responded_at = timezone.now()
        self.save()
        return True, "دعوت رد شد"

    def __str__(self):
        return f"Invitation to {self.invited_email} for {self.wishlist_item.title}"


class SocialShare(models.Model):
    """مدل اشتراک‌گذاری در شبکه‌های اجتماعی"""
    PLATFORM_CHOICES = [
        ('TELEGRAM', 'تلگرام'),
        ('WHATSAPP', 'واتساپ'),
        ('INSTAGRAM', 'اینستاگرام'),
        ('TWITTER', 'توییتر'),
        ('SMS', 'پیامک'),
        ('EMAIL', 'ایمیل'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    wishlist_item = models.ForeignKey(
        WishlistItem, on_delete=models.CASCADE, related_name='social_shares')
    shared_by = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='social_shares')

    platform = models.CharField(max_length=20, choices=PLATFORM_CHOICES)
    share_content = models.TextField()  # محتوای اشتراک‌گذاری شده

    # آمار
    click_count = models.PositiveIntegerField(default=0)
    conversion_count = models.PositiveIntegerField(
        default=0)  # تعداد کمک‌های ناشی از این اشتراک

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['wishlist_item', 'shared_by', 'platform']

    def __str__(self):
        return f"Social Share: {self.wishlist_item.title} on {self.platform}"


class ContributionGoal(models.Model):
    """مدل هدف‌گذاری کمک مالی"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    wishlist_item = models.OneToOneField(
        WishlistItem, on_delete=models.CASCADE, related_name='contribution_goal')

    # هدف‌ها
    target_amount = models.DecimalField(max_digits=12, decimal_places=2)
    target_contributors = models.PositiveIntegerField(default=1)
    deadline = models.DateTimeField(null=True, blank=True)

    # وضعیت
    is_achieved = models.BooleanField(default=False)
    achieved_at = models.DateTimeField(null=True, blank=True)

    # پاداش برای کمک‌کنندگان
    reward_message = models.TextField(blank=True)
    milestone_messages = models.JSONField(
        default=dict, blank=True)  # پیام‌ها برای مراحل مختلف

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def get_progress_percentage(self):
        """درصد پیشرفت"""
        from payment.models import ContributionRecord
        total_contributed = ContributionRecord.objects.filter(
            wishlist_item=self.wishlist_item
        ).aggregate(
            total=models.Sum('amount')
        )['total'] or 0

        if self.target_amount <= 0:
            return 0

        percentage = (total_contributed / self.target_amount) * 100
        return min(percentage, 100)

    def check_achievement(self):
        """بررسی دستیابی به هدف"""
        if self.is_achieved:
            return True

        progress = self.get_progress_percentage()
        if progress >= 100:
            self.is_achieved = True
            from django.utils import timezone
            self.achieved_at = timezone.now()
            self.save()
            return True

        return False

    def __str__(self):
        return f"Goal: {self.wishlist_item.title} - {self.target_amount} ریال"


class OTPVerification(models.Model):
    """مدل تایید کد OTP برای موبایل"""
    OTP_TYPE_CHOICES = [
        ('REGISTRATION', 'ثبت‌نام'),
        ('LOGIN', 'ورود'),
        ('PASSWORD_RESET', 'بازیابی رمز عبور'),
        ('PHONE_VERIFICATION', 'تایید شماره موبایل'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    phone_number = models.CharField(max_length=15)
    otp_code = models.CharField(max_length=6)
    otp_type = models.CharField(max_length=20, choices=OTP_TYPE_CHOICES)

    # وضعیت
    is_verified = models.BooleanField(default=False)
    attempts_count = models.PositiveIntegerField(default=0)
    max_attempts = models.PositiveIntegerField(default=3)

    # زمان‌ها
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    verified_at = models.DateTimeField(null=True, blank=True)

    # IP و امنیت
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['phone_number', 'otp_type', 'is_verified']),
            models.Index(fields=['expires_at']),
        ]
        verbose_name = _('تایید OTP')
        verbose_name_plural = _('تایید‌های OTP')

    def __str__(self):
        return f"{self.phone_number} - {self.get_otp_type_display()} - {self.otp_code}"

    def save(self, *args, **kwargs):
        if not self.expires_at:
            # OTP به مدت 5 دقیقه معتبر است
            self.expires_at = timezone.now() + timezone.timedelta(minutes=5)
        super().save(*args, **kwargs)

    @property
    def is_expired(self):
        return timezone.now() > self.expires_at

    def verify(self, entered_code):
        """تایید کد OTP"""
        if self.is_expired:
            return False, 'کد OTP منقضی شده است'

        if self.attempts_count >= self.max_attempts:
            return False, 'تعداد تلاش‌های مجاز تمام شده است'

        self.attempts_count += 1

        if self.otp_code == entered_code:
            self.is_verified = True
            self.verified_at = timezone.now()
            self.save()
            return True, 'کد OTP با موفقیت تایید شد'
        else:
            self.save()
            remaining = self.max_attempts - self.attempts_count
            if remaining > 0:
                return False, f'کد OTP اشتباه است. {remaining} تلاش باقی مانده'
            else:
                return False, 'کد OTP اشتباه است. تعداد تلاش‌های مجاز تمام شده'

    @classmethod
    def generate_otp(cls, phone_number, otp_type, ip_address=None, user_agent=''):
        """تولید OTP جدید"""
        import random

        # حذف OTP های قبلی برای همین شماره و نوع
        cls.objects.filter(
            phone_number=phone_number,
            otp_type=otp_type,
            is_verified=False
        ).delete()

        # تولید کد 6 رقمی
        otp_code = str(random.randint(100000, 999999))

        otp = cls.objects.create(
            phone_number=phone_number,
            otp_code=otp_code,
            otp_type=otp_type,
            ip_address=ip_address,
            user_agent=user_agent
        )

        return otp


class PhoneVerificationLog(models.Model):
    """لاگ تلاش‌های تایید شماره موبایل"""
    phone_number = models.CharField(max_length=15)
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField(blank=True)
    success = models.BooleanField(default=False)
    attempt_type = models.CharField(max_length=20)  # OTP_SEND, OTP_VERIFY
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = _('لاگ تایید موبایل')
        verbose_name_plural = _('لاگ‌های تایید موبایل')

    def __str__(self):
        return f"{self.phone_number} - {self.attempt_type} - {'موفق' if self.success else 'ناموفق'}"


class EmailVerification(models.Model):
    """مدل تایید ایمیل"""
    VERIFICATION_TYPES = (
        ('REGISTER', 'ثبت‌نام'),
        ('LOGIN', 'ورود'),
        ('RESET_PASSWORD', 'بازیابی رمز عبور'),
        ('CHANGE_EMAIL', 'تغییر ایمیل'),
    )

    email = models.EmailField(verbose_name='ایمیل', db_index=True)
    verification_type = models.CharField(
        max_length=20, choices=VERIFICATION_TYPES,
        verbose_name='نوع تایید'
    )
    token = models.CharField(
        max_length=100, unique=True, verbose_name='توکن تایید'
    )
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, null=True, blank=True,
        verbose_name='کاربر', related_name='email_verifications'
    )

    # Security fields
    ip_address = models.GenericIPAddressField(
        null=True, blank=True, verbose_name='آدرس IP'
    )
    user_agent = models.TextField(
        blank=True, verbose_name='User Agent'
    )

    # Status fields
    is_verified = models.BooleanField(
        default=False, verbose_name='تایید شده'
    )
    attempts_count = models.PositiveIntegerField(
        default=0, verbose_name='تعداد تلاش'
    )
    max_attempts = models.PositiveIntegerField(
        default=5, verbose_name='حداکثر تلاش'
    )

    # Timestamps
    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name='تاریخ ایجاد'
    )
    verified_at = models.DateTimeField(
        null=True, blank=True, verbose_name='تاریخ تایید'
    )
    expires_at = models.DateTimeField(
        verbose_name='تاریخ انقضا'
    )

    # Additional data
    extra_data = models.JSONField(
        default=dict, blank=True,
        verbose_name='داده‌های اضافی'
    )

    class Meta:
        verbose_name = 'تایید ایمیل'
        verbose_name_plural = 'تاییدهای ایمیل'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['email', 'verification_type']),
            models.Index(fields=['token']),
            models.Index(fields=['created_at']),
            models.Index(fields=['expires_at']),
        ]

    def __str__(self):
        return f'{self.email} - {self.get_verification_type_display()}'

    @property
    def is_expired(self):
        """بررسی انقضای توکن"""
        from django.utils import timezone
        return timezone.now() > self.expires_at

    @property
    def can_attempt(self):
        """بررسی امکان تلاش مجدد"""
        return self.attempts_count < self.max_attempts and not self.is_expired

    def mark_as_verified(self):
        """علامت‌گذاری به عنوان تایید شده"""
        from django.utils import timezone
        self.is_verified = True
        self.verified_at = timezone.now()
        self.save(update_fields=['is_verified', 'verified_at'])

    def increment_attempts(self):
        """افزایش تعداد تلاش"""
        self.attempts_count += 1
        self.save(update_fields=['attempts_count'])


class EmailVerificationLog(models.Model):
    """لاگ تلاش‌های تایید ایمیل"""
    ATTEMPT_TYPES = (
        ('SEND', 'ارسال'),
        ('VERIFY', 'تایید'),
        ('RESEND', 'ارسال مجدد'),
    )

    email = models.EmailField(verbose_name='ایمیل', db_index=True)
    attempt_type = models.CharField(
        max_length=10, choices=ATTEMPT_TYPES,
        verbose_name='نوع تلاش'
    )
    ip_address = models.GenericIPAddressField(
        null=True, blank=True, verbose_name='آدرس IP', db_index=True
    )
    user_agent = models.TextField(
        blank=True, verbose_name='User Agent'
    )
    success = models.BooleanField(
        default=False, verbose_name='موفق'
    )
    error_message = models.TextField(
        blank=True, verbose_name='پیام خطا'
    )
    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name='تاریخ ایجاد', db_index=True
    )

    class Meta:
        verbose_name = 'لاگ تایید ایمیل'
        verbose_name_plural = 'لاگ‌های تایید ایمیل'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['email', 'created_at']),
            models.Index(fields=['ip_address', 'created_at']),
        ]

    def __str__(self):
        return f'{self.email} - {self.get_attempt_type_display()}'


class DeviceFingerprint(models.Model):
    """ردپای دستگاه برای تشخیص ربات"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    fingerprint_hash = models.CharField(max_length=64, unique=True)

    # اطلاعات دستگاه
    user_agent = models.TextField()
    screen_resolution = models.CharField(max_length=20, blank=True)
    timezone = models.CharField(max_length=50, blank=True)
    language = models.CharField(max_length=10, blank=True)
    platform = models.CharField(max_length=50, blank=True)

    # اطلاعات مرورگر
    browser_name = models.CharField(max_length=50, blank=True)
    browser_version = models.CharField(max_length=20, blank=True)
    plugins_hash = models.CharField(max_length=64, blank=True)

    # آمار امنیتی
    registration_attempts = models.PositiveIntegerField(default=0)
    successful_registrations = models.PositiveIntegerField(default=0)
    last_seen = models.DateTimeField(auto_now=True)
    is_suspicious = models.BooleanField(default=False)
    risk_score = models.FloatField(default=0.0)  # 0-100

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=['fingerprint_hash']),
            models.Index(fields=['is_suspicious', 'risk_score']),
        ]
        verbose_name = _('ردپای دستگاه')
        verbose_name_plural = _('ردپای‌های دستگاه')

    def __str__(self):
        return f"Device {self.fingerprint_hash[:8]} - Risk: {self.risk_score}"

    def update_risk_score(self):
        """محاسبه امتیاز ریسک"""
        risk_factors = []

        # نسبت ثبت‌نام موفق به تلاش
        if self.registration_attempts > 0:
            success_rate = self.successful_registrations / self.registration_attempts
            if success_rate < 0.1:  # کمتر از 10% موفقیت
                risk_factors.append(30)

        # تعداد زیاد تلاش
        if self.registration_attempts > 5:
            risk_factors.append(25)

        # User Agent مشکوک
        suspicious_agents = ['bot', 'crawler', 'spider', 'scraper']
        if any(agent in self.user_agent.lower() for agent in suspicious_agents):
            risk_factors.append(40)

        # عدم وجود اطلاعات مرورگر
        if not self.screen_resolution or not self.timezone:
            risk_factors.append(20)

        self.risk_score = min(100, sum(risk_factors))
        self.is_suspicious = self.risk_score > 60
        self.save(update_fields=['risk_score', 'is_suspicious'])


class IPReputationLog(models.Model):
    """لاگ و امتیازدهی IP ها"""
    ip_address = models.GenericIPAddressField(db_index=True)

    # آمار فعالیت
    registration_attempts = models.PositiveIntegerField(default=0)
    successful_registrations = models.PositiveIntegerField(default=0)
    failed_otp_attempts = models.PositiveIntegerField(default=0)
    captcha_failures = models.PositiveIntegerField(default=0)

    # وضعیت امنیتی
    is_blocked = models.BooleanField(default=False)
    block_reason = models.CharField(max_length=200, blank=True)
    blocked_until = models.DateTimeField(null=True, blank=True)
    risk_score = models.FloatField(default=0.0)

    # اطلاعات جغرافیایی (اختیاری)
    country_code = models.CharField(max_length=2, blank=True)
    is_vpn = models.BooleanField(default=False)
    is_proxy = models.BooleanField(default=False)

    first_seen = models.DateTimeField(auto_now_add=True)
    last_activity = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=['ip_address', 'is_blocked']),
            models.Index(fields=['risk_score']),
        ]
        verbose_name = _('امتیاز IP')
        verbose_name_plural = _('امتیازات IP')

    def __str__(self):
        return f"IP {self.ip_address} - Risk: {self.risk_score}"

    def is_currently_blocked(self):
        """بررسی اینکه IP در حال حاضر مسدود است یا نه"""
        if not self.is_blocked:
            return False

        if self.blocked_until and timezone.now() > self.blocked_until:
            # انقضای مسدودیت
            self.is_blocked = False
            self.blocked_until = None
            self.save(update_fields=['is_blocked', 'blocked_until'])
            return False

        return True

    def update_risk_score(self):
        """محاسبه امتیاز ریسک IP"""
        risk_factors = []

        # نسبت شکست به موفقیت
        total_attempts = self.registration_attempts + self.failed_otp_attempts
        if total_attempts > 0:
            failure_rate = (self.failed_otp_attempts +
                            self.captcha_failures) / total_attempts
            if failure_rate > 0.7:  # بیش از 70% شکست
                risk_factors.append(35)

        # تعداد زیاد تلاش
        if self.registration_attempts > 10:
            risk_factors.append(30)

        # استفاده از VPN/Proxy
        if self.is_vpn or self.is_proxy:
            risk_factors.append(20)

        # تلاش‌های پی در پی ناموفق
        if self.failed_otp_attempts > 15:
            risk_factors.append(25)

        self.risk_score = min(100, sum(risk_factors))

        # مسدود کردن خودکار
        if self.risk_score > 80:
            self.is_blocked = True
            self.block_reason = 'امتیاز ریسک بالا (خودکار)'
            self.blocked_until = timezone.now() + timezone.timedelta(hours=24)

        self.save(update_fields=['risk_score',
                  'is_blocked', 'block_reason', 'blocked_until'])


class BehaviorAnalysis(models.Model):
    """تحلیل رفتار کاربر برای تشخیص ربات"""
    session_id = models.CharField(max_length=64, db_index=True)
    ip_address = models.GenericIPAddressField()
    device_fingerprint = models.ForeignKey(
        DeviceFingerprint, on_delete=models.SET_NULL, null=True, blank=True)

    # رفتار در فرم
    form_fill_time = models.FloatField(null=True)  # ثانیه
    typing_speed = models.FloatField(null=True)  # کاراکتر در ثانیه
    mouse_movements = models.PositiveIntegerField(default=0)
    clicks_count = models.PositiveIntegerField(default=0)
    key_presses = models.PositiveIntegerField(default=0)

    # رفتار مشکوک
    copy_paste_detected = models.BooleanField(default=False)
    auto_fill_detected = models.BooleanField(default=False)
    multiple_tabs = models.BooleanField(default=False)

    # زمان‌بندی
    time_on_page = models.FloatField(null=True)  # ثانیه
    created_at = models.DateTimeField(auto_now_add=True)

    # نتیجه تحلیل
    is_human_like = models.BooleanField(default=True)
    bot_probability = models.FloatField(default=0.0)  # 0-1

    class Meta:
        indexes = [
            models.Index(fields=['session_id']),
            models.Index(fields=['ip_address', 'created_at']),
        ]
        verbose_name = _('تحلیل رفتار')
        verbose_name_plural = _('تحلیل‌های رفتار')

    def __str__(self):
        return f"Session {self.session_id[:8]} - Bot Probability: {self.bot_probability:.2f}"

    def analyze_behavior(self):
        """تحلیل رفتار و تشخیص ربات"""
        bot_indicators = []

        # پر کردن فوری فرم (کمتر از 2 ثانیه)
        if self.form_fill_time and self.form_fill_time < 2:
            bot_indicators.append(0.4)

        # سرعت تایپ غیرطبیعی (بیش از 10 کاراکتر در ثانیه)
        if self.typing_speed and self.typing_speed > 10:
            bot_indicators.append(0.3)

        # عدم حرکت ماوس
        if self.mouse_movements == 0:
            bot_indicators.append(0.3)

        # استفاده از copy-paste
        if self.copy_paste_detected:
            bot_indicators.append(0.2)

        # زمان کم روی صفحه
        if self.time_on_page and self.time_on_page < 5:
            bot_indicators.append(0.2)

        # محاسبه احتمال ربات بودن
        self.bot_probability = min(1.0, sum(bot_indicators))
        self.is_human_like = self.bot_probability < 0.5

        self.save(update_fields=['bot_probability', 'is_human_like'])

        return self.is_human_like


class CaptchaChallenge(models.Model):
    """چالش‌های Captcha"""
    CHALLENGE_TYPE_CHOICES = [
        ('MATH', 'ریاضی ساده'),
        ('TEXT', 'تشخیص متن'),
        ('IMAGE', 'انتخاب تصویر'),
        ('RECAPTCHA', 'Google reCAPTCHA'),
        ('HCAPTCHA', 'hCaptcha'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    session_id = models.CharField(max_length=64)
    ip_address = models.GenericIPAddressField()
    challenge_type = models.CharField(
        max_length=20, choices=CHALLENGE_TYPE_CHOICES)

    # سوال و جواب
    question = models.TextField()
    correct_answer = models.CharField(max_length=100)
    user_answer = models.CharField(max_length=100, blank=True)

    # وضعیت
    is_solved = models.BooleanField(default=False)
    attempts_count = models.PositiveIntegerField(default=0)
    max_attempts = models.PositiveIntegerField(default=3)

    # زمان‌بندی
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    solved_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        indexes = [
            models.Index(fields=['session_id', 'is_solved']),
            models.Index(fields=['expires_at']),
        ]
        verbose_name = _('چالش Captcha')
        verbose_name_plural = _('چالش‌های Captcha')

    def __str__(self):
        return f"Captcha {self.challenge_type} - {self.session_id[:8]}"

    def save(self, *args, **kwargs):
        if not self.expires_at:
            # Captcha به مدت 10 دقیقه معتبر است
            self.expires_at = timezone.now() + timezone.timedelta(minutes=10)
        super().save(*args, **kwargs)

    @property
    def is_expired(self):
        return timezone.now() > self.expires_at

    def verify_answer(self, user_answer):
        """تایید پاسخ کاربر"""
        if self.is_expired:
            return False, 'چالش منقضی شده است'

        if self.attempts_count >= self.max_attempts:
            return False, 'تعداد تلاش‌های مجاز تمام شده است'

        self.attempts_count += 1
        self.user_answer = user_answer

        if self.challenge_type == 'MATH':
            # بررسی پاسخ ریاضی
            try:
                if str(eval(self.question.replace('=', '').strip())) == user_answer.strip():
                    self.is_solved = True
                    self.solved_at = timezone.now()
                    self.save()
                    return True, 'پاسخ صحیح است'
            except:
                pass
        else:
            # بررسی پاسخ متنی
            if self.correct_answer.lower().strip() == user_answer.lower().strip():
                self.is_solved = True
                self.solved_at = timezone.now()
                self.save()
                return True, 'پاسخ صحیح است'

        self.save()
        remaining = self.max_attempts - self.attempts_count
        if remaining > 0:
            return False, f'پاسخ اشتباه است. {remaining} تلاش باقی مانده'
        else:
            return False, 'پاسخ اشتباه است. تعداد تلاش‌های مجاز تمام شده'

    @classmethod
    def generate_math_challenge(cls, session_id, ip_address):
        """تولید چالش ریاضی ساده"""
        import random

        # تولید سوال ریاضی ساده
        operations = ['+', '-', '*']
        operation = random.choice(operations)

        if operation == '*':
            a, b = random.randint(1, 9), random.randint(1, 9)
        else:
            a, b = random.randint(1, 50), random.randint(1, 50)

        if operation == '-' and a < b:
            a, b = b, a  # تضمین عدد مثبت

        question = f"{a} {operation} {b} = ?"
        answer = str(eval(f"{a} {operation} {b}"))

        return cls.objects.create(
            session_id=session_id,
            ip_address=ip_address,
            challenge_type='MATH',
            question=question,
            correct_answer=answer
        )
