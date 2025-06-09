from django.test import TestCase
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from core.models import WishList, WishListItem, Contribution, Notification, Plan, Subscription


class WishListModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )

    def test_wishlist_creation(self):
        wishlist = WishList.objects.create(
            owner=self.user,
            title="Birthday Wishlist",
            description="My birthday wishlist",
            is_public=True
        )
        self.assertEqual(wishlist.title, "Birthday Wishlist")
        self.assertEqual(wishlist.owner, self.user)
        self.assertTrue(wishlist.is_public)

    def test_wishlist_item_creation(self):
        wishlist = WishList.objects.create(
            owner=self.user,
            title="Birthday Wishlist"
        )
        item = WishListItem.objects.create(
            wishlist=wishlist,
            name="Gaming Console",
            price=499.99,
            priority="HIGH"
        )
        self.assertEqual(item.name, "Gaming Console")
        self.assertEqual(float(item.price), 499.99)


class ContributionModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.contributor = User.objects.create_user(
            username='contributor',
            email='contributor@example.com',
            password='contribpass123'
        )
        self.wishlist = WishList.objects.create(
            owner=self.user,
            title="Birthday Wishlist"
        )
        self.item = WishListItem.objects.create(
            wishlist=self.wishlist,
            name="Gaming Console",
            price=499.99
        )

    def test_contribution_creation(self):
        contribution = Contribution.objects.create(
            item=self.item,
            contributor=self.contributor,
            amount=50.00
        )
        self.assertEqual(float(contribution.amount), 50.00)
        self.assertEqual(contribution.contributor, self.contributor)


class NotificationModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )

    def test_notification_creation(self):
        notification = Notification.objects.create(
            user=self.user,
            message="You received a new contribution!",
            notification_type="CONTRIBUTION"
        )
        self.assertEqual(notification.message,
                         "You received a new contribution!")
        self.assertEqual(notification.notification_type, "CONTRIBUTION")
        self.assertFalse(notification.is_read)


class PlanAndSubscriptionTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.plan = Plan.objects.create(
            name="Premium",
            price=9.99,
            features=["unlimited wishlists", "priority support"]
        )

    def test_subscription_creation(self):
        subscription = Subscription.objects.create(
            user=self.user,
            plan=self.plan,
            is_active=True
        )
        self.assertTrue(subscription.is_active)
        self.assertEqual(subscription.plan, self.plan)
        self.assertEqual(subscription.user, self.user)
