from pathlib import Path
import os
from datetime import timedelta

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get(
    'SECRET_KEY', 'django-insecure-wishlist-platform-secret-key-2024')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.environ.get('DEBUG', 'True') == 'True'

ALLOWED_HOSTS = ['localhost', '127.0.0.1', '0.0.0.0']

# Application definition
DJANGO_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

THIRD_PARTY_APPS = [
    'rest_framework',
    'rest_framework_simplejwt',
    'corsheaders',
    'drf_yasg',
    'django_filters',
]

LOCAL_APPS = [
    'core',
    'api',
    'payment',
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'wishlist_project.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'wishlist_project.wsgi.application'

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DB_NAME', 'wishlist_platform_db'),
        'USER': os.environ.get('DB_USER', 'wishlist_admin'),
        'PASSWORD': os.environ.get('DB_PASSWORD', 'wishlist_secure_123'),
        'HOST': os.environ.get('DB_HOST', 'localhost'),
        'PORT': os.environ.get('DB_PORT', '5432'),
    }
}

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Custom user model
AUTH_USER_MODEL = 'core.User'

# Internationalization
LANGUAGE_CODE = 'fa-ir'
TIME_ZONE = 'Asia/Tehran'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# REST Framework settings
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
    ],
    'DEFAULT_PARSER_CLASSES': [
        'rest_framework.parsers.JSONParser',
        'rest_framework.parsers.MultiPartParser',
        'rest_framework.parsers.FormParser',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ],
    'DATETIME_FORMAT': '%Y-%m-%d %H:%M:%S',
    'DATE_FORMAT': '%Y-%m-%d',
}

# JWT Settings
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=24),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=30),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'UPDATE_LAST_LOGIN': True,
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
    'VERIFYING_KEY': None,
    'AUDIENCE': None,
    'ISSUER': None,
    'JWK_URL': None,
    'LEEWAY': 0,
    'AUTH_HEADER_TYPES': ('Bearer',),
    'AUTH_HEADER_NAME': 'HTTP_AUTHORIZATION',
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',
    'USER_AUTHENTICATION_RULE': 'rest_framework_simplejwt.authentication.default_user_authentication_rule',
    'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
    'TOKEN_TYPE_CLAIM': 'token_type',
    'TOKEN_USER_CLASS': 'rest_framework_simplejwt.models.TokenUser',
    'JTI_CLAIM': 'jti',
    'SLIDING_TOKEN_REFRESH_EXP_CLAIM': 'refresh_exp',
    'SLIDING_TOKEN_LIFETIME': timedelta(hours=24),
    'SLIDING_TOKEN_REFRESH_LIFETIME': timedelta(days=30),
}

# CORS settings
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:8081",
    "http://127.0.0.1:8081",
    "http://localhost:19006",
    "http://127.0.0.1:19006",
]

CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_ALL_ORIGINS = DEBUG

# Swagger/OpenAPI Settings
SWAGGER_SETTINGS = {
    'SECURITY_DEFINITIONS': {
        'Bearer': {
            'type': 'apiKey',
            'name': 'Authorization',
            'in': 'header'
        }
    },
    'USE_SESSION_AUTH': False,
    'JSON_EDITOR': True,
    'SUPPORTED_SUBMIT_METHODS': [
        'get',
        'post',
        'put',
        'delete',
        'patch'
    ],
    'OPERATIONS_SORTER': 'alpha',
    'TAGS_SORTER': 'alpha',
    'DOC_EXPANSION': 'none',
    'DEEP_LINKING': True,
    'SHOW_EXTENSIONS': True,
    'DEFAULT_MODEL_RENDERING': 'example'
}

REDOC_SETTINGS = {
    'LAZY_RENDERING': False,
}

# File upload settings
FILE_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024  # 10MB
DATA_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024  # 10MB
FILE_UPLOAD_PERMISSIONS = 0o644

# Platform-specific Settings
PLATFORM_NAME = 'Wishlist Platform'
PLATFORM_VERSION = '2.0.0'
PLATFORM_DESCRIPTION = 'پلتفرم حرفه‌ای لیست آرزوها با قابلیت کیف پول و مشارکت'

# Business Logic Settings
DEFAULT_CURRENCY = 'IRR'
MIN_CONTRIBUTION_AMOUNT = 10000  # 10,000 Rials
MAX_CONTRIBUTION_AMOUNT = 50000000  # 50 Million Rials
WALLET_TRANSACTION_FEE_PERCENTAGE = 2.5  # 2.5% fee
FREE_PLAN_LIMITS = {
    'max_wishlists': 3,
    'max_items_per_wishlist': 20,
    'max_image_uploads': 50,
}

# Notification Settings
NOTIFICATION_BATCH_SIZE = 100
NOTIFICATION_RETRY_ATTEMPTS = 3
NOTIFICATION_RETRY_DELAY = 300  # 5 minutes

# Rate Limiting
RATELIMIT_ENABLE = True
RATELIMIT_USE_CACHE = 'default'

