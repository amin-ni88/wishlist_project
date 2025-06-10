"""
Custom Authentication Backends
"""
import requests
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
from django.conf import settings
import logging

logger = logging.getLogger(__name__)
User = get_user_model()


class GoogleOAuthBackend(ModelBackend):
    """Google OAuth Authentication Backend"""

    def authenticate(self, request, google_token=None, **kwargs):
        """
        احراز هویت کاربر با Google OAuth Token
        """
        if not google_token:
            return None

        try:
            # دریافت اطلاعات کاربر از Google
            user_info = self.get_google_user_info(google_token)
            if not user_info:
                return None

            email = user_info.get('email')
            if not email:
                logger.warning('Google user info missing email')
                return None

            # جستجو یا ایجاد کاربر
            user, created = self.get_or_create_user(user_info)

            if created:
                logger.info(f'New Google user created: {email}')
            else:
                logger.info(f'Existing Google user logged in: {email}')

            return user

        except Exception as e:
            logger.error(f'Google OAuth authentication failed: {str(e)}')
            return None

    def get_google_user_info(self, access_token):
        """
        دریافت اطلاعات کاربر از Google API
        """
        try:
            userinfo_url = settings.OAUTH_SETTINGS['GOOGLE']['USERINFO_URL']
            headers = {'Authorization': f'Bearer {access_token}'}

            response = requests.get(userinfo_url, headers=headers, timeout=10)
            response.raise_for_status()

            return response.json()

        except requests.exceptions.RequestException as e:
            logger.error(f'Failed to get Google user info: {str(e)}')
            return None
        except Exception as e:
            logger.error(
                f'Unexpected error getting Google user info: {str(e)}')
            return None

    def get_or_create_user(self, user_info):
        """
        دریافت یا ایجاد کاربر بر اساس اطلاعات Google
        """
        email = user_info['email']

        try:
            # جستجوی کاربر موجود
            user = User.objects.get(email=email)

            # به‌روزرسانی اطلاعات در صورت نیاز
            self.update_user_info(user, user_info)

            return user, False

        except User.DoesNotExist:
            # ایجاد کاربر جدید
            user = self.create_user_from_google(user_info)
            return user, True

    def create_user_from_google(self, user_info):
        """
        ایجاد کاربر جدید از اطلاعات Google
        """
        email = user_info['email']
        first_name = user_info.get('given_name', '')
        last_name = user_info.get('family_name', '')

        # تولید username یکتا از روی ایمیل
        username = self.generate_unique_username(email)

        user = User.objects.create_user(
            username=username,
            email=email,
            first_name=first_name,
            last_name=last_name,
            is_verified=True  # کاربران Google از قبل تایید شده‌اند
        )

        # ذخیره اطلاعات اضافی Google
        if hasattr(user, 'extra_data'):
            user.extra_data = {
                'google_id': user_info.get('id'),
                'google_picture': user_info.get('picture'),
                'google_locale': user_info.get('locale'),
                'auth_provider': 'google'
            }
            user.save()

        return user

    def update_user_info(self, user, user_info):
        """
        به‌روزرسانی اطلاعات کاربر
        """
        updated = False

        # به‌روزرسانی نام و نام خانوادگی
        first_name = user_info.get('given_name', '')
        last_name = user_info.get('family_name', '')

        if user.first_name != first_name:
            user.first_name = first_name
            updated = True

        if user.last_name != last_name:
            user.last_name = last_name
            updated = True

        # اطمینان از تایید بودن
        if not user.is_verified:
            user.is_verified = True
            updated = True

        if updated:
            user.save()

    def generate_unique_username(self, email):
        """
        تولید username یکتا
        """
        base_username = email.split('@')[0]
        username = base_username
        counter = 1

        while User.objects.filter(username=username).exists():
            username = f"{base_username}_{counter}"
            counter += 1

        return username
