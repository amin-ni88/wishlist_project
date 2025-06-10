#!/usr/bin/env python3
"""
تست سیستم ضد ربات

استفاده:
python test_antibot_system.py
"""

import os
import sys
import django
import requests
import time
import random
from concurrent.futures import ThreadPoolExecutor

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'wishlist_project.settings')
django.setup()

BASE_URL = 'http://127.0.0.1:8000'


class AntiBotTester:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })

    def test_normal_user_behavior(self):
        """تست رفتار کاربر عادی"""
        print("🧑 تست کاربر عادی...")

        # درخواست OTP
        data = {
            'phone_number': '09123456789',
            'behavior': {
                'fill_time': 15.5,  # زمان طبیعی
                'typing_speed': 3.2,  # سرعت طبیعی
                'mouse_movements': 45,
                'clicks': 8,
                'time_on_page': 30.0
            }
        }

        response = self.session.post(f'{BASE_URL}/auth/send-otp/', json=data)
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.json()}")
        return response.status_code == 200

    def test_bot_behavior(self):
        """تست رفتار ربات"""
        print("🤖 تست رفتار ربات...")

        # رفتار مشکوک
        data = {
            'phone_number': '09987654321',
            'behavior': {
                'fill_time': 0.5,  # خیلی سریع
                'typing_speed': 15.0,  # خیلی سریع
                'mouse_movements': 0,  # بدون حرکت ماوس
                'clicks': 1,
                'time_on_page': 2.0,  # خیلی کم
                'copy_paste': True
            }
        }

        response = self.session.post(f'{BASE_URL}/auth/send-otp/', json=data)
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.json()}")
        return response.status_code == 403  # باید مسدود شود

    def test_suspicious_user_agent(self):
        """تست User Agent مشکوک"""
        print("🕷️ تست User Agent مشکوک...")

        # تغییر User Agent به ربات
        self.session.headers['User-Agent'] = 'Python-requests/2.31.0 bot crawler'

        data = {'phone_number': '09111111111'}
        response = self.session.post(f'{BASE_URL}/auth/send-otp/', json=data)

        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.json()}")

        # بازگردانی User Agent
        self.session.headers['User-Agent'] = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
        return response.status_code == 403

    def test_honeypot_field(self):
        """تست فیلدهای تله"""
        print("🍯 تست Honeypot...")

        data = {
            'phone_number': '09222222222',
            'otp_code': '123456',
            'first_name': 'تست',
            'last_name': 'کاربر',
            'website': 'http://bot-site.com',  # فیلد تله
        }

        response = self.session.post(
            f'{BASE_URL}/auth/register-with-otp/', json=data)
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.json()}")
        return response.status_code == 400

    def test_rate_limiting(self):
        """تست محدودیت نرخ"""
        print("⏱️ تست Rate Limiting...")

        # چندین درخواست سریع
        for i in range(8):
            data = {'phone_number': f'0912345678{i}'}
            response = self.session.post(
                f'{BASE_URL}/auth/send-otp/', json=data)
            print(f"   تلاش {i+1}: {response.status_code}")

            if response.status_code == 429:  # Too Many Requests
                print("   ✅ Rate limiting فعال شد!")
                return True

            time.sleep(0.1)  # تاخیر کوتاه

        return False

    def test_captcha_generation(self):
        """تست تولید Captcha"""
        print("🔐 تست تولید Captcha...")

        response = self.session.post(f'{BASE_URL}/anti-bot/generate-captcha/',
                                     json={'type': 'MATH'})

        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            captcha_data = response.json()
            print(f"   Captcha: {captcha_data['captcha']['question']}")

            # تست تایید Captcha
            return self.test_captcha_verification(captcha_data['captcha'])

        return False

    def test_captcha_verification(self, captcha):
        """تست تایید Captcha"""
        print("✅ تست تایید Captcha...")

        # حل سوال ریاضی
        question = captcha['question'].replace('= ?', '').strip()
        try:
            answer = str(eval(question))

            data = {
                'captcha_id': captcha['id'],
                'answer': answer
            }

            response = self.session.post(
                f'{BASE_URL}/anti-bot/verify-captcha/', json=data)
            print(f"   پاسخ: {answer}")
            print(f"   Status: {response.status_code}")
            print(f"   Response: {response.json()}")

            return response.status_code == 200 and response.json().get('success')
        except:
            print("   خطا در حل سوال")
            return False

    def test_bot_status_check(self):
        """بررسی وضعیت ضد ربات"""
        print("📊 بررسی وضعیت...")

        response = self.session.post(f'{BASE_URL}/anti-bot/check-status/', json={
            'behavior': {
                'fill_time': 10.0,
                'typing_speed': 4.0,
                'mouse_movements': 20,
                'time_on_page': 25.0
            }
        })

        if response.status_code == 200:
            data = response.json()
            print(f"   امتیاز ریسک: {data['bot_check']['risk_score']}")
            print(
                f"   نیاز به Captcha: {data['bot_check']['require_captcha']}")
            print(f"   ردپای دستگاه: {data['device_fingerprint']['hash']}")
            return True

        return False

    def run_all_tests(self):
        """اجرای تمام تست‌ها"""
        print("🚀 شروع تست سیستم ضد ربات")
        print("=" * 50)

        tests = [
            ("رفتار عادی", self.test_normal_user_behavior),
            ("رفتار ربات", self.test_bot_behavior),
            ("User Agent مشکوک", self.test_suspicious_user_agent),
            ("Honeypot", self.test_honeypot_field),
            ("Rate Limiting", self.test_rate_limiting),
            ("تولید Captcha", self.test_captcha_generation),
            ("بررسی وضعیت", self.test_bot_status_check),
        ]

        results = []
        for test_name, test_func in tests:
            try:
                result = test_func()
                results.append((test_name, result))
                print(f"   {'✅' if result else '❌'} {test_name}")
            except Exception as e:
                print(f"   ❌ {test_name} - خطا: {e}")
                results.append((test_name, False))

            print("-" * 30)
            time.sleep(1)  # تاخیر بین تست‌ها

        # نتایج نهایی
        print("\n📋 نتایج نهایی:")
        passed = sum(1 for _, result in results if result)
        total = len(results)

        for test_name, result in results:
            status = "✅ موفق" if result else "❌ ناموفق"
            print(f"   {test_name}: {status}")

        print(f"\n🎯 نتیجه کلی: {passed}/{total} تست موفق")

        if passed == total:
            print("🎉 تمام تست‌ها موفق بودند!")
        elif passed > total // 2:
            print("⚠️ اکثر تست‌ها موفق بودند")
        else:
            print("🚨 اکثر تست‌ها ناموفق بودند - بررسی تنظیمات")


