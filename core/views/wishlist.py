from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Count, Q, Sum
from django.utils import timezone
from core.models import WishList, WishListItem, WishListShare
from core.serializers import WishListSerializer, WishListItemSerializer
from core.permissions import IsWishListOwner, IsPublicOrOwner
import uuid

class EnhancedWishListViewSet(viewsets.ModelViewSet):
    """
    Enhanced API endpoint for wishlists with additional features
    """
    serializer_class = WishListSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsWishListOwner]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'description', 'occasion_date']
    ordering_fields = ['created_at', 'occasion_date', 'title']
    
    def get_queryset(self):
        queryset = WishList.objects.annotate(
            item_count=Count('items'),
            total_value=Sum('items__price'),
            fulfilled_items=Count('items', filter=Q(items__status='FULFILLED'))
        )
        
        if self.request.user.is_authenticated:
            return queryset.filter(
                Q(is_public=True) | 
                Q(owner=self.request.user) |
                Q(shares__shared_with=self.request.user.email)
            ).distinct()
        return queryset.filter(is_public=True)

    def perform_create(self, serializer):
        # Check subscription limits
        if not self.request.user.check_subscription_limits():
            raise PermissionDenied(
                'You have reached your wishlist limit. Please upgrade your plan.'
            )
        serializer.save(owner=self.request.user)

    @action(detail=True, methods=['post'])
    def share(self, request, pk=None):
        """Share wishlist with other users"""
        wishlist = self.get_object()
        emails = request.data.get('emails', [])
        message = request.data.get('message', '')
        
        shares = []
        for email in emails:
            access_token = str(uuid.uuid4())
            share = WishListShare.objects.create(
                wishlist=wishlist,
                shared_with=email,
                access_token=access_token,
                expires_at=timezone.now() + timezone.timedelta(days=30)
            )
            shares.append(share)
            
            # Send email notification (implement in tasks)
            send_wishlist_share_email.delay(
                email=email,
                wishlist_id=wishlist.id,
                access_token=access_token,
                message=message
            )
        
        return Response({
            'status': 'shared',
            'share_count': len(shares)
        })

    @action(detail=True, methods=['get'])
    def statistics(self, request, pk=None):
        """Get wishlist statistics"""
        wishlist = self.get_object()
        items = wishlist.items.all()
        
        return Response({
            'total_items': items.count(),
            'fulfilled_items': items.filter(status='FULFILLED').count(),
            'total_value': items.aggregate(total=Sum('price'))['total'] or 0,
            'total_contributions': items.aggregate(
                total=Sum('contributions__amount')
            )['total'] or 0,
            'unique_contributors': items.values(
                'contributions__contributor'
            ).distinct().count(),
            'days_until_occasion': (
                wishlist.occasion_date - timezone.now().date()
            ).days if wishlist.occasion_date else None
        })

    @action(detail=True, methods=['post'])
    def duplicate(self, request, pk=None):
        """Duplicate a wishlist"""
        original = self.get_object()
        
        # Check subscription limits
        if not request.user.check_subscription_limits():
            raise PermissionDenied(
                'You have reached your wishlist limit. Please upgrade your plan.'
            )
        
        # Create new wishlist
        new_wishlist = WishList.objects.create(
            owner=request.user,
            title=f"Copy of {original.title}",
            description=original.description,
            is_public=False
        )
        
        # Copy items
        for item in original.items.all():
            WishListItem.objects.create(
                wishlist=new_wishlist,
                name=item.name,
                description=item.description,
                price=item.price,
                product_url=item.product_url,
                image=item.image,
                priority=item.priority
            )
        
        return Response(WishListSerializer(new_wishlist).data)

    @action(detail=True, methods=['post'])
    def archive(self, request, pk=None):
        """Archive a wishlist"""
        wishlist = self.get_object()
        wishlist.is_archived = True
        wishlist.archived_at = timezone.now()
        wishlist.save()
        
        return Response({'status': 'archived'})