# Anti-Bot Security Settings
ANTI_BOT_SETTINGS = {
    'ENABLE_CAPTCHA': True,
    'CAPTCHA_DIFFICULTY': 'MEDIUM',  # EASY, MEDIUM, HARD
    'MAX_RISK_SCORE': 80,  # حداکثر امتیاز ریسک قابل قبول
    'REQUIRE_CAPTCHA_THRESHOLD': 50,  # آستانه نیاز به Captcha
    'AUTO_BLOCK_THRESHOLD': 80,  # آستانه مسدود کردن خودکار
    'IP_BLOCK_DURATION_HOURS': 24,  # مدت مسدودیت IP (ساعت)
    'RATE_LIMIT_ATTEMPTS': 5,  # حداکثر تلاش در بازه زمانی
    'RATE_LIMIT_WINDOW_MINUTES': 60,  # بازه زمانی محدودیت (دقیقه)
    'DEVICE_RISK_FACTORS': {
        'SUSPICIOUS_USER_AGENT': 40,
        'HIGH_FAILURE_RATE': 35,
        'MULTIPLE_ATTEMPTS': 25,
        'MISSING_BROWSER_INFO': 20,
    },
    'BEHAVIOR_ANALYSIS': {
        'MIN_FORM_FILL_TIME': 2,  # حداقل زمان پر کردن فرم (ثانیه)
        'MAX_TYPING_SPEED': 10,  # حداکثر سرعت تایپ (کاراکتر/ثانیه)
        'MIN_PAGE_TIME': 5,  # حداقل زمان روی صفحه (ثانیه)
        'REQUIRE_MOUSE_MOVEMENT': True,  # نیاز به حرکت ماوس
    }
}

# Security Logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'security': {
            'format': '[SECURITY] {asctime} - {levelname} - {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': BASE_DIR / 'logs' / 'django.log',
            'formatter': 'verbose',
        },
        'security_file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': BASE_DIR / 'logs' / 'security.log',
            'formatter': 'security',
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file', 'console'],
            'level': 'INFO',
            'propagate': True,
        },
        'security': {
            'handlers': ['security_file', 'console'],
            'level': 'INFO',
            'propagate': False,
        },
        'core.services': {
            'handlers': ['file', 'console'],
            'level': 'DEBUG',
            'propagate': True,
        },
    },
}

# Cache Configuration (برای Rate Limiting)
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'unique-snowflake',
        'TIMEOUT': 300,  # 5 دقیقه
    }
}

# Session Configuration
SESSION_ENGINE = 'django.contrib.sessions.backends.db'
SESSION_COOKIE_AGE = 1800  # 30 دقیقه
SESSION_SAVE_EVERY_REQUEST = True
SESSION_EXPIRE_AT_BROWSER_CLOSE = True

# Security Headers
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
SECURE_REFERRER_POLICY = 'strict-origin-when-cross-origin'

# CORS Settings for Anti-Bot APIs
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",  # React Native development
    "http://127.0.0.1:3000",
]

# Django REST Framework Throttling
REST_FRAMEWORK['DEFAULT_THROTTLE_CLASSES'] = [
    'rest_framework.throttling.AnonRateThrottle',
    'rest_framework.throttling.UserRateThrottle'
]

REST_FRAMEWORK['DEFAULT_THROTTLE_RATES'] = {
    'anon': '100/hour',  # کاربران مهمان
    'user': '1000/hour',  # کاربران احراز هویت شده
    'otp': '5/hour',  # درخواست OTP
    'captcha': '20/hour',  # درخواست Captcha
}

# Honeypot Fields (فیلدهای تله)
HONEYPOT_FIELDS = [
    'website', 'url', 'homepage', 'company', 'organization',
    'business', 'email_confirmation', 'phone_confirmation'
]

# IP Geolocation (اختیاری - برای تشخیص VPN/Proxy)
IP_GEOLOCATION_API_KEY = os.getenv('IP_GEOLOCATION_API_KEY', '')
ENABLE_IP_GEOLOCATION = bool(IP_GEOLOCATION_API_KEY)

# reCAPTCHA Settings (اختیاری)
RECAPTCHA_PUBLIC_KEY = os.getenv('RECAPTCHA_PUBLIC_KEY', '')
RECAPTCHA_PRIVATE_KEY = os.getenv('RECAPTCHA_PRIVATE_KEY', '')
ENABLE_RECAPTCHA = bool(RECAPTCHA_PUBLIC_KEY and RECAPTCHA_PRIVATE_KEY)

# Google OAuth Configuration
GOOGLE_OAUTH_CLIENT_ID = os.getenv('GOOGLE_OAUTH_CLIENT_ID', '')
GOOGLE_OAUTH_CLIENT_SECRET = os.getenv('GOOGLE_OAUTH_CLIENT_SECRET', '')
GOOGLE_OAUTH_REDIRECT_URI = os.getenv(
    'GOOGLE_OAUTH_REDIRECT_URI', 'http://localhost:3000/auth/google/callback')

# OAuth settings
OAUTH_SETTINGS = {
    'GOOGLE': {
        'CLIENT_ID': GOOGLE_OAUTH_CLIENT_ID,
        'CLIENT_SECRET': GOOGLE_OAUTH_CLIENT_SECRET,
        'REDIRECT_URI': GOOGLE_OAUTH_REDIRECT_URI,
        'SCOPE': [
            'https://www.googleapis.com/auth/userinfo.email',
            'https://www.googleapis.com/auth/userinfo.profile',
            'openid'
        ],
        'AUTH_URL': 'https://accounts.google.com/o/oauth2/auth',
        'TOKEN_URL': 'https://oauth2.googleapis.com/token',
        'USERINFO_URL': 'https://www.googleapis.com/oauth2/v2/userinfo'
    }
}

# Social Authentication Backend
AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'core.backends.GoogleOAuthBackend',  # Custom Google OAuth backend
]

# Frontend URL for OAuth redirects
FRONTEND_URL = os.getenv('FRONTEND_URL', 'http://localhost:3000')
