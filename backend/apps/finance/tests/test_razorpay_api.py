from decimal import Decimal

import pytest
from rest_framework import status

from apps.finance.models import PaymentOrder
from apps.finance.razorpay_service import RazorpayService


@pytest.mark.django_db
def test_create_razorpay_order(api_client, student_record):
    api_client.force_authenticate(user=student_record.user)
    r = api_client.post(
        '/api/v1/finance/razorpay/create-order/',
        {'student': str(student_record.id), 'amount': '1500'},
        format='json',
    )
    assert r.status_code == status.HTTP_201_CREATED
    assert r.data['data']['razorpay_order_id']
    assert r.data['data']['mock_mode'] is True


@pytest.mark.django_db
def test_verify_razorpay_payment(api_client, student_record, college):
    order = RazorpayService.create_order(
        student=student_record,
        amount=Decimal('1000'),
        college=college,
    )
    api_client.force_authenticate(user=student_record.user)
    r = api_client.post(
        '/api/v1/finance/razorpay/verify/',
        {
            'razorpay_order_id': order.razorpay_order_id,
            'razorpay_payment_id': 'pay_test123',
            'razorpay_signature': '',
        },
        format='json',
    )
    assert r.status_code == status.HTTP_200_OK
    order.refresh_from_db()
    assert order.status == 'paid'


@pytest.mark.django_db
def test_fee_receipt_endpoint(api_client, accountant_user, student_record, fee_structure):
    from django.utils import timezone

    from apps.finance.models import FeePayment

    payment = FeePayment.objects.create(
        college=student_record.college,
        student=student_record,
        fee_structure=fee_structure,
        amount_due=1000,
        amount_paid=1000,
        due_date=timezone.localdate(),
        paid_date=timezone.localdate(),
        status='PAID',
        receipt_number='RCP-TEST01',
    )
    api_client.force_authenticate(user=accountant_user)
    r = api_client.get(f'/api/v1/finance/payments/{payment.id}/receipt/')
    assert r.status_code == status.HTTP_200_OK
    assert 'receipt_url' in r.data['data'] or 'receipt_number' in r.data['data']
