from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from celery import shared_task
from core.models import Notification, User, WishListItem, Contribution, UserSubscription
from datetime import timedelta
from django.utils import timezone

@shared_task
def send_email_notification(user_id, subject, template_name, context):
    """Send email notification using template"""
    try:
        user = User.objects.get(id=user_id)
        
        # Render email template
        html_message = render_to_string(f'notifications/{template_name}.html', context)
        plain_message = strip_tags(html_message)
        
        # Send email
        send_mail(
            subject=subject,
            message=plain_message,
            html_message=html_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False
        )
        
        return True
    except Exception as e:
        return False

@shared_task
def notify_contribution(contribution_id):
    """Notify wishlist owner about new contribution"""
    try:
        contribution = Contribution.objects.select_related(
            'item__wishlist__owner',
            'contributor'
        ).get(id=contribution_id)
        
        # Create notification
        notification = Notification.objects.create(
            user=contribution.item.wishlist.owner,
            type='CONTRIBUTION',
            message=f'New contribution of {contribution.amount} to "{contribution.item.name}"'
        )
        
        # Send email
        context = {
            'contribution': contribution,
            'item': contribution.item,
            'wishlist': contribution.item.wishlist,
            'contributor_name': 'Anonymous' if contribution.is_anonymous else contribution.contributor.username
        }
        
        send_email_notification.delay(
            user_id=contribution.item.wishlist.owner.id,
            subject='New Contribution to Your Wishlist',
            template_name='contribution_notification',
            context=context
        )
        
        return True
    except Exception as e:
        return False

@shared_task
def notify_wishlist_invite(invitation_id):
    """Notify user about wishlist invitation"""
    try:
        from core.models import ShareInvitation
        invitation = ShareInvitation.objects.select_related('wishlist', 'invited_by').get(id=invitation_id)
        
        # Create notification
        notification = Notification.objects.create(
            user=invitation.invited_user,
            type='WISHLIST_SHARE',
            message=f'{invitation.invited_by.username} shared a wishlist with you'
        )
        
        # Send email
        context = {
            'invitation': invitation,
            'wishlist': invitation.wishlist,
            'invited_by': invitation.invited_by
        }
        
        send_email_notification.delay(
            user_id=invitation.invited_user.id,
            subject='New Wishlist Invitation',
            template_name='wishlist_invite',
            context=context
        )
        
        return True
    except Exception as e:
        return False

@shared_task
def notify_subscription_expiry():
    """Notify users about subscription expiry"""
    # Get subscriptions expiring in the next week
    expiry_threshold = timezone.now().date() + timedelta(days=7)
    
    subscriptions = UserSubscription.objects.select_related('user', 'plan').filter(
        is_active=True,
        end_date__date=expiry_threshold
    )
    
    for subscription in subscriptions:
        # Create notification
        notification = Notification.objects.create(
            user=subscription.user,
            type='SUBSCRIPTION_EXPIRY',
            message=f'Your {subscription.plan.name} subscription will expire in 7 days'
        )
        
        # Send email
        context = {
            'subscription': subscription,
            'user': subscription.user,
            'days_remaining': 7
        }
        
        send_email_notification.delay(
            user_id=subscription.user.id,
            subject='Subscription Expiring Soon',
            template_name='subscription_expiry',
            context=context
        )
    
    return len(subscriptions)

@shared_task
def notify_item_price_change(item_id, old_price, new_price):
    """Notify wishlist owner about item price changes"""
    try:
        item = WishListItem.objects.select_related('wishlist__owner').get(id=item_id)
        
        # Calculate price change percentage
        change_percent = ((new_price - old_price) / old_price) * 100
        
        # Create notification
        notification = Notification.objects.create(
            user=item.wishlist.owner,
            type='PRICE_CHANGE',
            message=f'Price of "{item.name}" has {"increased" if change_percent > 0 else "decreased"} by {abs(change_percent):.1f}%'
        )
        
        # Send email if price decreased
        if new_price < old_price:
            context = {
                'item': item,
                'old_price': old_price,
                'new_price': new_price,
                'change_percent': abs(change_percent)
            }
            
            send_email_notification.delay(
                user_id=item.wishlist.owner.id,
                subject='Price Drop Alert!',
                template_name='price_drop',
                context=context
            )
        
        return True
    except Exception as e:
        return False
