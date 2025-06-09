from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.conf import settings
import os
import uuid
from PIL import Image
from io import BytesIO


class FileUploadService:
    """Service for handling file uploads with validation and optimization"""

    ALLOWED_IMAGE_TYPES = {'image/jpeg', 'image/png', 'image/webp'}
    MAX_IMAGE_SIZE = 10 * 1024 * 1024  # 10MB
    THUMB_SIZES = {
        'small': (150, 150),
        'medium': (300, 300),
        'large': (800, 800)
    }

    @classmethod
    def upload_image(cls, image_file, folder='images', generate_thumbnails=True):
        """
        Upload and process image file
        - Validates file type and size
        - Optimizes image
        - Generates thumbnails if requested
        """
        if not image_file:
            raise ValueError("No file provided")

        # Validate file type
        if image_file.content_type not in cls.ALLOWED_IMAGE_TYPES:
            raise ValueError("Invalid image type")

        # Validate file size
        if image_file.size > cls.MAX_IMAGE_SIZE:
            raise ValueError("File too large")

        # Generate unique filename
        ext = os.path.splitext(image_file.name)[1].lower()
        filename = f"{uuid.uuid4()}{ext}"
        path = os.path.join(folder, filename)

        # Open and optimize image
        img = Image.open(image_file)
        if img.mode in ('RGBA', 'P'):
            img = img.convert('RGB')

        # Save optimized image
        output = BytesIO()
        img.save(output, format='JPEG', quality=85, optimize=True)
        default_storage.save(path, ContentFile(output.getvalue()))

        result = {'original': path}

        # Generate thumbnails if requested
        if generate_thumbnails:
            result['thumbnails'] = cls._generate_thumbnails(
                img, folder, filename)

        return result

    @classmethod
    def _generate_thumbnails(cls, img, folder, filename):
        """Generate thumbnails in different sizes"""
        thumbnails = {}
        name, ext = os.path.splitext(filename)

        for size_name, dimensions in cls.THUMB_SIZES.items():
            thumb = img.copy()
            thumb.thumbnail(dimensions, Image.Resampling.LANCZOS)

            thumb_filename = f"{name}_{size_name}{ext}"
            thumb_path = os.path.join(folder, 'thumbnails', thumb_filename)

            output = BytesIO()
            thumb.save(output, format='JPEG', quality=85, optimize=True)
            default_storage.save(thumb_path, ContentFile(output.getvalue()))
            thumbnails[size_name] = thumb_path

        return thumbnails

    @classmethod
    def delete_image(cls, path):
        """Delete image and its thumbnails"""
        try:
            # Delete original
            if default_storage.exists(path):
                default_storage.delete(path)

            # Delete thumbnails if they exist
            folder = os.path.dirname(path)
            name, ext = os.path.splitext(os.path.basename(path))

            for size_name in cls.THUMB_SIZES.keys():
                thumb_path = os.path.join(
                    folder, 'thumbnails', f"{name}_{size_name}{ext}")
                if default_storage.exists(thumb_path):
                    default_storage.delete(thumb_path)

            return True
        except Exception as e:
            return False
