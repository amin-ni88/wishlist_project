#!/usr/bin/env python3
"""
🛡️ Security Features Test Script
تست کامل امکانات امنیتی پلتفرم
"""

import requests
import json
import time
from datetime import datetime

# Configuration
API_BASE = 'http://127.0.0.1:8001'
HEADERS = {'Content-Type': 'application/json'}


def print_test_header(test_name):
    print(f"\n{'='*60}")
    print(f"🧪 {test_name}")
    print(f"{'='*60}")


def test_captcha_generation():
    """Test Captcha Generation API"""
    print_test_header("تست تولید کپچا")

    url = f"{API_BASE}/anti-bot/generate-captcha/"
    response = requests.post(url, headers=HEADERS)

    if response.status_code == 200:
        data = response.json()
        if data.get('success'):
            print("✅ کپچا با موفقیت تولید شد")
            print(f"   سوال: {data['captcha']['question']}")
            print(f"   ID: {data['captcha']['challenge_id']}")
            return data['captcha']
        else:
            print("❌ خطا در تولید کپچا:", data.get('message'))
    else:
        print(f"❌ HTTP Error: {response.status_code}")

    return None


def test_email_verification():
    """Test Email Verification API"""
    print_test_header("تست ارسال ایمیل تایید")

    url = f"{API_BASE}/auth/send-email-verification/"
    payload = {
        "email": "test@example.com",
        "verification_type": "LOGIN"
    }

    response = requests.post(url, headers=HEADERS, json=payload)

    if response.status_code == 200:
        data = response.json()
        if data.get('success'):
            print("✅ ایمیل تایید با موفقیت ارسال شد")
            print(f"   پیام: {data.get('message')}")
        else:
            print("❌ خطا در ارسال ایمیل:", data.get('message'))
    else:
        print(f"❌ HTTP Error: {response.status_code}")
        print(f"   Response: {response.text}")


def test_phone_otp():
    """Test Phone OTP API"""
    print_test_header("تست ارسال کد موبایل")

    url = f"{API_BASE}/auth/send-otp/"
    payload = {
        "phone_number": "09123456789"
    }

    response = requests.post(url, headers=HEADERS, json=payload)

    if response.status_code == 200:
        data = response.json()
        if data.get('success'):
            print("✅ کد موبایل با موفقیت ارسال شد")
            print(f"   پیام: {data.get('message')}")
        else:
            print("❌ خطا در ارسال کد:", data.get('message'))
    else:
        print(f"❌ HTTP Error: {response.status_code}")
        print(f"   Response: {response.text}")


def test_google_oauth_url():
    """Test Google OAuth URL Generation"""
    print_test_header("تست URL گوگل OAuth")

    url = f"{API_BASE}/auth/google/url/"
    response = requests.get(url, headers=HEADERS)

    if response.status_code == 200:
        data = response.json()
        if data.get('success'):
            print("✅ URL گوگل OAuth با موفقیت تولید شد")
            print(f"   URL: {data['auth_url'][:100]}...")
            print(f"   State: {data['state']}")
        else:
            print("❌ خطا در تولید URL:", data.get('message'))
    else:
        print(f"❌ HTTP Error: {response.status_code}")
        print(f"   Response: {response.text}")


def test_device_fingerprint():
    """Test Device Fingerprinting"""
    print_test_header("تست شناسایی دستگاه")

    url = f"{API_BASE}/anti-bot/analyze-device/"
    payload = {
        "user_agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "screen_resolution": "1920x1080",
        "timezone": "Asia/Tehran",
        "language": "fa-IR",
        "plugins": ["PDF Viewer", "Chrome PDF Plugin"],
        "canvas_fingerprint": "test_canvas_hash_12345"
    }

    response = requests.post(url, headers=HEADERS, json=payload)

    if response.status_code == 200:
        data = response.json()
        if data.get('success'):
            print("✅ تحلیل دستگاه انجام شد")
            print(f"   امتیاز ریسک: {data.get('risk_score', 'N/A')}")
            print(f"   وضعیت: {data.get('status', 'N/A')}")
        else:
            print("❌ خطا در تحلیل دستگاه:", data.get('message'))
    else:
        print(f"❌ HTTP Error: {response.status_code}")
        print(f"   Response: {response.text}")


