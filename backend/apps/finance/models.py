import uuid
from decimal import Decimal

from django.db import models

from apps.core.models import CollegeScopedModel


class FeeStructure(CollegeScopedModel):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    department = models.ForeignKey(
        'colleges.Department',
        on_delete=models.CASCADE,
        related_name='fee_structures',
        null=True,
        blank=True,
    )
    branch = models.ForeignKey(
        'colleges.Branch',
        on_delete=models.CASCADE,
        related_name='fee_structures',
        null=True,
        blank=True,
    )
    semester = models.PositiveIntegerField()
    academic_year = models.ForeignKey(
        'colleges.AcademicYear',
        on_delete=models.CASCADE,
        related_name='fee_structures',
    )

    tuition_fee = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    exam_fee = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    library_fee = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    lab_fee = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    sports_fee = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    hostel_fee = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    transport_fee = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    other_fee = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    total_fee = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    is_active = models.BooleanField(default=True, db_index=True)

    class Meta:
        db_table = 'fee_structures'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.name} — Sem {self.semester}'

    def save(self, *args, **kwargs):
        self.total_fee = (
            self.tuition_fee
            + self.exam_fee
            + self.library_fee
            + self.lab_fee
            + self.sports_fee
            + self.hostel_fee
            + self.transport_fee
            + self.other_fee
        )
        super().save(*args, **kwargs)


class FeePayment(CollegeScopedModel):
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('PAID', 'Paid'),
        ('PARTIAL', 'Partial'),
        ('OVERDUE', 'Overdue'),
        ('WAIVED', 'Waived'),
    ]

    student = models.ForeignKey(
        'students.Student',
        on_delete=models.CASCADE,
        related_name='fee_payments',
    )
    fee_structure = models.ForeignKey(
        FeeStructure,
        on_delete=models.CASCADE,
        related_name='payments',
    )
    amount_due = models.DecimalField(max_digits=12, decimal_places=2)
    amount_paid = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    amount_remaining = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    discount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    fine = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    due_date = models.DateField()
    paid_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PENDING')
    payment_method = models.CharField(max_length=20, blank=True)
    transaction_id = models.CharField(max_length=100, blank=True)
    receipt_number = models.CharField(max_length=50, blank=True)
    remarks = models.TextField(blank=True)

    class Meta:
        db_table = 'fee_payments'
        ordering = ['-due_date']

    def __str__(self):
        return f'{self.student.enrollment_number} — {self.fee_structure.name}'

    def save(self, *args, **kwargs):
        self.amount_remaining = self.amount_due - self.amount_paid - self.discount + self.fine
        if self.status == 'WAIVED':
            super().save(*args, **kwargs)
            return
        if self.amount_remaining <= 0:
            self.status = 'PAID'
        elif self.amount_paid > 0:
            self.status = 'PARTIAL'
        elif self.status not in ('OVERDUE',):
            self.status = 'PENDING'
        super().save(*args, **kwargs)


class FeeComponent(CollegeScopedModel):
    """Line-item fee component linked to a fee structure."""

    fee_structure = models.ForeignKey(
        FeeStructure,
        on_delete=models.CASCADE,
        related_name='components',
    )
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=32, blank=True)
    amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    is_mandatory = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True, db_index=True)

    class Meta:
        db_table = 'fee_components'
        ordering = ['name']

    def __str__(self):
        return f'{self.name} ({self.amount})'


class StudentFeeAccount(CollegeScopedModel):
    STATUS_CHOICES = [
        ('ACTIVE', 'Active'),
        ('CLOSED', 'Closed'),
        ('WAIVED', 'Waived'),
    ]

    student = models.ForeignKey(
        'students.Student',
        on_delete=models.CASCADE,
        related_name='fee_accounts',
    )
    fee_structure = models.ForeignKey(
        FeeStructure,
        on_delete=models.CASCADE,
        related_name='student_accounts',
    )
    total_due = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_paid = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_discount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    balance = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='ACTIVE')
    due_date = models.DateField(null=True, blank=True)

    class Meta:
        db_table = 'student_fee_accounts'
        unique_together = [['student', 'fee_structure']]
        ordering = ['-created_at']

    def recalculate(self):
        self.balance = self.total_due - self.total_paid - self.total_discount
        if self.balance <= 0 and self.total_due > 0:
            self.status = 'CLOSED'
        return self.balance

    def save(self, *args, **kwargs):
        self.recalculate()
        super().save(*args, **kwargs)


