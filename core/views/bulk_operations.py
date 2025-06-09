from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db import transaction
from core.models.guest import GuestContributor, GuestContribution, GuestAccessToken
from core.serializers.guest import (
    GuestContributionSerializer,
    GuestAccessTokenSerializer
)
from core.models import WishList, WishListItem
from core.serializers import WishListSerializer, WishListItemSerializer
from django.utils import timezone


class GuestContributionViewSet(viewsets.ModelViewSet):
    """ViewSet for guest contributions"""
    serializer_class = GuestContributionSerializer

    def get_queryset(self):
        # Only show contributions for items the guest has access to
        token = self.request.query_params.get('access_token')
        if not token:
            return GuestContribution.objects.none()

        try:
            access = GuestAccessToken.objects.get(
                token=token,
                expires_at__gt=timezone.now()
            )
            return GuestContribution.objects.filter(
                item__wishlist=access.wishlist
            )
        except GuestAccessToken.DoesNotExist:
            return GuestContribution.objects.none()

    def create(self, request, *args, **kwargs):
        # Validate access token
        token = request.data.get('access_token')
        try:
            access = GuestAccessToken.objects.get(
                token=token,
                expires_at__gt=timezone.now()
            )
        except GuestAccessToken.DoesNotExist:
            return Response(
                {'error': 'Invalid or expired access token'},
                status=status.HTTP_403_FORBIDDEN
            )

        # Create contribution
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED
        )


class BulkOperationsViewSet(viewsets.ViewSet):
    """ViewSet for bulk operations on wishlists and items"""
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=False, methods=['post'])
    def bulk_create_items(self, request):
        """Create multiple items at once"""
        items_data = request.data.get('items', [])
        wishlist_id = request.data.get('wishlist_id')

        try:
            wishlist = WishList.objects.get(
                id=wishlist_id,
                owner=request.user
            )
        except WishList.DoesNotExist:
            return Response(
                {'error': 'Wishlist not found'},
                status=status.HTTP_404_NOT_FOUND
            )

        # Check subscription limits
        if not request.user.check_subscription_limits():
            return Response(
                {'error': 'Item limit reached'},
                status=status.HTTP_403_FORBIDDEN
            )

        created_items = []
        with transaction.atomic():
            for item_data in items_data:
                item_data['wishlist'] = wishlist.id
                serializer = WishListItemSerializer(data=item_data)
                if serializer.is_valid():
                    item = serializer.save()
                    created_items.append(item)

        return Response(
            WishListItemSerializer(created_items, many=True).data,
            status=status.HTTP_201_CREATED
        )

    @action(detail=False, methods=['post'])
    def bulk_update_items(self, request):
        """Update multiple items at once"""
        items_data = request.data.get('items', [])
        updated_items = []

        with transaction.atomic():
            for item_data in items_data:
                item_id = item_data.pop('id', None)
                if not item_id:
                    continue

                try:
                    item = WishListItem.objects.get(
                        id=item_id,
                        wishlist__owner=request.user
                    )
                    serializer = WishListItemSerializer(
                        item,
                        data=item_data,
                        partial=True
                    )
                    if serializer.is_valid():
                        item = serializer.save()
                        updated_items.append(item)
                except WishListItem.DoesNotExist:
                    continue

        return Response(
            WishListItemSerializer(updated_items, many=True).data
        )

    @action(detail=False, methods=['post'])
    def bulk_delete_items(self, request):
        """Delete multiple items at once"""
        item_ids = request.data.get('item_ids', [])

        deleted_count = WishListItem.objects.filter(
            id__in=item_ids,
            wishlist__owner=request.user
        ).delete()[0]

        return Response({
            'deleted_count': deleted_count
        })

    @action(detail=False, methods=['post'])
    def import_wishlist(self, request):
        """Import wishlist items from external source"""
        source = request.data.get('source')
        data = request.data.get('data')
        wishlist_id = request.data.get('wishlist_id')

        try:
            wishlist = WishList.objects.get(
                id=wishlist_id,
                owner=request.user
            )
        except WishList.DoesNotExist:
            return Response(
                {'error': 'Wishlist not found'},
                status=status.HTTP_404_NOT_FOUND
            )

        # Process import based on source
        if source == 'csv':
            items = self._process_csv_import(data)
        elif source == 'amazon':
            items = self._process_amazon_import(data)
        else:
            return Response(
                {'error': 'Unsupported import source'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Create items
        created_items = []
        for item_data in items:
            item_data['wishlist'] = wishlist.id
            serializer = WishListItemSerializer(data=item_data)
            if serializer.is_valid():
                item = serializer.save()
                created_items.append(item)

        return Response(
            WishListItemSerializer(created_items, many=True).data,
            status=status.HTTP_201_CREATED
        )

    def _process_csv_import(self, data):
        # Implementation for CSV import
        pass

    def _process_amazon_import(self, data):
        # Implementation for Amazon wishlist import
        pass
