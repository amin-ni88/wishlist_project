from rest_framework import status, generics, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db import transaction
from django.shortcuts import get_object_or_404
import urllib.request
import urllib.parse
import json
import uuid

from .models import Payment, Transaction, WalletBalance, ContributionRecord
from .serializers import (
    PaymentRequestSerializer, PaymentVerifySerializer,
    TransactionSerializer, WalletBalanceSerializer,
    ContributionRecordSerializer, ChargeWalletSerializer
)
from core.models import WishlistItem

# Zarinpal Configuration
ZARINPAL_MERCHANT_ID = 'XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX'  # باید تنظیم شود
ZARINPAL_REQUEST_URL = 'https://api.zarinpal.com/pg/v4/payment/request.json'
ZARINPAL_VERIFY_URL = 'https://api.zarinpal.com/pg/v4/payment/verify.json'
ZARINPAL_PAYMENT_URL = 'https://www.zarinpal.com/pg/StartPay/'


class PaymentRequestView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = PaymentRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data
        amount = data['amount']
        description = data['description']
        payment_type = data['type']
        wishlist_item_id = data.get('wishlist_item_id')
        is_anonymous = data.get('is_anonymous', False)

        # بررسی مبلغ (حداقل 1000 ریال - 100 تومان)
        if amount < 1000:
            return Response({
                'error': 'حداقل مبلغ قابل پرداخت 100 تومان است'
            }, status=status.HTTP_400_BAD_REQUEST)

        # بررسی آیتم در صورت کمک مالی
        wishlist_item = None
        if payment_type == 'CONTRIBUTION':
            if not wishlist_item_id:
                return Response({
                    'error': 'برای کمک مالی باید آیتم مشخص شود'
                }, status=status.HTTP_400_BAD_REQUEST)

            wishlist_item = get_object_or_404(
                WishlistItem, id=wishlist_item_id)

        try:
            with transaction.atomic():
                # ایجاد رکورد پرداخت
                order_id = f"{payment_type}_{uuid.uuid4().hex[:8]}_{int(uuid.uuid4().timestamp() * 1000)}"

                payment = Payment.objects.create(
                    user=request.user,
                    amount=amount,
                    type=payment_type,
                    description=description,
                    wishlist_item=wishlist_item,
                    is_anonymous=is_anonymous,
                    order_id=order_id,
                    callback_url=request.build_absolute_uri(
                        '/api/payment/callback/')
                )

                # درخواست به Zarinpal
                zarinpal_data = {
                    'merchant_id': ZARINPAL_MERCHANT_ID,
                    'amount': int(amount),
                    'description': description,
                    'callback_url': payment.callback_url,
                    'metadata': {
                        'order_id': order_id,
                        'mobile': getattr(request.user, 'phone', ''),
                        'email': request.user.email
                    }
                }

                req = urllib.request.Request(
                    ZARINPAL_REQUEST_URL,
                    data=json.dumps(zarinpal_data).encode('utf-8'),
                    headers={'Content-Type': 'application/json'}
                )
                response = urllib.request.urlopen(req)

                if response.getcode() == 200:
                    result = json.loads(response.read().decode('utf-8'))
                    if result.get('data', {}).get('code') == 100:
                        authority = result['data']['authority']
                        payment.authority = authority
                        payment.save()

                        return Response({
                            'status': 100,
                            'authority': authority,
                            'message': 'درخواست پرداخت با موفقیت ایجاد شد'
                        })
                    else:
                        payment.status = 'FAILED'
                        payment.save()
                        return Response({
                            'error': result.get('errors', {}).get('message', 'خطا در ایجاد درخواست پرداخت')
                        }, status=status.HTTP_400_BAD_REQUEST)
                else:
                    payment.status = 'FAILED'
                    payment.save()
                    return Response({
                        'error': 'خطا در ارتباط با درگاه پرداخت'
                    }, status=status.HTTP_503_SERVICE_UNAVAILABLE)

        except Exception as e:
            return Response({
                'error': f'خطای سیستمی: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class PaymentVerifyView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = PaymentVerifySerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        authority = serializer.validated_data['authority']
        amount = serializer.validated_data['amount']

        try:
            payment = Payment.objects.get(
                authority=authority, user=request.user)
        except Payment.DoesNotExist:
            return Response({
                'error': 'پرداخت یافت نشد'
            }, status=status.HTTP_404_NOT_FOUND)

        if payment.status == 'COMPLETED':
            return Response({
                'status': 100,
                'ref_id': payment.ref_id,
                'message': 'پرداخت قبلاً تایید شده است'
            })

        try:
            with transaction.atomic():
                # تایید پرداخت با Zarinpal
                verify_data = {
                    'merchant_id': ZARINPAL_MERCHANT_ID,
                    'amount': int(amount),
                    'authority': authority
                }

                req = urllib.request.Request(
                    ZARINPAL_VERIFY_URL,
                    data=json.dumps(verify_data).encode('utf-8'),
                    headers={'Content-Type': 'application/json'}
                )
                response = urllib.request.urlopen(req)

                if response.getcode() == 200:
                    result = json.loads(response.read().decode('utf-8'))
                    if result.get('data', {}).get('code') == 100:
                        ref_id = result['data']['ref_id']

                        # به‌روزرسانی پرداخت
                        payment.status = 'COMPLETED'
                        payment.ref_id = ref_id
                        payment.save()

                        # ایجاد تراکنش
                        transaction_obj = Transaction.objects.create(
                            user=request.user,
                            payment=payment,
                            amount=payment.amount,
                            type=payment.type,
                            status='COMPLETED',
                            description=payment.description,
                            wishlist_item=payment.wishlist_item,
                            is_anonymous=payment.is_anonymous
                        )

                        # پردازش بر اساس نوع پرداخت
                        if payment.type == 'WALLET_CHARGE':
                            # شارژ کیف پول
                            wallet, created = WalletBalance.objects.get_or_create(
                                user=request.user,
                                defaults={'balance': 0}
                            )
                            wallet.add_balance(payment.amount)

                        elif payment.type == 'CONTRIBUTION':
                            # ثبت کمک مالی
                            ContributionRecord.objects.create(
                                contributor=request.user,
                                wishlist_item=payment.wishlist_item,
                                transaction=transaction_obj,
                                amount=payment.amount,
                                is_anonymous=payment.is_anonymous
                            )

                        return Response({
                            'status': 100,
                            'ref_id': ref_id,
                            'message': 'پرداخت با موفقیت تایید شد'
                        })
                    else:
                        payment.status = 'FAILED'
                        payment.save()
                        return Response({
                            'error': result.get('errors', {}).get('message', 'پرداخت تایید نشد')
                        }, status=status.HTTP_400_BAD_REQUEST)
                else:
                    return Response({
                        'error': 'خطا در ارتباط با درگاه پرداخت'
                    }, status=status.HTTP_503_SERVICE_UNAVAILABLE)

        except Exception as e:
            return Response({
                'error': f'خطای سیستمی: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET', 'POST'])
@permission_classes([permissions.AllowAny])
def payment_callback(request):
    """Callback endpoint for Zarinpal"""
    if request.method == 'GET':
        authority = request.GET.get('Authority')
        status_param = request.GET.get('Status')

        if status_param == 'OK' and authority:
            return Response({
                'message': 'پرداخت موفق بود. لطفاً به اپلیکیشن برگردید.',
                'authority': authority,
                'status': 'success'
            })
        else:
            return Response({
                'message': 'پرداخت لغو شد یا با خطا مواجه شد.',
                'status': 'failed'
            })

    return Response({'message': 'Invalid request method'})


class TransactionListView(generics.ListAPIView):
    serializer_class = TransactionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Transaction.objects.filter(user=self.request.user)


class WalletBalanceView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        wallet, created = WalletBalance.objects.get_or_create(
            user=request.user,
            defaults={'balance': 0}
        )
        serializer = WalletBalanceSerializer(wallet)
        return Response(serializer.data)


class ChargeWalletView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = ChargeWalletSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        amount = serializer.validated_data['amount']

        # Create payment request for wallet charge
        payment_data = {
            'amount': amount,
            'description': f'شارژ کیف پول - {amount / 10} تومان',
            'type': 'WALLET_CHARGE'
        }

        payment_serializer = PaymentRequestSerializer(data=payment_data)
        if payment_serializer.is_valid():
            # Call PaymentRequestView
            payment_view = PaymentRequestView()
            return payment_view.post(request)

        return Response(payment_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ContributionListView(generics.ListAPIView):
    serializer_class = ContributionRecordSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        wishlist_item_id = self.request.query_params.get('item_id')
        if wishlist_item_id:
            return ContributionRecord.objects.filter(
                wishlist_item_id=wishlist_item_id
            )
        return ContributionRecord.objects.filter(
            contributor=self.request.user
        )
