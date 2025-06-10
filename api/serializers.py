from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from decimal import Decimal
from core.models import (
    User, UserFollow, Category, Tag, Occasion, Wishlist, WishlistItem,
    WalletTransaction, Contribution, SubscriptionPlan, UserSubscription,
    Notification
)


class UserRegistrationSerializer(serializers.ModelSerializer):
    """Serializer for user registration"""
    password = serializers.CharField(
        write_only=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = [
            'username', 'email', 'password', 'password_confirm',
            'first_name', 'last_name', 'phone_number', 'bio'
        ]

    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError(
                "رمز عبور و تکرار آن مطابقت ندارند.")
        return attrs

    def create(self, validated_data):
        validated_data.pop('password_confirm')
        user = User.objects.create_user(**validated_data)
        return user


class UserLoginSerializer(serializers.Serializer):
    """Serializer for user login"""
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        username = attrs.get('username')
        password = attrs.get('password')

        if username and password:
            user = authenticate(username=username, password=password)
            if not user:
                raise serializers.ValidationError(
                    'نام کاربری یا رمز عبور اشتباه است.')
            if not user.is_active:
                raise serializers.ValidationError('حساب کاربری غیرفعال است.')
            attrs['user'] = user
        else:
            raise serializers.ValidationError(
                'نام کاربری و رمز عبور الزامی است.')

        return attrs


class UserProfileSerializer(serializers.ModelSerializer):
    """Serializer for user profile"""
    followers_count = serializers.SerializerMethodField()
    following_count = serializers.SerializerMethodField()
    wishlists_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            'phone_number', 'profile_image', 'bio', 'birth_date',
            'wallet_balance', 'is_verified', 'profile_visibility',
            'followers_count', 'following_count', 'wishlists_count',
            'date_joined'
        ]
        read_only_fields = ['id', 'wallet_balance',
                            'is_verified', 'date_joined']

    def get_followers_count(self, obj):
        return obj.followers_set.count()

    def get_following_count(self, obj):
        return obj.following_set.count()

    def get_wishlists_count(self, obj):
        return obj.wishlists.filter(is_active=True).count()


class CategorySerializer(serializers.ModelSerializer):
    """Serializer for categories"""
    children = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = [
            'id', 'name', 'name_en', 'description', 'icon', 'color',
            'parent', 'is_active', 'sort_order', 'children'
        ]

    def get_children(self, obj):
        if obj.category_set.exists():
            return CategorySerializer(obj.category_set.filter(is_active=True), many=True).data
        return []


class TagSerializer(serializers.ModelSerializer):
    """Serializer for tags"""
    class Meta:
        model = Tag
        fields = ['id', 'name', 'color', 'usage_count']


class OccasionSerializer(serializers.ModelSerializer):
    """Serializer for occasions"""
    class Meta:
        model = Occasion
        fields = ['id', 'name', 'icon', 'color', 'is_recurring', 'sort_order']


class WishlistItemSerializer(serializers.ModelSerializer):
    """Serializer for wishlist items"""
    category_name = serializers.CharField(
        source='category.name', read_only=True)
    tags_data = TagSerializer(source='tags', many=True, read_only=True)
    contributions_count = serializers.SerializerMethodField()
    remaining_amount = serializers.ReadOnlyField()
    completion_percentage = serializers.ReadOnlyField()
    is_fully_funded = serializers.ReadOnlyField()

    class Meta:
        model = WishlistItem
        fields = [
            'id', 'name', 'description', 'price', 'contributed_amount',
            'product_url', 'image', 'brand', 'model', 'category', 'category_name',
            'tags', 'tags_data', 'priority', 'status', 'purchased_by',
            'purchased_at', 'purchase_notes', 'sort_order',
            'contributions_count', 'remaining_amount', 'completion_percentage',
            'is_fully_funded', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'contributed_amount', 'purchased_by', 'purchased_at', 'created_at', 'updated_at'
        ]

    def get_contributions_count(self, obj):
        return obj.contributions.filter(status='COMPLETED').count()


