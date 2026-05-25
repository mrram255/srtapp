from __future__ import annotations

from django.core.exceptions import ValidationError
from django.db import models

from apps.core.models import OrderedModel, TimeStampedModel


class Regulation(TimeStampedModel):
    REGULATION_TYPES = [
        ('cbcs', 'CBCS'),
        ('nep', 'NEP'),
        ('annual', 'Annual'),
        ('semester', 'Semester'),
    ]

    college = models.ForeignKey('colleges.College', on_delete=models.CASCADE, related_name='regulations')
    name = models.CharField(max_length=200)
    code = models.CharField(max_length=20, db_index=True)
    regulation_type = models.CharField(max_length=20, choices=REGULATION_TYPES, default='cbcs')
    effective_from = models.ForeignKey(
        'colleges.AcademicYear',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='regulations',
    )
    grading_scale = models.JSONField(default=dict, blank=True)
    pass_marks_internal = models.PositiveIntegerField(default=40)
    pass_marks_external = models.PositiveIntegerField(default=40)
    pass_marks_total = models.PositiveIntegerField(default=50)
    attendance_minimum = models.PositiveIntegerField(default=75)
    max_credits_per_semester = models.PositiveIntegerField(default=26)

    class Meta:
        db_table = 'academic_regulations'
        unique_together = [('college', 'code')]
        ordering = ['name']

    def __str__(self):
        return self.name


class Program(OrderedModel):
    LEVELS = [
        ('certificate', 'Certificate'),
        ('diploma', 'Diploma'),
        ('ug', 'Under Graduate'),
        ('pg', 'Post Graduate'),
        ('mphil', 'M.Phil'),
        ('phd', 'PhD'),
        ('postdoc', 'Post Doc'),
    ]
    PROGRAM_TYPES = [
        ('regular', 'Regular'),
        ('distance', 'Distance'),
        ('online', 'Online'),
        ('part_time', 'Part Time'),
    ]
    ACCREDITATION = [
        ('nba', 'NBA'),
        ('naac', 'NAAC'),
        ('both', 'Both'),
        ('none', 'None'),
    ]

    college = models.ForeignKey('colleges.College', on_delete=models.CASCADE, related_name='programs')
    department = models.ForeignKey('colleges.Department', on_delete=models.CASCADE, related_name='programs')
    legacy_branch = models.ForeignKey(
        'colleges.Branch',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='program_link',
    )
    regulation = models.ForeignKey(
        Regulation,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='programs',
    )
    name = models.CharField(max_length=200)
    short_name = models.CharField(max_length=50, blank=True)
    code = models.CharField(max_length=20, db_index=True)
    level = models.CharField(max_length=20, choices=LEVELS, default='ug')
    duration_years = models.PositiveIntegerField(default=4)
    total_semesters = models.PositiveIntegerField(default=8)
    total_credits = models.PositiveIntegerField(default=160)
    program_type = models.CharField(max_length=20, choices=PROGRAM_TYPES, default='regular')
    intake_capacity = models.PositiveIntegerField(default=60)
    is_nep_compliant = models.BooleanField(default=False)
    accreditation_status = models.CharField(max_length=20, choices=ACCREDITATION, default='none')

    class Meta:
        db_table = 'academic_programs'
        unique_together = [('college', 'code')]
        ordering = ['order', 'name']

    def __str__(self):
        return self.name


class Batch(TimeStampedModel):
    program = models.ForeignKey(Program, on_delete=models.CASCADE, related_name='batches')
    academic_year = models.ForeignKey(
        'colleges.AcademicYear',
        on_delete=models.CASCADE,
        related_name='batches',
    )
    name = models.CharField(max_length=100)
    start_year = models.PositiveIntegerField()
    end_year = models.PositiveIntegerField()
    current_semester = models.PositiveIntegerField(default=1)

    class Meta:
        db_table = 'academic_batches'
        ordering = ['-start_year', 'name']

    def __str__(self):
        return self.name


class Section(TimeStampedModel):
    batch = models.ForeignKey(Batch, on_delete=models.CASCADE, related_name='sections')
    name = models.CharField(max_length=20)
    max_students = models.PositiveIntegerField(default=60)
    class_teacher = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='class_sections',
    )

    class Meta:
        db_table = 'academic_sections'
        unique_together = [('batch', 'name')]
        ordering = ['name']

    def __str__(self):
        return f'{self.batch.name} — {self.name}'


class Semester(TimeStampedModel):
    STATUS_CHOICES = [
        ('upcoming', 'Upcoming'),
        ('ongoing', 'Ongoing'),
        ('exam', 'Exam'),
        ('completed', 'Completed'),
    ]

    academic_year = models.ForeignKey(
        'colleges.AcademicYear',
        on_delete=models.CASCADE,
        related_name='semesters',
    )
    batch = models.ForeignKey(Batch, on_delete=models.CASCADE, related_name='semesters')
    semester_number = models.PositiveIntegerField()
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    is_current = models.BooleanField(default=False, db_index=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='upcoming')

    class Meta:
        db_table = 'academic_semesters'
        unique_together = [('batch', 'semester_number', 'academic_year')]
        ordering = ['semester_number']

    def save(self, *args, **kwargs):
        if self.is_current:
            Semester.objects.filter(batch=self.batch, is_current=True).exclude(pk=self.pk).update(is_current=False)
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.batch.name} Sem {self.semester_number}'


