#!/usr/bin/env python3
"""
تست ساده سیستم OTP و ضد ربات

استفاده:
python test_otp_simple.py
"""

import requests
import json

BASE_URL = 'http://127.0.0.1:8000'


def test_send_otp():
    """تست ارسال OTP"""
    print("📱 تست ارسال OTP...")

    url = f'{BASE_URL}/auth/send-otp/'
    data = {
        'phone_number': '09123456789'
    }

    response = requests.post(url, json=data)
    print(f"Status: {response.status_code}")

    if response.status_code == 200:
        result = response.json()
        print(f"✅ موفق: {result.get('message')}")
        return True
    else:
        try:
            error = response.json()
            print(f"❌ خطا: {error}")

            # اگر نیاز به Captcha است
            if error.get('require_captcha'):
                print("🔐 نیاز به حل Captcha...")
                return test_captcha_flow()

        except:
            print(f"❌ خطای HTTP: {response.status_code}")

        return False


def test_captcha_flow():
    """تست جریان Captcha"""
    print("🔐 تولید Captcha...")

    # تولید Captcha
    url = f'{BASE_URL}/anti-bot/generate-captcha/'
    response = requests.post(url, json={'type': 'MATH'})

    if response.status_code != 200:
        print(f"❌ خطا در تولید Captcha: {response.status_code}")
        return False

    captcha_data = response.json()['captcha']
    question = captcha_data['question']
    captcha_id = captcha_data['id']

    print(f"سوال: {question}")

    # حل سوال
    try:
        math_expr = question.replace('= ?', '').strip()
        answer = str(eval(math_expr))
        print(f"پاسخ: {answer}")

        # ارسال پاسخ
        verify_url = f'{BASE_URL}/anti-bot/verify-captcha/'
        verify_data = {
            'captcha_id': captcha_id,
            'answer': answer
        }

        verify_response = requests.post(verify_url, json=verify_data)

        if verify_response.status_code == 200:
            result = verify_response.json()
            if result.get('success'):
                print("✅ Captcha حل شد!")

                # حالا دوباره OTP امتحان کن
                print("📱 تلاش مجدد برای ارسال OTP...")
                return test_send_otp()
            else:
                print(f"❌ پاسخ Captcha اشتباه: {result.get('message')}")
        else:
            print(f"❌ خطا در تایید Captcha: {verify_response.status_code}")

    except Exception as e:
        print(f"❌ خطا در حل سوال: {e}")

    return False


def test_bot_detection():
    """تست تشخیص ربات"""
    print("🤖 تست تشخیص ربات...")

    # درخواست با رفتار مشکوک
    url = f'{BASE_URL}/auth/send-otp/'
    headers = {
        'User-Agent': 'Python-Bot/1.0 crawler spider',
        'Content-Type': 'application/json'
    }
    data = {
        'phone_number': '09987654321',
        'behavior': {
            'fill_time': 0.1,  # خیلی سریع
            'typing_speed': 50.0,  # غیرطبیعی
            'mouse_movements': 0,  # بدون حرکت
            'time_on_page': 0.5,  # خیلی کم
        }
    }

    response = requests.post(url, json=data, headers=headers)

    if response.status_code == 403:
        result = response.json()
        print(f"✅ ربات تشخیص داده شد: {result.get('message')}")
        return True
    else:
        print(f"❌ ربات تشخیص داده نشد: {response.status_code}")
        return False


def main():
    print("🚀 تست سیستم OTP و ضد ربات")
    print("=" * 40)

    # بررسی در دسترس بودن سرور
    try:
        response = requests.get(f'{BASE_URL}/', timeout=5)
        print("✅ سرور Django در دسترس است\n")
    except:
        print("❌ سرور Django در دسترس نیست!")
        print("لطفاً سرور را اجرا کنید: python manage.py runserver")
        return

    # تست‌ها
    tests = [
        ("ارسال OTP معمولی", test_send_otp),
        ("تشخیص ربات", test_bot_detection),
    ]

    results = []
    for test_name, test_func in tests:
        print(f"\n📋 {test_name}...")
        try:
            success = test_func()
            results.append((test_name, success))
            print(f"{'✅' if success else '❌'} {test_name}")
        except Exception as e:
            print(f"❌ خطا در {test_name}: {e}")
            results.append((test_name, False))

        print("-" * 30)

    # نتیجه نهایی
    passed = sum(1 for _, success in results if success)
    total = len(results)

    print(f"\n🎯 نتیجه نهایی: {passed}/{total} تست موفق")

    if passed == total:
        print("🎉 همه تست‌ها موفق!")
    elif passed > 0:
        print("⚠️ برخی تست‌ها موفق")
    else:
        print("🚨 همه تست‌ها ناموفق")


if __name__ == '__main__':
    main()
