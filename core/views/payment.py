from django.shortcuts import render
from django.views import View
from django.conf import settings
from core.services.zarinpal import ZarinpalGateway
from core.services.payment import PaymentService
from core.models import Transaction


class PaymentVerificationView(View):
    def get(self, request):
        authority = request.GET.get('Authority')
        status = request.GET.get('Status')

        if not authority or status != 'OK':
            return render(request, 'payment/verify.html', {
                'success': False,
                'error_message': 'Payment was cancelled or invalid'
            })

        try:
            transaction = Transaction.objects.get(
                reference_id=authority,
                status='PENDING'
            )

            gateway = ZarinpalGateway(
                settings.ZARINPAL_MERCHANT_ID,
                settings.ZARINPAL_CALLBACK_URL,
                settings.ZARINPAL_SANDBOX
            )

            success, ref_id, status_code = gateway.verify_payment(
                authority,
                int(transaction.amount)
            )

            if success:
                # Process the successful payment
                transaction, subscription = PaymentService.process_payment_callback(
                    reference_id=authority,
                    status='SUCCESS',
                    gateway_response={'ref_id': ref_id}
                )

                return render(request, 'payment/verify.html', {
                    'success': True,
                    'ref_id': ref_id,
                    'subscription': subscription
                })
            else:
                transaction.status = 'FAILED'
                transaction.save()

                return render(request, 'payment/verify.html', {
                    'success': False,
                    'error_message': f'Payment verification failed: {ref_id}'
                })

        except Transaction.DoesNotExist:
            return render(request, 'payment/verify.html', {
                'success': False,
                'error_message': 'Invalid transaction'
            })
        except Exception as e:
            return render(request, 'payment/verify.html', {
                'success': False,
                'error_message': str(e)
            })
