from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator
from core.services.file_upload import FileUploadService
from .user import User


class WishList(models.Model):
    """Model for wishlists"""
    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='wishlists'
    )
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    is_public = models.BooleanField(default=False)
    can_receive_contributions = models.BooleanField(default=True)
    occasion_date = models.DateField(null=True, blank=True)
    cover_image = models.JSONField(
        null=True,
        blank=True,
        help_text='Stores paths to original and thumbnail images'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        # Process cover image if provided
        if hasattr(self, '_cover_image_file') and self._cover_image_file:
            try:
                upload_service = FileUploadService()
                image_data = upload_service.upload_image(
                    self._cover_image_file,
                    folder='wishlist_covers',
                    generate_thumbnails=True
                )

                # Delete old image if exists
                if self.cover_image:
                    upload_service.delete_image(self.cover_image['original'])

                self.cover_image = image_data
            except Exception as e:
                print(f"Error processing cover image: {e}")

            delattr(self, '_cover_image_file')

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.title} by {self.owner.username}"


class WishListItem(models.Model):
    """Model for items in wishlists"""
    PRIORITY_CHOICES = [
        ('LOW', 'Low'),
        ('MEDIUM', 'Medium'),
        ('HIGH', 'High')
    ]

    wishlist = models.ForeignKey(
        WishList,
        on_delete=models.CASCADE,
        related_name='items'
    )
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    quantity = models.PositiveIntegerField(default=1)
    priority = models.CharField(
        max_length=10,
        choices=PRIORITY_CHOICES,
        default='MEDIUM'
    )
    url = models.URLField(blank=True)
    images = models.JSONField(
        null=True,
        blank=True,
        help_text='Stores paths to original and thumbnail images'
    )
    is_purchased = models.BooleanField(default=False)
    purchase_date = models.DateTimeField(null=True, blank=True)
    reserved_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reserved_items'
    )
    reserved_until = models.DateTimeField(null=True, blank=True)
    external_ids = models.JSONField(
        default=dict,
        blank=True,
        help_text='Store IDs from external services (Amazon, etc.)'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        # Process images if provided
        if hasattr(self, '_image_files') and self._image_files:
            try:
                upload_service = FileUploadService()
                image_data_list = []

                for image_file in self._image_files:
                    image_data = upload_service.upload_image(
                        image_file,
                        folder='wishlist_items',
                        generate_thumbnails=True
                    )
                    image_data_list.append(image_data)

                # Delete old images if they exist
                if self.images:
                    for old_image in self.images:
                        upload_service.delete_image(old_image['original'])

                self.images = image_data_list
            except Exception as e:
                print(f"Error processing images: {e}")

            delattr(self, '_image_files')

        # Notify price change if significant
        if self.pk:  # If this is an update
            old_instance = WishListItem.objects.get(pk=self.pk)
            if old_instance.price != self.price:
                from core.tasks.notifications import notify_item_price_change
                notify_item_price_change.delay(
                    self.id,
                    float(old_instance.price),
                    float(self.price)
                )

        super().save(*args, **kwargs)

    @property
    def total_contributions(self):
        """Calculate total contributions received"""
        return self.contributions.aggregate(
            total=models.Sum('amount')
        )['total'] or 0

    @property
    def remaining_amount(self):
        """Calculate remaining amount needed"""
        return max(0, self.price - self.total_contributions)

    def __str__(self):
        return f"{self.name} in {self.wishlist.title}"

    class Meta:
        ordering = ['priority', '-created_at']
