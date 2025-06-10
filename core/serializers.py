from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from .models import (
    Wishlist, WishlistItem, Contribution, Notification,
    SubscriptionPlan, UserSubscription, Category, Tag,
    WishlistShare, WishlistInvitation, SocialShare,
    ContributionGoal
)

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True, validators=[validate_password])

    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            'phone_number', 'bio', 'avatar', 'wallet_balance', 'password'
        ]
        extra_kwargs = {
            'password': {'write_only': True},
            'wallet_balance': {'read_only': True}
        }

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User.objects.create_user(**validated_data)
        user.set_password(password)
        user.save()
        return user

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        user = super().update(instance, validated_data)
        if password:
            user.set_password(password)
            user.save()
        return user


class CategorySerializer(serializers.ModelSerializer):
    children = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ['id', 'name', 'description', 'icon',
                  'parent', 'children', 'created_at']

    def get_children(self, obj):
        if obj.children.exists():
            return CategorySerializer(obj.children.all(), many=True).data
        return []


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'name', 'color', 'created_at']


class WishlistSerializer(serializers.ModelSerializer):
    owner = UserSerializer(read_only=True)
    items_count = serializers.SerializerMethodField()
    total_value = serializers.SerializerMethodField()

    class Meta:
        model = Wishlist
        fields = [
            'id', 'title', 'description', 'owner', 'occasion_date',
            'is_public', 'created_at', 'updated_at', 'items_count', 'total_value'
        ]

    def get_items_count(self, obj):
        return obj.items.count()

    def get_total_value(self, obj):
        return obj.items.aggregate(
            total=serializers.models.Sum('price')
        )['total'] or 0


class WishlistItemSerializer(serializers.ModelSerializer):
    wishlist = WishlistSerializer(read_only=True)
    wishlist_id = serializers.IntegerField(write_only=True)
    category = CategorySerializer(read_only=True)
    category_id = serializers.IntegerField(write_only=True, required=False)
    tags = TagSerializer(many=True, read_only=True)
    tag_ids = serializers.ListField(
        child=serializers.IntegerField(), write_only=True, required=False
    )
    total_contributions = serializers.DecimalField(
        max_digits=10, decimal_places=2, read_only=True
    )
    remaining_amount = serializers.DecimalField(
        max_digits=10, decimal_places=2, read_only=True
    )
    contribution_percentage = serializers.SerializerMethodField()

    class Meta:
        model = WishlistItem
        fields = [
            'id', 'wishlist', 'wishlist_id', 'name', 'description', 'price',
            'product_url', 'image', 'status', 'priority', 'category', 'category_id',
            'tags', 'tag_ids', 'price_history', 'is_reserved', 'reserved_by',
            'reserved_until', 'external_ids', 'created_at', 'updated_at',
            'total_contributions', 'remaining_amount', 'contribution_percentage'
        ]

    def get_contribution_percentage(self, obj):
        if obj.price and hasattr(obj, 'total_contributions') and obj.total_contributions:
            return round((float(obj.total_contributions) / float(obj.price)) * 100, 2)
        return 0

    def create(self, validated_data):
        tag_ids = validated_data.pop('tag_ids', [])
        item = super().create(validated_data)
        if tag_ids:
            item.tags.set(tag_ids)
        return item

    def update(self, instance, validated_data):
        tag_ids = validated_data.pop('tag_ids', None)
        item = super().update(instance, validated_data)
        if tag_ids is not None:
            item.tags.set(tag_ids)
        return item


class ContributionSerializer(serializers.ModelSerializer):
    item = WishlistItemSerializer(read_only=True)
    contributor = UserSerializer(read_only=True)

    class Meta:
        model = Contribution
        fields = [
            'id', 'item', 'contributor', 'amount', 'message',
            'is_anonymous', 'created_at'
        ]


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = [
            'id', 'user', 'type', 'message', 'is_read', 'created_at'
        ]


class SubscriptionPlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubscriptionPlan
        fields = [
            'id', 'name', 'type', 'duration_type', 'monthly_price',
            'yearly_price', 'lifetime_price', 'max_wishlists',
            'max_items_per_list', 'can_add_images', 'can_receive_contributions',
            'priority_support', 'description', 'is_active', 'created_at'
        ]


class UserSubscriptionSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    plan = SubscriptionPlanSerializer(read_only=True)
    plan_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = UserSubscription
        fields = [
            'id', 'user', 'plan', 'plan_id', 'start_date', 'end_date',
            'is_active', 'auto_renew', 'payment_id', 'created_at', 'updated_at'
        ]


