import uuid

from django.db import models

from apps.core.models import CollegeScopedModel, TimeStampedModel


class Student(CollegeScopedModel):
    """Student profile linked to User."""

    user = models.OneToOneField(
        'accounts.User',
        on_delete=models.CASCADE,
        related_name='student_profile',
        limit_choices_to={'role': 'STUDENT'},
    )
    enrollment_number = models.CharField(max_length=50, db_index=True)
    roll_number = models.CharField(max_length=50, db_index=True)

    department = models.ForeignKey(
        'colleges.Department',
        on_delete=models.CASCADE,
        related_name='students',
    )
    branch = models.ForeignKey(
        'colleges.Branch',
        on_delete=models.CASCADE,
        related_name='students',
    )
    academic_year = models.ForeignKey(
        'colleges.AcademicYear',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='students',
    )

    semester = models.PositiveIntegerField(default=1)
    section = models.CharField(max_length=10, default='A')
    batch_year = models.PositiveIntegerField()

    date_of_birth = models.DateField()
    gender = models.CharField(
        max_length=10,
        choices=[
            ('MALE', 'Male'),
            ('FEMALE', 'Female'),
            ('OTHER', 'Other'),
        ],
    )
    blood_group = models.CharField(max_length=5, blank=True)
    nationality = models.CharField(max_length=50, default='Indian')
    religion = models.CharField(max_length=50, blank=True)
    category = models.CharField(max_length=50, blank=True)

    address = models.TextField()
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    pincode = models.CharField(max_length=10)
    emergency_contact = models.CharField(max_length=15)
    emergency_contact_name = models.CharField(max_length=200)

    admission_date = models.DateField()
    admission_type = models.CharField(
        max_length=20,
        choices=[
            ('REGULAR', 'Regular'),
            ('LATERAL', 'Lateral Entry'),
            ('TRANSFER', 'Transfer'),
        ],
        default='REGULAR',
    )
    previous_education = models.TextField(blank=True)
    previous_percentage = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)

    photo = models.CharField(max_length=500, blank=True)
    signature = models.CharField(max_length=500, blank=True)
    id_card = models.CharField(max_length=500, blank=True)
    documents = models.JSONField(blank=True, default=dict)

    is_active = models.BooleanField(default=True, db_index=True)
    graduation_date = models.DateField(null=True, blank=True)

    class Meta:
        db_table = 'students'
        unique_together = [
            ['college', 'enrollment_number'],
            ['college', 'roll_number'],
        ]
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.user.full_name} ({self.enrollment_number})'

    @property
    def full_name(self):
        return self.user.full_name

    @property
    def email(self):
        return self.user.email


    # ── Section 5: Additional fields ──────────────────────────────
    university_roll_number = models.CharField(
        max_length=50, unique=True, null=True, blank=True, db_index=True
    )
    admission_number = models.CharField(
        max_length=50, unique=True, null=True, blank=True, db_index=True
    )
    caste = models.CharField(max_length=100, blank=True)
    sub_category = models.CharField(max_length=100, blank=True)
    domicile_state = models.CharField(max_length=100, blank=True)
    mother_tongue = models.CharField(max_length=100, blank=True)
    identification_mark = models.CharField(max_length=200, blank=True)
    student_status = models.CharField(
        max_length=20,
        choices=[
            ('active', 'Active'), ('detained', 'Detained'),
            ('suspended', 'Suspended'), ('rusticated', 'Rusticated'),
            ('dropped_out', 'Dropped Out'), ('passout', 'Passed Out'),
            ('alumni', 'Alumni'), ('year_back', 'Year Back'),
            ('semester_back', 'Semester Back'),
        ],
        default='active', db_index=True,
    )
    status_changed_at = models.DateTimeField(null=True, blank=True)
    status_reason = models.TextField(blank=True)
    abc_id = models.CharField(max_length=100, blank=True, help_text="Academic Bank of Credits ID")
    digilocker_id = models.CharField(max_length=100, blank=True)
    hostel_resident = models.BooleanField(default=False)
    transport_user = models.BooleanField(default=False)
    library_card_number = models.CharField(max_length=50, blank=True)


