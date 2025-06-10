from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from django.db.models import Q, Sum, Count, Avg
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from decimal import Decimal
from django.utils import timezone

from core.models import (
    User, UserFollow, Category, Tag, Occasion, Wishlist, WishlistItem,
    WalletTransaction, Contribution, SubscriptionPlan, UserSubscription,
    Notification
)
from .serializers import (
    UserRegistrationSerializer, UserLoginSerializer, UserProfileSerializer,
    CategorySerializer, TagSerializer, OccasionSerializer,
    WishlistSerializer, WishlistCreateSerializer, WishlistItemSerializer,
    WalletTransactionSerializer, ContributionSerializer, ContributionCreateSerializer,
    SubscriptionPlanSerializer, UserSubscriptionSerializer,
    NotificationSerializer, UserFollowSerializer,
    WishlistStatsSerializer, UserStatsSerializer
)


class AuthViewSet(viewsets.GenericViewSet):
    """Authentication endpoints"""
    permission_classes = [permissions.AllowAny]

    @action(detail=False, methods=['post'])
    def register(self, request):
        """User registration"""
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            refresh = RefreshToken.for_user(user)
            return Response({
                'user': UserProfileSerializer(user).data,
                'tokens': {
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                }
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'])
    def login(self, request):
        """User login"""
        serializer = UserLoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            refresh = RefreshToken.for_user(user)
            return Response({
                'user': UserProfileSerializer(user).data,
                'tokens': {
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                }
            })
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserViewSet(viewsets.ModelViewSet):
    """User management endpoints"""
    queryset = User.objects.all()
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ['username', 'first_name', 'last_name', 'email']
    ordering_fields = ['date_joined', 'username']
    ordering = ['-date_joined']

    def get_queryset(self):
        if self.action == 'list':
            # Only show public profiles or friends
            return User.objects.filter(
                Q(profile_visibility='PUBLIC') |
                Q(followers__follower=self.request.user)
            ).distinct()
        return super().get_queryset()

    @action(detail=False, methods=['get', 'patch'])
    def profile(self, request):
        """Get or update current user profile"""
        if request.method == 'GET':
            serializer = UserProfileSerializer(request.user)
            return Response(serializer.data)

        serializer = UserProfileSerializer(
            request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def follow(self, request, pk=None):
        """Follow a user"""
        user_to_follow = self.get_object()
        if user_to_follow == request.user:
            return Response(
                {'error': 'نمی‌توانید خودتان را دنبال کنید'},
                status=status.HTTP_400_BAD_REQUEST
            )

        follow, created = UserFollow.objects.get_or_create(
            follower=request.user,
            followed=user_to_follow
        )

        if created:
            return Response({'message': 'کاربر با موفقیت دنبال شد'})
        return Response({'message': 'قبلاً این کاربر را دنبال کرده‌اید'})

    @action(detail=True, methods=['post'])
    def unfollow(self, request, pk=None):
        """Unfollow a user"""
        user_to_unfollow = self.get_object()
        try:
            follow = UserFollow.objects.get(
                follower=request.user,
                followed=user_to_unfollow
            )
            follow.delete()
            return Response({'message': 'دنبال کردن لغو شد'})
        except UserFollow.DoesNotExist:
            return Response(
                {'error': 'این کاربر را دنبال نمی‌کردید'},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Get user statistics"""
        user = request.user
        stats = {
            'total_contributions': user.contributions.filter(
                status='COMPLETED'
            ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00'),
            'contributions_count': user.contributions.filter(status='COMPLETED').count(),
            'wishlists_created': user.wishlists.filter(is_active=True).count(),
            'items_purchased': user.purchased_items.count(),
            'wallet_balance': user.wallet_balance,
            'followers_count': user.followers_set.count(),
            'following_count': user.following_set.count(),
        }
        serializer = UserStatsSerializer(stats)
        return Response(serializer.data)


class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    """Category endpoints"""
    queryset = Category.objects.filter(is_active=True)
    serializer_class = CategorySerializer
    permission_classes = [permissions.AllowAny]
    ordering = ['sort_order', 'name']


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """Tag endpoints"""
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['name']
    ordering = ['-usage_count', 'name']


class OccasionViewSet(viewsets.ReadOnlyModelViewSet):
    """Occasion endpoints"""
    queryset = Occasion.objects.all()
    serializer_class = OccasionSerializer
    permission_classes = [permissions.AllowAny]
    ordering = ['sort_order', 'name']


class WishlistViewSet(viewsets.ModelViewSet):
    """Wishlist management endpoints"""
    serializer_class = WishlistSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['visibility', 'occasion', 'is_completed']
    search_fields = ['title', 'description']
    ordering_fields = ['created_at', 'updated_at', 'occasion_date']
    ordering = ['-created_at']

    def get_queryset(self):
        if self.action == 'list':
            # Show public wishlists and user's own wishlists
            return Wishlist.objects.filter(
                Q(visibility='PUBLIC', is_active=True) |
                Q(owner=self.request.user)
            ).select_related('owner', 'occasion').prefetch_related('items')
        return Wishlist.objects.all()

    def get_serializer_class(self):
        if self.action == 'create':
            return WishlistCreateSerializer
        return WishlistSerializer

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    @action(detail=True, methods=['get'])
    def by_slug(self, request, pk=None):
        """Get wishlist by slug"""
        wishlist = get_object_or_404(Wishlist, slug=pk)

        # Check permissions
        if wishlist.visibility == 'PRIVATE' and wishlist.owner != request.user:
            return Response(
                {'error': 'دسترسی مجاز نیست'},
                status=status.HTTP_403_FORBIDDEN
            )

        # Increment view count
        if wishlist.owner != request.user:
            wishlist.view_count += 1
            wishlist.save(update_fields=['view_count'])

        serializer = WishlistSerializer(wishlist)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def share(self, request, pk=None):
        """Share wishlist"""
        wishlist = self.get_object()
        if wishlist.owner != request.user:
            return Response(
                {'error': 'فقط صاحب لیست می‌تواند آن را به اشتراک بگذارد'},
                status=status.HTTP_403_FORBIDDEN
            )

        wishlist.share_count += 1
        wishlist.save(update_fields=['share_count'])

        share_url = f"/wishlist/{wishlist.slug}"
        return Response({
            'share_url': share_url,
            'message': 'لینک اشتراک‌گذاری ایجاد شد'
        })

    @action(detail=False, methods=['get'])
    def my_wishlists(self, request):
        """Get current user's wishlists"""
        wishlists = Wishlist.objects.filter(
            owner=request.user
        ).select_related('occasion').prefetch_related('items')

        serializer = WishlistSerializer(wishlists, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Get wishlist statistics"""
        user_wishlists = Wishlist.objects.filter(owner=request.user)

        stats = {
            'total_wishlists': user_wishlists.count(),
            'active_wishlists': user_wishlists.filter(is_active=True, is_completed=False).count(),
            'completed_wishlists': user_wishlists.filter(is_completed=True).count(),
            'total_items': WishlistItem.objects.filter(wishlist__owner=request.user).count(),
            'total_value': user_wishlists.aggregate(
                total=Sum('items__price')
            )['total'] or Decimal('0.00'),
            'total_contributed': user_wishlists.aggregate(
                total=Sum('items__contributed_amount')
            )['total'] or Decimal('0.00'),
        }

        if stats['total_value'] > 0:
            stats['completion_rate'] = float(
                stats['total_contributed'] / stats['total_value'] * 100)
        else:
            stats['completion_rate'] = 0.0

        serializer = WishlistStatsSerializer(stats)
        return Response(serializer.data)


class WishlistItemViewSet(viewsets.ModelViewSet):
    """Wishlist item management endpoints"""
    serializer_class = WishlistItemSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['status', 'category', 'priority']
    search_fields = ['name', 'description', 'brand']
    ordering_fields = ['created_at', 'price', 'priority', 'sort_order']
    ordering = ['sort_order', '-priority']

    def get_queryset(self):
        return WishlistItem.objects.filter(
            wishlist__owner=self.request.user
        ).select_related('wishlist', 'category').prefetch_related('tags')

    def perform_create(self, serializer):
        wishlist_id = self.request.data.get('wishlist')
        wishlist = get_object_or_404(
            Wishlist, id=wishlist_id, owner=self.request.user)
        serializer.save(wishlist=wishlist)

    @action(detail=True, methods=['post'])
    def mark_purchased(self, request, pk=None):
        """Mark item as purchased"""
        item = self.get_object()
        if item.wishlist.owner != request.user:
            return Response(
                {'error': 'فقط صاحب لیست می‌تواند آیتم را خریداری شده علامت‌گذاری کند'},
                status=status.HTTP_403_FORBIDDEN
            )

        item.status = 'PURCHASED'
        item.purchased_by = request.user
        item.purchased_at = timezone.now()
        item.save()

        return Response({'message': 'آیتم به عنوان خریداری شده علامت‌گذاری شد'})


class ContributionViewSet(viewsets.ModelViewSet):
    """Contribution management endpoints"""
    serializer_class = ContributionSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['status', 'is_anonymous']
    ordering = ['-created_at']

    def get_queryset(self):
        if self.request.user.is_authenticated:
            return Contribution.objects.filter(
                Q(contributor=self.request.user) |
                Q(item__wishlist__owner=self.request.user)
            ).select_related('item', 'contributor', 'item__wishlist')
        return Contribution.objects.none()

    def get_serializer_class(self):
        if self.action == 'create':
            return ContributionCreateSerializer
        return ContributionSerializer

    def perform_create(self, serializer):
        # Set contributor if user is authenticated
        if self.request.user.is_authenticated:
            serializer.save(contributor=self.request.user)
        else:
            serializer.save()

    @action(detail=False, methods=['post'])
    def contribute(self, request):
        """Make a contribution to an item"""
        serializer = ContributionCreateSerializer(
            data=request.data,
            context={'request': request}
        )

        if serializer.is_valid():
            contribution = serializer.save()

            # Process payment logic here
            # For now, we'll mark it as completed
            contribution.status = 'COMPLETED'
            contribution.completed_at = timezone.now()
            contribution.save()

            # Update item contributed amount
            item = contribution.item
            item.contributed_amount += contribution.amount
            item.save()

            return Response(
                ContributionSerializer(contribution).data,
                status=status.HTTP_201_CREATED
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class WalletTransactionViewSet(viewsets.ReadOnlyModelViewSet):
    """Wallet transaction endpoints"""
    serializer_class = WalletTransactionSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['transaction_type', 'status']
    ordering = ['-created_at']

    def get_queryset(self):
        return WalletTransaction.objects.filter(
            user=self.request.user
        ).select_related('related_item', 'related_contribution')

    @action(detail=False, methods=['post'])
    def deposit(self, request):
        """Deposit money to wallet"""
        amount = request.data.get('amount')
        if not amount or float(amount) <= 0:
            return Response(
                {'error': 'مبلغ باید بیشتر از صفر باشد'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Create transaction
        transaction = WalletTransaction.objects.create(
            user=request.user,
            transaction_type='DEPOSIT',
            amount=Decimal(str(amount)),
            description=f'واریز {amount} تومان به کیف پول',
            status='COMPLETED'
        )

        # Update user balance
        request.user.wallet_balance += transaction.amount
        request.user.save()

        return Response(WalletTransactionSerializer(transaction).data)


class SubscriptionPlanViewSet(viewsets.ReadOnlyModelViewSet):
    """Subscription plan endpoints"""
    queryset = SubscriptionPlan.objects.filter(is_active=True)
    serializer_class = SubscriptionPlanSerializer
    permission_classes = [permissions.AllowAny]
    ordering = ['sort_order', 'monthly_price']


class UserSubscriptionViewSet(viewsets.ReadOnlyModelViewSet):
    """User subscription endpoints"""
    serializer_class = UserSubscriptionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return UserSubscription.objects.filter(user=self.request.user)

    @action(detail=False, methods=['get'])
    def current(self, request):
        """Get current user subscription"""
        try:
            subscription = UserSubscription.objects.get(
                user=request.user,
                is_active=True
            )
            serializer = UserSubscriptionSerializer(subscription)
            return Response(serializer.data)
        except UserSubscription.DoesNotExist:
            return Response(
                {'message': 'هیچ اشتراک فعالی وجود ندارد'},
                status=status.HTTP_404_NOT_FOUND
            )


class NotificationViewSet(viewsets.ModelViewSet):
    """Notification management endpoints"""
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['notification_type', 'is_read']
    ordering = ['-created_at']

    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user)

    @action(detail=True, methods=['post'])
    def mark_read(self, request, pk=None):
        """Mark notification as read"""
        notification = self.get_object()
        notification.is_read = True
        notification.read_at = timezone.now()
        notification.save()

        return Response({'message': 'اعلان به عنوان خوانده شده علامت‌گذاری شد'})

    @action(detail=False, methods=['post'])
    def mark_all_read(self, request):
        """Mark all notifications as read"""
        count = Notification.objects.filter(
            user=request.user,
            is_read=False
        ).update(is_read=True, read_at=timezone.now())

        return Response({'message': f'{count} اعلان به عنوان خوانده شده علامت‌گذاری شد'})

    @action(detail=False, methods=['get'])
    def unread_count(self, request):
        """Get unread notifications count"""
        count = Notification.objects.filter(
            user=request.user,
            is_read=False
        ).count()

        return Response({'unread_count': count})


# Additional utility views
class SearchView(APIView):
    """Global search endpoint"""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        query = request.query_params.get('q', '')
        if not query:
            return Response({'error': 'پارامتر جستجو الزامی است'}, status=400)

        # Search in wishlists
        wishlists = Wishlist.objects.filter(
            Q(title__icontains=query) | Q(description__icontains=query),
            visibility='PUBLIC',
            is_active=True
        )[:10]

        # Search in users
        users = User.objects.filter(
            Q(username__icontains=query) |
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query),
            profile_visibility='PUBLIC'
        )[:10]

        return Response({
            'wishlists': WishlistSerializer(wishlists, many=True).data,
            'users': UserProfileSerializer(users, many=True).data,
        })


class DashboardView(APIView):
    """Dashboard data endpoint"""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user

        # Recent wishlists
        recent_wishlists = Wishlist.objects.filter(
            owner=user,
            is_active=True
        ).order_by('-updated_at')[:5]

        # Recent contributions received
        recent_contributions = Contribution.objects.filter(
            item__wishlist__owner=user,
            status='COMPLETED'
        ).order_by('-created_at')[:5]

        # Notifications
        unread_notifications = Notification.objects.filter(
            user=user,
            is_read=False
        ).order_by('-created_at')[:5]

        return Response({
            'recent_wishlists': WishlistSerializer(recent_wishlists, many=True).data,
            'recent_contributions': ContributionSerializer(recent_contributions, many=True).data,
            'unread_notifications': NotificationSerializer(unread_notifications, many=True).data,
            'wallet_balance': user.wallet_balance,
        })
