from django.db import models
from django.conf import settings
import uuid
from datetime import timedelta
from django.utils import timezone


class GuestContributor(models.Model):
    """Model for tracking guest contributors"""
    email = models.EmailField()
    name = models.CharField(max_length=100)
    verification_token = models.CharField(max_length=100, unique=True)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.email})"

    @staticmethod
    def generate_token():
        return str(uuid.uuid4())


class GuestContribution(models.Model):
    """Model for tracking contributions from non-registered users"""
    item = models.ForeignKey(
        'WishListItem',
        on_delete=models.CASCADE,
        related_name='guest_contributions'
    )
    guest = models.ForeignKey(
        GuestContributor,
        on_delete=models.CASCADE,
        related_name='contributions'
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    message = models.TextField(blank=True)
    transaction_id = models.CharField(max_length=100)
    status = models.CharField(
        max_length=20,
        choices=[
            ('PENDING', 'Pending'),
            ('SUCCESS', 'Success'),
            ('FAILED', 'Failed')
        ],
        default='PENDING'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.guest.name}'s contribution to {self.item.name}"


class GuestAccessToken(models.Model):
    """Model for managing temporary access to wishlists for guests"""
    wishlist = models.ForeignKey(
        'WishList',
        on_delete=models.CASCADE,
        related_name='guest_access_tokens'
    )
    token = models.CharField(max_length=100, unique=True)
    email = models.EmailField()
    expires_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Access token for {self.email} - {self.wishlist.title}"

    @staticmethod
    def generate_token():
        return str(uuid.uuid4())

    def is_valid(self):
        return timezone.now() < self.expires_at

    @staticmethod
    def create_token(wishlist, email, duration=timedelta(days=7)):
        token = GuestAccessToken.objects.create(
            wishlist=wishlist,
            email=email,
            token=GuestAccessToken.generate_token(),
            expires_at=timezone.now() + duration
        )
        return token
