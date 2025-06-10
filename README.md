# 🎁 Wishlist App - اپلیکیشن لیست آرزو

اپلیکیشن جامع لیست آرزو با قابلیت‌های پرداخت، اشتراک‌گذاری و دعوت دوستان

## 📱 ویژگی‌ها

### 🔐 احراز هویت و امنیت

- سیستم ثبت‌نام و ورود با JWT
- احراز هویت دو مرحله‌ای
- رمزگذاری داده‌های حساس
- سیستم امنیتی پیشرفته با تشخیص تقلب

### 🛍️ مدیریت لیست آرزو

- ایجاد و مدیریت لیست‌های آرزو
- افزودن آیتم‌ها با تصویر و توضیحات
- دسته‌بندی آیتم‌ها
- تعیین اولویت و تاریخ مناسبت

### 💳 سیستم پرداخت

- ادغام با درگاه پرداخت زرین‌پال
- کیف پول داخلی
- پرداخت مستقیم و کمک‌های مالی
- ردیابی تراکنش‌ها و گزارش‌گیری

### 🤝 اشتراک‌گذاری و دعوت

- اشتراک‌گذاری لیست‌ها در شبکه‌های اجتماعی
- ارسال دعوت‌نامه به دوستان
- پیوند‌های اشتراک‌گذاری امن
- تنظیمات حریم خصوصی

### 🔔 اعلان‌ها

- اعلان‌های push
- اعلان‌های ایمیل
- یادآوری‌های هوشمند
- ردیابی فعالیت‌ها

### 🎨 طراحی و UI/UX

- فونت‌های فارسی (دانا و وزیر)
- طراحی Material Design 3
- پشتیبانی از RTL
- رنگ‌بندی و طراحی مدرن
- انیمیشن‌ها و تعاملات روان

## 🏗️ معماری پروژه

### Backend (Django)

```
├── wishlist_project/
│   ├── settings.py          # تنظیمات اصلی
│   ├── urls.py             # URL routing
│   └── wsgi.py             # WSGI config
├── core/                   # اپلیکیشن اصلی
│   ├── models.py           # مدل‌های دیتابیس
│   ├── views.py            # API views
│   ├── serializers.py      # Serializers
│   └── urls.py             # URL patterns
├── payment/                # سیستم پرداخت
│   ├── models.py           # مدل‌های پرداخت
│   ├── views.py            # API های پرداخت
│   ├── serializers.py      # Serializers پرداخت
│   └── security.py         # سیستم امنیتی
└── requirements.txt        # Dependencies
```

### Frontend (React Native)

```
├── src/
│   ├── components/         # کامپوننت‌های قابل استفاده مجدد
│   ├── screens/           # صفحات اپلیکیشن
│   ├── navigation/        # تنظیمات navigation
│   ├── services/          # API services
│   ├── context/           # Context providers
│   ├── theme/            # تنظیمات theme
│   └── utils/            # ابزارهای کمکی
├── assets/               # تصاویر و فونت‌ها
└── package.json         # Dependencies
```

## 🚀 راه‌اندازی پروژه

### پیش‌نیازها

- Python 3.8+
- Node.js 16+
- React Native CLI
- PostgreSQL یا SQLite
- Redis (اختیاری)

### نصب Backend

1. **کلون پروژه**

```bash
git clone <repository-url>
cd wishlist_project
```

2. **ایجاد محیط مجازی**

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# یا
venv\Scripts\activate     # Windows
```

3. **نصب dependencies**

```bash
pip install -r requirements.txt
```

4. **تنظیم متغیرهای محیطی**

```bash
cp .env.example .env
# ویرایش .env با اطلاعات خود
```

5. **اجرای migrations**

```bash
python manage.py makemigrations
python manage.py migrate
```

6. **ایجاد superuser**

```bash
python manage.py createsuperuser
```

7. **راه‌اندازی سرور**

```bash
python manage.py runserver 8001
```

### نصب Frontend

1. **رفتن به پوشه frontend**

```bash
cd wishlist_frontend
```

2. **نصب dependencies**

```bash
npm install
```

3. **تنظیم آدرس سرور**

```typescript
// src/services/axiosConfig.ts
const BASE_URL = "http://YOUR_SERVER_IP:8001";
```

4. **اجرای اپلیکیشن**

```bash
# Android
npx react-native run-android

