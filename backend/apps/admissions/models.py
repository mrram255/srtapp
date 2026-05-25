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

    class Meta:
        db_table = 'admission_applications'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.application_number} - {self.first_name} {self.last_name}'
