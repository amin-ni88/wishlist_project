from django.conf import settings
from django.core.mail import send_mail
from .permissions import IsWishListOwner, IsContributor, IsPublicOrOwner
from rest_framework import viewsets, permissions, status, filters
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
from django.db.models import Sum, F
from django.utils import timezone
from django.contrib.auth import authenticate
from .services import OTPService, AntiBotService, SecurityEventLogger, EmailService
from .models import (
    User, Wishlist, WishlistItem, Contribution, Notification,
    SubscriptionPlan, UserSubscription, WishlistShare, WishlistInvitation, SocialShare
)
from .serializers import (
    UserSerializer, WishlistSerializer, WishlistItemSerializer,
    ContributionSerializer, NotificationSerializer, SubscriptionPlanSerializer,
    UserSubscriptionSerializer, WishlistShareSerializer, WishlistInvitationSerializer,
    SocialShareSerializer, SendOTPSerializer, RegisterWithOTPSerializer,
    SendEmailVerificationSerializer, RegisterWithEmailSerializer, LoginWithEmailSerializer,
    VerifyEmailSerializer
)
from rest_framework.permissions import AllowAny


class CustomTokenObtainPairView(TokenObtainPairView):
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        if response.status_code == 200:
            user = authenticate(
                username=request.data.get('username'),
                password=request.data.get('password')
            )
            if user:
                response.data['user'] = {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                }
        return response


class RegisterView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            refresh = RefreshToken.for_user(user)
            return Response({
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                },
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserViewSet(viewsets.ModelViewSet):
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return User.objects.filter(id=self.request.user.id)

    @action(detail=False, methods=['get', 'patch'])
    def me(self, request):
        if request.method == 'GET':
            serializer = self.get_serializer(request.user)
            return Response(serializer.data)
        elif request.method == 'PATCH':
            serializer = self.get_serializer(
                request.user, data=request.data, partial=True
            )
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class WishlistViewSet(viewsets.ModelViewSet):
    serializer_class = WishlistSerializer
    permission_classes = [
        permissions.IsAuthenticatedOrReadOnly, IsWishListOwner]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'description']
    ordering_fields = ['created_at', 'occasion_date']

    def get_queryset(self):
        queryset = Wishlist.objects.all()
        if self.request.user.is_authenticated:
            return queryset.filter(
                is_public=True) | queryset.filter(owner=self.request.user)
        return queryset.filter(is_public=True)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    @action(detail=True, methods=['post'])
    def share(self, request, pk=None):
        # Here you would implement sharing logic
        return Response({'status': 'shared'})