class CurriculumSubject(TimeStampedModel):
    SUBJECT_TYPES = [
        ('theory', 'Theory'),
        ('practical', 'Practical'),
        ('project', 'Project'),
        ('seminar', 'Seminar'),
        ('internship', 'Internship'),
    ]
    CATEGORIES = [
        ('core', 'Core'),
        ('elective_dept', 'Department Elective'),
        ('elective_open', 'Open Elective'),
        ('language', 'Language'),
        ('mandatory', 'Mandatory'),
        ('audit', 'Audit'),
        ('ability_enhancement', 'Ability Enhancement'),
        ('skill_enhancement', 'Skill Enhancement'),
        ('value_added', 'Value Added'),
        ('minor', 'Minor'),
    ]

    college = models.ForeignKey('colleges.College', on_delete=models.CASCADE, related_name='curriculum_subjects')
    program = models.ForeignKey(Program, on_delete=models.CASCADE, related_name='subjects')
    regulation = models.ForeignKey(
        Regulation,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='subjects',
    )
    semester_number = models.PositiveIntegerField()
    name = models.CharField(max_length=200)
    short_name = models.CharField(max_length=50, blank=True)
    code = models.CharField(max_length=20, db_index=True)
    subject_type = models.CharField(max_length=20, choices=SUBJECT_TYPES, default='theory')
    category = models.CharField(max_length=30, choices=CATEGORIES, default='core')
    credits = models.PositiveIntegerField(default=3)
    lecture_hours = models.PositiveIntegerField(default=3)
    tutorial_hours = models.PositiveIntegerField(default=0)
    practical_hours = models.PositiveIntegerField(default=0)
    internal_marks_max = models.PositiveIntegerField(default=30)
    external_marks_max = models.PositiveIntegerField(default=70)
    total_marks_max = models.PositiveIntegerField(default=100)

    class Meta:
        db_table = 'academic_curriculum_subjects'
        unique_together = [('college', 'code')]
        ordering = ['semester_number', 'name']

    def clean(self):
        if self.program_id and self.college_id and self.program.college_id != self.college_id:
            raise ValidationError({'program': 'Program must belong to the same college.'})

    def __str__(self):
        return f'{self.code} — {self.name}'


class HolidayCalendar(TimeStampedModel):
    HOLIDAY_TYPES = [
        ('national', 'National'),
        ('state', 'State'),
        ('religious', 'Religious'),
        ('college', 'College'),
        ('exam', 'Exam'),
    ]
    APPLICABLE = [
        ('all', 'All'),
        ('students', 'Students'),
        ('staff', 'Staff'),
        ('specific_dept', 'Specific Department'),
    ]

    academic_year = models.ForeignKey(
        'colleges.AcademicYear',
        on_delete=models.CASCADE,
        related_name='holidays',
    )
    date = models.DateField(db_index=True)
    name = models.CharField(max_length=200)
    holiday_type = models.CharField(max_length=20, choices=HOLIDAY_TYPES, default='national')
    is_half_day = models.BooleanField(default=False)
    applicable_to = models.CharField(max_length=20, choices=APPLICABLE, default='all')
    departments = models.ManyToManyField('colleges.Department', blank=True, related_name='holidays')

    class Meta:
        db_table = 'academic_holidays'
        ordering = ['date']

    def __str__(self):
        return f'{self.date} — {self.name}'


class AcademicEvent(TimeStampedModel):
    EVENT_TYPES = [
        ('semester_start', 'Semester Start'),
        ('semester_end', 'Semester End'),
        ('exam_start', 'Exam Start'),
        ('exam_end', 'Exam End'),
        ('result_publish', 'Result Publish'),
        ('admission_start', 'Admission Start'),
        ('admission_end', 'Admission End'),
        ('convocation', 'Convocation'),
        ('annual_day', 'Annual Day'),
        ('sports_day', 'Sports Day'),
        ('other', 'Other'),
    ]

    academic_year = models.ForeignKey(
        'colleges.AcademicYear',
        on_delete=models.CASCADE,
        related_name='academic_events',
    )
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    event_type = models.CharField(max_length=30, choices=EVENT_TYPES, default='other')
    start_date = models.DateField()
    end_date = models.DateField()
    is_all_day = models.BooleanField(default=True)
    applicable_departments = models.ManyToManyField(
        'colleges.Department',
        blank=True,
        related_name='academic_events',
    )
    created_by = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='academic_events_created',
    )

    class Meta:
        db_table = 'academic_events'
        ordering = ['start_date']

    def __str__(self):
        return self.title
