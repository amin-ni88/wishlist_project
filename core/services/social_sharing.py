from typing import Dict, Optional
import requests
from django.conf import settings
from core.models import WishList, WishListItem
import tweepy
import facebook
from linkedin import linkedin

class SocialMediaSharing:
    """Service for sharing wishlists on social media platforms"""
    
    @staticmethod
    def share_on_twitter(
        wishlist: WishList,
        access_token: str,
        access_token_secret: str
    ) -> bool:
        """Share wishlist on Twitter"""
        try:
            auth = tweepy.OAuthHandler(
                settings.TWITTER_API_KEY,
                settings.TWITTER_API_SECRET
            )
            auth.set_access_token(access_token, access_token_secret)
            api = tweepy.API(auth)
            
            # Create tweet text
            tweet_text = (
                f"Check out my wishlist: {wishlist.title}\n"
                f"{settings.SITE_URL}/wishlists/{wishlist.id}"
            )
            
            # Add image if available
            media_ids = []
            featured_items = wishlist.items.filter(image__isnull=False)[:4]
            for item in featured_items:
                media = api.media_upload(item.image.path)
                media_ids.append(media.media_id)
            
            # Post tweet
            api.update_status(
                status=tweet_text,
                media_ids=media_ids if media_ids else None
            )
            return True
            
        except Exception as e:
            print(f"Error sharing on Twitter: {str(e)}")
            return False

    @staticmethod
    def share_on_facebook(
        wishlist: WishList,
        access_token: str
    ) -> bool:
        """Share wishlist on Facebook"""
        try:
            graph = facebook.GraphAPI(access_token)
            
            # Prepare post data
            post_data = {
                'message': f"Check out my wishlist: {wishlist.title}",
                'link': f"{settings.SITE_URL}/wishlists/{wishlist.id}",
            }
            
            # Add image if available
            featured_item = wishlist.items.filter(
                image__isnull=False
            ).first()
            if featured_item:
                post_data['picture'] = featured_item.image.url
            
            # Post to Facebook
            graph.put_object("me", "feed", **post_data)
            return True
            
        except Exception as e:
            print(f"Error sharing on Facebook: {str(e)}")
            return False

    @staticmethod
    def share_on_linkedin(
        wishlist: WishList,
        access_token: str
    ) -> bool:
        """Share wishlist on LinkedIn"""
        try:
            application = linkedin.LinkedInApplication(token=access_token)
            
            # Prepare post data
            post_data = {
                'comment': f"Check out my wishlist: {wishlist.title}",
                'content': {
                    'title': wishlist.title,
                    'description': wishlist.description[:100] + '...',
                    'submitted-url': f"{settings.SITE_URL}/wishlists/{wishlist.id}",
                },
                'visibility': {
                    'code': 'anyone'
                }
            }
            
            # Add image if available
            featured_item = wishlist.items.filter(
                image__isnull=False
            ).first()
            if featured_item:
                post_data['content']['submitted-image-url'] = featured_item.image.url
            
            # Post to LinkedIn
            application.submit_share(**post_data)
            return True
            
        except Exception as e:
            print(f"Error sharing on LinkedIn: {str(e)}")
            return False

    @staticmethod
    def generate_social_preview(wishlist: WishList) -> Dict:
        """Generate social media preview data"""
        featured_items = wishlist.items.all()[:3]
        total_value = sum(item.price for item in wishlist.items.all())
        
        return {
            'title': wishlist.title,
            'description': wishlist.description[:200] + '...',
            'item_count': wishlist.items.count(),
            'total_value': total_value,
            'featured_items': [
                {
                    'name': item.name,
                    'price': item.price,
                    'image_url': item.image.url if item.image else None
                }
                for item in featured_items
            ],
            'share_url': f"{settings.SITE_URL}/wishlists/{wishlist.id}"
        }
