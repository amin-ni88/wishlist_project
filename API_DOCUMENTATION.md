# 📚 مستندات API سیستم احراز هویت پلتفرم لیست آرزوها

## 🔐 انواع احراز هویت

پلتفرم لیست آرزوها از سه روش احراز هویت پشتیبانی می‌کند:

### 1. 📱 احراز هویت با شماره موبایل (OTP)

### 2. 📧 احراز هویت با ایمیل

### 3. 🔑 احراز هویت با Google OAuth

---

## 📱 احراز هویت با شماره موبایل

### ارسال کد OTP

**Endpoint:** `POST /auth/send-otp/`

**Request Body:**

```json
{
  "phone_number": "09123456789"
}
```

**Response (موفق):**

```json
{
  "success": true,
  "message": "کد تایید ارسال شد"
}
```

**Response (خطا):**

```json
{
  "success": false,
  "message": "شماره موبایل معتبر نیست"
}
```

### ثبت‌نام با OTP

**Endpoint:** `POST /auth/register-with-otp/`

**Request Body:**

```json
{
  "phone_number": "09123456789",
  "otp_code": "123456",
  "first_name": "نام",
  "last_name": "نام خانوادگی",
  "email": "email@example.com"
}
```

**Response (موفق):**

```json
{
  "success": true,
  "message": "ثبت‌نام با موفقیت انجام شد",
  "user": {
    "id": "uuid-here",
    "phone_number": "09123456789",
    "first_name": "نام",
    "last_name": "نام خانوادگی"
  },
  "tokens": {
    "access": "jwt-access-token",
    "refresh": "jwt-refresh-token"
  }
}
```

---

## 📧 احراز هویت با ایمیل

### ارسال ایمیل تایید

**Endpoint:** `POST /auth/send-email-verification/`

**Request Body:**

```json
{
  "email": "user@example.com",
  "verification_type": "REGISTER"
}
```

**Parameters:**

- `verification_type`: `REGISTER`, `LOGIN`, `RESET_PASSWORD`

**Response (موفق):**

```json
{
  "success": true,
  "message": "ایمیل تایید ارسال شد"
}
```

### ثبت‌نام با ایمیل

**Endpoint:** `POST /auth/register-with-email/`

**Request Body:**

```json
{
  "email": "user@example.com",
  "token": "email-verification-token",
  "password": "securePassword123",
  "first_name": "نام",
  "last_name": "نام خانوادگی"
}
```

**Response (موفق):**

```json
{
  "success": true,
  "message": "ثبت‌نام با موفقیت انجام شد",
  "user": {
    "id": "uuid-here",
    "email": "user@example.com",
    "first_name": "نام",
    "last_name": "نام خانوادگی"
  },
  "tokens": {
    "access": "jwt-access-token",
    "refresh": "jwt-refresh-token"
  }
}
```

### ورود با ایمیل

**Endpoint:** `POST /auth/login-with-email/`

**Request Body:**

```json
{
  "email": "user@example.com",
  "password": "securePassword123"
}
```

**Response (موفق):**

```json
{
  "success": true,
  "message": "ورود موفقیت‌آمیز",
  "user": {
    "id": "uuid-here",
    "email": "user@example.com",
    "first_name": "نام",
    "last_name": "نام خانوادگی",
    "is_verified": true
  },
  "tokens": {
    "access": "jwt-access-token",
    "refresh": "jwt-refresh-token"
  }
}
```

### تایید ایمیل

**Endpoint:** `POST /auth/verify-email/`

**Request Body:**

```json
{
  "token": "email-verification-token"
}
```

**Response (موفق):**

```json
{
  "success": true,
  "message": "ایمیل با موفقیت تایید شد"
}
```

---

## 🔑 احراز هویت با Google OAuth

### دریافت URL احراز هویت Google

**Endpoint:** `GET /auth/google/url/`

**Response:**

```json
{
  "success": true,
  "auth_url": "https://accounts.google.com/o/oauth2/auth?...",
  "state": "random-state-token"
}
```

