from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db import transaction
from django.db.models import Sum
from django.utils.translation import gettext_lazy as _

from core.models import Contribution, WishListItem
from core.serializers.contribution import ContributionSerializer
from core.permissions import IsWishListOwnerOrContributor


class ContributionViewSet(viewsets.ModelViewSet):
    serializer_class = ContributionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if self.action in ['list', 'retrieve']:
            # Show all contributions for wishlist owner
            if 'item_id' in self.kwargs:
                item = WishListItem.objects.get(id=self.kwargs['item_id'])
                if item.wishlist.owner == self.request.user:
                    return Contribution.objects.filter(item_id=self.kwargs['item_id'])

            # Show only own contributions for others
            return Contribution.objects.filter(contributor=self.request.user)
        return Contribution.objects.none()

    def create(self, request, *args, **kwargs):
        """Create a new contribution"""
        # Add item to serializer context
        item_id = self.kwargs.get('item_id')
        if not item_id:
            return Response(
                {'error': 'Item ID is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            item = WishListItem.objects.get(id=item_id)
        except WishListItem.DoesNotExist:
            return Response(
                {'error': 'Item not found'},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = self.get_serializer(
            data=request.data,
            context={'request': request, 'item': item}
        )
        serializer.is_valid(raise_exception=True)

        try:
            with transaction.atomic():
                contribution = serializer.save(item=item)
                return Response(
                    serializer.data,
                    status=status.HTTP_201_CREATED
                )
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=False, methods=['get'])
    def summary(self, request, item_id=None):
        """Get contribution summary for an item"""
        try:
            item = WishListItem.objects.get(id=item_id)
        except WishListItem.DoesNotExist:
            return Response(
                {'error': 'Item not found'},
                status=status.HTTP_404_NOT_FOUND
            )

        contributions = Contribution.objects.filter(item=item)
        total = contributions.aggregate(Sum('amount'))['amount__sum'] or 0
        contributor_count = contributions.values(
            'contributor').distinct().count()

        return Response({
            'total_amount': total,
            'remaining_amount': max(0, item.price - total),
            'contributor_count': contributor_count,
            'is_fulfilled': total >= item.price
        })
