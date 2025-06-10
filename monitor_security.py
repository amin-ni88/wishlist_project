#!/usr/bin/env python3
"""
ابزار نظارت امنیتی سیستم ضد ربات

استفاده:
python monitor_security.py
"""

from core.models import (
    DeviceFingerprint, IPReputationLog,
    BehaviorAnalysis, CaptchaChallenge,
    OTPVerification, PhoneVerificationLog
)
from django.db.models import Count, Avg, Q
import os
import sys
import django
from datetime import datetime, timedelta
from django.utils import timezone

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'wishlist_project.settings')
django.setup()


class SecurityMonitor:
    """کلاس نظارت امنیتی"""

    def __init__(self):
        self.today = timezone.now().date()
        self.week_ago = self.today - timedelta(days=7)
        self.month_ago = self.today - timedelta(days=30)

    def get_dashboard_stats(self):
        """آمار داشبورد کلی"""
        print("🛡️ داشبورد امنیتی سیستم ضد ربات")
        print("=" * 50)

        # آمار کلی
        total_devices = DeviceFingerprint.objects.count()
        suspicious_devices = DeviceFingerprint.objects.filter(
            is_suspicious=True).count()

        total_ips = IPReputationLog.objects.count()
        blocked_ips = IPReputationLog.objects.filter(is_blocked=True).count()

        print(f"📱 دستگاه‌ها:")
        print(f"   - کل: {total_devices}")
        print(f"   - مشکوک: {suspicious_devices}")
        print(
            f"   - نرخ مشکوک: {(suspicious_devices/total_devices*100):.1f}%" if total_devices > 0 else "   - نرخ مشکوک: 0%")

        print(f"\n🌐 IP ها:")
        print(f"   - کل: {total_ips}")
        print(f"   - مسدود: {blocked_ips}")
        print(
            f"   - نرخ مسدود: {(blocked_ips/total_ips*100):.1f}%" if total_ips > 0 else "   - نرخ مسدود: 0%")

        return {
            'devices': {'total': total_devices, 'suspicious': suspicious_devices},
            'ips': {'total': total_ips, 'blocked': blocked_ips}
        }

    def get_recent_activity(self):
        """فعالیت‌های اخیر"""
        print(f"\n📊 فعالیت 7 روز اخیر:")

        # تحلیل رفتار
        behaviors = BehaviorAnalysis.objects.filter(
            created_at__date__gte=self.week_ago
        ).aggregate(
            total=Count('id'),
            bot_like=Count('id', filter=Q(is_human_like=False)),
            avg_bot_prob=Avg('bot_probability')
        )

        print(f"🧠 تحلیل رفتار:")
        print(f"   - کل تحلیل: {behaviors['total']}")
        print(f"   - رفتار ربات: {behaviors['bot_like']}")
        if behaviors['avg_bot_prob']:
            print(f"   - میانگین احتمال ربات: {behaviors['avg_bot_prob']:.2f}")

        # Captcha
        captchas = CaptchaChallenge.objects.filter(
            created_at__date__gte=self.week_ago
        ).aggregate(
            total=Count('id'),
            solved=Count('id', filter=Q(is_solved=True)),
            failed=Count('id', filter=Q(
                attempts_count__gte=3, is_solved=False))
        )

        print(f"\n🔐 Captcha:")
        print(f"   - کل چالش: {captchas['total']}")
        print(f"   - حل شده: {captchas['solved']}")
        print(f"   - شکست خورده: {captchas['failed']}")
        if captchas['total'] > 0:
            success_rate = (captchas['solved'] / captchas['total']) * 100
            print(f"   - نرخ موفقیت: {success_rate:.1f}%")

        # OTP
        otps = OTPVerification.objects.filter(
            created_at__date__gte=self.week_ago
        ).aggregate(
            total=Count('id'),
            used=Count('id', filter=Q(is_verified=True))
        )

        print(f"\n📱 OTP:")
        print(f"   - کل ارسال: {otps['total']}")
        print(f"   - استفاده شده: {otps['used']}")
        if otps['total'] > 0:
            usage_rate = (otps['used'] / otps['total']) * 100
            print(f"   - نرخ استفاده: {usage_rate:.1f}%")

    def get_top_risky_items(self):
        """آیتم‌های پرخطر"""
        print(f"\n⚠️ آیتم‌های پرخطر:")

        # دستگاه‌های پرخطر
        risky_devices = DeviceFingerprint.objects.filter(
            risk_score__gt=70
        ).order_by('-risk_score')[:5]

        if risky_devices:
            print(f"🔴 دستگاه‌های پرخطر:")
            for device in risky_devices:
                print(
                    f"   - {device.fingerprint_hash[:12]}... (امتیاز: {device.risk_score})")

        # IP های پرخطر
        risky_ips = IPReputationLog.objects.filter(
            risk_score__gt=70
        ).order_by('-risk_score')[:5]

        if risky_ips:
            print(f"\n🔴 IP های پرخطر:")
            for ip in risky_ips:
                status = "مسدود" if ip.is_blocked else "فعال"
                print(
                    f"   - {ip.ip_address} (امتیاز: {ip.risk_score}, وضعیت: {status})")

    def get_security_trends(self):
        """روند امنیتی"""
        print(f"\n📈 روند امنیتی:")

        # روند هفتگی
        week_stats = []
        for i in range(7):
            date = self.today - timedelta(days=i)

            daily_attempts = OTPVerification.objects.filter(
                created_at__date=date
            ).count()

            daily_blocks = IPReputationLog.objects.filter(
                last_activity__date=date,
                is_blocked=True
            ).count()

            week_stats.append({
                'date': date,
                'attempts': daily_attempts,
                'blocks': daily_blocks
            })

        print("روز‌های اخیر (تاریخ | تلاش‌ها | مسدودی‌ها):")
        for stat in reversed(week_stats):
            print(
                f"   {stat['date']} | {stat['attempts']:3d} | {stat['blocks']:3d}")

    def check_security_alerts(self):
        """بررسی هشدارهای امنیتی"""
        print(f"\n🚨 هشدارهای امنیتی:")

        alerts = []

        # تعداد زیاد ربات در روز اخیر
        recent_bots = BehaviorAnalysis.objects.filter(
            created_at__date=self.today,
            is_human_like=False
        ).count()

        if recent_bots > 10:
            alerts.append(f"تعداد بالای ربات امروز: {recent_bots}")

        # IP های با تلاش زیاد
        high_attempt_ips = IPReputationLog.objects.filter(
            registration_attempts__gt=20
        ).count()

        if high_attempt_ips > 5:
            alerts.append(f"IP های با تلاش زیاد: {high_attempt_ips}")

        # Captcha های شکست خورده زیاد
        failed_captchas = CaptchaChallenge.objects.filter(
            created_at__date=self.today,
            attempts_count__gte=3,
            is_solved=False
        ).count()

        if failed_captchas > 20:
            alerts.append(f"Captcha های شکست خورده زیاد: {failed_captchas}")

        # نمایش هشدارها
        if alerts:
            for alert in alerts:
                print(f"   🚨 {alert}")
        else:
            print("   ✅ هیچ هشدار فوری‌ای وجود ندارد")

    def generate_report(self):
        """تولید گزارش کامل"""
        print(
            f"\n📄 گزارش امنیتی - {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        print("=" * 60)

        self.get_dashboard_stats()
        self.get_recent_activity()
        self.get_top_risky_items()
        self.get_security_trends()
        self.check_security_alerts()

        print(f"\n✅ گزارش تکمیل شد")

    def live_monitor(self):
        """نظارت زنده (هر 30 ثانیه)"""
        import time

        print("🔴 حالت نظارت زنده (Ctrl+C برای خروج)")
        print("=" * 50)

        try:
            while True:
                os.system('clear' if os.name == 'posix' else 'cls')

                print(
                    f"🕐 آخرین بروزرسانی: {datetime.now().strftime('%H:%M:%S')}")

                # آمار فوری
                recent_attempts = OTPVerification.objects.filter(
                    created_at__gte=timezone.now() - timedelta(minutes=5)
                ).count()

                recent_blocks = IPReputationLog.objects.filter(
                    last_activity__gte=timezone.now() - timedelta(minutes=5),
                    is_blocked=True
                ).count()

                active_captchas = CaptchaChallenge.objects.filter(
                    created_at__gte=timezone.now() - timedelta(minutes=10),
                    is_solved=False
                ).count()

                print(f"📊 آمار 5 دقیقه اخیر:")
                print(f"   - تلاش‌های OTP: {recent_attempts}")
                print(f"   - IP های مسدود شده: {recent_blocks}")
                print(f"   - Captcha های فعال: {active_captchas}")

                # وضعیت کلی
                self.get_dashboard_stats()

                print(f"\n⏳ بروزرسانی بعدی در 30 ثانیه...")
                time.sleep(30)

        except KeyboardInterrupt:
            print(f"\n👋 نظارت متوقف شد")


def main():
    monitor = SecurityMonitor()

    if len(sys.argv) > 1:
        command = sys.argv[1]

        if command == 'live':
            monitor.live_monitor()
        elif command == 'report':
            monitor.generate_report()
        elif command == 'alerts':
            monitor.check_security_alerts()
        else:
            print("دستورات موجود:")
            print("  python monitor_security.py report  # گزارش کامل")
            print("  python monitor_security.py live    # نظارت زنده")
            print("  python monitor_security.py alerts  # هشدارها")
    else:
        # گزارش پیش‌فرض
        monitor.generate_report()


if __name__ == '__main__':
    main()