### پردازش بازگشت از Google

**Endpoint:** `POST /auth/google/callback/`

**Request Body:**

```json
{
  "code": "google-authorization-code",
  "state": "state-token"
}
```

**Response (موفق):**

```json
{
  "success": true,
  "message": "ورود با Google موفقیت‌آمیز بود",
  "user": {
    "id": "uuid-here",
    "email": "user@gmail.com",
    "first_name": "نام",
    "last_name": "نام خانوادگی",
    "is_verified": true
  },
  "tokens": {
    "access": "jwt-access-token",
    "refresh": "jwt-refresh-token"
  }
}
```

### احراز هویت مستقیم با Google Token

**Endpoint:** `POST /auth/google/direct/`

**Request Body:**

```json
{
  "access_token": "google-access-token"
}
```

**Response (موفق):**

```json
{
  "success": true,
  "message": "ورود با Google موفقیت‌آمیز بود",
  "user": {
    "id": "uuid-here",
    "email": "user@gmail.com",
    "first_name": "نام",
    "last_name": "نام خانوادگی",
    "is_verified": true
  },
  "tokens": {
    "access": "jwt-access-token",
    "refresh": "jwt-refresh-token"
  }
}
```

---

## 🛡️ سیستم ضد ربات

### تولید Captcha

**Endpoint:** `POST /anti-bot/generate-captcha/`

**Request Body:**

```json
{
  "type": "MATH"
}
```

**Parameters:**

- `type`: `MATH`, `TEXT`, `IMAGE`

**Response:**

```json
{
  "success": true,
  "captcha": {
    "id": "captcha-uuid",
    "question": "5 + 3 = ?",
    "expires_at": "2025-01-01T12:00:00Z"
  }
}
```

### تایید Captcha

**Endpoint:** `POST /anti-bot/verify-captcha/`

**Request Body:**

```json
{
  "captcha_id": "captcha-uuid",
  "answer": "8"
}
```

**Response (موفق):**

```json
{
  "success": true,
  "message": "پاسخ صحیح است"
}
```

### بررسی وضعیت امنیتی

**Endpoint:** `GET /anti-bot/check-status/`

**Response:**

```json
{
  "success": true,
  "data": {
    "is_bot": false,
    "risk_score": 25,
    "blocked_reasons": [],
    "require_captcha": false,
    "device_fingerprint": {},
    "ip_reputation": {},
    "session_id": "session-uuid"
  }
}
```

---

## 🔒 امنیت و محدودیت‌ها

### Rate Limiting

- **OTP**: حداکثر 5 درخواست در ساعت
- **Email**: حداکثر 5 درخواست در ساعت برای هر ایمیل
- **Captcha**: حداکثر 20 درخواست در ساعت
- **عمومی**: حداکثر 100 درخواست در ساعت برای کاربران ناشناس

### امنیت ضد ربات

- **Device Fingerprinting**: تشخیص دستگاه بر اساس ویژگی‌های مرورگر
- **IP Reputation**: امتیازدهی IP ها بر اساس رفتار مشکوک
- **Behavior Analysis**: تحلیل رفتار کاربر (سرعت تایپ، حرکات ماوس، زمان)
- **Honeypot Fields**: فیلدهای مخفی برای تشخیص ربات
- **Captcha**: چالش‌های ریاضی برای تایید انسان بودن

### Honeypot Fields

فیلدهای زیر باید خالی باشند (برای تشخیص ربات):

- `website`
- `url`
- `homepage`
- `company`

---

## 🏗️ نمونه کدهای استفاده

### JavaScript (Frontend)

