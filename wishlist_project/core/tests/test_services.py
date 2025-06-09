from django.test import TestCase
from django.contrib.auth.models import User
from core.services.zarinpal import ZarinPalService
from core.services.calendar_integration import CalendarService
from core.services.social_sharing import SocialSharingService
from unittest.mock import patch

class ZarinPalServiceTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.service = ZarinPalService()

    @patch('core.services.zarinpal.requests.post')
    def test_create_payment(self, mock_post):
        mock_post.return_value.json.return_value = {
            'data': {
                'authority': 'test_authority',
                'url': 'https://sandbox.zarinpal.com/pg/StartPay/test_authority'
            },
            'errors': []
        }
        
        result = self.service.create_payment(
            amount=1000,
            description='Test payment',
            email='test@example.com'
        )
        
        self.assertIn('payment_url', result)
        self.assertIn('authority', result)

class CalendarServiceTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.service = CalendarService()

    @patch('core.services.calendar_integration.googleapiclient.discovery.build')
    def test_add_event(self, mock_build):
        mock_calendar = mock_build.return_value
        mock_calendar.events.return_value.insert.return_value.execute.return_value = {
            'id': 'test_event_id'
        }
        
        result = self.service.add_event(
            user=self.user,
            title='Birthday Party',
            date='2024-12-25',
            description='My birthday celebration'
        )
        
        self.assertEqual(result['status'], 'success')
        self.assertEqual(result['event_id'], 'test_event_id')

class SocialSharingServiceTests(TestCase):
    def setUp(self):
        self.service = SocialSharingService()

    @patch('core.services.social_sharing.requests.post')
    def test_share_to_facebook(self, mock_post):
        mock_post.return_value.json.return_value = {
            'id': 'post_id_123'
        }
        
        result = self.service.share_to_facebook(
            title='My Wishlist',
            description='Check out my birthday wishlist!',
            url='https://example.com/wishlist/123'
        )
        
        self.assertEqual(result['status'], 'success')
        self.assertEqual(result['post_id'], 'post_id_123')

    @patch('core.services.social_sharing.tweepy.API')
    def test_share_to_twitter(self, mock_api):
        mock_api.return_value.update_status.return_value._json = {
            'id_str': 'tweet_id_123'
        }
        
        result = self.service.share_to_twitter(
            message='Check out my birthday wishlist! https://example.com/wishlist/123'
        )
        
        self.assertEqual(result['status'], 'success')
        self.assertEqual(result['tweet_id'], 'tweet_id_123')
