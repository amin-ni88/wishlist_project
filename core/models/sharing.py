from django.db import models
from django.conf import settings

class WishListShare(models.Model):
    """Model for tracking wishlist shares"""
    wishlist = models.ForeignKey(
        'WishList',
        on_delete=models.CASCADE,
        related_name='shares'
    )
    shared_with = models.EmailField()
    access_token = models.CharField(max_length=100)
    is_used = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()

    class Meta:
        unique_together = ['wishlist', 'shared_with']

    def __str__(self):
        return f"{self.wishlist.title} shared with {self.shared_with}"
