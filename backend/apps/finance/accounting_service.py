from __future__ import annotations

from decimal import Decimal

from django.db import transaction

from .models import ChartOfAccount, JournalEntry, JournalLine, PayrollRun, Payslip, SalaryStructure


class AccountingService:
    @staticmethod
    @transaction.atomic
    def create_journal_entry(*, college, entry_date, description, lines: list[dict], posted_by) -> JournalEntry:
        total_debit = sum(Decimal(str(l.get('debit', 0))) for l in lines)
        total_credit = sum(Decimal(str(l.get('credit', 0))) for l in lines)
        if total_debit != total_credit:
            raise ValueError('Debits must equal credits.')

        entry = JournalEntry.objects.create(
            college=college,
            entry_date=entry_date,
            description=description,
            status='posted',
            posted_by=posted_by,
        )
        for line in lines:
            account = ChartOfAccount.objects.get(pk=line['account'], college=college)
            JournalLine.objects.create(
                journal_entry=entry,
                account=account,
                debit=line.get('debit', 0),
                credit=line.get('credit', 0),
                narration=line.get('narration', ''),
            )
        return entry

    @staticmethod
    @transaction.atomic
    def process_payroll(*, college, month: int, year: int, processed_by) -> PayrollRun:
        run, _ = PayrollRun.objects.get_or_create(
            college=college,
            month=month,
            year=year,
            defaults={'status': 'draft'},
        )
        structures = SalaryStructure.objects.filter(college=college, is_active=True, is_deleted=False)
        total_gross = Decimal('0')
        total_net = Decimal('0')
        Payslip.objects.filter(payroll_run=run).delete()

        for structure in structures:
            if not structure.staff_id:
                continue
            gross = structure.basic_salary + structure.hra
            for val in (structure.allowances or {}).values():
                gross += Decimal(str(val))
            tds = (gross * Decimal('0.1')).quantize(Decimal('0.01'))
            deductions = tds
            net = gross - deductions
            Payslip.objects.create(
                college=college,
                payroll_run=run,
                staff=structure.staff,
                gross_salary=gross,
                deductions=deductions,
                tds=tds,
                net_salary=net,
            )
            total_gross += gross
            total_net += net

        run.total_gross = total_gross
        run.total_net = total_net
        run.status = 'processed'
        run.processed_by = processed_by
        run.save(update_fields=['total_gross', 'total_net', 'status', 'processed_by'])
        return run
