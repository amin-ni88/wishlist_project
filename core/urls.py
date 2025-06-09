from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    UserViewSet, NotificationViewSet, PlanViewSet
)
from .views.wishlist import EnhancedWishListViewSet
from .views.wishlist_item import EnhancedWishListItemViewSet
from .views.subscription_management import SubscriptionManagementViewSet
from .views.analytics import AnalyticsViewSet
from .views.payment import PaymentVerificationView
from .views.wallet import WalletViewSet
from .views.contribution import ContributionViewSet
from .views.bulk_operations import (
    GuestContributionViewSet,
    BulkOperationsViewSet
)

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')
router.register(r'wishlists', EnhancedWishListViewSet, basename='wishlist')
router.register(r'items', EnhancedWishListItemViewSet,
                basename='wishlist-item')
router.register(r'notifications', NotificationViewSet, basename='notification')
router.register(r'plans', PlanViewSet, basename='plan')
router.register(
    r'subscriptions',
    SubscriptionManagementViewSet,
    basename='subscription'
)
router.register(r'analytics', AnalyticsViewSet, basename='analytics')


urlpatterns = [
    path('', include(router.urls)),
    path(
        'payments/verify/',
        PaymentVerificationView.as_view(),
        name='payment-verify'
    ),
]
