from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from core.models import WishList, WishListItem
import json


class WishListViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client.login(username='testuser', password='testpass123')

    def test_create_wishlist(self):
        response = self.client.post(
            reverse('create_wishlist'),
            {
                'title': 'New Wishlist',
                'description': 'Test description',
                'is_public': True
            },
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.content)
        self.assertEqual(data['title'], 'New Wishlist')

    def test_list_wishlists(self):
        WishList.objects.create(
            owner=self.user,
            title="Test Wishlist",
            description="Test description"
        )
        response = self.client.get(reverse('list_wishlists'))
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(len(data), 1)


class WishListItemViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client.login(username='testuser', password='testpass123')
        self.wishlist = WishList.objects.create(
            owner=self.user,
            title="Test Wishlist"
        )

    def test_add_item(self):
        response = self.client.post(
            reverse('add_wishlist_item', kwargs={
                    'wishlist_id': self.wishlist.id}),
            {
                'name': 'New Item',
                'price': 99.99,
                'priority': 'HIGH'
            },
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.content)
        self.assertEqual(data['name'], 'New Item')


class PaymentViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client.login(username='testuser', password='testpass123')

    def test_create_payment(self):
        response = self.client.post(
            reverse('create_payment'),
            {
                'amount': 100.00,
                'description': 'Test payment'
            },
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertIn('payment_url', data)


class BulkOperationsViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client.login(username='testuser', password='testpass123')
        self.wishlist = WishList.objects.create(
            owner=self.user,
            title="Test Wishlist"
        )

    def test_bulk_create_items(self):
        items_data = [
            {
                'name': 'Item 1',
                'price': 99.99,
                'priority': 'HIGH'
            },
            {
                'name': 'Item 2',
                'price': 49.99,
                'priority': 'MEDIUM'
            }
        ]
        response = self.client.post(
            reverse('bulk_create_items', kwargs={
                    'wishlist_id': self.wishlist.id}),
            json.dumps(items_data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.content)
        self.assertEqual(len(data), 2)
