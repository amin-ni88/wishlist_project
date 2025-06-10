from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.db import models

from .models import (
    User, UserFollow, Category, Tag, Occasion, Wishlist, WishlistItem,
    WalletTransaction, Contribution, SubscriptionPlan, UserSubscription,
    Notification, OTPVerification, PhoneVerificationLog,
    DeviceFingerprint, IPReputationLog, BehaviorAnalysis, CaptchaChallenge,
    WishlistShare, WishlistInvitation, SocialShare, ContributionGoal,
    EmailVerification, EmailVerificationLog
)


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Enhanced user admin"""
    list_display = [
        'username', 'email', 'get_full_name', 'wallet_balance',
        'is_verified', 'profile_visibility', 'date_joined'
    ]
    list_filter = [
        'is_verified', 'profile_visibility', 'is_staff', 'is_active', 'date_joined'
    ]
    search_fields = ['username', 'email',
                     'first_name', 'last_name', 'phone_number']
    readonly_fields = ['date_joined', 'last_login']

    fieldsets = BaseUserAdmin.fieldsets + (
        ('اطلاعات تکمیلی', {
            'fields': (
                'phone_number', 'profile_image', 'bio', 'birth_date',
                'wallet_balance', 'is_verified', 'verification_token',
                'profile_visibility'
            )
        }),
    )

    def get_full_name(self, obj):
        return obj.get_full_name() or '-'
    get_full_name.short_description = 'نام کامل'


@admin.register(UserFollow)
class UserFollowAdmin(admin.ModelAdmin):
    """User follow admin"""
    list_display = ['follower', 'followed', 'created_at']
    list_filter = ['created_at']
    search_fields = ['follower__username', 'followed__username']
    raw_id_fields = ['follower', 'followed']


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """Category admin"""
    list_display = ['name', 'name_en', 'parent', 'is_active', 'sort_order']
    list_filter = ['is_active', 'parent']
    search_fields = ['name', 'name_en', 'description']
    list_editable = ['is_active', 'sort_order']
    prepopulated_fields = {'name_en': ('name',)}


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    """Tag admin"""
    list_display = ['name', 'color_preview', 'usage_count', 'created_at']
    list_filter = ['created_at']
    search_fields = ['name']
    readonly_fields = ['usage_count']

    def color_preview(self, obj):
        return format_html(
            '<span style="background-color: {}; padding: 2px 8px; border-radius: 3px; color: white;">{}</span>',
            obj.color, obj.color
        )
    color_preview.short_description = 'رنگ'


@admin.register(Occasion)
class OccasionAdmin(admin.ModelAdmin):
    """Occasion admin"""
    list_display = ['name', 'icon', 'color_preview',
                    'is_recurring', 'sort_order']
    list_filter = ['is_recurring']
    search_fields = ['name']
    list_editable = ['sort_order']

    def color_preview(self, obj):
        return format_html(
            '<span style="background-color: {}; padding: 2px 8px; border-radius: 3px; color: white;">{}</span>',
            obj.color, obj.color
        )
    color_preview.short_description = 'رنگ'


class WishlistItemInline(admin.TabularInline):
    """Inline for wishlist items"""
    model = WishlistItem
    extra = 0
    fields = ['name', 'price', 'contributed_amount', 'status', 'priority']
    readonly_fields = ['contributed_amount']


@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    """Wishlist admin"""
    list_display = [
        'title', 'owner', 'occasion', 'visibility', 'is_active',
        'items_count', 'total_value', 'completion_percentage', 'created_at'
    ]
    list_filter = [
        'visibility', 'is_active', 'is_completed', 'occasion', 'created_at'
    ]
    search_fields = ['title', 'description', 'owner__username']
    readonly_fields = [
        'slug', 'view_count', 'share_count', 'total_value',
        'total_contributed', 'completion_percentage', 'created_at', 'updated_at'
    ]
    raw_id_fields = ['owner']
    inlines = [WishlistItemInline]

    def items_count(self, obj):
        return obj.items.count()
    items_count.short_description = 'تعداد آیتم'

    def completion_percentage(self, obj):
        try:
            # محاسبه درصد تکمیل
            total_price = float(obj.total_value or 0)
            total_contributed = float(obj.total_contributed or 0)
            percentage = (total_contributed / total_price *
                          100) if total_price > 0 else 0.0

            color = 'green' if percentage >= 100 else 'orange' if percentage >= 50 else 'red'
            return format_html(
                '<span style="color: {};">{}</span>',
                color, f'{percentage:.1f}%'
            )
        except (AttributeError, TypeError, ZeroDivisionError):
            return format_html('<span style="color: red;">0.0%</span>')
    completion_percentage.short_description = 'درصد تکمیل'


@admin.register(WishlistItem)
class WishlistItemAdmin(admin.ModelAdmin):
    """Wishlist item admin"""
    list_display = [
        'name', 'wishlist', 'price', 'contributed_amount',
        'remaining_amount', 'status', 'priority', 'created_at'
    ]
    list_filter = ['status', 'priority', 'category', 'created_at']
    search_fields = ['name', 'description', 'wishlist__title']
    readonly_fields = [
        'contributed_amount', 'remaining_amount', 'completion_percentage',
        'is_fully_funded', 'created_at', 'updated_at'
    ]
    raw_id_fields = ['wishlist', 'category', 'purchased_by']
    filter_horizontal = ['tags']

    def remaining_amount(self, obj):
        return obj.remaining_amount
    remaining_amount.short_description = 'مبلغ باقی‌مانده'


@admin.register(WalletTransaction)
class WalletTransactionAdmin(admin.ModelAdmin):
    """Wallet transaction admin"""
    list_display = [
        'user', 'transaction_type', 'amount', 'status',
        'payment_method', 'created_at'
    ]
    list_filter = ['transaction_type', 'status',
                   'payment_method', 'created_at']
    search_fields = [
        'user__username', 'description', 'transaction_id', 'reference_number'
    ]
    readonly_fields = ['created_at', 'completed_at']
    raw_id_fields = ['user', 'related_item', 'related_contribution']


@admin.register(Contribution)
class ContributionAdmin(admin.ModelAdmin):
    """Contribution admin"""
    list_display = [
        'get_contributor_name', 'item', 'amount', 'status',
        'is_anonymous', 'created_at'
    ]
    list_filter = ['status', 'is_anonymous', 'created_at']
    search_fields = [
        'contributor__username', 'guest_name', 'guest_email',
        'item__name', 'item__wishlist__title'
    ]
    readonly_fields = ['created_at', 'completed_at']
    raw_id_fields = ['item', 'contributor', 'wallet_transaction']

    def get_contributor_name(self, obj):
        if obj.is_anonymous:
            return 'ناشناس'
        if obj.guest_name:
            return obj.guest_name
        if obj.contributor:
            return obj.contributor.get_full_name() or obj.contributor.username
        return 'ناشناس'
    get_contributor_name.short_description = 'مشارکت‌کننده'


@admin.register(SubscriptionPlan)
class SubscriptionPlanAdmin(admin.ModelAdmin):
    """Subscription plan admin"""
    list_display = [
        'name', 'monthly_price', 'yearly_price', 'yearly_discount_percentage',
        'max_wishlists', 'is_popular', 'is_active', 'sort_order'
    ]
    list_filter = ['is_popular', 'is_active']
    search_fields = ['name', 'name_en', 'description']
    list_editable = ['is_popular', 'is_active', 'sort_order']


@admin.register(UserSubscription)
class UserSubscriptionAdmin(admin.ModelAdmin):
    """User subscription admin"""
    list_display = [
        'user', 'plan', 'is_active', 'start_date', 'end_date',
        'days_remaining', 'auto_renew'
    ]
    list_filter = ['is_active', 'auto_renew', 'plan', 'start_date']
    search_fields = ['user__username', 'plan__name']
    readonly_fields = ['is_expired',
                       'days_remaining', 'created_at', 'updated_at']
    raw_id_fields = ['user']

    def days_remaining(self, obj):
        days = obj.days_remaining
        color = 'red' if days <= 7 else 'orange' if days <= 30 else 'green'
        return format_html(
            '<span style="color: {};">{} روز</span>',
            color, days
        )
    days_remaining.short_description = 'روزهای باقی‌مانده'


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    """Notification admin"""
    list_display = [
        'user', 'title', 'notification_type', 'is_read',
        'is_sent', 'created_at'
    ]
    list_filter = [
        'notification_type', 'is_read', 'is_sent', 'send_push',
        'send_email', 'created_at'
    ]
    search_fields = ['user__username', 'title', 'message']
    readonly_fields = ['created_at', 'read_at', 'sent_at']
    raw_id_fields = [
        'user', 'related_wishlist', 'related_item', 'related_user'
    ]


@admin.register(OTPVerification)
class OTPVerificationAdmin(admin.ModelAdmin):
    """OTP Verification admin"""
    list_display = [
        'phone_number', 'otp_type', 'otp_code', 'is_verified',
        'attempts_count', 'max_attempts', 'created_at', 'expires_at'
    ]
    list_filter = ['otp_type', 'is_verified', 'created_at']
    search_fields = ['phone_number', 'otp_code']
    readonly_fields = [
        'otp_code', 'attempts_count', 'created_at', 'verified_at', 'expires_at'
    ]
    ordering = ['-created_at']

    def has_add_permission(self, request):
        return False  # نمی‌توان به صورت دستی OTP اضافه کرد

    def has_change_permission(self, request, obj=None):
        return False  # نمی‌توان OTP را تغییر داد


@admin.register(PhoneVerificationLog)
class PhoneVerificationLogAdmin(admin.ModelAdmin):
    """Phone Verification Log admin"""
    list_display = [
        'phone_number', 'attempt_type', 'success', 'ip_address', 'created_at'
    ]
    list_filter = ['attempt_type', 'success', 'created_at']
    search_fields = ['phone_number', 'ip_address']
    readonly_fields = ['phone_number', 'ip_address',
                       'user_agent', 'success', 'attempt_type', 'created_at']
    ordering = ['-created_at']

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser


@admin.register(DeviceFingerprint)
class DeviceFingerprintAdmin(admin.ModelAdmin):
    list_display = (
        'fingerprint_hash_short', 'user_agent_short', 'platform',
        'registration_attempts', 'successful_registrations',
        'risk_score', 'is_suspicious', 'last_seen'
    )
    list_filter = (
        'is_suspicious', 'platform', 'created_at', 'last_seen'
    )
    search_fields = ('fingerprint_hash', 'user_agent', 'platform')
    readonly_fields = (
        'id', 'fingerprint_hash', 'created_at', 'last_seen'
    )
    ordering = ('-risk_score', '-last_seen')

    def fingerprint_hash_short(self, obj):
        return obj.fingerprint_hash[:12] + '...' if obj.fingerprint_hash else ''
    fingerprint_hash_short.short_description = 'ردپای دستگاه'

    def user_agent_short(self, obj):
        return obj.user_agent[:50] + '...' if len(obj.user_agent) > 50 else obj.user_agent
    user_agent_short.short_description = 'User Agent'

    def get_queryset(self, request):
        return super().get_queryset(request).order_by('-risk_score')


@admin.register(IPReputationLog)
class IPReputationLogAdmin(admin.ModelAdmin):
    list_display = (
        'ip_address', 'registration_attempts', 'successful_registrations',
        'failed_otp_attempts', 'captcha_failures', 'risk_score',
        'is_blocked', 'blocked_until', 'last_activity'
    )
    list_filter = (
        'is_blocked', 'is_vpn', 'is_proxy', 'country_code',
        'first_seen', 'last_activity'
    )
    search_fields = ('ip_address', 'block_reason')
    readonly_fields = ('first_seen', 'last_activity')
    actions = ['block_ips', 'unblock_ips', 'reset_risk_scores']
    ordering = ('-risk_score', '-last_activity')

    def block_ips(self, request, queryset):
        from django.utils import timezone
        queryset.update(
            is_blocked=True,
            block_reason='مسدود شده توسط ادمین',
            blocked_until=timezone.now() + timezone.timedelta(hours=24)
        )
        self.message_user(request, f'{queryset.count()} IP مسدود شد')
    block_ips.short_description = 'مسدود کردن IP های انتخاب شده'

    def unblock_ips(self, request, queryset):
        queryset.update(
            is_blocked=False,
            block_reason='',
            blocked_until=None
        )
        self.message_user(request, f'{queryset.count()} IP آزاد شد')
    unblock_ips.short_description = 'آزاد کردن IP های انتخاب شده'

    def reset_risk_scores(self, request, queryset):
        queryset.update(risk_score=0.0)
        self.message_user(request, f'امتیاز ریسک {queryset.count()} IP صفر شد')
    reset_risk_scores.short_description = 'صفر کردن امتیاز ریسک'


@admin.register(BehaviorAnalysis)
class BehaviorAnalysisAdmin(admin.ModelAdmin):
    list_display = (
        'session_id_short', 'ip_address', 'form_fill_time',
        'typing_speed', 'mouse_movements', 'is_human_like',
        'bot_probability', 'created_at'
    )
    list_filter = (
        'is_human_like', 'copy_paste_detected', 'auto_fill_detected',
        'multiple_tabs', 'created_at'
    )
    search_fields = ('session_id', 'ip_address')
    readonly_fields = (
        'session_id', 'created_at', 'bot_probability', 'is_human_like'
    )
    ordering = ('-bot_probability', '-created_at')

    def session_id_short(self, obj):
        return obj.session_id[:12] + '...' if obj.session_id else ''
    session_id_short.short_description = 'شناسه نشست'

    fieldsets = (
        ('اطلاعات اساسی', {
            'fields': ('session_id', 'ip_address', 'device_fingerprint', 'created_at')
        }),
        ('رفتار در فرم', {
            'fields': (
                'form_fill_time', 'typing_speed', 'mouse_movements',
                'clicks_count', 'key_presses', 'time_on_page'
            )
        }),
        ('رفتارهای مشکوک', {
            'fields': (
                'copy_paste_detected', 'auto_fill_detected', 'multiple_tabs'
            )
        }),
        ('نتیجه تحلیل', {
            'fields': ('is_human_like', 'bot_probability')
        }),
    )


@admin.register(CaptchaChallenge)
class CaptchaChallengeAdmin(admin.ModelAdmin):
    list_display = (
        'id_short', 'challenge_type', 'session_id_short',
        'ip_address', 'question_short', 'is_solved',
        'attempts_count', 'max_attempts', 'created_at', 'expires_at'
    )
    list_filter = (
        'challenge_type', 'is_solved', 'created_at', 'expires_at'
    )
    search_fields = ('session_id', 'ip_address', 'question')
    readonly_fields = (
        'id', 'created_at', 'solved_at', 'expires_at'
    )
    ordering = ('-created_at',)

    def id_short(self, obj):
        return str(obj.id)[:8] + '...'
    id_short.short_description = 'شناسه'

    def session_id_short(self, obj):
        return obj.session_id[:12] + '...' if obj.session_id else ''
    session_id_short.short_description = 'شناسه نشست'

    def question_short(self, obj):
        return obj.question[:30] + '...' if len(obj.question) > 30 else obj.question
    question_short.short_description = 'سوال'

    def get_readonly_fields(self, request, obj=None):
        if obj:  # ویرایش موجود
            return self.readonly_fields + ('question', 'correct_answer')
        return self.readonly_fields

    fieldsets = (
        ('اطلاعات چالش', {
            'fields': ('id', 'challenge_type', 'session_id', 'ip_address')
        }),
        ('سوال و پاسخ', {
            'fields': ('question', 'correct_answer', 'user_answer')
        }),
        ('وضعیت', {
            'fields': (
                'is_solved', 'attempts_count', 'max_attempts',
                'created_at', 'expires_at', 'solved_at'
            )
        }),
    )


@admin.register(EmailVerification)
class EmailVerificationAdmin(admin.ModelAdmin):
    """Email Verification admin"""
    list_display = [
        'email', 'verification_type', 'is_verified',
        'attempts_count', 'max_attempts', 'created_at', 'expires_at'
    ]
    list_filter = ['verification_type', 'is_verified', 'created_at']
    search_fields = ['email', 'token']
    readonly_fields = [
        'token', 'attempts_count', 'created_at', 'verified_at', 'expires_at'
    ]
    ordering = ['-created_at']

    def has_add_permission(self, request):
        return False  # نمی‌توان به صورت دستی ایمیل تایید اضافه کرد

    def has_change_permission(self, request, obj=None):
        return False  # نمی‌توان ایمیل تایید را تغییر داد


@admin.register(EmailVerificationLog)
class EmailVerificationLogAdmin(admin.ModelAdmin):
    """Email Verification Log admin"""
    list_display = [
        'email', 'attempt_type', 'success', 'ip_address', 'created_at'
    ]
    list_filter = ['attempt_type', 'success', 'created_at']
    search_fields = ['email', 'ip_address']
    readonly_fields = ['email', 'ip_address',
                       'user_agent', 'success', 'attempt_type', 'created_at']
    ordering = ['-created_at']

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser


# Security Dashboard
class SecurityDashboard:
    """داشبورد امنیتی برای نمایش آمار کلی"""

    @staticmethod
    def get_security_stats():
        from django.db.models import Count, Avg, Sum
        from django.utils import timezone
        from datetime import timedelta

        today = timezone.now().date()
        week_ago = today - timedelta(days=7)

        # آمار IP ها
        ip_stats = IPReputationLog.objects.aggregate(
            total_ips=Count('id'),
            blocked_ips=Count('id', filter=models.Q(is_blocked=True)),
            high_risk_ips=Count('id', filter=models.Q(risk_score__gt=60)),
            avg_risk_score=Avg('risk_score')
        )

        # آمار دستگاه‌ها
        device_stats = DeviceFingerprint.objects.aggregate(
            total_devices=Count('id'),
            suspicious_devices=Count(
                'id', filter=models.Q(is_suspicious=True)),
            avg_risk_score=Avg('risk_score')
        )

        # آمار رفتار
        behavior_stats = BehaviorAnalysis.objects.filter(
            created_at__date__gte=week_ago
        ).aggregate(
            total_analyses=Count('id'),
            bot_like_behaviors=Count(
                'id', filter=models.Q(is_human_like=False)),
            avg_bot_probability=Avg('bot_probability')
        )

        # آمار Captcha
        captcha_stats = CaptchaChallenge.objects.filter(
            created_at__date__gte=week_ago
        ).aggregate(
            total_challenges=Count('id'),
            solved_challenges=Count('id', filter=models.Q(is_solved=True)),
            failed_challenges=Count('id', filter=models.Q(
                attempts_count__gte=models.F('max_attempts'),
                is_solved=False
            ))
        )

        return {
            'ip_stats': ip_stats,
            'device_stats': device_stats,
            'behavior_stats': behavior_stats,
            'captcha_stats': captcha_stats,
        }


# Admin site customization
admin.site.site_header = 'مدیریت پلتفرم لیست آرزوها'
admin.site.site_title = 'Wishlist Platform'
admin.site.index_title = 'پنل مدیریت'