class WishlistSerializer(serializers.ModelSerializer):
    """Serializer for wishlists"""
    owner_name = serializers.CharField(
        source='owner.get_full_name', read_only=True)
    owner_username = serializers.CharField(
        source='owner.username', read_only=True)
    occasion_name = serializers.CharField(
        source='occasion.name', read_only=True)
    items_count = serializers.SerializerMethodField()
    total_value = serializers.ReadOnlyField()
    total_contributed = serializers.ReadOnlyField()
    completion_percentage = serializers.ReadOnlyField()
    items = WishlistItemSerializer(many=True, read_only=True)

    class Meta:
        model = Wishlist
        fields = [
            'id', 'slug', 'title', 'description', 'owner', 'owner_name', 'owner_username',
            'occasion', 'occasion_name', 'occasion_date', 'visibility',
            'allow_contributions', 'allow_anonymous_contributions',
            'cover_image', 'theme_color', 'is_active', 'is_completed',
            'completion_date', 'view_count', 'share_count',
            'items_count', 'total_value', 'total_contributed', 'completion_percentage',
            'items', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'slug', 'owner', 'view_count', 'share_count', 'is_completed',
            'completion_date', 'created_at', 'updated_at'
        ]

    def get_items_count(self, obj):
        return obj.items.filter(status__in=['ACTIVE', 'RESERVED', 'PURCHASED']).count()


class WishlistCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating wishlists"""
    class Meta:
        model = Wishlist
        fields = [
            'title', 'description', 'occasion', 'occasion_date',
            'visibility', 'allow_contributions', 'allow_anonymous_contributions',
            'cover_image', 'theme_color'
        ]


class WalletTransactionSerializer(serializers.ModelSerializer):
    """Serializer for wallet transactions"""
    user_name = serializers.CharField(
        source='user.get_full_name', read_only=True)
    transaction_type_display = serializers.CharField(
        source='get_transaction_type_display', read_only=True)
    status_display = serializers.CharField(
        source='get_status_display', read_only=True)

    class Meta:
        model = WalletTransaction
        fields = [
            'id', 'user', 'user_name', 'transaction_type', 'transaction_type_display',
            'amount', 'status', 'status_display', 'related_item', 'related_contribution',
            'payment_method', 'transaction_id', 'reference_number',
            'description', 'notes', 'created_at', 'completed_at'
        ]
        read_only_fields = [
            'id', 'user', 'status', 'transaction_id', 'reference_number',
            'created_at', 'completed_at'
        ]


class ContributionSerializer(serializers.ModelSerializer):
    """Serializer for contributions"""
    contributor_name = serializers.SerializerMethodField()
    item_name = serializers.CharField(source='item.name', read_only=True)
    wishlist_title = serializers.CharField(
        source='item.wishlist.title', read_only=True)
    status_display = serializers.CharField(
        source='get_status_display', read_only=True)

    class Meta:
        model = Contribution
        fields = [
            'id', 'item', 'item_name', 'wishlist_title', 'contributor',
            'contributor_name', 'amount', 'message', 'is_anonymous',
            'guest_name', 'guest_email', 'status', 'status_display',
            'created_at', 'completed_at'
        ]
        read_only_fields = ['id', 'status', 'created_at', 'completed_at']

    def get_contributor_name(self, obj):
        if obj.is_anonymous:
            return 'ناشناس'
        if obj.guest_name:
            return obj.guest_name
        if obj.contributor:
            return obj.contributor.get_full_name() or obj.contributor.username
        return 'ناشناس'


class ContributionCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating contributions"""
    class Meta:
        model = Contribution
        fields = [
            'item', 'amount', 'message', 'is_anonymous',
            'guest_name', 'guest_email'
        ]

    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError(
                "مبلغ کمک باید بیشتر از صفر باشد.")
        return value

    def validate(self, attrs):
        # Check if user is authenticated or guest info is provided
        request = self.context.get('request')
        if not request.user.is_authenticated:
            if not attrs.get('guest_name') or not attrs.get('guest_email'):
                raise serializers.ValidationError(
                    "برای کمک مهمان، نام و ایمیل الزامی است."
                )

        # Check item availability
        item = attrs['item']
        if item.status != 'ACTIVE':
            raise serializers.ValidationError(
                "این آیتم برای کمک در دسترس نیست.")

        if not item.wishlist.allow_contributions:
            raise serializers.ValidationError("این لیست آرزو کمک نمی‌پذیرد.")

        # Check contribution amount doesn't exceed remaining
        if attrs['amount'] > item.remaining_amount:
            raise serializers.ValidationError(
                f"مبلغ کمک نمی‌تواند بیشتر از {item.remaining_amount} باشد."
            )

        return attrs


