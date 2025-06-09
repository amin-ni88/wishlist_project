from typing import Optional
from decimal import Decimal
from django.conf import settings
from django.utils import timezone
from core.models import Transaction, PaymentGateway, UserSubscription, Plan
from core.models.payment import Transaction


class PaymentService:
    @staticmethod
    def create_wallet_transaction(
        user,
        amount: Decimal,
        transaction_type: str,
        description: str = ''
    ) -> Transaction:
        """Create a wallet transaction"""
        return Transaction.objects.create(
            user=user,
            amount=amount,
            transaction_type=transaction_type,
            payment_method='WALLET',
            status='SUCCESS',
            reference_id=f'W-{timezone.now().timestamp()}',
            description=description
        )

    @staticmethod
    def process_plan_purchase(
        user,
        plan: Plan,
        duration_type: str,
        payment_method: str,
        gateway_id: Optional[int] = None
    ) -> tuple[Transaction, UserSubscription]:
        """Process a plan purchase"""
        amount = plan.get_price(duration_type)

        # Calculate subscription duration
        if duration_type == 'MONTHLY':
            duration = timezone.timedelta(days=30)
        elif duration_type == 'YEARLY':
            duration = timezone.timedelta(days=365)
        else:  # LIFETIME
            duration = timezone.timedelta(days=36500)  # 100 years

        # Create transaction
        transaction = Transaction.objects.create(
            user=user,
            amount=amount,
            transaction_type='PLAN_PURCHASE',
            payment_method=payment_method,
            gateway_id=gateway_id,
            status='PENDING',
            reference_id=f'P-{timezone.now().timestamp()}',
            description=f'Purchase of {plan.name} plan ({duration_type})'
        )

        # Create subscription (will be activated after payment)
        subscription = UserSubscription.objects.create(
            user=user,
            plan=plan,
            start_date=timezone.now(),
            end_date=timezone.now() + duration,
            is_active=False,
            auto_renew=duration_type != 'LIFETIME'
        )

        return transaction, subscription

    @staticmethod
    def process_payment_callback(
        reference_id: str,
        status: str,
        gateway_response: dict
    ) -> Optional[Transaction]:
        """Process payment gateway callback"""
        try:
            transaction = Transaction.objects.get(reference_id=reference_id)
            transaction.status = status
            transaction.save()

            if status == 'SUCCESS':
                if transaction.transaction_type == 'PLAN_PURCHASE':
                    # Activate subscription
                    subscription = UserSubscription.objects.get(
                        user=transaction.user,
                        is_active=False,
                        created_at__date=transaction.created_at.date()
                    )
                    subscription.is_active = True
                    subscription.save()

                elif transaction.transaction_type == 'WALLET_CHARGE':
                    # Update user's wallet balance
                    user = transaction.user
                    user.wallet_balance += transaction.amount
                    user.save()

            return transaction
        except Transaction.DoesNotExist:
            return None
