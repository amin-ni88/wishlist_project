from celery import shared_task
from django.utils import timezone
from datetime import timedelta
from core.models import WishList, Notification


@shared_task
def check_subscription_status():
    """Check subscription status and send notifications"""
    from core.models import UserSubscription, Notification
    from django.utils import timezone

    # Check subscriptions expiring in 7 days
    expiry_threshold = timezone.now() + timedelta(days=7)
    expiring_subscriptions = UserSubscription.objects.filter(
        is_active=True,
        end_date__lte=expiry_threshold,
        end_date__gt=timezone.now()
    )

    for subscription in expiring_subscriptions:
        days_left = (subscription.end_date - timezone.now()).days
        Notification.objects.create(
            user=subscription.user,
            type='SUBSCRIPTION_EXPIRING',
            message=f'Your {subscription.plan.name} plan will expire in {days_left} days'
        )

    # Deactivate expired subscriptions
    expired_subscriptions = UserSubscription.objects.filter(
        is_active=True,
        end_date__lte=timezone.now()
    )

    for subscription in expired_subscriptions:
        subscription.is_active = False
        subscription.save()
        Notification.objects.create(
            user=subscription.user,
            type='SUBSCRIPTION_EXPIRED',
            message=f'Your {subscription.plan.name} plan has expired'
        )


@shared_task
def check_upcoming_occasions():
    """Check for upcoming occasions and send notifications"""
    # Check occasions in the next 7 days
    upcoming_date = timezone.now().date() + timedelta(days=7)

    upcoming_wishlists = WishList.objects.filter(
        occasion_date__lte=upcoming_date,
        occasion_date__gte=timezone.now().date()
    )

    for wishlist in upcoming_wishlists:
        # Notify the owner
        Notification.objects.create(
            user=wishlist.owner,
            type='OCCASION_REMINDER',
            message=f"Your occasion '{wishlist.title}' is coming up on "
            f"{wishlist.occasion_date.strftime('%B %d, %Y')}"
        )

        # Notify contributors
        contributors = wishlist.items.filter(
            contributions__isnull=False
        ).values_list('contributions__contributor', flat=True).distinct()

        for contributor_id in contributors:
            if contributor_id and contributor_id != wishlist.owner.id:
                Notification.objects.create(
                    user_id=contributor_id,
                    type='OCCASION_REMINDER',
                    message=f"The occasion '{wishlist.title}' you contributed to "
                    f"is coming up on {wishlist.occasion_date.strftime('%B %d, %Y')}"
                )