class WishlistShareSerializer(serializers.ModelSerializer):
    wishlist = WishlistSerializer(read_only=True)

    class Meta:
        model = WishlistShare
        fields = [
            'id', 'wishlist', 'shared_with', 'is_used',
            'created_at', 'expires_at'
        ]
        extra_kwargs = {
            'access_token': {'write_only': True}
        }


class WishlistPublicShareSerializer(serializers.ModelSerializer):
    """Serializer برای اشتراک‌گذاری عمومی لیست آرزو"""
    share_url = serializers.SerializerMethodField()
    shared_by_name = serializers.SerializerMethodField()
    wishlist_title = serializers.SerializerMethodField()

    class Meta:
        model = WishlistShare
        fields = [
            'id', 'wishlist', 'shared_by', 'shared_by_name', 'wishlist_title',
            'share_type', 'share_token', 'expires_at', 'allow_contributions',
            'allow_comments', 'show_progress', 'view_count', 'share_url',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'shared_by', 'share_token',
                            'view_count', 'created_at', 'updated_at']

    def get_share_url(self, obj):
        return obj.get_share_url()

    def get_shared_by_name(self, obj):
        return f"{obj.shared_by.first_name} {obj.shared_by.last_name}".strip() or obj.shared_by.username

    def get_wishlist_title(self, obj):
        return obj.wishlist.title


class WishlistInvitationSerializer(serializers.ModelSerializer):
    """Serializer برای دعوت‌نامه‌ها"""
    invitation_url = serializers.SerializerMethodField()
    invited_by_name = serializers.SerializerMethodField()
    wishlist_item_title = serializers.SerializerMethodField()
    status_display = serializers.SerializerMethodField()

    class Meta:
        model = WishlistInvitation
        fields = [
            'id', 'wishlist_item', 'wishlist_item_title', 'invited_by', 'invited_by_name',
            'invited_email', 'invited_phone', 'invited_name', 'message',
            'suggested_amount', 'status', 'status_display', 'invitation_token',
            'invitation_url', 'sent_at', 'responded_at', 'expires_at'
        ]
        read_only_fields = [
            'id', 'invited_by', 'invitation_token', 'sent_at',
            'responded_at', 'expires_at'
        ]

    def get_invitation_url(self, obj):
        return obj.get_invitation_url()

    def get_invited_by_name(self, obj):
        return f"{obj.invited_by.first_name} {obj.invited_by.last_name}".strip() or obj.invited_by.username

    def get_wishlist_item_title(self, obj):
        return obj.wishlist_item.name

    def get_status_display(self, obj):
        status_map = {
            'PENDING': 'در انتظار',
            'ACCEPTED': 'پذیرفته شده',
            'DECLINED': 'رد شده',
            'EXPIRED': 'منقضی شده',
        }
        return status_map.get(obj.status, obj.status)


class SocialShareSerializer(serializers.ModelSerializer):
    """Serializer برای اشتراک‌گذاری در شبکه‌های اجتماعی"""
    shared_by_name = serializers.SerializerMethodField()
    wishlist_item_title = serializers.SerializerMethodField()
    platform_display = serializers.SerializerMethodField()

    class Meta:
        model = SocialShare
        fields = [
            'id', 'wishlist_item', 'wishlist_item_title', 'shared_by', 'shared_by_name',
            'platform', 'platform_display', 'share_content', 'click_count',
            'conversion_count', 'created_at'
        ]
        read_only_fields = ['id', 'shared_by',
                            'click_count', 'conversion_count', 'created_at']

    def get_shared_by_name(self, obj):
        return f"{obj.shared_by.first_name} {obj.shared_by.last_name}".strip() or obj.shared_by.username

    def get_wishlist_item_title(self, obj):
        return obj.wishlist_item.name

    def get_platform_display(self, obj):
        platform_map = {
            'TELEGRAM': 'تلگرام',
            'WHATSAPP': 'واتساپ',
            'INSTAGRAM': 'اینستاگرام',
            'TWITTER': 'توییتر',
            'SMS': 'پیامک',
            'EMAIL': 'ایمیل',
        }
        return platform_map.get(obj.platform, obj.platform)


