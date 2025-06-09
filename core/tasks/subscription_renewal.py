from celery import shared_task
from django.utils import timezone
from core.models import UserSubscription
from core.services.payment import PaymentService
from django.db import transaction
from decimal import Decimal


@shared_task
def process_subscription_renewals():
    """Process automatic renewals for subscriptions"""
    # Get subscriptions due for renewal (1 day before expiry)
    renewal_threshold = timezone.now() + timezone.timedelta(days=1)

    subscriptions = UserSubscription.objects.filter(
        is_active=True,
        auto_renew=True,
        end_date__lte=renewal_threshold
    ).select_related('user', 'plan')

    for subscription in subscriptions:
        try:
            with transaction.atomic():
                user = subscription.user
                plan = subscription.plan

                # Calculate renewal period and amount
                if subscription.duration_type == 'MONTHLY':
                    amount = plan.monthly_price
                    duration = timezone.timedelta(days=30)
                else:  # YEARLY
                    amount = plan.yearly_price
                    duration = timezone.timedelta(days=365)

                # Check if user has sufficient wallet balance
                if user.wallet_balance >= amount:
                    # Create wallet transaction
                    PaymentService.create_wallet_transaction(
                        user=user,
                        amount=Decimal(amount),
                        transaction_type='PLAN_PURCHASE',
                        description=f'Auto-renewal of {plan.name} plan'
                    )

                    # Update user's wallet
                    user.wallet_balance -= amount
                    user.save()

                    # Extend subscription
                    subscription.end_date = subscription.end_date + duration
                    subscription.save()
                else:
                    # Create pending transaction for online payment
                    PaymentService.process_plan_purchase(
                        user=user,
                        plan=plan,
                        duration_type=subscription.duration_type,
                        payment_method='ONLINE',
                        gateway_id=1  # Default to first active gateway
                    )

                    # Deactivate auto-renew to prevent multiple attempts
                    subscription.auto_renew = False
                    subscription.save()

        except Exception as e:
            # Log error and continue with next subscription
            print(
                f"Error processing renewal for subscription {subscription.id}: {str(e)}")
            continue
