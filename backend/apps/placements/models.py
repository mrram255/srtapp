from django.db import models

from apps.core.models import CollegeScopedModel


class Company(CollegeScopedModel):
    name = models.CharField(max_length=255)
    industry = models.CharField(max_length=100, blank=True)
    website = models.URLField(blank=True)
    logo = models.CharField(max_length=500, blank=True)
    description = models.TextField(blank=True)
    contact_person = models.CharField(max_length=200, blank=True)
    contact_email = models.EmailField(blank=True)
    contact_phone = models.CharField(max_length=15, blank=True)
    is_active = models.BooleanField(default=True, db_index=True)

    class Meta:
        db_table = 'placement_companies'
        ordering = ['name']

    def __str__(self):
        return self.name


class JobPosting(CollegeScopedModel):
    STATUS_CHOICES = [
        ('DRAFT', 'Draft'),
        ('OPEN', 'Open'),
        ('CLOSED', 'Closed'),
        ('FILLED', 'Filled'),
    ]

    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='job_postings')
    title = models.CharField(max_length=255)
    description = models.TextField()
    requirements = models.TextField()
    salary_range = models.CharField(max_length=100, blank=True)
    job_type = models.CharField(
        max_length=20,
        choices=[
            ('FULL_TIME', 'Full Time'),
            ('INTERNSHIP', 'Internship'),
            ('PART_TIME', 'Part Time'),
        ],
        default='FULL_TIME',
    )
    location = models.CharField(max_length=255, blank=True)
    openings = models.PositiveIntegerField(default=1)
    application_deadline = models.DateField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='DRAFT')
    is_active = models.BooleanField(default=True, db_index=True)

    class Meta:
        db_table = 'job_postings'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.title} at {self.company.name}'


class PlacementApplication(CollegeScopedModel):
    STATUS_CHOICES = [
        ('APPLIED', 'Applied'),
        ('SHORTLISTED', 'Shortlisted'),
        ('REJECTED', 'Rejected'),
        ('INTERVIEW', 'Interview Scheduled'),
        ('SELECTED', 'Selected'),
        ('OFFERED', 'Offered'),
        ('ACCEPTED', 'Accepted'),
        ('DECLINED', 'Declined'),
    ]

    student = models.ForeignKey('students.Student', on_delete=models.CASCADE, related_name='placement_applications')
    job = models.ForeignKey(JobPosting, on_delete=models.CASCADE, related_name='applications')
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='APPLIED')
    resume = models.CharField(max_length=500, blank=True)
    cover_letter = models.TextField(blank=True)
    applied_at = models.DateTimeField(auto_now_add=True)
    interview_date = models.DateTimeField(null=True, blank=True)
    offer_letter = models.CharField(max_length=500, blank=True)
    package_offered = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    remarks = models.TextField(blank=True)

    class Meta:
        db_table = 'placement_applications'
        unique_together = [['student', 'job']]
        ordering = ['-applied_at']

    def __str__(self):
        return f'{self.student.enrollment_number} - {self.job.title}'