class ContributionGoalSerializer(serializers.ModelSerializer):
    """Serializer برای هدف‌گذاری کمک مالی"""
    progress_percentage = serializers.SerializerMethodField()
    current_contributors = serializers.SerializerMethodField()
    is_deadline_passed = serializers.SerializerMethodField()

    class Meta:
        model = ContributionGoal
        fields = [
            'id', 'wishlist_item', 'target_amount', 'target_contributors',
            'deadline', 'is_achieved', 'achieved_at', 'reward_message',
            'milestone_messages', 'progress_percentage', 'current_contributors',
            'is_deadline_passed', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'is_achieved',
                            'achieved_at', 'created_at', 'updated_at']

    def get_progress_percentage(self, obj):
        return obj.get_progress_percentage()

    def get_current_contributors(self, obj):
        return obj.wishlist_item.contributions.count()

    def get_is_deadline_passed(self, obj):
        if not obj.deadline:
            return False
        from django.utils import timezone
        return timezone.now() > obj.deadline


class SharedWishlistViewSerializer(serializers.ModelSerializer):
    """Serializer برای نمایش لیست آرزوی اشتراک‌گذاری شده"""
    items = WishlistItemSerializer(many=True, read_only=True)
    owner_name = serializers.SerializerMethodField()
    total_items = serializers.SerializerMethodField()
    total_value = serializers.SerializerMethodField()

    class Meta:
        model = Wishlist
        fields = [
            'id', 'title', 'description', 'occasion_date', 'is_public',
            'owner_name', 'items', 'total_items', 'total_value', 'created_at'
        ]

    def get_owner_name(self, obj):
        return f"{obj.owner.first_name} {obj.owner.last_name}".strip() or obj.owner.username

    def get_total_items(self, obj):
        return obj.items.count()

    def get_total_value(self, obj):
        from django.db.models import Sum
        return obj.items.aggregate(total=Sum('price'))['total'] or 0


class InvitationResponseSerializer(serializers.Serializer):
    """Serializer برای پاسخ به دعوت‌نامه"""
    token = serializers.CharField(max_length=64)
    message = serializers.CharField(max_length=500, required=False)


# OTP Authentication Serializers
class SendOTPSerializer(serializers.Serializer):
    """Serializer برای ارسال OTP"""
    phone_number = serializers.CharField(max_length=15)

    def validate_phone_number(self, value):
        from .services import PhoneValidationService
        if not PhoneValidationService.is_valid_iranian_phone(value):
            raise serializers.ValidationError('شماره موبایل معتبر نیست')
        return value


class RegisterWithOTPSerializer(serializers.Serializer):
    """Serializer برای ثبت‌نام با OTP"""
    phone_number = serializers.CharField(max_length=15)
    otp_code = serializers.CharField(max_length=6)
    first_name = serializers.CharField(max_length=30, required=False)
    last_name = serializers.CharField(max_length=30, required=False)
    email = serializers.EmailField(required=False)

    # فیلدهای Honeypot (تله برای ربات‌ها)
    website = serializers.CharField(
        max_length=200, required=False, allow_blank=True)
    url = serializers.CharField(
        max_length=200, required=False, allow_blank=True)
    homepage = serializers.CharField(
        max_length=200, required=False, allow_blank=True)
    company = serializers.CharField(
        max_length=100, required=False, allow_blank=True)

    def validate_phone_number(self, value):
        from .services import PhoneValidationService
        if not PhoneValidationService.is_valid_iranian_phone(value):
            raise serializers.ValidationError('شماره موبایل معتبر نیست')
        return value

    def validate_otp_code(self, value):
        if not value.isdigit() or len(value) != 6:
            raise serializers.ValidationError('کد OTP باید 6 رقم باشد')
        return value


class LoginWithOTPSerializer(serializers.Serializer):
    """Serializer برای ورود با OTP"""
    phone_number = serializers.CharField(max_length=15)
    otp_code = serializers.CharField(max_length=6)

    def validate_phone_number(self, value):
        from .services import PhoneValidationService
        if not PhoneValidationService.is_valid_iranian_phone(value):
            raise serializers.ValidationError('شماره موبایل معتبر نیست')
        return value

    def validate_otp_code(self, value):
        if not value.isdigit() or len(value) != 6:
            raise serializers.ValidationError('کد OTP باید 6 رقم باشد')
        return value


class VerifyPhoneSerializer(serializers.Serializer):
    """Serializer برای تایید شماره موبایل"""
    phone_number = serializers.CharField(max_length=15)
    otp_code = serializers.CharField(max_length=6)

    def validate_phone_number(self, value):
        from .services import PhoneValidationService
        if not PhoneValidationService.is_valid_iranian_phone(value):
            raise serializers.ValidationError('شماره موبایل معتبر نیست')
        return value


