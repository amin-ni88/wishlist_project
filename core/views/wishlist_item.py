from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Sum, F, Count
from django.utils import timezone
from core.models import WishListItem, Contribution
from core.serializers import WishListItemSerializer, ContributionSerializer
from core.permissions import IsWishListOwner, IsPublicOrOwner
import requests
from urllib.parse import urlparse
from bs4 import BeautifulSoup


class EnhancedWishListItemViewSet(viewsets.ModelViewSet):
    """
    Enhanced API endpoint for wishlist items with additional features
    """
    serializer_class = WishListItemSerializer
    permission_classes = [
        permissions.IsAuthenticatedOrReadOnly, IsPublicOrOwner]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['created_at', 'price', 'priority', 'status']

    def get_queryset(self):
        queryset = WishListItem.objects.annotate(
            total_contributions=Sum('contributions__amount'),
            remaining_amount=F('price') - Sum('contributions__amount'),
            contributor_count=Count(
                'contributions__contributor', distinct=True)
        )

        # Filter by wishlist if provided
        wishlist_id = self.request.query_params.get('wishlist')
        if wishlist_id:
            queryset = queryset.filter(wishlist_id=wishlist_id)

        return queryset

    def perform_create(self, serializer):
        # Check if wishlist belongs to user
        wishlist = serializer.validated_data['wishlist']
        if wishlist.owner != self.request.user:
            raise PermissionDenied(
                'You can only add items to your own wishlists')

        # Check item limit
        if not self.request.user.can_add_more_items(wishlist):
            raise PermissionDenied(
                'You have reached the item limit for this wishlist'
            )

        serializer.save()

    @action(detail=True, methods=['post'])
    def contribute(self, request, pk=None):
        """Contribute to an item"""
        item = self.get_object()
        amount = request.data.get('amount')

        if not amount:
            return Response(
                {'error': 'Amount is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        user = request.user
        if user.wallet_balance < float(amount):
            return Response(
                {'error': 'Insufficient funds'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Check if user can receive contributions
        if not item.wishlist.owner.can_receive_contributions():
            return Response(
                {'error': 'This user cannot receive contributions'},
                status=status.HTTP_400_BAD_REQUEST
            )

        contribution = Contribution.objects.create(
            item=item,
            contributor=user,
            amount=amount,
            message=request.data.get('message', ''),
            is_anonymous=request.data.get('is_anonymous', False)
        )

        # Update user's wallet
        user.wallet_balance -= float(amount)
        user.save()

        # Check if item is fulfilled
        total_contributions = item.contributions.aggregate(
            total=Sum('amount')
        )['total'] or 0

        if total_contributions >= item.price:
            item.status = 'FULFILLED'
            item.fulfilled_at = timezone.now()
            item.save()

        return Response(ContributionSerializer(contribution).data)

    @action(detail=True, methods=['post'])
    def fetch_details(self, request, pk=None):
        """Fetch item details from URL"""
        item = self.get_object()
        url = item.product_url

        if not url:
            return Response(
                {'error': 'No product URL provided'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            response = requests.get(url, timeout=5)
            soup = BeautifulSoup(response.text, 'html.parser')

            # Extract details (implement based on supported sites)
            title = soup.find('meta', property='og:title')
            price = soup.find('meta', property='og:price:amount')
            image = soup.find('meta', property='og:image')

            updates = {}
            if title and not item.name:
                updates['name'] = title['content']
            if price and not item.price:
                updates['price'] = float(price['content'])
            if image and not item.image:
                updates['image_url'] = image['content']

            if updates:
                for key, value in updates.items():
                    setattr(item, key, value)
                item.save()

            return Response(WishListItemSerializer(item).data)

        except Exception as e:
            return Response(
                {'error': f'Failed to fetch details: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=True, methods=['get'])
    def contribution_history(self, request, pk=None):
        """Get contribution history for an item"""
        item = self.get_object()
        contributions = item.contributions.order_by('-created_at')

        return Response({
            'total_contributions': contributions.aggregate(
                total=Sum('amount')
            )['total'] or 0,
            'contribution_count': contributions.count(),
            'unique_contributors': contributions.values(
                'contributor'
            ).distinct().count(),
            'contributions': ContributionSerializer(
                contributions,
                many=True
            ).data
        })