# iOS
npx react-native run-ios
```

## 🔧 تنظیمات پیشرفته

### پیکربندی زرین‌پال

```python
# settings.py
ZARINPAL_MERCHANT_ID = 'YOUR_MERCHANT_ID'
ZARINPAL_SANDBOX = True  # برای تست
```

### تنظیمات ایمیل

```python
# settings.py
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'your-email@gmail.com'
EMAIL_HOST_PASSWORD = 'your-password'
```

### تنظیمات امنیتی

```python
# settings.py
# رمزگذاری
ENCRYPTION_KEY = 'your-32-byte-key'

# Rate limiting
RATELIMIT_ENABLE = True
RATELIMIT_USE_CACHE = 'default'

# CORS
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]
```

## 📊 مدل‌های دیتابیس

### Core Models

- **User**: کاربران
- **WishList**: لیست‌های آرزو
- **WishListItem**: آیتم‌های لیست
- **Category**: دسته‌بندی‌ها
- **Tag**: برچسب‌ها

### Payment Models

- **Payment**: پرداخت‌ها
- **Transaction**: تراکنش‌ها
- **WalletBalance**: موجودی کیف پول
- **ContributionRecord**: رکورد کمک‌ها

### Sharing Models

- **WishlistShare**: اشتراک‌گذاری‌ها
- **WishlistInvitation**: دعوت‌نامه‌ها
- **SocialShare**: اشتراک در شبکه‌های اجتماعی
- **ContributionGoal**: اهداف کمک‌های مالی

## 🔐 API Documentation

### Authentication

```http
POST /auth/login/
POST /auth/register/
POST /auth/token/refresh/
```

### Wishlists

```http
GET    /api/wishlists/
POST   /api/wishlists/
GET    /api/wishlists/{id}/
PUT    /api/wishlists/{id}/
DELETE /api/wishlists/{id}/
```

### Payments

```http
POST /api/payments/request/
POST /api/payments/verify/
GET  /api/payments/history/
```

### Sharing

```http
POST /api/shares/
GET  /api/shares/
POST /api/invitations/
GET  /api/shared/{token}/
```

## 🎨 Theme و طراحی

### رنگ‌ها

- **Primary**: `#6C5CE7` (بنفش)
- **Secondary**: `#A29BFE` (بنفش روشن)
- **Success**: `#00B894` (سبز)
- **Error**: `#E84393` (قرمز)
- **Warning**: `#FDCB6E` (زرد)

### فونت‌ها

- **Headers**: دانا (Dana)
- **Body Text**: وزیر (Vazir)

### Spacing

- **Small**: 8px
- **Medium**: 16px
- **Large**: 24px
- **XL**: 32px

## 🧪 تست

### Backend Tests

```bash
python manage.py test
```

### Frontend Tests

```bash
npm test
```

### Coverage Report

```bash
coverage run --source='.' manage.py test
coverage report
```

## 📦 Build و Deploy

### Backend Production

```bash
# Collect static files
python manage.py collectstatic

# Production server
gunicorn wishlist_project.wsgi:application
```

### Frontend Build

```bash
# Android
cd android && ./gradlew assembleRelease

# iOS
cd ios && xcodebuild -workspace WishlistApp.xcworkspace -scheme WishlistApp archive
```

## 🤝 مشارکت

1. Fork کنید
2. Feature branch ایجاد کنید (`git checkout -b feature/AmazingFeature`)
3. تغییرات را commit کنید (`git commit -m 'Add some AmazingFeature'`)
4. Push کنید (`git push origin feature/AmazingFeature`)
5. Pull Request باز کنید

## 📄 مجوز

این پروژه تحت مجوز MIT منتشر شده است. برای اطلاعات بیشتر `LICENSE` را مطالعه کنید.

## 🆘 پشتیبانی

برای سوالات و مشکلات:

- Issues: [GitHub Issues](github-url/issues)
- Email: support@example.com
- Telegram: @support_channel

## 🎯 نقشه راه

### نسخه 1.1

- [ ] پشتیبانی از چندین زبان
- [ ] اپلیکیشن وب
- [ ] API GraphQL

### نسخه 1.2

- [ ] یکپارچه‌سازی با فروشگاه‌ها
- [ ] سیستم امتیازدهی
- [ ] قابلیت‌های اجتماعی پیشرفته

### نسخه 2.0

- [ ] هوش مصنوعی برای پیشنهادات
- [ ] واقعیت افزوده
- [ ] پشتیبانی از ارزهای دیجیتال

---

ساخته شده با ❤️ توسط تیم توسعه لیست آرزو
