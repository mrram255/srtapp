from django.db import models

from apps.core.models import CollegeScopedModel


class Teacher(CollegeScopedModel):
    """Teacher profile linked to User."""

    user = models.OneToOneField(
        'accounts.User',
        on_delete=models.CASCADE,
        related_name='teacher_profile',
        limit_choices_to={'role': 'TEACHER'},
    )
    employee_id = models.CharField(max_length=50, db_index=True)

    department = models.ForeignKey(
        'colleges.Department',
        on_delete=models.CASCADE,
        related_name='teachers',
    )
    designation = models.CharField(
        max_length=100,
        choices=[
            ('PROFESSOR', 'Professor'),
            ('ASSOCIATE_PROFESSOR', 'Associate Professor'),
            ('ASSISTANT_PROFESSOR', 'Assistant Professor'),
            ('LECTURER', 'Lecturer'),
            ('VISITING_FACULTY', 'Visiting Faculty'),
            ('LAB_ASSISTANT', 'Lab Assistant'),
        ],
    )
    specialization = models.CharField(max_length=200, blank=True)
    qualification = models.CharField(max_length=200)
    experience_years = models.PositiveIntegerField(default=0)

    office_room = models.CharField(max_length=50, blank=True)
    office_hours = models.CharField(max_length=200, blank=True)

    resume = models.CharField(max_length=500, blank=True)
    documents = models.JSONField(blank=True, default=dict)

    joining_date = models.DateField()
    employment_type = models.CharField(
        max_length=20,
        choices=[
            ('PERMANENT', 'Permanent'),
            ('CONTRACT', 'Contract'),
            ('PART_TIME', 'Part Time'),
            ('VISITING', 'Visiting'),
        ],
        default='PERMANENT',
    )

    is_active = models.BooleanField(default=True, db_index=True)

    class Meta:
        db_table = 'teachers'
        ordering = ['-created_at']
        constraints = [
            models.UniqueConstraint(fields=['college', 'employee_id'], name='uniq_teacher_college_employee_id'),
        ]

    def __str__(self):
        return f'{self.user.full_name} ({self.employee_id})'

    @property
    def full_name(self):
        return self.user.full_name

    @property
    def email(self):
        return self.user.email


class TeacherSubjectAssignment(CollegeScopedModel):
    """Subjects assigned to teachers."""

    teacher = models.ForeignKey(
        Teacher,
        on_delete=models.CASCADE,
        related_name='subject_assignments',
    )
    subject = models.ForeignKey(
        'academics.Subject',
        on_delete=models.CASCADE,
        related_name='teacher_assignments',
    )
    semester = models.PositiveIntegerField()
    section = models.CharField(max_length=10)
    academic_year = models.ForeignKey(
        'colleges.AcademicYear',
        on_delete=models.CASCADE,
        related_name='teacher_assignments',
    )
    is_primary = models.BooleanField(default=True)

    class Meta:
        db_table = 'teacher_subject_assignments'
        unique_together = [['teacher', 'subject', 'semester', 'section', 'academic_year']]
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.teacher.user.full_name} — {self.subject.name}'
