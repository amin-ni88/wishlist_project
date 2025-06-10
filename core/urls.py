from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    UserViewSet, WishlistViewSet, WishlistItemViewSet,
    ContributionViewSet, NotificationViewSet, PlanViewSet,
    SubscriptionViewSet, CustomTokenObtainPairView, RegisterView,
    WishlistShareViewSet, WishlistInvitationViewSet, SocialShareViewSet,
    shared_wishlist_view, create_share_link,
    send_otp, register_with_otp, generate_captcha, verify_captcha,
    check_bot_status, send_email_verification, register_with_email,
    login_with_email, verify_email_token, google_oauth_url,
    google_oauth_callback, google_oauth_direct
)

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')
router.register(r'wishlists', WishlistViewSet, basename='wishlist')
router.register(r'items', WishlistItemViewSet, basename='wishlist-item')
router.register(r'contributions', ContributionViewSet, basename='contribution')
router.register(r'notifications', NotificationViewSet, basename='notification')
router.register(r'plans', PlanViewSet, basename='plan')
router.register(r'subscriptions', SubscriptionViewSet, basename='subscription')
router.register(r'shares', WishlistShareViewSet, basename='wishlist-share')
router.register(r'invitations', WishlistInvitationViewSet,
                basename='wishlist-invitation')
router.register(r'social-shares', SocialShareViewSet, basename='social-share')

urlpatterns = [
    path('', include(router.urls)),
    path('auth/login/', CustomTokenObtainPairView.as_view(),
         name='token_obtain_pair'),
    path('auth/register/', RegisterView.as_view(), name='register'),
    path('auth/token/refresh/', TokenRefreshView.as_view(),
         name='token_refresh'),
    path('api/shared/<str:share_token>/', shared_wishlist_view,
         name='shared-wishlist'),
    path('api/create-share-link/', create_share_link,
         name='create-share-link'),

    # OTP Authentication
    path('auth/send-otp/', send_otp, name='send_otp'),
    path('auth/register-with-otp/', register_with_otp,
         name='register_with_otp'),

    # Email Authentication
    path('auth/send-email-verification/', send_email_verification,
         name='send_email_verification'),
    path('auth/register-with-email/', register_with_email,
         name='register_with_email'),
    path('auth/login-with-email/', login_with_email,
         name='login_with_email'),
    path('auth/verify-email/', verify_email_token,
         name='verify_email'),

    # Google OAuth
    path('auth/google/url/', google_oauth_url,
         name='google_oauth_url'),
    path('auth/google/callback/', google_oauth_callback,
         name='google_oauth_callback'),
    path('auth/google/direct/', google_oauth_direct,
         name='google_oauth_direct'),

    # Anti-Bot System
    path('anti-bot/generate-captcha/', generate_captcha,
         name='generate_captcha'),
    path('anti-bot/verify-captcha/', verify_captcha,
         name='verify_captcha'),
    path('anti-bot/check-status/', check_bot_status,
         name='check_bot_status'),
]