class WishlistItemViewSet(viewsets.ModelViewSet):
    serializer_class = WishlistItemSerializer
    permission_classes = [
        permissions.IsAuthenticatedOrReadOnly, IsPublicOrOwner]

    def get_queryset(self):
        queryset = WishlistItem.objects.annotate(
            total_contributions=Sum('contributions__amount'),
            remaining_amount=F('price') - Sum('contributions__amount')
        )

        wishlist_id = self.request.query_params.get('wishlist')
        if wishlist_id:
            queryset = queryset.filter(wishlist_id=wishlist_id)

        return queryset

    @action(detail=True, methods=['post'])
    def contribute(self, request, pk=None):
        item = self.get_object()
        amount = request.data.get('amount')
        if not amount:
            return Response(
                {'error': 'Amount is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        user = request.user
        if user.wallet_balance < float(amount):
            return Response(
                {'error': 'Insufficient funds'},
                status=status.HTTP_400_BAD_REQUEST
            )

        contribution = Contribution.objects.create(
            item=item,
            contributor=user,
            amount=amount,
            message=request.data.get('message', ''),
            is_anonymous=request.data.get('is_anonymous', False)
        )

        user.wallet_balance -= float(amount)
        user.save()

        if item.contributions.aggregate(
                total=Sum('amount'))['total'] >= item.price:
            item.status = 'FULFILLED'
            item.save()

        return Response(ContributionSerializer(contribution).data)


class ContributionViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = ContributionSerializer
    permission_classes = [permissions.IsAuthenticated, IsContributor]

    def get_queryset(self):
        return Contribution.objects.filter(contributor=self.request.user)


class NotificationViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user)

    @action(detail=True, methods=['post'])
    def mark_read(self, request, pk=None):
        notification = self.get_object()
        notification.is_read = True
        notification.save()
        return Response({'status': 'marked_read'})


class PlanViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for viewing subscription plans
    """
    queryset = SubscriptionPlan.objects.filter(is_active=True)
    serializer_class = SubscriptionPlanSerializer
    permission_classes = [permissions.AllowAny]


class SubscriptionViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing user subscriptions
    """
    serializer_class = UserSubscriptionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return UserSubscription.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        # Here you would integrate with a payment gateway
        plan = SubscriptionPlan.objects.get(
            id=self.request.data.get('plan_id'))

        # Calculate end date (e.g., 30 days from now)
        end_date = timezone.now() + timezone.timedelta(days=30)

        # Create subscription
        serializer.save(
            user=self.request.user,
            plan=plan,
            end_date=end_date,
            is_active=True
        )

    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        subscription = self.get_object()
        subscription.auto_renew = False
        subscription.save()
        return Response({'status': 'subscription will not renew'})

    @action(detail=True, methods=['post'])
    def renew(self, request, pk=None):
        subscription = self.get_object()
        if not subscription.is_active:
            return Response(
                {'error': 'Cannot renew inactive subscription'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Here you would handle payment processing
        subscription.end_date = (
            subscription.end_date + timezone.timedelta(days=30)
        )
        subscription.auto_renew = True
        subscription.save()

        return Response({'status': 'subscription renewed'})


class WishlistShareViewSet(viewsets.ModelViewSet):
    """ViewSet برای مدیریت اشتراک‌گذاری لیست آرزو"""
    serializer_class = WishlistShareSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return WishlistShare.objects.filter(shared_by=self.request.user)

    def perform_create(self, serializer):
        serializer.save(shared_by=self.request.user)

    @action(detail=False, methods=['get'])
    def public_shares(self, request):
        """دریافت اشتراک‌گذاری‌های عمومی"""
        public_shares = WishlistShare.objects.filter(
            share_type='PUBLIC',
            expires_at__isnull=True
        ).select_related('wishlist', 'shared_by')

        serializer = self.get_serializer(public_shares, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def increment_view(self, request, pk=None):
        """افزایش تعداد بازدید"""
        share = self.get_object()
        share.view_count += 1
        share.save()
        return Response({'view_count': share.view_count})


class WishlistInvitationViewSet(viewsets.ModelViewSet):
    """ViewSet برای مدیریت دعوت‌نامه‌ها"""
    serializer_class = WishlistInvitationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return WishlistInvitation.objects.filter(invited_by=self.request.user)

    def perform_create(self, serializer):
        invitation = serializer.save(invited_by=self.request.user)
        # ارسال ایمیل دعوت
        self.send_invitation_email(invitation)

    def send_invitation_email(self, invitation):
        """ارسال ایمیل دعوت"""
        try:
            subject = f'دعوت برای کمک به {invitation.wishlist_item.name}'
            message = f"""
سلام {invitation.invited_name or 'دوست عزیز'},

{invitation.invited_by.first_name or invitation.invited_by.username} شما را دعوت کرده تا در تحقق آرزویش کمک کنید.

آیتم: {invitation.wishlist_item.name}
قیمت: {invitation.wishlist_item.price:,} تومان
پیام: {invitation.message}

برای کمک کردن روی لینک زیر کلیک کنید:
{invitation.get_invitation_url()}

با تشکر،
تیم لیست آرزو
            """

            send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[invitation.invited_email],
                fail_silently=False,
            )
        except Exception as e:
            print(f"Error sending invitation email: {e}")

    @action(detail=False, methods=['get'], permission_classes=[permissions.AllowAny])
    def accept_invitation(self, request):
        """پذیرش دعوت‌نامه"""
        token = request.query_params.get('token')
        if not token:
            return Response({'error': 'توکن دعوت‌نامه الزامی است'},
                            status=status.HTTP_400_BAD_REQUEST)

        try:
            invitation = WishlistInvitation.objects.get(invitation_token=token)
            success, message = invitation.accept_invitation()

            if success:
                return Response({
                    'message': message,
                    'wishlist_item': WishlistItemSerializer(invitation.wishlist_item).data
                })
            else:
                return Response({'error': message},
                                status=status.HTTP_400_BAD_REQUEST)

        except WishlistInvitation.DoesNotExist:
            return Response({'error': 'دعوت‌نامه یافت نشد'},
                            status=status.HTTP_404_NOT_FOUND)

    @action(detail=False, methods=['post'], permission_classes=[permissions.AllowAny])
    def decline_invitation(self, request):
        """رد دعوت‌نامه"""
        token = request.data.get('token')
        if not token:
            return Response({'error': 'توکن دعوت‌نامه الزامی است'},
                            status=status.HTTP_400_BAD_REQUEST)

        try:
            invitation = WishlistInvitation.objects.get(invitation_token=token)
            success, message = invitation.decline_invitation()

            return Response({'message': message})

        except WishlistInvitation.DoesNotExist:
            return Response({'error': 'دعوت‌نامه یافت نشد'},
                            status=status.HTTP_404_NOT_FOUND)


class SocialShareViewSet(viewsets.ModelViewSet):
    """ViewSet برای مدیریت اشتراک‌گذاری در شبکه‌های اجتماعی"""
    serializer_class = SocialShareSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return SocialShare.objects.filter(shared_by=self.request.user)

    def perform_create(self, serializer):
        serializer.save(shared_by=self.request.user)

    @action(detail=True, methods=['post'])
    def track_click(self, request, pk=None):
        """ثبت کلیک روی لینک اشتراک‌گذاری"""
        share = self.get_object()
        share.click_count += 1
        share.save()
        return Response({'click_count': share.click_count})

    @action(detail=True, methods=['post'])
    def track_conversion(self, request, pk=None):
        """ثبت تبدیل (کمک مالی ناشی از اشتراک)"""
        share = self.get_object()
        share.conversion_count += 1
        share.save()
        return Response({'conversion_count': share.conversion_count})


@api_view(['GET'])
@permission_classes([AllowAny])
def shared_wishlist_view(request, share_token):
    """نمایش لیست آرزوی اشتراک‌گذاری شده"""
    try:
        share = WishlistShare.objects.get(share_token=share_token)

        if share.is_expired():
            return Response({'error': 'لینک اشتراک‌گذاری منقضی شده'},
                            status=status.HTTP_410_GONE)

        # افزایش تعداد بازدید
        share.view_count += 1
        share.save()

        # سریالایز کردن داده‌ها
        wishlist_data = WishlistSerializer(share.wishlist).data

        # فیلتر کردن داده‌ها بر اساس تنظیمات اشتراک‌گذاری
        if not share.show_progress:
            # حذف اطلاعات پیشرفت
            for item in wishlist_data.get('items', []):
                item.pop('total_contributions', None)
                item.pop('contribution_percentage', None)

        return Response({
            'wishlist': wishlist_data,
            'share_settings': {
                'allow_contributions': share.allow_contributions,
                'allow_comments': share.allow_comments,
                'show_progress': share.show_progress,
            },
            'view_count': share.view_count
        })

    except WishlistShare.DoesNotExist:
        return Response({'error': 'لینک اشتراک‌گذاری یافت نشد'},
                        status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def create_share_link(request):
    """ایجاد لینک اشتراک‌گذاری"""
    wishlist_id = request.data.get('wishlist_id')
    share_type = request.data.get('share_type', 'PRIVATE')
    allow_contributions = request.data.get('allow_contributions', True)
    allow_comments = request.data.get('allow_comments', True)
    show_progress = request.data.get('show_progress', True)
    expires_in_days = request.data.get('expires_in_days')

    try:
        wishlist = Wishlist.objects.get(id=wishlist_id, user=request.user)

        # حذف اشتراک‌گذاری قبلی (در صورت وجود)
        WishlistShare.objects.filter(
            wishlist=wishlist,
            shared_by=request.user
        ).delete()

        # ایجاد اشتراک‌گذاری جدید
        share_data = {
            'wishlist': wishlist,
            'shared_by': request.user,
            'share_type': share_type,
            'allow_contributions': allow_contributions,
            'allow_comments': allow_comments,
            'show_progress': show_progress,
        }

        if expires_in_days:
            from datetime import timedelta
            share_data['expires_at'] = timezone.now(
            ) + timedelta(days=expires_in_days)

        share = WishlistShare.objects.create(**share_data)

        return Response({
            'share_url': share.get_share_url(),
            'share_token': share.share_token,
            'expires_at': share.expires_at,
        })

    except Wishlist.DoesNotExist:
        return Response({'error': 'لیست آرزو یافت نشد'},
                        status=status.HTTP_404_NOT_FOUND)


# API های احراز هویت با موبایل
@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def send_otp(request):
    """ارسال کد OTP به شماره موبایل"""
    serializer = SendOTPSerializer(data=request.data)

    if not serializer.is_valid():
        return Response({
            'success': False,
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

    phone_number = serializer.validated_data['phone_number']

    # 🛡️ بررسی جامع ضد ربات
    bot_check = AntiBotService.comprehensive_bot_check(request)

    if bot_check['is_bot']:
        SecurityEventLogger.log_bot_detection(
            request,
            bot_check['risk_score'],
            bot_check['blocked_reasons']
        )
        return Response({
            'success': False,
            'message': 'درخواست مشکوک تشخیص داده شد',
            'error_code': 'BOT_DETECTED'
        }, status=status.HTTP_403_FORBIDDEN)

    # بررسی محدودیت نرخ
    rate_ok, rate_message = AntiBotService.rate_limit_check(request)
    if not rate_ok:
        return Response({
            'success': False,
            'message': rate_message,
            'error_code': 'RATE_LIMITED'
        }, status=status.HTTP_429_TOO_MANY_REQUESTS)

    # نیاز به Captcha
    if bot_check['require_captcha']:
        return Response({
            'success': False,
            'message': 'لطفاً ابتدا کد امنیتی را حل کنید',
            'require_captcha': True,
            'error_code': 'CAPTCHA_REQUIRED'
        }, status=status.HTTP_200_OK)

    # ارسال OTP
    success, message = OTPService.send_otp(phone_number, request)

    if success:
        return Response({
            'success': True,
            'message': message,
            'expires_in': 300  # 5 دقیقه
        }, status=status.HTTP_200_OK)
    else:
        return Response({
            'success': False,
            'message': message
        }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def register_with_otp(request):
    """ثبت‌نام کاربر جدید با تایید OTP"""
    serializer = RegisterWithOTPSerializer(data=request.data)

    if not serializer.is_valid():
        return Response({
            'success': False,
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

    phone_number = serializer.validated_data['phone_number']
    otp_code = serializer.validated_data['otp_code']

    # 🛡️ بررسی فیلدهای تله (Honeypot)
    if AntiBotService.honeypot_check(request.data):
        SecurityEventLogger.log_bot_detection(
            request, 100, ['Honeypot field filled']
        )
        return Response({
            'success': False,
            'message': 'درخواست نامعتبر',
            'error_code': 'INVALID_REQUEST'
        }, status=status.HTTP_400_BAD_REQUEST)

    # بررسی جامع ضد ربات با تحلیل رفتار
    form_behavior = request.data.get('behavior', {})
    bot_check = AntiBotService.comprehensive_bot_check(request, form_behavior)

    if bot_check['is_bot']:
        SecurityEventLogger.log_bot_detection(
            request,
            bot_check['risk_score'],
            bot_check['blocked_reasons']
        )
        return Response({
            'success': False,
            'message': 'درخواست مشکوک تشخیص داده شد',
            'error_code': 'BOT_DETECTED'
        }, status=status.HTTP_403_FORBIDDEN)

    # تایید OTP
    is_valid, message = OTPService.verify_otp(phone_number, otp_code, request)

    if not is_valid:
        return Response({
            'success': False,
            'message': message
        }, status=status.HTTP_400_BAD_REQUEST)

    # بررسی وجود کاربر
    if User.objects.filter(username=phone_number).exists():
        return Response({
            'success': False,
            'message': 'کاربری با این شماره موبایل قبلاً ثبت‌نام کرده است'
        }, status=status.HTTP_400_BAD_REQUEST)

    try:
        # ایجاد کاربر جدید
        user = User.objects.create_user(
            username=phone_number,
            phone_number=phone_number,
            first_name=serializer.validated_data.get('first_name', ''),
            last_name=serializer.validated_data.get('last_name', ''),
            email=serializer.validated_data.get('email', ''),
            is_phone_verified=True
        )

        # ثبت موفقیت در امتیازات امنیتی
        fingerprint = AntiBotService.track_device_fingerprint(request, False)
        fingerprint.successful_registrations += 1
        fingerprint.save()

        # تولید token
        refresh = RefreshToken.for_user(user)

        return Response({
            'success': True,
            'message': 'ثبت‌نام با موفقیت انجام شد',
            'user': {
                'id': user.id,
                'username': user.username,
                'phone_number': user.phone_number,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'email': user.email,
            },
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }
        }, status=status.HTTP_201_CREATED)

    except Exception as e:
        return Response({
            'success': False,
            'message': f'خطا در ایجاد کاربر: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([AllowAny])
def generate_captcha(request):
    """تولید چالش Captcha"""
    try:
        challenge_type = request.data.get('type', 'MATH')
        captcha = AntiBotService.generate_captcha_challenge(
            request, challenge_type)

        return Response({
            'success': True,
            'captcha': {
                'id': str(captcha.id),
                'question': captcha.question,
                'type': captcha.challenge_type,
                'expires_at': captcha.expires_at.isoformat(),
                'max_attempts': captcha.max_attempts
            }
        }, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({
            'success': False,
            'message': f'خطا در تولید چالش: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([AllowAny])
def verify_captcha(request):
    """تایید پاسخ Captcha"""
    captcha_id = request.data.get('captcha_id')
    user_answer = request.data.get('answer')

    if not captcha_id or not user_answer:
        return Response({
            'success': False,
            'message': 'شناسه چالش و پاسخ الزامی است'
        }, status=status.HTTP_400_BAD_REQUEST)

    try:
        success, message = AntiBotService.verify_captcha(
            request, captcha_id, user_answer
        )

        if not success:
            SecurityEventLogger.log_captcha_failure(request, 1)

        return Response({
            'success': success,
            'message': message
        }, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({
            'success': False,
            'message': f'خطا در تایید چالش: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([AllowAny])
def check_bot_status(request):
    """بررسی وضعیت ضد ربات (برای تست و دیباگ)"""
    if not settings.DEBUG:
        return Response({
            'success': False,
            'message': 'این API فقط در حالت DEBUG فعال است'
        }, status=status.HTTP_403_FORBIDDEN)

    form_behavior = request.data.get('behavior', {})
    bot_check = AntiBotService.comprehensive_bot_check(request, form_behavior)

    # اطلاعات ردپای دستگاه
    fingerprint = AntiBotService.track_device_fingerprint(request, False)

    # اطلاعات IP
    from .models import IPReputationLog
    ip_address = AntiBotService.get_client_ip(request)
    try:
        ip_log = IPReputationLog.objects.get(ip_address=ip_address)
        ip_info = {
            'risk_score': ip_log.risk_score,
            'is_blocked': ip_log.is_currently_blocked(),
            'registration_attempts': ip_log.registration_attempts,
            'failed_attempts': ip_log.failed_otp_attempts,
        }
    except IPReputationLog.DoesNotExist:
        ip_info = {'message': 'IP جدید است'}

    return Response({
        'success': True,
        'bot_check': bot_check,
        'device_fingerprint': {
            'hash': fingerprint.fingerprint_hash[:12] + '...',
            'risk_score': fingerprint.risk_score,
            'is_suspicious': fingerprint.is_suspicious,
            'attempts': fingerprint.registration_attempts,
        },
        'ip_reputation': ip_info,
        'session_id': AntiBotService.get_session_id(request),
    }, status=status.HTTP_200_OK)


# Email Authentication Views
@api_view(['POST'])
@permission_classes([AllowAny])
def send_email_verification(request):
    """ارسال ایمیل تایید"""
    serializer = SendEmailVerificationSerializer(data=request.data)
    if not serializer.is_valid():
        return Response({
            'success': False,
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

    email = serializer.validated_data['email']
    verification_type = serializer.validated_data['verification_type']

    # بررسی امنیت ضد ربات
    ip_address = AntiBotService.get_client_ip(request)
    user_agent = request.META.get('HTTP_USER_AGENT', '')

    bot_check = AntiBotService.check_request_security(
        ip_address=ip_address,
        user_agent=user_agent,
        session_id=request.session.session_key,
        action='EMAIL_VERIFICATION'
    )

    if bot_check['is_blocked']:
        SecurityEventLogger.log_blocked_request(
            ip_address, user_agent, 'EMAIL_VERIFICATION',
            bot_check['block_reasons']
        )
        return Response({
            'success': False,
            'message': 'درخواست مسدود شده. لطفاً بعداً تلاش کنید',
            'require_captcha': bot_check.get('require_captcha', False)
        }, status=status.HTTP_429_TOO_MANY_REQUESTS)

    # ارسال ایمیل تایید
    success, message = EmailService.send_verification_email(
        email=email,
        verification_type=verification_type,
        ip_address=ip_address,
        user_agent=user_agent
    )

    if success:
        return Response({
            'success': True,
            'message': message
        }, status=status.HTTP_200_OK)
    else:
        return Response({
            'success': False,
            'message': message
        }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def register_with_email(request):
    """ثبت‌نام با ایمیل"""
    serializer = RegisterWithEmailSerializer(data=request.data)
    if not serializer.is_valid():
        return Response({
            'success': False,
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

    # بررسی honeypot fields
    honeypot_fields = ['website', 'url', 'homepage', 'company']
    for field in honeypot_fields:
        if serializer.validated_data.get(field):
            # احتمال ربات - درخواست را رد کن
            return Response({
                'success': False,
                'message': 'خطا در ثبت‌نام'
            }, status=status.HTTP_400_BAD_REQUEST)

    email = serializer.validated_data['email']
    token = serializer.validated_data['token']
    password = serializer.validated_data['password']
    first_name = serializer.validated_data.get('first_name', '')
    last_name = serializer.validated_data.get('last_name', '')

    # بررسی امنیت ضد ربات
    ip_address = AntiBotService.get_client_ip(request)
    user_agent = request.META.get('HTTP_USER_AGENT', '')

    bot_check = AntiBotService.check_request_security(
        ip_address=ip_address,
        user_agent=user_agent,
        session_id=request.session.session_key,
        action='REGISTER'
    )

    if bot_check['is_blocked']:
        SecurityEventLogger.log_blocked_request(
            ip_address, user_agent, 'REGISTER',
            bot_check['block_reasons']
        )
        return Response({
            'success': False,
            'message': 'درخواست مسدود شده. لطفاً بعداً تلاش کنید'
        }, status=status.HTTP_429_TOO_MANY_REQUESTS)

    # تایید توکن ایمیل
    success, message = EmailService.verify_email(
        token=token,
        ip_address=ip_address,
        user_agent=user_agent
    )

    if not success:
        return Response({
            'success': False,
            'message': message
        }, status=status.HTTP_400_BAD_REQUEST)

    # بررسی وجود کاربر با این ایمیل
    if User.objects.filter(email=email).exists():
        return Response({
            'success': False,
            'message': 'کاربری با این ایمیل قبلاً ثبت‌نام کرده است'
        }, status=status.HTTP_400_BAD_REQUEST)

    try:
        # ایجاد کاربر جدید
        user = User.objects.create_user(
            username=email,  # استفاده از ایمیل به عنوان username
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
            is_verified=True
        )

        # تولید توکن JWT
        refresh = RefreshToken.for_user(user)

        return Response({
            'success': True,
            'message': 'ثبت‌نام با موفقیت انجام شد',
            'user': {
                'id': str(user.id),
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
            },
            'tokens': {
                'access': str(refresh.access_token),
                'refresh': str(refresh)
            }
        }, status=status.HTTP_201_CREATED)

    except Exception as e:
        return Response({
            'success': False,
            'message': 'خطا در ثبت‌نام'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([AllowAny])
def login_with_email(request):
    """ورود با ایمیل و رمز عبور"""
    serializer = LoginWithEmailSerializer(data=request.data)
    if not serializer.is_valid():
        return Response({
            'success': False,
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

    email = serializer.validated_data['email']
    password = serializer.validated_data['password']

    # احراز هویت کاربر
    user = authenticate(request, username=email, password=password)

    if user:
        if user.is_active:
            # تولید توکن JWT
            refresh = RefreshToken.for_user(user)

            return Response({
                'success': True,
                'message': 'ورود موفقیت‌آمیز',
                'user': {
                    'id': str(user.id),
                    'email': user.email,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'is_verified': user.is_verified,
                },
                'tokens': {
                    'access': str(refresh.access_token),
                    'refresh': str(refresh)
                }
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                'success': False,
                'message': 'حساب کاربری غیرفعال است'
            }, status=status.HTTP_400_BAD_REQUEST)
    else:
        return Response({
            'success': False,
            'message': 'ایمیل یا رمز عبور اشتباه است'
        }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def verify_email_token(request):
    """تایید توکن ایمیل"""
    serializer = VerifyEmailSerializer(data=request.data)
    if not serializer.is_valid():
        return Response({
            'success': False,
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

    token = serializer.validated_data['token']

    # تایید توکن
    ip_address = AntiBotService.get_client_ip(request)
    user_agent = request.META.get('HTTP_USER_AGENT', '')

    success, message = EmailService.verify_email(
        token=token,
        ip_address=ip_address,
        user_agent=user_agent
    )

    if success:
        return Response({
            'success': True,
            'message': message
        }, status=status.HTTP_200_OK)
    else:
        return Response({
            'success': False,
            'message': message
        }, status=status.HTTP_400_BAD_REQUEST)


# Google OAuth Views
@api_view(['GET'])
@permission_classes([AllowAny])
def google_oauth_url(request):
    """دریافت URL احراز هویت Google"""
    from urllib.parse import urlencode
    from django.conf import settings
    import secrets

    # تولید state برای امنیت
    state = secrets.token_urlsafe(32)
    request.session['oauth_state'] = state

    oauth_config = settings.OAUTH_SETTINGS['GOOGLE']

    params = {
        'client_id': oauth_config['CLIENT_ID'],
        'redirect_uri': oauth_config['REDIRECT_URI'],
        'scope': ' '.join(oauth_config['SCOPE']),
        'response_type': 'code',
        'state': state,
        'access_type': 'offline',
        'prompt': 'consent'
    }

    auth_url = f"{oauth_config['AUTH_URL']}?{urlencode(params)}"

    return Response({
        'success': True,
        'auth_url': auth_url,
        'state': state
    }, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([AllowAny])
def google_oauth_callback(request):
    """پردازش بازگشت از Google OAuth"""
    import requests
    from django.conf import settings
    from django.contrib.auth import authenticate
    from rest_framework_simplejwt.tokens import RefreshToken

    authorization_code = request.data.get('code')
    state = request.data.get('state')

    if not authorization_code:
        return Response({
            'success': False,
            'message': 'کد احراز هویت ارسال نشده است'
        }, status=status.HTTP_400_BAD_REQUEST)

    # بررسی state برای جلوگیری از CSRF
    session_state = request.session.get('oauth_state')
    if not session_state or session_state != state:
        return Response({
            'success': False,
            'message': 'State نامعتبر است'
        }, status=status.HTTP_400_BAD_REQUEST)

    try:
        # تبدیل کد به access token
        oauth_config = settings.OAUTH_SETTINGS['GOOGLE']

        token_data = {
            'client_id': oauth_config['CLIENT_ID'],
            'client_secret': oauth_config['CLIENT_SECRET'],
            'code': authorization_code,
            'grant_type': 'authorization_code',
            'redirect_uri': oauth_config['REDIRECT_URI']
        }

        token_response = requests.post(
            oauth_config['TOKEN_URL'],
            data=token_data,
            timeout=10
        )
        token_response.raise_for_status()
        token_info = token_response.json()

        access_token = token_info.get('access_token')
        if not access_token:
            return Response({
                'success': False,
                'message': 'دریافت access token ناموفق بود'
            }, status=status.HTTP_400_BAD_REQUEST)

        # احراز هویت کاربر با Google token
        user = authenticate(request, google_token=access_token)

        if not user:
            return Response({
                'success': False,
                'message': 'احراز هویت با Google ناموفق بود'
            }, status=status.HTTP_400_BAD_REQUEST)

        # تولید JWT token
        refresh = RefreshToken.for_user(user)

        # پاک کردن state از session
        request.session.pop('oauth_state', None)

        return Response({
            'success': True,
            'message': 'ورود با Google موفقیت‌آمیز بود',
            'user': {
                'id': str(user.id),
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'is_verified': user.is_verified,
            },
            'tokens': {
                'access': str(refresh.access_token),
                'refresh': str(refresh)
            }
        }, status=status.HTTP_200_OK)

    except requests.exceptions.RequestException as e:
        return Response({
            'success': False,
            'message': 'خطا در ارتباط با Google'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    except Exception as e:
        return Response({
            'success': False,
            'message': 'خطای غیرمنتظره در احراز هویت'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([AllowAny])
def google_oauth_direct(request):
    """احراز هویت مستقیم با Google Token (برای mobile apps)"""
    from django.contrib.auth import authenticate
    from rest_framework_simplejwt.tokens import RefreshToken

    access_token = request.data.get('access_token')

    if not access_token:
        return Response({
            'success': False,
            'message': 'Access token ارسال نشده است'
        }, status=status.HTTP_400_BAD_REQUEST)

    try:
        # احراز هویت کاربر با Google token
        user = authenticate(request, google_token=access_token)

        if not user:
            return Response({
                'success': False,
                'message': 'احراز هویت با Google ناموفق بود'
            }, status=status.HTTP_400_BAD_REQUEST)

        # تولید JWT token
        refresh = RefreshToken.for_user(user)

        return Response({
            'success': True,
            'message': 'ورود با Google موفقیت‌آمیز بود',
            'user': {
                'id': str(user.id),
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'is_verified': user.is_verified,
            },
            'tokens': {
                'access': str(refresh.access_token),
                'refresh': str(refresh)
            }
        }, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({
            'success': False,
            'message': 'خطای غیرمنتظره در احراز هویت'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
