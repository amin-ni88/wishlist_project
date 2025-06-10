import requests
import logging
from django.conf import settings
from django.utils import timezone
from .models import OTPVerification, PhoneVerificationLog

logger = logging.getLogger(__name__)


class PhoneValidationService:
    """سرویس اعتبارسنجی شماره موبایل"""

    @staticmethod
    def is_valid_iranian_phone(phone_number):
        """بررسی معتبر بودن شماره موبایل ایرانی"""
        import re

        if not phone_number:
            return False

        # حذف فاصله‌ها و کاراکترهای اضافی
        phone = re.sub(r'[\s\-\(\)]', '', phone_number)

        # الگوهای معتبر شماره موبایل ایرانی
        patterns = [
            r'^09\d{9}$',  # 09xxxxxxxxx
            r'^\+989\d{9}$',  # +989xxxxxxxxx
            r'^00989\d{9}$',  # 00989xxxxxxxxx
            r'^989\d{9}$',  # 989xxxxxxxxx
        ]

        for pattern in patterns:
            if re.match(pattern, phone):
                return True

        return False

    @staticmethod
    def format_phone_number(phone_number):
        """فرمت کردن شماره موبایل به فرمت استاندارد"""
        import re

        if not phone_number:
            return None

        # حذف فاصله‌ها و کاراکترهای اضافی
        phone = re.sub(r'[\s\-\(\)]', '', phone_number)

        # تبدیل به فرمت 09xxxxxxxxx
        if re.match(r'^09\d{9}$', phone):
            return phone
        elif re.match(r'^\+989\d{9}$', phone):
            return '0' + phone[3:]
        elif re.match(r'^00989\d{9}$', phone):
            return '0' + phone[4:]
        elif re.match(r'^989\d{9}$', phone):
            return '0' + phone[2:]

        return None


class SMSService:
    """سرویس ارسال پیامک"""

    @staticmethod
    def send_otp(phone_number, otp_code, otp_type='REGISTRATION'):
        """ارسال کد OTP به شماره موبایل"""
        try:
            # در محیط تست، فقط در لاگ ثبت می‌کنیم
            if settings.DEBUG:
                logger.info(f"SMS OTP: {phone_number} -> {otp_code}")
                print(f"📱 SMS sent to {phone_number}: Your OTP is {otp_code}")
                return True, "OTP sent successfully (DEBUG mode)"

            # در محیط واقعی، از API پیامک استفاده کنید
            # مثال برای Kavenegar:
            api_key = getattr(settings, 'KAVENEGAR_API_KEY', None)
            if not api_key:
                logger.warning("KAVENEGAR_API_KEY not configured")
                return False, "SMS service not configured"

            # پیام OTP
            message_template = {
                'REGISTRATION': f'کد تایید ثبت‌نام شما: {otp_code}',
                'LOGIN': f'کد ورود شما: {otp_code}',
                'PASSWORD_RESET': f'کد بازیابی رمز عبور: {otp_code}',
                'PHONE_VERIFICATION': f'کد تایید شماره موبایل: {otp_code}',
            }

            message = message_template.get(
                otp_type, f'کد تایید شما: {otp_code}')

            # ارسال پیامک (مثال Kavenegar)
            url = "https://api.kavenegar.com/v1/{}/sms/send.json".format(
                api_key)
            data = {
                'receptor': phone_number,
                'message': message,
                'sender': '1000596446'  # شماره ارسال‌کننده
            }

            response = requests.post(url, data=data, timeout=10)

            if response.status_code == 200:
                result = response.json()
                if result.get('return', {}).get('status') == 200:
                    logger.info(f"SMS sent successfully to {phone_number}")
                    return True, "SMS sent successfully"
                else:
                    error = result.get('return', {}).get(
                        'message', 'Unknown error')
                    logger.error(f"SMS API error: {error}")
                    return False, f"SMS API error: {error}"
            else:
                logger.error(f"SMS API HTTP error: {response.status_code}")
                return False, f"SMS service error: {response.status_code}"

        except requests.RequestException as e:
            logger.error(f"SMS sending failed: {str(e)}")
            return False, f"SMS sending failed: {str(e)}"
        except Exception as e:
            logger.error(f"Unexpected SMS error: {str(e)}")
            return False, f"Unexpected error: {str(e)}"


