from rest_framework import serializers
from core.models.guest import GuestContributor, GuestContribution, GuestAccessToken
from core.models import WishListItem


class GuestContributorSerializer(serializers.ModelSerializer):
    class Meta:
        model = GuestContributor
        fields = ('id', 'name', 'email')
        read_only_fields = ('id',)


class GuestContributionSerializer(serializers.ModelSerializer):
    guest = GuestContributorSerializer()

    class Meta:
        model = GuestContribution
        fields = (
            'id', 'item', 'guest', 'amount', 'message',
            'status', 'created_at'
        )
        read_only_fields = ('id', 'status', 'created_at')

    def create(self, validated_data):
        guest_data = validated_data.pop('guest')
        guest, _ = GuestContributor.objects.get_or_create(
            email=guest_data['email'],
            defaults={'name': guest_data['name']}
        )
        return GuestContribution.objects.create(
            guest=guest,
            **validated_data
        )


class GuestAccessTokenSerializer(serializers.ModelSerializer):
    class Meta:
        model = GuestAccessToken
        fields = ('token', 'email', 'expires_at', 'created_at')
        read_only_fields = ('token', 'created_at')
