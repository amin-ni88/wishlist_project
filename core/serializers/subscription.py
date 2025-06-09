from rest_framework import serializers
from core.models import Plan, UserSubscription

class PlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = Plan
        fields = [
            'id',
            'name',
            'type',
            'duration_type',
            'monthly_price',
            'yearly_price',
            'lifetime_price',
            'max_wishlists',
            'max_items_per_list',
            'can_add_images',
            'can_receive_contributions',
            'priority_support',
            'description',
            'is_active'
        ]

class UserSubscriptionSerializer(serializers.ModelSerializer):
    plan = PlanSerializer(read_only=True)
    days_remaining = serializers.SerializerMethodField()
    
    class Meta:
        model = UserSubscription
        fields = [
            'id',
            'plan',
            'start_date',
            'end_date',
            'is_active',
            'auto_renew',
            'days_remaining',
            'created_at'
        ]
        read_only_fields = ['start_date', 'end_date', 'is_active']

    def get_days_remaining(self, obj):
        """Calculate days remaining in subscription"""
        if not obj.is_active:
            return 0
        
        today = timezone.now().date()
        if today > obj.end_date:
            return 0
            
        return (obj.end_date - today).days

class SubscriptionPurchaseSerializer(serializers.Serializer):
    plan_id = serializers.IntegerField()
    duration_type = serializers.ChoiceField(
        choices=['MONTHLY', 'YEARLY', 'LIFETIME']
    )
    payment_method = serializers.ChoiceField(
        choices=['WALLET', 'ONLINE']
    )
    auto_renew = serializers.BooleanField(default=False)

    def validate_plan_id(self, value):
        """Validate plan exists and is active"""
        try:
            plan = Plan.objects.get(id=value, is_active=True)
        except Plan.DoesNotExist:
            raise serializers.ValidationError("Invalid or inactive plan selected")
        return value

    def validate(self, data):
        """Validate plan price for duration"""
        plan = Plan.objects.get(id=data['plan_id'])
        price = plan.get_price(data['duration_type'])
        
        if not price:
            raise serializers.ValidationError(
                f"Selected plan does not support {data['duration_type']} duration"
            )
            
        # Check wallet balance if paying with wallet
        if data['payment_method'] == 'WALLET':
            user = self.context['request'].user
            if user.wallet_balance < price:
                raise serializers.ValidationError(
                    "Insufficient wallet balance"
                )
                
        data['price'] = price
        return data
