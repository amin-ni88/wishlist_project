from django.urls import path
from . import views

urlpatterns = [
    path('request/', views.PaymentRequestView.as_view(),
         name='payment-request'),
    path('verify/', views.PaymentVerifyView.as_view(), name='payment-verify'),
    path('callback/', views.payment_callback, name='payment-callback'),
    path('transactions/', views.TransactionListView.as_view(),
         name='transaction-list'),
    path('wallet/', views.WalletBalanceView.as_view(), name='wallet-balance'),
    path('wallet/charge/', views.ChargeWalletView.as_view(), name='wallet-charge'),
    path('contributions/', views.ContributionListView.as_view(),
         name='contribution-list'),
]
