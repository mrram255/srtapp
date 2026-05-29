from django.db import models

from apps.core.models import CollegeScopedModel


def default_empty_dict():
    return {}


class AdmissionApplication(CollegeScopedModel):
    STATUS_CHOICES = [
        ('DRAFT', 'Draft'),
        ('SUBMITTED', 'Submitted'),
        ('UNDER_REVIEW', 'Under Review'),
        ('SHORTLISTED', 'Shortlisted'),
        ('REJECTED', 'Rejected'),
        ('ACCEPTED', 'Accepted'),
        ('ENROLLED', 'Enrolled'),
    ]

    application_number = models.CharField(max_length=50, unique=True, db_index=True)

    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=15)
    date_of_birth = models.DateField()
    gender = models.CharField(
        max_length=10,
        choices=[
            ('MALE', 'Male'),
            ('FEMALE', 'Female'),
            ('OTHER', 'Other'),
        ],
    )

    department = models.ForeignKey(
        'colleges.Department',
        on_delete=models.CASCADE,
        related_name='admissions',
    )
    branch = models.ForeignKey(
        'colleges.Branch',
        on_delete=models.CASCADE,
        related_name='admissions',
    )
    previous_school = models.CharField(max_length=255)
    previous_percentage = models.DecimalField(max_digits=5, decimal_places=2)
    entrance_exam_score = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)

    photo = models.CharField(max_length=500, blank=True)
    marksheet = models.CharField(max_length=500, blank=True)
    identity_proof = models.CharField(max_length=500, blank=True)
    other_documents = models.JSONField(default=default_empty_dict, blank=True)

    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='DRAFT')
    reviewed_by = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reviewed_admissions',
    )
    reviewed_at = models.DateTimeField(null=True, blank=True)
    remarks = models.TextField(blank=True)
    cycle = models.ForeignKey(
        'AdmissionCycle',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='applications',
    )

    class Meta:
        db_table = 'admission_applications'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.application_number} - {self.first_name} {self.last_name}'


class AdmissionCycle(CollegeScopedModel):
    name = models.CharField(max_length=200)
    academic_year = models.ForeignKey(
        'colleges.AcademicYear',
        on_delete=models.CASCADE,
        related_name='admission_cycles',
    )
    start_date = models.DateField()
    end_date = models.DateField()
    is_active = models.BooleanField(default=True, db_index=True)

    class Meta:
        db_table = 'admission_cycles'
        ordering = ['-start_date']

    def __str__(self):
        return self.name


class AdmissionInquiry(CollegeScopedModel):
    STATUS_CHOICES = [
        ('new', 'New'),
        ('contacted', 'Contacted'),
        ('converted', 'Converted'),
        ('lost', 'Lost'),
    ]

    name = models.CharField(max_length=200)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=15)
    source = models.CharField(max_length=50, blank=True)
    status = models.CharField(max_length=16, choices=STATUS_CHOICES, default='new', db_index=True)
    department = models.ForeignKey(
        'colleges.Department',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='admission_inquiries',
    )
    notes = models.TextField(blank=True)
    assigned_to = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_inquiries',
    )
    application = models.ForeignKey(
        AdmissionApplication,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='inquiries',
    )

    class Meta:
        db_table = 'admission_inquiries'
        ordering = ['-created_at']

    def __str__(self):
        return self.name


class MeritList(CollegeScopedModel):
    cycle = models.ForeignKey(AdmissionCycle, on_delete=models.CASCADE, related_name='merit_lists')
    title = models.CharField(max_length=200)
    department = models.ForeignKey(
        'colleges.Department',
        on_delete=models.CASCADE,
        related_name='merit_lists',
    )
    published_at = models.DateTimeField(null=True, blank=True)
    is_published = models.BooleanField(default=False, db_index=True)

    class Meta:
        db_table = 'merit_lists'
        ordering = ['-created_at']

    def __str__(self):
        return self.title


class MeritListEntry(CollegeScopedModel):
    merit_list = models.ForeignKey(MeritList, on_delete=models.CASCADE, related_name='entries')
    application = models.ForeignKey(AdmissionApplication, on_delete=models.CASCADE, related_name='merit_entries')
    rank = models.PositiveIntegerField()
    score = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    seat_accepted = models.BooleanField(default=False)

    class Meta:
        db_table = 'merit_list_entries'
        ordering = ['rank']
        unique_together = [['merit_list', 'application']]
