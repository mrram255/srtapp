from decimal import Decimal

import pytest
from rest_framework import status

from apps.finance.models import FeePayment, StudentFeeAccount
from apps.finance.services import FinanceService


@pytest.mark.django_db
def test_list_fee_structures(api_client, accountant_user, fee_structure):
    api_client.force_authenticate(user=accountant_user)
    r = api_client.get('/api/v1/finance/structures/')
    assert r.status_code == status.HTTP_200_OK
    assert len(r.data['data']) >= 1


@pytest.mark.django_db
def test_record_payment_via_api(api_client, accountant_user, student_record, fee_structure):
    api_client.force_authenticate(user=accountant_user)
    r = api_client.post(
        '/api/v1/finance/payments/',
        {
            'student': str(student_record.id),
            'fee_structure': str(fee_structure.id),
            'amount_due': '52000',
            'amount_paid': '10000',
            'due_date': '2026-06-01',
            'payment_method': 'CASH',
        },
        format='json',
    )
    assert r.status_code == status.HTTP_201_CREATED


@pytest.mark.django_db
def test_finance_service_record_payment(student_record, fee_structure):
    payment = FinanceService.record_payment(
        student=student_record,
        fee_structure=fee_structure,
        amount=fee_structure.total_fee,
    )
    assert payment.receipt_number
    assert payment.status == 'PAID'
    account = StudentFeeAccount.objects.get(student=student_record, fee_structure=fee_structure)
    assert account.total_paid == fee_structure.total_fee


@pytest.mark.django_db
def test_defaulters_list(api_client, accountant_user, student_record, fee_structure):
    StudentFeeAccount.objects.create(
        college=student_record.college,
        student=student_record,
        fee_structure=fee_structure,
        total_due=50000,
        balance=30000,
        status='ACTIVE',
    )
    api_client.force_authenticate(user=accountant_user)
    r = api_client.get('/api/v1/finance/defaulters/')
    assert r.status_code == status.HTTP_200_OK
    assert len(r.data['data']) >= 1


@pytest.mark.django_db
def test_fee_accounts_list(api_client, accountant_user, student_record, fee_structure):
    StudentFeeAccount.objects.create(
        college=student_record.college,
        student=student_record,
        fee_structure=fee_structure,
        total_due=50000,
    )
    api_client.force_authenticate(user=accountant_user)
    r = api_client.get('/api/v1/finance/accounts/')
    assert r.status_code == status.HTTP_200_OK


@pytest.mark.django_db
def test_student_sees_own_payments(api_client, student_record, fee_structure):
    FeePayment.objects.create(
        college=student_record.college,
        student=student_record,
        fee_structure=fee_structure,
        amount_due=50000,
        amount_paid=10000,
        due_date='2026-06-01',
    )
    api_client.force_authenticate(user=student_record.user)
    r = api_client.get('/api/v1/finance/payments/')
    assert r.status_code == status.HTTP_200_OK
