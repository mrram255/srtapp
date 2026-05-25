import uuid

from django.db import models

from apps.core.models import CollegeScopedModel


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
