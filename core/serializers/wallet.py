from rest_framework import serializers
from django.contrib.auth import get_user_model
from core.models import Transaction

User = get_user_model()


class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = [
            'id',
            'amount',
            'transaction_type',
            'payment_method',
            'status',
            'reference_id',
            'description',
            'created_at'
        ]


class WalletChargeRequestSerializer(serializers.Serializer):
    amount = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        min_value=1
    )

    def validate_amount(self, value):
        """Validate minimum and maximum charge amounts"""
        if value < 1:
            raise serializers.ValidationError(
                "Charge amount must be at least 1"
            )
        if value > 1000000:  # 1 million
            raise serializers.ValidationError(
                "Charge amount cannot exceed 1,000,000"
            )
        return value


class WalletTransferRequestSerializer(serializers.Serializer):
    recipient = serializers.SlugRelatedField(
        slug_field='username',
        queryset=User.objects.all()
    )
    amount = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        min_value=1
    )
    note = serializers.CharField(
        max_length=200,
        required=False
    )

    def validate_recipient(self, value):
        """Validate recipient is not the sender"""
        request = self.context.get('request')
        if request and value == request.user:
            raise serializers.ValidationError(
                "Cannot transfer to yourself"
            )
        return value

    def validate_amount(self, value):
        """Validate transfer amount"""
        if value < 1:
            raise serializers.ValidationError(
                "Transfer amount must be at least 1"
            )
        request = self.context.get('request')
        if request and value > request.user.wallet_balance:
            raise serializers.ValidationError(
                "Insufficient wallet balance"
            )
        return value
