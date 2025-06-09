from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import WishList, WishListItem, Contribution, Notification, Plan, UserSubscription, PaymentHistory

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name', 
                 'phone_number', 'bio', 'avatar', 'wallet_balance')
        read_only_fields = ('wallet_balance',)
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        user = super().create(validated_data)
        if password:
            user.set_password(password)
            user.save()
        return user

class WishListItemSerializer(serializers.ModelSerializer):
    total_contributions = serializers.DecimalField(
        max_digits=10, decimal_places=2, read_only=True)
    remaining_amount = serializers.DecimalField(
        max_digits=10, decimal_places=2, read_only=True)
    
    class Meta:
        model = WishListItem
        fields = '__all__'
        read_only_fields = ('status',)

class WishListSerializer(serializers.ModelSerializer):
    items = WishListItemSerializer(many=True, read_only=True)
    owner = UserSerializer(read_only=True)
    
    class Meta:
        model = WishList
        fields = '__all__'
        read_only_fields = ('owner',)

class ContributionSerializer(serializers.ModelSerializer):
    contributor = UserSerializer(read_only=True)
    
    class Meta:
        model = Contribution
        fields = '__all__'
        read_only_fields = ('contributor',)

class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = '__all__'
        read_only_fields = ('user',)

class PlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = Plan
        fields = '__all__'


class UserSubscriptionSerializer(serializers.ModelSerializer):
    plan = PlanSerializer(read_only=True)
    plan_id = serializers.IntegerField(write_only=True)
    
    class Meta:
        model = UserSubscription
        fields = (
            'id', 'plan', 'plan_id', 'start_date', 'end_date',
            'is_active', 'auto_renew', 'created_at'
        )
        read_only_fields = ('start_date', 'is_active', 'created_at')


class PaymentHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentHistory
        fields = '__all__'
        read_only_fields = ('user', 'created_at')
