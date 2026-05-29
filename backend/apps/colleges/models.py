"""
College scope hierarchy (single source for tenant + org structure):

  College → Department → Branch → AcademicYear

Programs, batches, subjects, and calendar live in ``apps.academic`` and reference
``colleges.*`` FKs. Institution branding/profile may also exist in ``apps.institutions``
(one-to-one with College) — do not duplicate Department/Branch there.
"""

from django.db import models

from apps.core.models import BaseModel


class College(BaseModel):
    """College/Institution model."""

    name = models.CharField(max_length=255)
    code = models.CharField(max_length=20, unique=True, db_index=True)
    address = models.TextField()
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    country = models.CharField(max_length=100, default='India')
    pincode = models.CharField(max_length=10)
    phone = models.CharField(max_length=15)
    email = models.EmailField()
    website = models.URLField(blank=True)
    logo = models.CharField(max_length=500, blank=True)
    established_year = models.PositiveIntegerField()
    affiliation = models.CharField(max_length=255, blank=True)
    accreditation = models.CharField(max_length=50, blank=True)
    principal_name = models.CharField(max_length=200, blank=True)
    is_active = models.BooleanField(default=True, db_index=True)

    class Meta:
        db_table = 'colleges'
        ordering = ['name']

    def __str__(self):
        return self.name


class Department(BaseModel):
    """Department within a college."""

    college = models.ForeignKey(
        College,
        on_delete=models.CASCADE,
        related_name='departments',
    )
    name = models.CharField(max_length=200)
    code = models.CharField(max_length=20)
    description = models.TextField(blank=True)
    hod = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='headed_departments',
        limit_choices_to={'role': 'HOD'},
    )
    is_active = models.BooleanField(default=True, db_index=True)

    class Meta:
        db_table = 'departments'
        unique_together = ['college', 'code']
        ordering = ['name']

    def __str__(self):
        return f'{self.name} ({self.college.code})'


class Branch(BaseModel):
    """Branch/Specialization within a department."""

    college = models.ForeignKey(
        College,
        on_delete=models.CASCADE,
        related_name='branches',
    )
    department = models.ForeignKey(
        Department,
        on_delete=models.CASCADE,
        related_name='branches',
    )
    name = models.CharField(max_length=200)
    code = models.CharField(max_length=20)
    duration_years = models.PositiveIntegerField(default=4)
    total_semesters = models.PositiveIntegerField(default=8)
    is_active = models.BooleanField(default=True, db_index=True)

    class Meta:
        db_table = 'branches'
        unique_together = ['college', 'code']
        ordering = ['name']

    def __str__(self):
        return f'{self.name} ({self.department.name})'


class AcademicYear(BaseModel):
    """Academic year configuration."""

    college = models.ForeignKey(
        College,
        on_delete=models.CASCADE,
        related_name='academic_years',
    )
    year = models.CharField(max_length=9)
    start_date = models.DateField()
    end_date = models.DateField()
    is_current = models.BooleanField(default=False, db_index=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'academic_years'
        unique_together = ['college', 'year']
        ordering = ['-year']

    def __str__(self):
        return f'{self.year} ({self.college.name})'

    def save(self, *args, **kwargs):
        if self.is_current:
            AcademicYear.objects.filter(college=self.college, is_current=True).update(is_current=False)
        super().save(*args, **kwargs)