def test_concurrent_requests():
    """تست درخواست‌های همزمان"""
    print("\n🔄 تست درخواست‌های همزمان...")

    def make_request(i):
        tester = AntiBotTester()
        data = {'phone_number': f'0912345{i:04d}'}
        response = tester.session.post(f'{BASE_URL}/auth/send-otp/', json=data)
        return response.status_code

    # 20 درخواست همزمان
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(make_request, i) for i in range(20)]
        results = [future.result() for future in futures]

    success_count = sum(1 for status in results if status == 200)
    blocked_count = sum(1 for status in results if status in [403, 429])

    print(f"   موفق: {success_count}")
    print(f"   مسدود: {blocked_count}")
    print(f"   سایر: {len(results) - success_count - blocked_count}")


if __name__ == '__main__':
    # بررسی اینکه سرور در حال اجرا است
    try:
        response = requests.get(f'{BASE_URL}/', timeout=5)
        print("✅ سرور Django در دسترس است")
    except:
        print("❌ سرور Django در دسترس نیست - لطفاً ابتدا سرور را اجرا کنید:")
        print("python manage.py runserver")
        sys.exit(1)

    # شروع تست‌ها
    tester = AntiBotTester()
    tester.run_all_tests()

    # تست درخواست‌های همزمان
    test_concurrent_requests()

    print("\n🏁 تست‌ها تمام شد!")
