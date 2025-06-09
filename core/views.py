from rest_framework import viewsets, permissions, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Sum, F
from django.shortcuts import get_object_or_404
from django.utils import timezone
from .models import WishList, WishListItem, Contribution, Notification, Plan, UserSubscription
from .serializers import (
    UserSerializer, WishListSerializer, WishListItemSerializer,
    ContributionSerializer, NotificationSerializer, PlanSerializer, UserSubscriptionSerializer
)
from .permissions import IsWishListOwner, IsContributor, IsPublicOrOwner

class UserViewSet(viewsets.ModelViewSet):
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return self.model.objects.filter(is_active=True)

class WishListViewSet(viewsets.ModelViewSet):
    serializer_class = WishListSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsWishListOwner]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'description']
    ordering_fields = ['created_at', 'occasion_date']
    
    def get_queryset(self):
        queryset = WishList.objects.all()
        if self.request.user.is_authenticated:
            return queryset.filter(
                is_public=True) | queryset.filter(owner=self.request.user)
        return queryset.filter(is_public=True)
    
    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    @action(detail=True, methods=['post'])
    def share(self, request, pk=None):
        wishlist = self.get_object()
        emails = request.data.get('emails', [])
        # Here you would implement sharing logic
        return Response({'status': 'shared'})

class WishListItemViewSet(viewsets.ModelViewSet):
    serializer_class = WishListItemSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsPublicOrOwner]
    
    def get_queryset(self):
        return WishListItem.objects.annotate(
            total_contributions=Sum('contributions__amount'),
            remaining_amount=F('price') - Sum('contributions__amount')
        )
    
    @action(detail=True, methods=['post'])
    def contribute(self, request, pk=None):
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
        
        contribution = Contribution.objects.create(
            item=item,
            contributor=user,
            amount=amount,
            message=request.data.get('message', ''),
            is_anonymous=request.data.get('is_anonymous', False)
        )
        
        user.wallet_balance -= float(amount)
        user.save()
        
        if item.contributions.aggregate(
            total=Sum('amount'))['total'] >= item.price:
            item.status = 'FULFILLED'
            item.save()
        
        return Response(ContributionSerializer(contribution).data)

class ContributionViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = ContributionSerializer
    permission_classes = [permissions.IsAuthenticated, IsContributor]
    
    def get_queryset(self):
        return Contribution.objects.filter(contributor=self.request.user)

class NotificationViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user)
    
    @action(detail=True, methods=['post'])
    def mark_read(self, request, pk=None):
        notification = self.get_object()
        notification.is_read = True
        notification.save()
        return Response({'status': 'marked_read'})

class PlanViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for viewing subscription plans
    """
    queryset = Plan.objects.all()
    serializer_class = PlanSerializer
    permission_classes = [permissions.AllowAny]

class SubscriptionViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing user subscriptions
    """
    serializer_class = UserSubscriptionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return UserSubscription.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        # Here you would integrate with a payment gateway
        plan = Plan.objects.get(id=serializer.validated_data['plan_id'])
        
        # Calculate end date (e.g., 30 days from now)
        end_date = timezone.now() + timezone.timedelta(days=30)
        
        # Create subscription
        serializer.save(
            user=self.request.user,
            plan=plan,
            end_date=end_date,
            is_active=True
        )

    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        subscription = self.get_object()
        subscription.auto_renew = False
        subscription.save()
        return Response({'status': 'subscription will not renew'})

    @action(detail=True, methods=['post'])
    def renew(self, request, pk=None):
        subscription = self.get_object()
        if not subscription.is_active:
            return Response(
                {'error': 'Cannot renew inactive subscription'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Here you would handle payment processing
        subscription.end_date = (
            subscription.end_date + timezone.timedelta(days=30)
        )
        subscription.auto_renew = True
        subscription.save()
        
        return Response({'status': 'subscription renewed'})