class Scholarship(CollegeScopedModel):
    student = models.ForeignKey(
        'students.Student',
        on_delete=models.CASCADE,
        related_name='scholarships',
    )
    name = models.CharField(max_length=200)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    academic_year = models.ForeignKey(
        'colleges.AcademicYear',
        on_delete=models.CASCADE,
        related_name='scholarships',
    )
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'scholarships'
        ordering = ['-created_at']


class ChartOfAccount(CollegeScopedModel):
    ACCOUNT_TYPES = [
        ('asset', 'Asset'),
        ('liability', 'Liability'),
        ('equity', 'Equity'),
        ('income', 'Income'),
        ('expense', 'Expense'),
    ]

    code = models.CharField(max_length=20)
    name = models.CharField(max_length=200)
    account_type = models.CharField(max_length=16, choices=ACCOUNT_TYPES)
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL, related_name='children')
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'chart_of_accounts'
        unique_together = [['college', 'code']]
        ordering = ['code']

    def __str__(self):
        return f'{self.code} — {self.name}'


class JournalEntry(CollegeScopedModel):
    STATUS_CHOICES = [('draft', 'Draft'), ('posted', 'Posted')]

    entry_date = models.DateField()
    description = models.CharField(max_length=255)
    reference = models.CharField(max_length=50, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='draft')
    posted_by = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='journal_entries_posted',
    )

    class Meta:
        db_table = 'journal_entries'
        ordering = ['-entry_date']


class JournalLine(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    journal_entry = models.ForeignKey(JournalEntry, on_delete=models.CASCADE, related_name='lines')
    account = models.ForeignKey(ChartOfAccount, on_delete=models.PROTECT, related_name='journal_lines')
    debit = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    credit = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    narration = models.CharField(max_length=255, blank=True)

    class Meta:
        db_table = 'journal_lines'


class Vendor(CollegeScopedModel):
    name = models.CharField(max_length=200)
    contact_person = models.CharField(max_length=100, blank=True)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=15, blank=True)
    gstin = models.CharField(max_length=20, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'vendors'
        ordering = ['name']


class Budget(CollegeScopedModel):
    account = models.ForeignKey(ChartOfAccount, on_delete=models.CASCADE, related_name='budgets')
    fiscal_year = models.CharField(max_length=9)
    amount_allocated = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    amount_spent = models.DecimalField(max_digits=14, decimal_places=2, default=0)

    class Meta:
        db_table = 'budgets'
        unique_together = [['college', 'account', 'fiscal_year']]


class SalaryStructure(CollegeScopedModel):
    staff = models.ForeignKey(
        'staff.Staff',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='salary_structures',
    )
    designation = models.CharField(max_length=100)
    basic_salary = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    hra = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    allowances = models.JSONField(default=dict, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'salary_structures'


class PayrollRun(CollegeScopedModel):
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('processed', 'Processed'),
        ('paid', 'Paid'),
    ]

    month = models.PositiveSmallIntegerField()
    year = models.PositiveIntegerField()
    status = models.CharField(max_length=12, choices=STATUS_CHOICES, default='draft')
    total_gross = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    total_net = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    processed_by = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='payroll_runs_processed',
    )

    class Meta:
        db_table = 'payroll_runs'
        unique_together = [['college', 'month', 'year']]


class Payslip(CollegeScopedModel):
    payroll_run = models.ForeignKey(PayrollRun, on_delete=models.CASCADE, related_name='payslips')
    staff = models.ForeignKey('staff.Staff', on_delete=models.CASCADE, related_name='payslips')
    gross_salary = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    deductions = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    tds = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    net_salary = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    pdf_url = models.CharField(max_length=500, blank=True)

    class Meta:
        db_table = 'payslips'
        unique_together = [['payroll_run', 'staff']]


class PaymentOrder(CollegeScopedModel):
    STATUS_CHOICES = [
        ('created', 'Created'),
        ('paid', 'Paid'),
        ('failed', 'Failed'),
    ]

    student = models.ForeignKey('students.Student', on_delete=models.CASCADE, related_name='payment_orders')
    fee_payment = models.ForeignKey(
        FeePayment,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='payment_orders',
    )
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    currency = models.CharField(max_length=3, default='INR')
    razorpay_order_id = models.CharField(max_length=100, blank=True, db_index=True)
    razorpay_payment_id = models.CharField(max_length=100, blank=True)
    razorpay_signature = models.CharField(max_length=255, blank=True)
    status = models.CharField(max_length=12, choices=STATUS_CHOICES, default='created')
    receipt_url = models.CharField(max_length=500, blank=True)

    class Meta:
        db_table = 'payment_orders'
        ordering = ['-created_at']