# Anti-Bot Serializers
class CaptchaGenerateSerializer(serializers.Serializer):
    """Serializer برای تولید Captcha"""
    type = serializers.ChoiceField(
        choices=['MATH', 'TEXT', 'IMAGE'],
        default='MATH'
    )


class CaptchaVerifySerializer(serializers.Serializer):
    """Serializer برای تایید Captcha"""
    captcha_id = serializers.UUIDField()
    answer = serializers.CharField(max_length=100)


class BehaviorAnalysisSerializer(serializers.Serializer):
    """Serializer برای تحلیل رفتار کاربر"""
    fill_time = serializers.FloatField(required=False)  # زمان پر کردن فرم
    typing_speed = serializers.FloatField(required=False)  # سرعت تایپ
    mouse_movements = serializers.IntegerField(
        required=False)  # تعداد حرکات ماوس
    clicks = serializers.IntegerField(required=False)  # تعداد کلیک‌ها
    key_presses = serializers.IntegerField(required=False)  # تعداد فشردن کلید
    time_on_page = serializers.FloatField(required=False)  # زمان روی صفحه
    copy_paste = serializers.BooleanField(
        required=False, default=False)  # استفاده از copy-paste
    auto_fill = serializers.BooleanField(
        required=False, default=False)  # استفاده از auto-fill


class SecurityStatusSerializer(serializers.Serializer):
    """Serializer برای نمایش وضعیت امنیتی"""
    is_bot = serializers.BooleanField()
    risk_score = serializers.IntegerField()
    blocked_reasons = serializers.ListField(child=serializers.CharField())
    require_captcha = serializers.BooleanField()
    device_fingerprint = serializers.DictField()
    ip_reputation = serializers.DictField()
    session_id = serializers.CharField()


# Email Authentication Serializers
class SendEmailVerificationSerializer(serializers.Serializer):
    """Serializer برای ارسال ایمیل تایید"""
    email = serializers.EmailField()
    verification_type = serializers.ChoiceField(
        choices=['REGISTER', 'LOGIN', 'RESET_PASSWORD'],
        default='REGISTER'
    )

    def validate_email(self, value):
        from .services import EmailValidationService
        if not EmailValidationService.is_valid_email(value):
            raise serializers.ValidationError('ایمیل معتبر نیست')
        if EmailValidationService.is_disposable_email(value):
            raise serializers.ValidationError(
                'استفاده از ایمیل موقت مجاز نیست')
        return EmailValidationService.normalize_email(value)


class RegisterWithEmailSerializer(serializers.Serializer):
    """Serializer برای ثبت‌نام با ایمیل"""
    email = serializers.EmailField()
    token = serializers.CharField(max_length=100)
    first_name = serializers.CharField(max_length=30, required=False)
    last_name = serializers.CharField(max_length=30, required=False)
    password = serializers.CharField(
        min_length=8,
        validators=[validate_password]
    )

    # فیلدهای Honeypot (تله برای ربات‌ها)
    website = serializers.CharField(
        max_length=200, required=False, allow_blank=True)
    url = serializers.CharField(
        max_length=200, required=False, allow_blank=True)
    homepage = serializers.CharField(
        max_length=200, required=False, allow_blank=True)
    company = serializers.CharField(
        max_length=100, required=False, allow_blank=True)

    def validate_email(self, value):
        from .services import EmailValidationService
        if not EmailValidationService.is_valid_email(value):
            raise serializers.ValidationError('ایمیل معتبر نیست')
        return EmailValidationService.normalize_email(value)

    def validate_token(self, value):
        if len(value) != 64:
            raise serializers.ValidationError('توکن نامعتبر است')
        return value


class LoginWithEmailSerializer(serializers.Serializer):
    """Serializer برای ورود با ایمیل و رمز عبور"""
    email = serializers.EmailField()
    password = serializers.CharField()

    def validate_email(self, value):
        from .services import EmailValidationService
        if not EmailValidationService.is_valid_email(value):
            raise serializers.ValidationError('ایمیل معتبر نیست')
        return EmailValidationService.normalize_email(value)


class VerifyEmailSerializer(serializers.Serializer):
    """Serializer برای تایید ایمیل با توکن"""
    token = serializers.CharField(max_length=100)

    def validate_token(self, value):
        if len(value) != 64:
            raise serializers.ValidationError('توکن نامعتبر است')
        return value