class OTPService:
    """سرویس مدیریت OTP"""

    @staticmethod
    def send_otp(phone_number, request):
        """ارسال OTP جدید"""
        try:
            # فرمت کردن شماره موبایل
            formatted_phone = PhoneValidationService.format_phone_number(
                phone_number)
            if not formatted_phone:
                return False, 'شماره موبایل معتبر نیست'

            # دریافت IP و User Agent
            ip_address = AntiBotService.get_client_ip(request)
            user_agent = request.META.get('HTTP_USER_AGENT', '')

            # بررسی محدودیت تعداد درخواست (Rate limiting)
            recent_attempts = PhoneVerificationLog.objects.filter(
                phone_number=formatted_phone,
                attempt_type='OTP_SEND',
                created_at__gte=timezone.now() - timezone.timedelta(minutes=1)
            ).count()

            if recent_attempts >= 3:
                return False, 'تعداد درخواست‌های شما زیاد است. لطفاً یک دقیقه صبر کنید'

            # تولید OTP جدید
            otp = OTPVerification.generate_otp(
                phone_number=formatted_phone,
                otp_type='REGISTRATION',
                ip_address=ip_address,
                user_agent=user_agent
            )

            # ارسال پیامک
            success, message = SMSService.send_otp(
                formatted_phone, otp.otp_code, 'REGISTRATION')

            # ثبت لاگ
            PhoneVerificationLog.objects.create(
                phone_number=formatted_phone,
                ip_address=ip_address or '0.0.0.0',
                user_agent=user_agent,
                success=success,
                attempt_type='OTP_SEND'
            )

            if success:
                return True, f'کد تایید به شماره {formatted_phone} ارسال شد'
            else:
                return False, f'خطا در ارسال پیامک: {message}'

        except Exception as e:
            logger.error(f"OTP send error: {str(e)}")
            return False, f'خطای سیستم: {str(e)}'

    @staticmethod
    def verify_otp(phone_number, otp_code, request):
        """تایید OTP"""
        try:
            # فرمت کردن شماره موبایل
            formatted_phone = PhoneValidationService.format_phone_number(
                phone_number)
            if not formatted_phone:
                return False, 'شماره موبایل معتبر نیست'

            # دریافت IP و User Agent
            ip_address = AntiBotService.get_client_ip(request)
            user_agent = request.META.get('HTTP_USER_AGENT', '')

            # یافتن آخرین OTP معتبر
            otp = OTPVerification.objects.filter(
                phone_number=formatted_phone,
                otp_type='REGISTRATION',
                is_verified=False
            ).order_by('-created_at').first()

            if not otp:
                PhoneVerificationLog.objects.create(
                    phone_number=formatted_phone,
                    ip_address=ip_address or '0.0.0.0',
                    user_agent=user_agent,
                    success=False,
                    attempt_type='OTP_VERIFY'
                )
                return False, 'کد OTP یافت نشد یا منقضی شده است'

            # تایید کد
            success, message = otp.verify(otp_code)

            # ثبت لاگ
            PhoneVerificationLog.objects.create(
                phone_number=formatted_phone,
                ip_address=ip_address or '0.0.0.0',
                user_agent=user_agent,
                success=success,
                attempt_type='OTP_VERIFY'
            )

            return success, message

        except Exception as e:
            logger.error(f"OTP verify error: {str(e)}")
            return False, f'خطای سیستم: {str(e)}'

    @staticmethod
    def format_phone_number(phone_number):
        """فرمت کردن شماره موبایل"""
        # حذف کاراکترهای غیر عددی
        phone = ''.join(filter(str.isdigit, phone_number))

        # اگر با 0 شروع شده، آن را حذف کن
        if phone.startswith('0'):
            phone = phone[1:]

        # اگر با 98 شروع شده، آن را حذف کن
        if phone.startswith('98'):
            phone = phone[2:]

        # بررسی اینکه شماره موبایل ایرانی است
        if len(phone) == 10 and phone.startswith('9'):
            return f"+98{phone}"

        return None

    @staticmethod
    def is_valid_phone_number(phone_number):
        """بررسی معتبر بودن شماره موبایل"""
        formatted = OTPService.format_phone_number(phone_number)
        return formatted is not None


