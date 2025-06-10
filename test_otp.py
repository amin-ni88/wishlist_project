#!/usr/bin/env python3
"""
اسکریپت تست API های OTP
"""

import requests
import json
import time

BASE_URL = "http://127.0.0.1:8001"


def test_send_otp():
    """تست ارسال OTP"""
    print("🧪 تست ارسال OTP...")

    url = f"{BASE_URL}/auth/send-otp/"
    data = {
        "phone_number": "09123456789",
        "otp_type": "REGISTRATION"
    }

    try:
        response = requests.post(url, json=data)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")

        if response.status_code == 200:
            print("✅ ارسال OTP موفق بود!")
            return True
        else:
            print("❌ خطا در ارسال OTP")
            return False

    except requests.exceptions.RequestException as e:
        print(f"❌ خطای اتصال: {e}")
        return False


def test_verify_otp():
    """تست تایید OTP"""
    print("\n🧪 تست تایید OTP...")

    url = f"{BASE_URL}/auth/register-with-otp/"
    data = {
        "phone_number": "09123456789",
        "otp_code": "123456",  # کد تست - در محیط تولید باید کد واقعی وارد شود
        "first_name": "علی",
        "last_name": "احمدی"
    }

    try:
        response = requests.post(url, json=data)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")

        if response.status_code == 200:
            print("✅ تایید OTP و ثبت‌نام موفق بود!")
            return True
        else:
            print("❌ خطا در تایید OTP")
            return False

    except requests.exceptions.RequestException as e:
        print(f"❌ خطای اتصال: {e}")
        return False


def test_api_endpoints():
    """تست دسترسی به endpoint ها"""
    print("\n🧪 تست دسترسی به API endpoints...")

    endpoints = [
        "/auth/send-otp/",
        "/auth/register-with-otp/",
        "/auth/login-with-otp/",
        "/auth/verify-phone/",
        "/api/wishlists/",
        "/api/payments/",
        "/admin/"
    ]

    for endpoint in endpoints:
        try:
            url = f"{BASE_URL}{endpoint}"
            response = requests.get(url)
            status = "✅" if response.status_code in [
                200, 405, 401, 403] else "❌"
            print(f"{status} {endpoint} - Status: {response.status_code}")
        except Exception as e:
            print(f"❌ {endpoint} - Error: {e}")


def main():
    print("🎁 تست سیستم احراز هویت با موبایل")
    print("=" * 50)

    # تست دسترسی به endpoints
    test_api_endpoints()

    # تست ارسال OTP
    if test_send_otp():
        time.sleep(1)
        # در محیط تست، کد OTP را از لاگ سرور دریافت کنید
        print("\n📝 نکته: در محیط تست، کد OTP در لاگ سرور نمایش داده می‌شود")
        print(
            "برای تست کامل، کد OTP را از لاگ کپی کرده و در تابع test_verify_otp وارد کنید")

        # test_verify_otp()

    print("\n🎉 تست‌ها تمام شدند!")


if __name__ == "__main__":
    main()
