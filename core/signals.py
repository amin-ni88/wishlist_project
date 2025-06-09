from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Contribution, Notification, WishListItem

@receiver(post_save, sender=Contribution)
def create_contribution_notification(sender, instance, created, **kwargs):
    if created:
        # Notify the wishlist owner
        Notification.objects.create(
            user=instance.item.wishlist.owner,
            type='CONTRIBUTION',
            message=f"{'Someone' if instance.is_anonymous else instance.contributor.username} "
                   f"contributed {instance.amount} to your wishlist item '{instance.item.name}'"
        )

@receiver(post_save, sender=WishListItem)
def notify_on_item_fulfillment(sender, instance, **kwargs):
    if instance.status == 'FULFILLED':
        # Notify the wishlist owner
        Notification.objects.create(
            user=instance.wishlist.owner,
            type='ITEM_FULFILLED',
            message=f"Your wishlist item '{instance.name}' has been fully funded!"
        )
        
        # Notify all contributors
        contributors = instance.contributions.values_list('contributor', flat=True).distinct()
        for contributor_id in contributors:
            if contributor_id and contributor_id != instance.wishlist.owner.id:
                Notification.objects.create(
                    user_id=contributor_id,
                    type='ITEM_FULFILLED',
                    message=f"The item '{instance.name}' you contributed to has been fully funded!"
                )
