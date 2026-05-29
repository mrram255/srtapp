from __future__ import annotations

import uuid
from decimal import Decimal

from django.db import transaction
from django.utils import timezone

from .models import FeePayment, StudentFeeAccount


class FinanceService:
    @staticmethod
    @transaction.atomic
    def record_payment(*, student, fee_structure, amount: Decimal, payment_method: str = 'CASH', remarks: str = '') -> FeePayment:
        account, _ = StudentFeeAccount.objects.get_or_create(
            student=student,
            fee_structure=fee_structure,
            defaults={
                'college': student.college,
                'total_due': fee_structure.total_fee,
                'due_date': timezone.localdate(),
            },
        )
        if account.total_due == 0:
            account.total_due = fee_structure.total_fee
            account.save(update_fields=['total_due'])

        amount_due = account.balance if account.balance > 0 else fee_structure.total_fee
        payment = FeePayment.objects.create(
            college=student.college,
            student=student,
            fee_structure=fee_structure,
            amount_due=amount_due,
            amount_paid=amount,
            due_date=account.due_date or timezone.localdate(),
            paid_date=timezone.localdate(),
            status='PAID',
            payment_method=payment_method,
            transaction_id=f'TXN-{uuid.uuid4().hex[:12].upper()}',
            receipt_number=f'RCP-{uuid.uuid4().hex[:8].upper()}',
            remarks=remarks,
        )

        account.total_paid += amount
        account.recalculate()
        account.save(update_fields=['total_paid', 'balance', 'status'])

        return payment

    @staticmethod
    def list_defaulters(college):
        return StudentFeeAccount.objects.filter(
            college=college,
            is_deleted=False,
            balance__gt=0,
            status='ACTIVE',
        ).select_related('student', 'student__user', 'fee_structure')
