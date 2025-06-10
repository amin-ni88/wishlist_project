from rest_framework import serializers
from .models import Payment, Transaction, WalletBalance, ContributionRecord
from core.models import WishlistItem


class PaymentRequestSerializer(serializers.Serializer):
    amount = serializers.DecimalField(max_digits=12, decimal_places=2)
    description = serializers.CharField(max_length=500)
    type = serializers.ChoiceField(choices=Payment.PAYMENT_TYPE_CHOICES)
    wishlist_item_id = serializers.UUIDField(required=False)
    is_anonymous = serializers.BooleanField(default=False)
    callback_url = serializers.URLField(required=False)


class PaymentResponseSerializer(serializers.Serializer):
    status = serializers.IntegerField()
    authority = serializers.CharField(max_length=50)
    message = serializers.CharField(required=False)


class PaymentVerifySerializer(serializers.Serializer):
    authority = serializers.CharField(max_length=50)
    amount = serializers.DecimalField(max_digits=12, decimal_places=2)


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = '__all__'
        read_only_fields = ('id', 'user', 'authority',
                            'ref_id', 'created_at', 'updated_at')


class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = '__all__'
        read_only_fields = ('id', 'user', 'created_at', 'updated_at')


class WalletBalanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = WalletBalance
        fields = ['balance', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']


class ContributionRecordSerializer(serializers.ModelSerializer):
    contributor_name = serializers.SerializerMethodField()

    class Meta:
        model = ContributionRecord
        fields = [
            'id', 'contributor_name', 'amount', 'is_anonymous',
            'message', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']

    def get_contributor_name(self, obj):
        if obj.is_anonymous:
            return "کمک‌کننده ناشناس"
        first_name = obj.contributor.first_name
        last_name = obj.contributor.last_name
        full_name = f"{first_name} {last_name}".strip()
        return full_name or obj.contributor.username


class WishlistItemContributionsSerializer(serializers.ModelSerializer):
    contributions = ContributionRecordSerializer(
        many=True, source='payment_contributions')
    total_contributed = serializers.SerializerMethodField()
    contributors_count = serializers.SerializerMethodField()

    class Meta:
        model = WishlistItem
        fields = [
            'id', 'title', 'price', 'total_contributed',
            'contributors_count', 'contributions'
        ]

    def get_total_contributed(self, obj):
        return sum(contribution.amount for contribution in obj.payment_contributions.all())

    def get_contributors_count(self, obj):
        return obj.payment_contributions.count()


class ChargeWalletSerializer(serializers.Serializer):
    amount = serializers.DecimalField(
        max_digits=12, decimal_places=2, min_value=1000)  # حداقل 100 تومان