class AntiBotService:
    """سرویس جامع ضد ربات"""

    @staticmethod
    def get_client_ip(request):
        """دریافت IP واقعی کلاینت"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip

    @staticmethod
    def get_session_id(request):
        """دریافت یا ایجاد session ID"""
        if not request.session.session_key:
            request.session.create()
        return request.session.session_key

    @staticmethod
    def generate_device_fingerprint(request):
        """تولید ردپای دستگاه"""
        import hashlib

        # جمع‌آوری اطلاعات دستگاه
        user_agent = request.META.get('HTTP_USER_AGENT', '')
        accept_language = request.META.get('HTTP_ACCEPT_LANGUAGE', '')
        accept_encoding = request.META.get('HTTP_ACCEPT_ENCODING', '')

        # تولید هش منحصر به فرد
        fingerprint_data = f"{user_agent}|{accept_language}|{accept_encoding}"
        fingerprint_hash = hashlib.sha256(
            fingerprint_data.encode('utf-8')
        ).hexdigest()

        return fingerprint_hash, {
            'user_agent': user_agent,
            'language': accept_language[:10] if accept_language else '',
            'platform': request.META.get('HTTP_SEC_CH_UA_PLATFORM', ''),
        }

    @classmethod
    def track_device_fingerprint(cls, request, registration_attempt=True):
        """ردگیری و ثبت ردپای دستگاه"""
        from .models import DeviceFingerprint

        fingerprint_hash, device_info = cls.generate_device_fingerprint(
            request)

        fingerprint, created = DeviceFingerprint.objects.get_or_create(
            fingerprint_hash=fingerprint_hash,
            defaults={
                'user_agent': device_info['user_agent'],
                'language': device_info['language'],
                'platform': device_info['platform'],
            }
        )

        if registration_attempt:
            fingerprint.registration_attempts += 1

        fingerprint.update_risk_score()
        fingerprint.save()

        return fingerprint

    @classmethod
    def check_ip_reputation(cls, request):
        """بررسی اعتبار IP"""
        from .models import IPReputationLog

        ip_address = cls.get_client_ip(request)
        ip_log, created = IPReputationLog.objects.get_or_create(
            ip_address=ip_address,
            defaults={'registration_attempts': 0}
        )

        # بررسی مسدودیت
        if ip_log.is_currently_blocked():
            return False, f'IP مسدود شده تا {ip_log.blocked_until}'

        # افزایش شمارنده تلاش
        ip_log.registration_attempts += 1
        ip_log.update_risk_score()
        ip_log.save()

        # بررسی امتیاز ریسک
        if ip_log.risk_score > 60:
            return False, 'IP مشکوک - لطفاً بعداً تلاش کنید'

        return True, 'IP معتبر است'

    @classmethod
    def analyze_user_behavior(cls, request, form_data=None):
        """تحلیل رفتار کاربر"""
        from .models import BehaviorAnalysis, DeviceFingerprint

        session_id = cls.get_session_id(request)
        ip_address = cls.get_client_ip(request)

        # دریافت ردپای دستگاه
        fingerprint_hash, _ = cls.generate_device_fingerprint(request)
        try:
            device_fingerprint = DeviceFingerprint.objects.get(
                fingerprint_hash=fingerprint_hash
            )
        except DeviceFingerprint.DoesNotExist:
            device_fingerprint = None

        # تحلیل رفتار از داده‌های فرم
        behavior_data = {
            'session_id': session_id,
            'ip_address': ip_address,
            'device_fingerprint': device_fingerprint,
        }

        if form_data:
            behavior_data.update({
                'form_fill_time': form_data.get('fill_time', 0),
                'typing_speed': form_data.get('typing_speed', 0),
                'mouse_movements': form_data.get('mouse_movements', 0),
                'clicks_count': form_data.get('clicks', 0),
                'key_presses': form_data.get('key_presses', 0),
                'copy_paste_detected': form_data.get('copy_paste', False),
                'time_on_page': form_data.get('time_on_page', 0),
            })

        behavior = BehaviorAnalysis.objects.create(**behavior_data)
        is_human = behavior.analyze_behavior()

        return is_human, behavior.bot_probability

    @classmethod
    def generate_captcha_challenge(cls, request, challenge_type='MATH'):
        """تولید چالش Captcha"""
        from .models import CaptchaChallenge

        session_id = cls.get_session_id(request)
        ip_address = cls.get_client_ip(request)

        if challenge_type == 'MATH':
            return CaptchaChallenge.generate_math_challenge(session_id, ip_address)

        # سایر انواع چالش در آینده...
        raise ValueError(f"نوع چالش {challenge_type} پشتیبانی نمی‌شود")

    @classmethod
    def verify_captcha(cls, request, captcha_id, user_answer):
        """تایید پاسخ Captcha"""
        from .models import CaptchaChallenge, IPReputationLog

        try:
            captcha = CaptchaChallenge.objects.get(
                id=captcha_id,
                session_id=cls.get_session_id(request)
            )

            success, message = captcha.verify_answer(user_answer)

            # ثبت نتیجه در IP log
            ip_address = cls.get_client_ip(request)
            ip_log, _ = IPReputationLog.objects.get_or_create(
                ip_address=ip_address
            )

            if not success:
                ip_log.captcha_failures += 1
                ip_log.update_risk_score()
                ip_log.save()

            return success, message

        except CaptchaChallenge.DoesNotExist:
            return False, 'چالش یافت نشد'

    @classmethod
    def comprehensive_bot_check(cls, request, form_data=None):
        """بررسی جامع ضد ربات"""
        results = {
            'is_bot': False,
            'risk_score': 0,
            'blocked_reasons': [],
            'require_captcha': False,
        }

        # 1. بررسی IP
        ip_valid, ip_message = cls.check_ip_reputation(request)
        if not ip_valid:
            results['is_bot'] = True
            results['blocked_reasons'].append(ip_message)
            results['risk_score'] += 40

        # 2. بررسی ردپای دستگاه
        fingerprint = cls.track_device_fingerprint(request)
        if fingerprint.is_suspicious:
            results['risk_score'] += 30
            results['blocked_reasons'].append('دستگاه مشکوک')

        # 3. تحلیل رفتار
        if form_data:
            is_human, bot_probability = cls.analyze_user_behavior(
                request, form_data)
            if not is_human:
                results['risk_score'] += int(bot_probability * 50)
                results['blocked_reasons'].append('رفتار غیرانسانی')

        # 4. بررسی User Agent
        user_agent = request.META.get('HTTP_USER_AGENT', '').lower()
        bot_indicators = ['bot', 'crawler', 'spider', 'scraper', 'automated']
        if any(indicator in user_agent for indicator in bot_indicators):
            results['risk_score'] += 35
            results['blocked_reasons'].append('User Agent مشکوک')

        # 5. تصمیم‌گیری نهایی
        if results['risk_score'] > 80:
            results['is_bot'] = True
        elif results['risk_score'] > 50:
            results['require_captcha'] = True

        return results

    @classmethod
    def honeypot_check(cls, request_data):
        """بررسی فیلدهای تله (Honeypot)"""
        honeypot_fields = [
            'website',  # فیلد مخفی که انسان‌ها نمی‌بینند
            'url',
            'homepage',
            'company',  # فیلدهایی که ربات‌ها معمولاً پر می‌کنند
        ]

        for field in honeypot_fields:
            if request_data.get(field):
                return True  # احتمالاً ربات است

        return False

    @classmethod
    def rate_limit_check(cls, request, max_attempts=3, window_minutes=60):
        """بررسی محدودیت نرخ درخواست"""
        from django.core.cache import cache

        ip_address = cls.get_client_ip(request)
        cache_key = f"registration_attempts:{ip_address}"

        attempts = cache.get(cache_key, 0)
        if attempts >= max_attempts:
            return False, f'حداکثر {max_attempts} تلاش در {window_minutes} دقیقه'

        # افزایش شمارنده
        cache.set(cache_key, attempts + 1, window_minutes * 60)
        return True, f'{max_attempts - attempts - 1} تلاش باقی مانده'


class SecurityEventLogger:
    """ثبت رویدادهای امنیتی"""

    @staticmethod
    def log_security_event(request, event_type, description, severity='INFO'):
        """ثبت رویداد امنیتی"""
        import logging

        security_logger = logging.getLogger('security')

        ip_address = AntiBotService.get_client_ip(request)
        user_agent = request.META.get('HTTP_USER_AGENT', '')

        log_data = {
            'event_type': event_type,
            'ip_address': ip_address,
            'user_agent': user_agent,
            'description': description,
            'severity': severity,
            'timestamp': timezone.now().isoformat(),
        }

        if severity == 'CRITICAL':
            security_logger.critical(f"SECURITY EVENT: {log_data}")
        elif severity == 'WARNING':
            security_logger.warning(f"SECURITY EVENT: {log_data}")
        else:
            security_logger.info(f"SECURITY EVENT: {log_data}")

    @classmethod
    def log_bot_detection(cls, request, bot_score, reasons):
        """ثبت تشخیص ربات"""
        cls.log_security_event(
            request,
            'BOT_DETECTED',
            f'احتمال ربات: {bot_score}% - دلایل: {", ".join(reasons)}',
            'WARNING'
        )

    @classmethod
    def log_ip_block(cls, request, reason):
        """ثبت مسدود شدن IP"""
        cls.log_security_event(
            request,
            'IP_BLOCKED',
            f'IP مسدود شد - دلیل: {reason}',
            'CRITICAL'
        )

    @classmethod
    def log_captcha_failure(cls, request, attempts):
        """ثبت شکست در Captcha"""
        cls.log_security_event(
            request,
            'CAPTCHA_FAILED',
            f'شکست در حل Captcha - تلاش {attempts}ام',
            'WARNING'
        )


class EmailValidationService:
    """سرویس تایید ایمیل"""

    @staticmethod
    def is_valid_email(email):
        """بررسی معتبر بودن ایمیل"""
        import re
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))

    @staticmethod
    def is_disposable_email(email):
        """بررسی ایمیل موقت"""
        disposable_domains = [
            '10minutemail.com', 'tempmail.org', 'guerrillamail.com',
            'mailinator.com', 'temp-mail.org', 'throwaway.email',
            'yopmail.com', 'mohmal.com', 'emailondeck.com',
            'maildrop.cc', 'trashmail.com', 'getairmail.com'
        ]

        if '@' not in email:
            return True

        domain = email.split('@')[1].lower()
        return domain in disposable_domains

    @staticmethod
    def normalize_email(email):
        """نرمال‌سازی ایمیل"""
        if not email:
            return email

        email = email.strip().lower()

        # حذف نقطه‌های اضافی در Gmail
        if '@gmail.com' in email:
            local_part = email.split('@')[0]
            local_part = local_part.replace('.', '')
            email = f"{local_part}@gmail.com"

        return email

    @staticmethod
    def generate_verification_token():
        """تولید توکن تایید ایمیل"""
        import secrets
        import string

        alphabet = string.ascii_letters + string.digits
        return ''.join(secrets.choice(alphabet) for _ in range(64))

    @staticmethod
    def send_verification_email(email, token, verification_type='REGISTER'):
        """ارسال ایمیل تایید"""
        from django.core.mail import send_mail
        from django.conf import settings
        from django.template.loader import render_to_string

        try:
            # تعیین موضوع و قالب بر اساس نوع تایید
            subjects = {
                'REGISTER': 'تایید ثبت‌نام در پلتفرم لیست آرزوها',
                'LOGIN': 'تایید ورود به حساب کاربری',
                'RESET_PASSWORD': 'بازیابی رمز عبور',
                'CHANGE_EMAIL': 'تایید تغییر ایمیل'
            }

            subject = subjects.get(verification_type, 'تایید ایمیل')

            # ساخت لینک تایید
            verification_url = f"{settings.FRONTEND_URL}/verify-email?token={token}"

            # رندر قالب ایمیل
            html_message = render_to_string('emails/email_verification.html', {
                'verification_url': verification_url,
                'verification_type': verification_type,
                'token': token
            })

            plain_message = f"""
            سلام،
            
            برای تایید ایمیل خود روی لینک زیر کلیک کنید:
            {verification_url}
            
            این لینک به مدت 30 دقیقه معتبر است.
            
            با تشکر،
            تیم پلتفرم لیست آرزوها
            """

            send_mail(
                subject=subject,
                message=plain_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[email],
                html_message=html_message,
                fail_silently=False,
            )

            return True, 'ایمیل تایید با موفقیت ارسال شد'

        except Exception as e:
            return False, f'خطا در ارسال ایمیل: {str(e)}'


class EmailService:
    """سرویس مدیریت ایمیل"""

    @staticmethod
    def create_verification(email, verification_type, user=None, ip_address=None, user_agent=''):
        """ایجاد تایید ایمیل جدید"""
        from django.utils import timezone
        from datetime import timedelta
        from .models import EmailVerification

        # حذف تایید‌های قبلی معتبر
        EmailVerification.objects.filter(
            email=email,
            verification_type=verification_type,
            is_verified=False
        ).delete()

        # تولید توکن جدید
        token = EmailValidationService.generate_verification_token()

        # ایجاد تایید جدید
        verification = EmailVerification.objects.create(
            email=email,
            verification_type=verification_type,
            token=token,
            user=user,
            ip_address=ip_address,
            user_agent=user_agent,
            expires_at=timezone.now() + timedelta(minutes=30)
        )

        return verification

    @staticmethod
    def send_verification_email(email, verification_type='REGISTER', user=None, ip_address=None, user_agent=''):
        """ارسال ایمیل تایید"""
        from .models import EmailVerificationLog

        try:
            # بررسی معتبر بودن ایمیل
            if not EmailValidationService.is_valid_email(email):
                return False, 'ایمیل معتبر نیست'

            # بررسی ایمیل موقت
            if EmailValidationService.is_disposable_email(email):
                return False, 'استفاده از ایمیل موقت مجاز نیست'

            # نرمال‌سازی ایمیل
            email = EmailValidationService.normalize_email(email)

            # بررسی محدودیت نرخ ارسال
            if not EmailService._check_rate_limit(email, ip_address):
                return False, 'تعداد زیادی درخواست ارسال شده. لطفاً بعداً تلاش کنید'

            # ایجاد تایید جدید
            verification = EmailService.create_verification(
                email, verification_type, user, ip_address, user_agent
            )

            # ارسال ایمیل
            success, message = EmailValidationService.send_verification_email(
                email, verification.token, verification_type
            )

            # ثبت لاگ
            EmailVerificationLog.objects.create(
                email=email,
                attempt_type='SEND',
                ip_address=ip_address,
                user_agent=user_agent,
                success=success,
                error_message='' if success else message
            )

            if success:
                return True, 'ایمیل تایید ارسال شد'
            else:
                return False, message

        except Exception as e:
            # ثبت خطا
            EmailVerificationLog.objects.create(
                email=email,
                attempt_type='SEND',
                ip_address=ip_address,
                user_agent=user_agent,
                success=False,
                error_message=str(e)
            )
            return False, 'خطا در ارسال ایمیل تایید'

    @staticmethod
    def verify_email(token, ip_address=None, user_agent=''):
        """تایید ایمیل با توکن"""
        from .models import EmailVerification, EmailVerificationLog
        from django.contrib.auth import get_user_model

        User = get_user_model()

        try:
            verification = EmailVerification.objects.get(
                token=token,
                is_verified=False
            )

            # بررسی انقضا
            if verification.is_expired:
                EmailVerificationLog.objects.create(
                    email=verification.email,
                    attempt_type='VERIFY',
                    ip_address=ip_address,
                    user_agent=user_agent,
                    success=False,
                    error_message='توکن منقضی شده'
                )
                return False, 'توکن منقضی شده است'

            # بررسی تعداد تلاش
            if not verification.can_attempt:
                EmailVerificationLog.objects.create(
                    email=verification.email,
                    attempt_type='VERIFY',
                    ip_address=ip_address,
                    user_agent=user_agent,
                    success=False,
                    error_message='تعداد تلاش‌های مجاز تمام شده'
                )
                return False, 'تعداد تلاش‌های مجاز تمام شده است'

            # تایید موفق
            verification.mark_as_verified()

            # اگر کاربری وجود داشته باشد، ایمیل را تایید کن
            if verification.user:
                verification.user.email = verification.email
                verification.user.is_verified = True
                verification.user.save(update_fields=['email', 'is_verified'])

            # ثبت لاگ موفقیت
            EmailVerificationLog.objects.create(
                email=verification.email,
                attempt_type='VERIFY',
                ip_address=ip_address,
                user_agent=user_agent,
                success=True
            )

            return True, 'ایمیل با موفقیت تایید شد'

        except EmailVerification.DoesNotExist:
            EmailVerificationLog.objects.create(
                email='',
                attempt_type='VERIFY',
                ip_address=ip_address,
                user_agent=user_agent,
                success=False,
                error_message='توکن نامعتبر'
            )
            return False, 'توکن نامعتبر است'

        except Exception as e:
            EmailVerificationLog.objects.create(
                email='',
                attempt_type='VERIFY',
                ip_address=ip_address,
                user_agent=user_agent,
                success=False,
                error_message=str(e)
            )
            return False, 'خطا در تایید ایمیل'

    @staticmethod
    def _check_rate_limit(email, ip_address):
        """بررسی محدودیت نرخ ارسال"""
        from django.utils import timezone
        from datetime import timedelta
        from .models import EmailVerificationLog

        now = timezone.now()
        one_hour_ago = now - timedelta(hours=1)

        # محدودیت بر اساس ایمیل (5 بار در ساعت)
        email_count = EmailVerificationLog.objects.filter(
            email=email,
            attempt_type='SEND',
            created_at__gte=one_hour_ago
        ).count()

        if email_count >= 5:
            return False

        # محدودیت بر اساس IP (20 بار در ساعت)
        if ip_address:
            ip_count = EmailVerificationLog.objects.filter(
                ip_address=ip_address,
                attempt_type='SEND',
                created_at__gte=one_hour_ago
            ).count()

            if ip_count >= 20:
                return False

        return True
