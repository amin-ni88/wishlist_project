from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db import models
from .models import Contribution, Notification, WishlistItem, User
from django.utils import timezone


@receiver(post_save, sender=Contribution)
def update_item_contribution(sender, instance, created, **kwargs):
    """Update wishlist item contribution amount when a contribution is made"""
    if created and instance.status == 'COMPLETED':
        item = instance.item
        item.contributed_amount += instance.amount

        # Check if item is fully funded
        if item.contributed_amount >= item.price:
            item.status = 'PURCHASED'

        item.save(update_fields=['contributed_amount', 'status'])

        # Create notification for wishlist owner
        Notification.objects.create(
            user=item.wishlist.owner,
            title='کمک جدید دریافت شد',
            message=f'مبلغ {instance.amount:,} تومان برای آیتم "{item.name}" کمک شد.',
            notification_type='CONTRIBUTION',
            related_item=item,
            related_user=instance.contributor,
        )


@receiver(post_save, sender=WishlistItem)
def check_wishlist_completion(sender, instance, **kwargs):
    """Check if wishlist is completed when an item status changes"""
    wishlist = instance.wishlist

    # Check if all items are purchased or fully funded
    active_items = wishlist.items.filter(status='ACTIVE')
    if not active_items.exists():
        unfunded_items = wishlist.items.exclude(
            status__in=['PURCHASED', 'RECEIVED']
        ).filter(contributed_amount__lt=models.F('price'))

        if not unfunded_items.exists():
            wishlist.is_completed = True
            wishlist.completion_date = timezone.now()
            wishlist.save(update_fields=['is_completed', 'completion_date'])

            # Create completion notification
            Notification.objects.create(
                user=wishlist.owner,
                title='لیست آرزو تکمیل شد',
                message=f'تبریک! لیست آرزوی "{wishlist.title}" شما به طور کامل تأمین شد.',
                notification_type='WISHLIST_COMPLETE',
                related_wishlist=wishlist,
            )


@receiver(post_save, sender=User)
def create_user_welcome_notification(sender, instance, created, **kwargs):
    """Create welcome notification for new users"""
    if created:
        Notification.objects.create(
            user=instance,
            title='خوش آمدید!',
            message=f'سلام {instance.get_full_name() or instance.username}! به پلتفرم لیست آرزوها خوش آمدید.',
            notification_type='SYSTEM',
        )
