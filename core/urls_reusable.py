"""
URLs for reusable parts of the wishlist application.
These URLs are intended to be included in the main URLconf.
"""

from django.urls import path

from core.views.wallet import WalletViewSet
from core.views.contribution import ContributionViewSet
from core.views.payment import PaymentVerificationView

urlpatterns = [
    # Wallet URLs
    path(
        'wallet/charge/',
        WalletViewSet.as_view({'post': 'charge'}),
        name='wallet-charge'
    ),
    path(
        'wallet/transfer/',
        WalletViewSet.as_view({'post': 'transfer'}),
        name='wallet-transfer'
    ),
    path(
        'wallet/balance/',
        WalletViewSet.as_view({'get': 'balance'}),
        name='wallet-balance'
    ),
    path(
        'wallet/transactions/',
        WalletViewSet.as_view({'get': 'transactions'}),
        name='wallet-transactions'
    ),

    # Contribution URLs
    path(
        'items/<int:item_id>/contributions/',
        ContributionViewSet.as_view({
            'get': 'list',
            'post': 'create'
        }),
        name='item-contributions'
    ),
    path(
        'items/<int:item_id>/contributions/summary/',
        ContributionViewSet.as_view({'get': 'summary'}),
        name='item-contributions-summary'
    ),

    # Payment verification URLs
    path(
        'payments/verify/<str:reference_id>/',
        PaymentVerificationView.as_view(),
        name='payment-verify'
    ),
    path(
        'wallet/verify/<str:reference_id>/',
        WalletViewSet.as_view({'get': 'verify_charge'}),
        name='wallet-verify'
    ),
]
