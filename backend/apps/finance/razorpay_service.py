from __future__ import annotations

import hashlib
import hmac
import uuid
from decimal import Decimal

from django.conf import settings

from .models import PaymentOrder


class RazorpayService:
    @staticmethod
    def is_configured() -> bool:
        return bool(getattr(settings, 'RAZORPAY_KEY_ID', '') and getattr(settings, 'RAZORPAY_KEY_SECRET', ''))

    @staticmethod
    def create_order(*, student, amount: Decimal, fee_payment=None, college) -> PaymentOrder:
        amount_paise = int(amount * 100)
        order_id = f'order_{uuid.uuid4().hex[:16]}'

        if RazorpayService.is_configured():
            try:
                import razorpay

                client = razorpay.Client(
                    auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET),
                )
                rz_order = client.order.create(
                    {'amount': amount_paise, 'currency': 'INR', 'payment_capture': 1},
                )
                order_id = rz_order['id']
            except Exception:
                pass

        return PaymentOrder.objects.create(
            college=college,
            student=student,
            fee_payment=fee_payment,
            amount=amount,
            razorpay_order_id=order_id,
            status='created',
        )

    @staticmethod
    def verify_signature(order_id: str, payment_id: str, signature: str) -> bool:
        secret = getattr(settings, 'RAZORPAY_KEY_SECRET', '')
        if not secret:
            return True
        payload = f'{order_id}|{payment_id}'
        expected = hmac.new(secret.encode(), payload.encode(), hashlib.sha256).hexdigest()
        return hmac.compare_digest(expected, signature)

    @staticmethod
    def mark_paid(order: PaymentOrder, payment_id: str, signature: str = '') -> PaymentOrder:
        if signature and not RazorpayService.verify_signature(order.razorpay_order_id, payment_id, signature):
            order.status = 'failed'
            order.save(update_fields=['status'])
            return order

        order.razorpay_payment_id = payment_id
        order.razorpay_signature = signature
        order.status = 'paid'
        order.save(update_fields=['razorpay_payment_id', 'razorpay_signature', 'status'])

        if order.fee_payment_id:
            from django.utils import timezone

            fp = order.fee_payment
            fp.amount_paid += order.amount
            fp.payment_method = 'RAZORPAY'
            fp.transaction_id = payment_id
            fp.paid_date = timezone.localdate()
            fp.save()

        return order