class SubscriptionPlanSerializer(serializers.ModelSerializer):
    """Serializer for subscription plans"""
    yearly_savings = serializers.SerializerMethodField()

    class Meta:
        model = SubscriptionPlan
        fields = [
            'id', 'name', 'name_en', 'description', 'monthly_price', 'yearly_price',
            'yearly_discount_percentage', 'yearly_savings', 'max_wishlists',
            'max_items_per_wishlist', 'max_image_uploads', 'can_use_custom_domains',
            'can_export_data', 'priority_support', 'advanced_analytics',
            'color', 'sort_order', 'is_popular', 'is_active'
        ]

    def get_yearly_savings(self, obj):
        monthly_total = obj.monthly_price * 12
        return monthly_total - obj.yearly_price


class UserSubscriptionSerializer(serializers.ModelSerializer):
    """Serializer for user subscriptions"""
    plan_name = serializers.CharField(source='plan.name', read_only=True)
    plan_details = SubscriptionPlanSerializer(source='plan', read_only=True)
    is_expired = serializers.ReadOnlyField()
    days_remaining = serializers.ReadOnlyField()

    class Meta:
        model = UserSubscription
        fields = [
            'id', 'user', 'plan', 'plan_name', 'plan_details',
            'is_active', 'start_date', 'end_date', 'auto_renew',
            'payment_method', 'last_payment_date', 'next_payment_date',
            'is_expired', 'days_remaining', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'user', 'start_date', 'last_payment_date',
            'created_at', 'updated_at'
        ]


class NotificationSerializer(serializers.ModelSerializer):
    """Serializer for notifications"""
    notification_type_display = serializers.CharField(
        source='get_notification_type_display', read_only=True)
    related_wishlist_title = serializers.CharField(
        source='related_wishlist.title', read_only=True)
    related_item_name = serializers.CharField(
        source='related_item.name', read_only=True)
    related_user_name = serializers.CharField(
        source='related_user.get_full_name', read_only=True)

    class Meta:
        model = Notification
        fields = [
            'id', 'title', 'message', 'notification_type', 'notification_type_display',
            'related_wishlist', 'related_wishlist_title', 'related_item', 'related_item_name',
            'related_user', 'related_user_name', 'is_read', 'is_sent',
            'send_push', 'send_email', 'send_sms', 'created_at', 'read_at', 'sent_at'
        ]
        read_only_fields = [
            'id', 'user', 'is_sent', 'created_at', 'sent_at'
        ]


class UserFollowSerializer(serializers.ModelSerializer):
    """Serializer for user follows"""
    follower_name = serializers.CharField(
        source='follower.get_full_name', read_only=True)
    followed_name = serializers.CharField(
        source='followed.get_full_name', read_only=True)

    class Meta:
        model = UserFollow
        fields = [
            'id', 'follower', 'follower_name', 'followed', 'followed_name', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


# Statistics Serializers
class WishlistStatsSerializer(serializers.Serializer):
    """Serializer for wishlist statistics"""
    total_wishlists = serializers.IntegerField()
    active_wishlists = serializers.IntegerField()
    completed_wishlists = serializers.IntegerField()
    total_items = serializers.IntegerField()
    total_value = serializers.DecimalField(max_digits=12, decimal_places=2)
    total_contributed = serializers.DecimalField(
        max_digits=12, decimal_places=2)
    completion_rate = serializers.FloatField()


class UserStatsSerializer(serializers.Serializer):
    """Serializer for user statistics"""
    total_contributions = serializers.DecimalField(
        max_digits=12, decimal_places=2)
    contributions_count = serializers.IntegerField()
    wishlists_created = serializers.IntegerField()
    items_purchased = serializers.IntegerField()
    wallet_balance = serializers.DecimalField(max_digits=12, decimal_places=2)
    followers_count = serializers.IntegerField()
    following_count = serializers.IntegerField()
