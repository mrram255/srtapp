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
