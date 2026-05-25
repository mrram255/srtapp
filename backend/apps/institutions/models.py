from __future__ import annotations

from django.db import models

from apps.core.models import TimeStampedModel


class Institution(TimeStampedModel):
    INSTITUTION_TYPES = [
        ('university', 'University'),
        ('autonomous', 'Autonomous'),
        ('affiliated', 'Affiliated'),
        ('deemed', 'Deemed'),
    ]

    college = models.OneToOneField(
        'colleges.College',
        on_delete=models.CASCADE,
        related_name='institution',
        null=True,
        blank=True,
    )
    name = models.CharField(max_length=255)
    short_name = models.CharField(max_length=50, blank=True)
    code = models.CharField(max_length=20, unique=True, db_index=True)
    logo = models.CharField(max_length=500, blank=True)
    favicon = models.CharField(max_length=500, blank=True)
    institution_type = models.CharField(max_length=20, choices=INSTITUTION_TYPES, default='affiliated')
    affiliation_university = models.CharField(max_length=255, blank=True)
    affiliation_number = models.CharField(max_length=100, blank=True)
    aicte_approval_number = models.CharField(max_length=100, blank=True)
    naac_grade = models.CharField(max_length=10, blank=True)
    naac_valid_until = models.DateField(null=True, blank=True)
    nirf_rank = models.PositiveIntegerField(null=True, blank=True)
    nirf_year = models.PositiveIntegerField(null=True, blank=True)
    established_year = models.PositiveIntegerField(null=True, blank=True)
    website_url = models.URLField(blank=True)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    fax = models.CharField(max_length=20, blank=True)
    address_line_1 = models.CharField(max_length=255, blank=True)
    address_line_2 = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=100, default='India', blank=True)
    pincode = models.CharField(max_length=10, blank=True)
    principal_name = models.CharField(max_length=200, blank=True)
    principal_signature = models.CharField(max_length=500, blank=True)
    registrar_name = models.CharField(max_length=200, blank=True)
    registrar_signature = models.CharField(max_length=500, blank=True)
    stamp_image = models.CharField(max_length=500, blank=True)
    gstin = models.CharField(max_length=20, blank=True)
    pan_number = models.CharField(max_length=20, blank=True)
    bank_name = models.CharField(max_length=200, blank=True)
    bank_account = models.CharField(max_length=50, blank=True)
    bank_ifsc = models.CharField(max_length=20, blank=True)

    class Meta:
        db_table = 'institutions'
        ordering = ['name']

    def __str__(self):
        return self.name


class InstitutionSettings(TimeStampedModel):
    GRADING_SYSTEMS = [
        ('CGPA_10', 'CGPA 10'),
        ('CGPA_4', 'CGPA 4'),
        ('percentage', 'Percentage'),
        ('grade', 'Grade'),
    ]
    RESULT_DISPLAY = [
        ('cgpa', 'CGPA'),
        ('percentage', 'Percentage'),
        ('both', 'Both'),
    ]

    institution = models.OneToOneField(
        Institution,
        on_delete=models.CASCADE,
        related_name='settings',
    )
    academic_year_start_month = models.PositiveIntegerField(default=6)
    attendance_minimum_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=75)
    grading_system = models.CharField(max_length=20, choices=GRADING_SYSTEMS, default='CGPA_10')
    result_display_mode = models.CharField(max_length=20, choices=RESULT_DISPLAY, default='cgpa')
    fee_late_fine_per_day = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    fee_due_reminder_days = models.JSONField(default=list, blank=True)
    sms_enabled = models.BooleanField(default=False)
    whatsapp_enabled = models.BooleanField(default=False)
    email_enabled = models.BooleanField(default=True)
    sms_api_key = models.CharField(max_length=255, blank=True)
    whatsapp_api_key = models.CharField(max_length=255, blank=True)
    certificate_qr_enabled = models.BooleanField(default=True)
    certificate_blockchain_enabled = models.BooleanField(default=False)
    enrollment_number_format = models.CharField(max_length=100, default='{year}-{dept}-{seq:04d}')
    receipt_number_format = models.CharField(max_length=100, default='RCP-{year}-{seq:06d}')
    timezone = models.CharField(max_length=50, default='Asia/Kolkata')
    date_format = models.CharField(max_length=20, default='DD/MM/YYYY')

    class Meta:
        db_table = 'institution_settings'

    def __str__(self):
        return f'Settings — {self.institution.name}'