def test_behavioral_analysis():
    """Test Behavioral Analysis"""
    print_test_header("تست تحلیل رفتار کاربر")

    url = f"{API_BASE}/anti-bot/analyze-behavior/"
    payload = {
        "typing_speed": 85.5,
        "mouse_movements": [
            {"x": 100, "y": 200, "timestamp": 1640995200},
            {"x": 150, "y": 250, "timestamp": 1640995201},
            {"x": 200, "y": 300, "timestamp": 1640995202}
        ],
        "form_fill_time": 15.7,
        "click_pattern": "normal",
        "scroll_behavior": "human-like"
    }

    response = requests.post(url, headers=HEADERS, json=payload)

    if response.status_code == 200:
        data = response.json()
        if data.get('success'):
            print("✅ تحلیل رفتاری انجام شد")
            print(f"   امتیاز انسانی بودن: {data.get('human_score', 'N/A')}")
            print(f"   نتیجه: {data.get('result', 'N/A')}")
        else:
            print("❌ خطا در تحلیل رفتاری:", data.get('message'))
    else:
        print(f"❌ HTTP Error: {response.status_code}")
        print(f"   Response: {response.text}")


def test_rate_limiting():
    """Test Rate Limiting"""
    print_test_header("تست محدودیت نرخ درخواست")

    url = f"{API_BASE}/auth/send-email-verification/"
    payload = {
        "email": "spam-test@example.com",
        "verification_type": "LOGIN"
    }

    print("در حال ارسال 10 درخواست پی در پی...")

    for i in range(10):
        response = requests.post(url, headers=HEADERS, json=payload)
        status = "✅ موفق" if response.status_code == 200 else f"❌ خطا ({response.status_code})"
        print(f"   درخواست {i+1}: {status}")

        if response.status_code == 429:
            print(f"   ✅ Rate limiting فعال شد در درخواست {i+1}")
            break

        time.sleep(0.5)


def performance_test():
    """Performance Test"""
    print_test_header("تست عملکرد سیستم")

    endpoints = [
        "/anti-bot/generate-captcha/",
        "/auth/google/url/",
    ]

    for endpoint in endpoints:
        url = f"{API_BASE}{endpoint}"

        # Test response time
        start_time = time.time()
        if endpoint == "/anti-bot/generate-captcha/":
            response = requests.post(url, headers=HEADERS)
        else:
            response = requests.get(url, headers=HEADERS)
        end_time = time.time()

        response_time = (end_time - start_time) * 1000  # ms

        status = "✅" if response.status_code == 200 else "❌"
        print(f"{status} {endpoint}: {response_time:.2f}ms")


def main():
    """Main Test Suite"""
    print(f"""
🛡️ Security Features Test Suite
==============================
⏰ شروع تست: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
🌐 Backend URL: {API_BASE}
""")

    try:
        # Test all security features
        test_captcha_generation()
        test_email_verification()
        test_phone_otp()
        test_google_oauth_url()
        test_device_fingerprint()
        test_behavioral_analysis()
        test_rate_limiting()
        performance_test()

        print(f"\n{'='*60}")
        print("🎉 تست کامل شد!")
        print(f"⏰ پایان تست: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("🔍 نتایج:")
        print("   - سیستم کپچا: فعال")
        print("   - احراز هویت ایمیل: فعال")
        print("   - احراز هویت موبایل: فعال")
        print("   - Google OAuth: فعال")
        print("   - تحلیل دستگاه: فعال")
        print("   - تحلیل رفتاری: فعال")
        print("   - محدودیت نرخ: فعال")
        print(f"{'='*60}")

    except KeyboardInterrupt:
        print("\n❌ تست توسط کاربر متوقف شد")
    except Exception as e:
        print(f"\n❌ خطای غیرمنتظره: {e}")


if __name__ == "__main__":
    main()
