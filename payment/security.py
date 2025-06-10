import hashlib
import hmac
import time

from decimal import Decimal
from django.conf import settings
from django.core.cache import cache
from django.contrib.auth import get_user_model
from django.utils import timezone
import logging

User = get_user_model()
logger = logging.getLogger(__name__)


class PaymentSecurity:
    """کلاس امنیت پرداخت‌ها"""

    # محدودیت‌های امنیتی
    MAX_DAILY_AMOUNT = Decimal('10000000')  # 1 میلیون تومان در روز
    MAX_SINGLE_AMOUNT = Decimal('5000000')  # 500 هزار تومان در تراکنش
    MAX_DAILY_TRANSACTIONS = 20
    FRAUD_DETECTION_THRESHOLD = 5  # تعداد تراکنش مشکوک

    @staticmethod
    def generate_secure_token(user_id, amount, timestamp=None):
        """تولید توکن امنیتی برای تراکنش"""
        if timestamp is None:
            timestamp = int(time.time())

        data = f"{user_id}:{amount}:{timestamp}:{settings.SECRET_KEY}"
        return hmac.new(
            settings.SECRET_KEY.encode('utf-8'),
            data.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()

    @staticmethod
    def verify_token(user_id, amount, token, timestamp, max_age=300):
        """تایید توکن امنیتی (حداکثر 5 دقیقه اعتبار)"""
        current_time = int(time.time())
        if current_time - timestamp > max_age:
            return False

        expected_token = PaymentSecurity.generate_secure_token(
            user_id, amount, timestamp
        )
        return hmac.compare_digest(token, expected_token)

    @staticmethod
    def check_daily_limits(user):
        """بررسی محدودیت‌های روزانه"""
        from .models import Transaction

        today = timezone.now().date()
        daily_transactions = Transaction.objects.filter(
            user=user,
            created_at__date=today,
            status='COMPLETED'
        )

        # بررسی تعداد تراکنش‌ها
        max_transactions = PaymentSecurity.MAX_DAILY_TRANSACTIONS
        if daily_transactions.count() >= max_transactions:
            return False, "تعداد تراکنش‌های روزانه به حد مجاز رسیده"

        # بررسی مبلغ کل روزانه
        daily_amount = sum(t.amount for t in daily_transactions)
        max_daily_amount = PaymentSecurity.MAX_DAILY_AMOUNT
        if daily_amount >= max_daily_amount:
            return False, "مبلغ تراکنش‌های روزانه به حد مجاز رسیده"

        return True, "مجاز"

    @staticmethod
    def check_single_transaction(amount):
        """بررسی محدودیت تراکنش واحد"""
        if amount > PaymentSecurity.MAX_SINGLE_AMOUNT:
            return False, f"حداکثر مبلغ مجاز {PaymentSecurity.MAX_SINGLE_AMOUNT} ریال است"
        return True, "مجاز"

    @staticmethod
    def detect_fraud(user, amount, description):
        """تشخیص تراکنش مشکوک"""
        risk_score = 0
        flags = []

        # بررسی تراکنش‌های اخیر
        cache_key = f"recent_transactions_{user.id}"
        recent_transactions = cache.get(cache_key, [])

        # تراکنش‌های مکرر در زمان کوتاه
        current_time = time.time()
        recent_count = sum(1 for t in recent_transactions
                           if current_time - t['time'] < 300)  # 5 دقیقه

        if recent_count >= 3:
            risk_score += 30
            flags.append("تراکنش‌های مکرر در زمان کوتاه")

        # مبلغ غیرعادی
        if amount > PaymentSecurity.MAX_SINGLE_AMOUNT * 0.8:
            risk_score += 20
            flags.append("مبلغ بالا")

        # الگوی مشکوک در توضیحات
        suspicious_patterns = ['test', 'hack', 'چک', 'تست']
        if any(pattern in description.lower() for pattern in suspicious_patterns):
            risk_score += 25
            flags.append("توضیحات مشکوک")

        # ذخیره تراکنش جدید
        recent_transactions.append({
            'time': current_time,
            'amount': float(amount),
            'description': description
        })

        # نگهداری حداکثر 10 تراکنش اخیر
        recent_transactions = recent_transactions[-10:]
        cache.set(cache_key, recent_transactions, 3600)  # 1 ساعت

        # لاگ کردن تراکنش‌های مشکوک
        if risk_score >= 50:
            logger.warning(f"Suspicious transaction detected: User {user.id}, "
                           f"Amount {amount}, Risk Score {risk_score}, Flags: {flags}")

        return risk_score, flags

    @staticmethod
    def encrypt_sensitive_data(data):
        """رمزنگاری داده‌های حساس"""
        import base64
        from cryptography.fernet import Fernet

        # در production باید کلید را از environment variable بخوانید
        key = base64.urlsafe_b64encode(settings.SECRET_KEY[:32].encode())
        cipher_suite = Fernet(key)

        encrypted_data = cipher_suite.encrypt(data.encode('utf-8'))
        return base64.urlsafe_b64encode(encrypted_data).decode('utf-8')

    @staticmethod
    def decrypt_sensitive_data(encrypted_data):
        """رمزگشایی داده‌های حساس"""
        import base64
        from cryptography.fernet import Fernet

        key = base64.urlsafe_b64encode(settings.SECRET_KEY[:32].encode())
        cipher_suite = Fernet(key)

        try:
            decoded_data = base64.urlsafe_b64decode(
                encrypted_data.encode('utf-8'))
            decrypted_data = cipher_suite.decrypt(decoded_data)
            return decrypted_data.decode('utf-8')
        except Exception:
            return None

    @staticmethod
    def validate_payment_integrity(payment_data):
        """اعتبارسنجی یکپارچگی داده‌های پرداخت"""
        required_fields = ['amount', 'description', 'type']

        for field in required_fields:
            if field not in payment_data or not payment_data[field]:
                return False, f"فیلد {field} الزامی است"

        # بررسی نوع داده‌ها
        try:
            amount = Decimal(str(payment_data['amount']))
            if amount <= 0:
                return False, "مبلغ باید مثبت باشد"
        except (ValueError, TypeError):
            return False, "مبلغ نامعتبر"

        # بررسی طول توضیحات
        if len(payment_data['description']) > 500:
            return False, "توضیحات خیلی طولانی است"

        return True, "معتبر"

    @staticmethod
    def log_security_event(user, event_type, details, risk_level='INFO'):
        """ثبت رویدادهای امنیتی"""
        logger.log(
            getattr(logging, risk_level),
            f"Security Event - User: {user.id}, Type: {event_type}, "
            f"Details: {details}, Time: {timezone.now()}"
        )

        # در صورت نیاز، ارسال هشدار به ادمین‌ها
        if risk_level in ['WARNING', 'ERROR', 'CRITICAL']:
            # اینجا می‌توانید سیستم هشدار پیاده‌سازی کنید
            pass


class PaymentRateLimit:
    """محدودسازی نرخ درخواست‌های پرداخت"""

    @staticmethod
    def is_rate_limited(user_id, action='payment_request'):
        """بررسی محدودیت نرخ درخواست"""
        cache_key = f"rate_limit_{action}_{user_id}"

        # محدودیت‌های مختلف برای اقدامات مختلف
        limits = {
            # 10 درخواست در ساعت
            'payment_request': {'count': 10, 'window': 3600},
            # 20 تایید در ساعت
            'payment_verify': {'count': 20, 'window': 3600},
            'wallet_charge': {'count': 5, 'window': 3600},     # 5 شارژ در ساعت
        }

        limit_config = limits.get(action, {'count': 10, 'window': 3600})

        current_count = cache.get(cache_key, 0)
        if current_count >= limit_config['count']:
            return True, f"محدودیت نرخ: حداکثر {limit_config['count']} درخواست در {limit_config['window']} ثانیه"

        # افزایش شمارنده
        cache.set(cache_key, current_count + 1, limit_config['window'])
        return False, "مجاز"


class TransactionVerification:
    """تایید و اعتبارسنجی تراکنش‌ها"""

    @staticmethod
    def verify_zarinpal_callback(authority, status, merchant_id):
        """تایید callback از زرین‌پال"""
        if status != 'OK':
            return False, "پرداخت توسط کاربر لغو شده"

        if not authority or len(authority) < 30:
            return False, "Authority نامعتبر"

        # بررسی تکراری نبودن Authority
        from .models import Payment
        if Payment.objects.filter(authority=authority, status='COMPLETED').exists():
            return False, "این Authority قبلاً استفاده شده"

        return True, "معتبر"

    @staticmethod
    def create_verification_hash(payment_id, amount, authority):
        """ایجاد hash تایید برای تراکنش"""
        data = f"{payment_id}:{amount}:{authority}:{settings.SECRET_KEY}"
        return hashlib.sha256(data.encode('utf-8')).hexdigest()

    @staticmethod
    def verify_payment_signature(payment_data, signature):
        """تایید امضای پرداخت"""
        expected_signature = PaymentSecurity.generate_secure_token(
            payment_data['user_id'],
            payment_data['amount'],
            payment_data['timestamp']
        )
        return hmac.compare_digest(signature, expected_signature)