class StudentDocument(CollegeScopedModel):
    """Student uploaded documents."""

    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name='student_documents',
    )
    document_type = models.CharField(
        max_length=50,
        choices=[
            ('PHOTO', 'Photo'),
            ('SIGNATURE', 'Signature'),
            ('AADHAAR', 'Aadhaar Card'),
            ('MARKSHEET_10TH', '10th Marksheet'),
            ('MARKSHEET_12TH', '12th Marksheet'),
            ('TC', 'Transfer Certificate'),
            ('CASTE_CERTIFICATE', 'Caste Certificate'),
            ('INCOME_CERTIFICATE', 'Income Certificate'),
            ('DOMICILE', 'Domicile Certificate'),
            ('OTHER', 'Other'),
        ],
    )
    file_url = models.CharField(max_length=500)
    file_name = models.CharField(max_length=255)
    file_size = models.PositiveIntegerField()
    mime_type = models.CharField(max_length=100)
    is_verified = models.BooleanField(default=False)
    verified_by = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='+',
    )
    verified_at = models.DateTimeField(null=True, blank=True)
    remarks = models.TextField(blank=True)

    class Meta:
        db_table = 'student_documents'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.student.enrollment_number} - {self.document_type}'


class StudentSemesterRecord(TimeStampedModel):
    STATUS_CHOICES = [
        ('ongoing', 'Ongoing'),
        ('passed', 'Passed'),
        ('failed', 'Failed'),
        ('detained', 'Detained'),
        ('backlog', 'Backlog'),
    ]

    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name='semester_records',
    )
    semester_number = models.PositiveSmallIntegerField()
    academic_year_label = models.CharField(max_length=20, help_text="e.g. 2024-25")
    sgpa = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True)
    cgpa = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True)
    total_credits_earned = models.PositiveIntegerField(default=0)
    attendance_percentage = models.DecimalField(
        max_digits=5, decimal_places=2, null=True, blank=True
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='ongoing')
    promoted_to_next = models.BooleanField(default=False)

    class Meta:
        db_table = 'student_semester_records'
        unique_together = ['student', 'semester_number', 'academic_year_label']
        ordering = ['student', 'semester_number']
        indexes = [models.Index(fields=['student', 'status'])]

    def __str__(self):
        return f"{self.student.enrollment_number} | Sem {self.semester_number} | {self.status}"


class StudentDocumentVerification(TimeStampedModel):
    DOC_TYPE_CHOICES = [
        ('photo', 'Photo'),
        ('aadhaar', 'Aadhaar Card'),
        ('ssc_marksheet', 'SSC Marksheet'),
        ('hsc_marksheet', 'HSC Marksheet'),
        ('caste_cert', 'Caste Certificate'),
        ('income_cert', 'Income Certificate'),
        ('domicile', 'Domicile Certificate'),
        ('transfer_cert', 'Transfer Certificate'),
        ('migration_cert', 'Migration Certificate'),
        ('gap_cert', 'Gap Certificate'),
        ('medical_cert', 'Medical Certificate'),
        ('disability_cert', 'Disability Certificate'),
        ('diploma_marksheet', 'Diploma Marksheet'),
        ('graduation_marksheet', 'Graduation Marksheet'),
    ]
    VERIFY_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('verified', 'Verified'),
        ('rejected', 'Rejected'),
        ('re_upload_requested', 'Re-Upload Requested'),
    ]

    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name='document_verifications',
    )
    document_type = models.CharField(max_length=30, choices=DOC_TYPE_CHOICES)
    status = models.CharField(
        max_length=25, choices=VERIFY_STATUS_CHOICES, default='pending', db_index=True
    )
    verified_by = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='verified_documents',
    )
    verified_at = models.DateTimeField(null=True, blank=True)
    remarks = models.TextField(blank=True)

    class Meta:
        db_table = 'student_document_verifications'
        unique_together = ['student', 'document_type']
        ordering = ['student', 'document_type']

    def __str__(self):
        return f"{self.student.enrollment_number} | {self.document_type} | {self.status}"


# ═══════════════════════════════════════════════════════════════════
# ADDITIONAL STUDENT MODELS — Section 5
# ═══════════════════════════════════════════════════════════════════


# ── Section 5 Student field additions ─────────────────────────────
# Monkey-patch via new migration — fields added below as migration
# (actual field addition done via migrations/0004)
