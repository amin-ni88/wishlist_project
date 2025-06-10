from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions

from .views import (
    AuthViewSet, UserViewSet, CategoryViewSet, TagViewSet, OccasionViewSet,
    WishlistViewSet, WishlistItemViewSet, ContributionViewSet,
    WalletTransactionViewSet, SubscriptionPlanViewSet, UserSubscriptionViewSet,
    NotificationViewSet, SearchView, DashboardView
)

# API Documentation
schema_view = get_schema_view(
    openapi.Info(
        title="Wishlist Platform API",
        default_version='v2.0',
        description="پلتفرم حرفه‌ای لیست آرزوها با قابلیت کیف پول و مشارکت",
        terms_of_service="https://www.wishlistplatform.com/terms/",
        contact=openapi.Contact(email="support@wishlistplatform.com"),
        license=openapi.License(name="MIT License"),
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
)

# Router configuration
router = DefaultRouter()
router.register(r'auth', AuthViewSet, basename='auth')
router.register(r'users', UserViewSet)
router.register(r'categories', CategoryViewSet)
router.register(r'tags', TagViewSet)
router.register(r'occasions', OccasionViewSet)
router.register(r'wishlists', WishlistViewSet, basename='wishlist')
router.register(r'wishlist-items', WishlistItemViewSet,
                basename='wishlistitem')
router.register(r'contributions', ContributionViewSet, basename='contribution')
router.register(r'wallet-transactions', WalletTransactionViewSet,
                basename='wallettransaction')
router.register(r'subscription-plans', SubscriptionPlanViewSet)
router.register(r'user-subscriptions', UserSubscriptionViewSet,
                basename='usersubscription')
router.register(r'notifications', NotificationViewSet, basename='notification')

urlpatterns = [
    # API Documentation
    path('docs/', schema_view.with_ui('swagger',
         cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc',
         cache_timeout=0), name='schema-redoc'),
    path('schema/', schema_view.without_ui(cache_timeout=0), name='schema-json'),

    # Authentication
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # Utility endpoints
    path('search/', SearchView.as_view(), name='search'),
    path('dashboard/', DashboardView.as_view(), name='dashboard'),

    # Router URLs
    path('', include(router.urls)),
]