```javascript
// ثبت‌نام با ایمیل
async function registerWithEmail(email, password, firstName, lastName) {
  // 1. ارسال ایمیل تایید
  const verifyResponse = await fetch("/auth/send-email-verification/", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      email: email,
      verification_type: "REGISTER",
    }),
  });

  if (!verifyResponse.ok) {
    throw new Error("خطا در ارسال ایمیل تایید");
  }

  // 2. کاربر باید ایمیل را چک کند و token را دریافت کند
  // سپس با token ثبت‌نام کند
  const registerResponse = await fetch("/auth/register-with-email/", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      email: email,
      token: emailToken, // از ایمیل دریافت شده
      password: password,
      first_name: firstName,
      last_name: lastName,
    }),
  });

  const result = await registerResponse.json();
  if (result.success) {
    localStorage.setItem("access_token", result.tokens.access);
    localStorage.setItem("refresh_token", result.tokens.refresh);
  }

  return result;
}

// ورود با Google
async function loginWithGoogle() {
  // 1. دریافت URL احراز هویت
  const urlResponse = await fetch("/auth/google/url/");
  const urlData = await urlResponse.json();

  // 2. هدایت کاربر به Google
  window.location.href = urlData.auth_url;

  // 3. پس از بازگشت از Google، کد را ارسال کنید
  // این کار معمولاً در صفحه callback انجام می‌شود
}

// تایید Captcha
async function verifyCaptcha(captchaId, answer) {
  const response = await fetch("/anti-bot/verify-captcha/", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      captcha_id: captchaId,
      answer: answer,
    }),
  });

  return await response.json();
}
```

### Python (Backend Integration)

```python
import requests

class WishlistAuthClient:
    def __init__(self, base_url):
        self.base_url = base_url

    def send_otp(self, phone_number):
        response = requests.post(
            f"{self.base_url}/auth/send-otp/",
            json={"phone_number": phone_number}
        )
        return response.json()

    def register_with_otp(self, phone_number, otp_code, first_name, last_name):
        response = requests.post(
            f"{self.base_url}/auth/register-with-otp/",
            json={
                "phone_number": phone_number,
                "otp_code": otp_code,
                "first_name": first_name,
                "last_name": last_name
            }
        )
        return response.json()

    def login_with_email(self, email, password):
        response = requests.post(
            f"{self.base_url}/auth/login-with-email/",
            json={
                "email": email,
                "password": password
            }
        )
        return response.json()

# استفاده
client = WishlistAuthClient("http://localhost:8001")
result = client.send_otp("09123456789")
print(result)
```

---

## 🐛 خطاهای رایج

### خطاهای احراز هویت

| کد خطا | پیام                    | علت                              |
| ------ | ----------------------- | -------------------------------- |
| 400    | شماره موبایل معتبر نیست | فرمت شماره موبایل اشتباه         |
| 400    | کد OTP نامعتبر است      | کد OTP اشتباه یا منقضی شده       |
| 400    | ایمیل معتبر نیست        | فرمت ایمیل اشتباه                |
| 400    | توکن نامعتبر است        | توکن تایید ایمیل اشتباه یا منقضی |
| 429    | تعداد زیادی درخواست     | محدودیت rate limiting            |
| 500    | خطای سرور               | مشکل داخلی سرور                  |

### خطاهای سیستم ضد ربات

| کد خطا | پیام                | علت                       |
| ------ | ------------------- | ------------------------- |
| 429    | درخواست مسدود شده   | تشخیص رفتار ربات          |
| 400    | پاسخ Captcha اشتباه | پاسخ نادرست به چالش       |
| 400    | Captcha منقضی شده   | مدت زمان Captcha تمام شده |

---

## 📞 پشتیبانی

برای سوالات فنی یا گزارش مشکلات:

- **ایمیل:** support@wishlist-platform.com
- **مستندات:** https://docs.wishlist-platform.com
- **GitHub:** https://github.com/wishlist-platform/api

---

## 🔄 تغییرات نسخه‌ها

### نسخه 2.0.0 (فعلی)

- ✅ احراز هویت با ایمیل
- ✅ احراز هویت با Google OAuth
- ✅ سیستم پیشرفته ضد ربات
- ✅ Device fingerprinting
- ✅ IP reputation system
- ✅ Behavior analysis

### نسخه 1.0.0

- ✅ احراز هویت با شماره موبایل
- ✅ سیستم OTP
- ✅ مدیریت JWT tokens
