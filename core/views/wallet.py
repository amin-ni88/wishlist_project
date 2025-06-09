from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db import transaction
from django.utils.translation import gettext_lazy as _

from core.models import Transaction
from core.services.payment import PaymentService
from core.serializers.payment import (
    TransactionSerializer,
    WalletChargeRequestSerializer,
    WalletTransferRequestSerializer
)

class WalletViewSet(viewsets.GenericViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = TransactionSerializer

    def get_queryset(self):
        return Transaction.objects.filter(user=self.request.user)

    @action(detail=False, methods=['get'])
    def balance(self, request):
        """Get user's current wallet balance"""
        return Response({
            'balance': request.user.wallet_balance
        })

    @action(detail=False, methods=['post'])
    def charge(self, request):
        """Charge wallet using payment gateway"""
        serializer = WalletChargeRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        amount = serializer.validated_data['amount']
        payment_service = PaymentService()
        
        try:
            transaction = payment_service.create_wallet_transaction(
                user=request.user,
                amount=amount,
                transaction_type='WALLET_CHARGE',
                payment_method='ONLINE'
            )
            
            # Get payment URL from payment gateway
            payment_url = payment_service.get_payment_url(
                amount=amount,
                callback_url=f"/api/wallet/verify/{transaction.reference_id}/"
            )
            
            return Response({
                'transaction_id': transaction.reference_id,
                'payment_url': payment_url
            })
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=False, methods=['post'])
    def transfer(self, request):
        """Transfer money from wallet to another user"""
        serializer = WalletTransferRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        recipient = serializer.validated_data['recipient']
        amount = serializer.validated_data['amount']
        
        if request.user.wallet_balance < amount:
            return Response(
                {'error': _('Insufficient balance')},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            with transaction.atomic():
                # Deduct from sender
                request.user.deduct_from_wallet(amount)
                
                # Add to recipient
                recipient.add_to_wallet(amount)
                
                # Create transactions for both parties
                payment_service = PaymentService()
                sender_transaction = payment_service.create_wallet_transaction(
                    user=request.user,
                    amount=-amount,
                    transaction_type='WALLET_TRANSFER_SENT',
                    description=f'Transfer to {recipient.username}'
                )
                
                recipient_transaction = payment_service.create_wallet_transaction(
                    user=recipient,
                    amount=amount,
                    transaction_type='WALLET_TRANSFER_RECEIVED',
                    description=f'Transfer from {request.user.username}'
                )
                
                return Response({
                    'message': _('Transfer successful'),
                    'transaction_id': sender_transaction.reference_id
                })
                
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=False, methods=['get'])
    def transactions(self, request):
        """Get user's transaction history"""
        page = self.paginate_queryset(self.get_queryset())
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(serializer.data)
