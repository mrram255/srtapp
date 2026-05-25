import uuid
from django.db import models
from django.utils import timezone
from apps.core.models import CollegeScopedModel, TimeStampedModel


class Designation(CollegeScopedModel):
    CATEGORY_CHOICES = [
        ('teaching', 'Teaching'),
        ('non_teaching', 'Non-Teaching'),
        ('administrative', 'Administrative'),
    ]

    name = models.CharField(max_length=100)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='teaching')
    level = models.PositiveIntegerField(default=0, help_text="Higher = senior")

    class Meta:
        db_table = 'staff_designations'
        unique_together = ['college', 'name']
        ordering = ['level', 'name']

    def __str__(self):
        return f"{self.name} ({self.get_category_display()})"


class Staff(CollegeScopedModel):
    STAFF_TYPE_CHOICES = [
        ('teaching', 'Teaching'),
        ('non_teaching', 'Non-Teaching'),
        ('contract', 'Contract'),
        ('visiting', 'Visiting'),
        ('guest', 'Guest'),
    ]
    APPOINTMENT_TYPE_CHOICES = [
        ('regular', 'Regular'),
        ('adhoc', 'Ad-hoc'),
        ('temporary', 'Temporary'),
        ('contractual', 'Contractual'),
        ('part_time', 'Part-Time'),
    ]
    QUALIFICATION_CHOICES = [
        ('phd', 'PhD'),
        ('mphil', 'M.Phil'),
        ('masters', 'Masters'),
        ('bachelors', 'Bachelors'),
        ('diploma', 'Diploma'),
    ]
    PHD_STATUS_CHOICES = [
        ('completed', 'Completed'),
        ('pursuing', 'Pursuing'),
        ('not_applicable', 'Not Applicable'),
    ]
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('on_leave', 'On Leave'),
        ('deputation', 'Deputation'),
        ('resigned', 'Resigned'),
        ('retired', 'Retired'),
        ('terminated', 'Terminated'),
    ]

    user = models.OneToOneField(
        'accounts.User',
        on_delete=models.CASCADE,
        related_name='staff_profile',
        limit_choices_to={'role': 'STAFF'},
    )
    employee_id = models.CharField(max_length=50, unique=True, db_index=True, blank=True)

    # ── Employment ──────────────────────────────────────────────────
    staff_type = models.CharField(max_length=20, choices=STAFF_TYPE_CHOICES, default='teaching')
    designation = models.ForeignKey(
        Designation,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='staff_members',
    )
    department = models.ForeignKey(
        'colleges.Department',
        on_delete=models.CASCADE,
        related_name='staff_members',
    )
    date_of_joining = models.DateField()
    date_of_retirement = models.DateField(null=True, blank=True)
    appointment_type = models.CharField(
        max_length=20, choices=APPOINTMENT_TYPE_CHOICES, default='regular'
    )
    appointment_order_number = models.CharField(max_length=100, blank=True)
    appointment_order_date = models.DateField(null=True, blank=True)
    appointment_order_file = models.CharField(
        max_length=500, blank=True, help_text="MinIO object key"
    )

    # ── Qualification ────────────────────────────────────────────────
    highest_qualification = models.CharField(
        max_length=20, choices=QUALIFICATION_CHOICES, blank=True
    )
    specialization = models.CharField(max_length=200, blank=True)
    phd_status = models.CharField(
        max_length=20, choices=PHD_STATUS_CHOICES, default='not_applicable'
    )
    phd_university = models.CharField(max_length=200, blank=True)
    phd_year = models.PositiveIntegerField(null=True, blank=True)
    phd_thesis_title = models.CharField(max_length=500, blank=True)
    net_set_qualified = models.BooleanField(default=False)
    net_set_year = models.PositiveIntegerField(null=True, blank=True)
    net_set_subject = models.CharField(max_length=200, blank=True)
    # [{degree, university, year, percentage}]
    qualifications = models.JSONField(default=list, blank=True)

    # ── Experience ───────────────────────────────────────────────────
    total_experience_years = models.DecimalField(
        max_digits=4, decimal_places=1, default=0
    )
    teaching_experience_years = models.DecimalField(
        max_digits=4, decimal_places=1, default=0
    )
    industry_experience_years = models.DecimalField(
        max_digits=4, decimal_places=1, default=0
    )
    # [{org, designation, from_date, to_date}]
    previous_experiences = models.JSONField(default=list, blank=True)

    # ── Salary ───────────────────────────────────────────────────────
    pay_band = models.CharField(max_length=50, blank=True)
    grade_pay = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    basic_pay = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    bank_name = models.CharField(max_length=100, blank=True)
    bank_account = models.CharField(max_length=50, blank=True)
    bank_ifsc = models.CharField(max_length=20, blank=True)
    pf_number = models.CharField(max_length=50, blank=True)
    esi_number = models.CharField(max_length=50, blank=True)
    uan_number = models.CharField(max_length=50, blank=True)
    pan_number = models.CharField(max_length=20, blank=True)

    # ── Research ─────────────────────────────────────────────────────
    google_scholar_id = models.CharField(max_length=100, blank=True)
    scopus_id = models.CharField(max_length=100, blank=True)
    orcid_id = models.CharField(max_length=100, blank=True)
    vidwan_id = models.CharField(max_length=100, blank=True)
    research_interests = models.JSONField(default=list, blank=True)

    # ── Documents (MinIO paths) ───────────────────────────────────────
    resume = models.CharField(max_length=500, blank=True)

    # ── Status ───────────────────────────────────────────────────────
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active', db_index=True)

    class Meta:
        db_table = 'staff_members'
        ordering = ['employee_id']
        indexes = [
            models.Index(fields=['college', 'department']),
            models.Index(fields=['college', 'staff_type']),
            models.Index(fields=['college', 'status']),
        ]

    def __str__(self):
        return f"{self.employee_id} — {self.user.get_full_name()}"

    def save(self, *args, **kwargs):
        if not self.employee_id:
            self.employee_id = self._generate_employee_id()
        super().save(*args, **kwargs)

    def _generate_employee_id(self):
        college_code = getattr(self.college, 'code', 'COL')[:3].upper()
        year = timezone.now().year % 100
        # Count within college (safe even before save)
        count = Staff.objects.filter(college_id=self.college_id).count() + 1
        return f"{college_code}{year:02d}{count:05d}"


class StaffServiceBook(TimeStampedModel):
    ENTRY_TYPE_CHOICES = [
        ('joining', 'Joining'),
        ('promotion', 'Promotion'),
        ('increment', 'Increment'),
        ('transfer', 'Transfer'),
        ('deputation', 'Deputation'),
        ('suspension', 'Suspension'),
        ('reinstatement', 'Reinstatement'),
        ('retirement', 'Retirement'),
    ]

    staff = models.ForeignKey(
        Staff,
        on_delete=models.CASCADE,
        related_name='service_book_entries',
    )
    entry_type = models.CharField(max_length=20, choices=ENTRY_TYPE_CHOICES)
    effective_date = models.DateField(db_index=True)
    order_number = models.CharField(max_length=100, blank=True)
    order_date = models.DateField(null=True, blank=True)
    description = models.TextField()
    old_designation = models.ForeignKey(
        Designation,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='old_entries',
    )
    new_designation = models.ForeignKey(
        Designation,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='new_entries',
    )
    old_pay = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    new_pay = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    document = models.CharField(max_length=500, blank=True, help_text="MinIO object key")

    class Meta:
        db_table = 'staff_service_book'
        ordering = ['-effective_date']

    def __str__(self):
        return f"{self.staff.employee_id} | {self.entry_type} | {self.effective_date}"
