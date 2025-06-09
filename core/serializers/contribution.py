from rest_framework import serializers
from django.contrib.auth import get_user_model
from core.models import Contribution, WishListItem

User = get_user_model()

class ContributorSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'avatar']

class ContributionSerializer(serializers.ModelSerializer):
    contributor = ContributorSerializer(read_only=True)
    
    class Meta:
        model = Contribution
        fields = [
            'id',
            'item',
            'contributor',
            'amount',
            'message',
            'is_anonymous',
            'created_at'
        ]
        read_only_fields = ['contributor']

    def validate_amount(self, value):
        """Validate contribution amount"""
        if value <= 0:
            raise serializers.ValidationError(
                "Contribution amount must be greater than 0"
            )
        
        item = self.context.get('item')
        if item:
            remaining = item.price - item.contributions.aggregate(
                total=models.Sum('amount')
            )['total'] or item.price
            
            if value > remaining:
                raise serializers.ValidationError(
                    f"Contribution amount cannot exceed remaining amount: {remaining}"
                )
        
        return value

    def validate_item(self, value):
        """Validate item is available for contribution"""
        if not value.wishlist.can_receive_contributions:
            raise serializers.ValidationError(
                "This wishlist is not accepting contributions"
            )
        if value.is_purchased:
            raise serializers.ValidationError(
                "This item has already been purchased"
            )
        return value

    def create(self, validated_data):
        """Create contribution and handle wallet transaction"""
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            raise serializers.ValidationError(
                "Must be authenticated to make contributions"
            )
            
        # Deduct from user's wallet
        if not request.user.deduct_from_wallet(validated_data['amount']):
            raise serializers.ValidationError("Insufficient wallet balance")
            
        # Create contribution
        contribution = Contribution.objects.create(
            contributor=request.user,
            **validated_data
        )
        
        # Update item status if fully funded
        item = validated_data['item']
        total_contributions = item.contributions.aggregate(
            total=models.Sum('amount')
        )['total'] or 0
        
        if total_contributions >= item.price:
            item.is_purchased = True
            item.save()
            
            # Create notification for wishlist owner
            Notification.objects.create(
                user=item.wishlist.owner,
                type='ITEM_FULFILLED',
                message=f'Your item "{item.name}" has been fully funded!'
            )
        
        return contribution
