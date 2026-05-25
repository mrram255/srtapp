from django.core.exceptions import ValidationError
from django.db import models

from apps.core.models import CollegeScopedModel


class Course(CollegeScopedModel):
    name = models.CharField(max_length=200)
    code = models.CharField(max_length=20, db_index=True)
    description = models.TextField(blank=True)
    credits = models.PositiveIntegerField(default=3)
    duration_hours = models.PositiveIntegerField(default=45)
    is_active = models.BooleanField(default=True, db_index=True)

    class Meta:
        db_table = 'courses'
        unique_together = [['college', 'code']]
        ordering = ['name']

    def __str__(self):
        return f'{self.name} ({self.code})'


class Subject(CollegeScopedModel):
    name = models.CharField(max_length=200)
    code = models.CharField(max_length=20, db_index=True)
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='subjects',
    )
    department = models.ForeignKey(
        'colleges.Department',
        on_delete=models.CASCADE,
        related_name='subjects',
    )
    semester = models.PositiveIntegerField()
    credits = models.PositiveIntegerField(default=3)
    theory_hours = models.PositiveIntegerField(default=3)
    practical_hours = models.PositiveIntegerField(default=1)
    is_active = models.BooleanField(default=True, db_index=True)

    class Meta:
        db_table = 'subjects'
        unique_together = [['college', 'code']]
        ordering = ['semester', 'name']

    def clean(self):
        super().clean()
        if self.department_id and self.college_id and self.department.college_id != self.college_id:
            raise ValidationError({'department': 'Department must belong to the selected college.'})
        if self.course_id and self.college_id and self.course.college_id != self.college_id:
            raise ValidationError({'course': 'Course must belong to the selected college.'})

    def __str__(self):
        return f'{self.name} (Sem {self.semester})'


class Timetable(CollegeScopedModel):
    DAYS = [
        ('MONDAY', 'Monday'),
        ('TUESDAY', 'Tuesday'),
        ('WEDNESDAY', 'Wednesday'),
        ('THURSDAY', 'Thursday'),
        ('FRIDAY', 'Friday'),
        ('SATURDAY', 'Saturday'),
    ]

    subject = models.ForeignKey(
        Subject,
        on_delete=models.CASCADE,
        related_name='timetable_entries',
    )
    teacher = models.ForeignKey(
        'teachers.Teacher',
        on_delete=models.CASCADE,
        related_name='timetable_entries',
    )
    department = models.ForeignKey(
        'colleges.Department',
        on_delete=models.CASCADE,
        related_name='timetable_entries',
    )
    semester = models.PositiveIntegerField()
    section = models.CharField(max_length=10)
    day = models.CharField(max_length=10, choices=DAYS)
    start_time = models.TimeField()
    end_time = models.TimeField()
    room_number = models.CharField(max_length=50)
    academic_year = models.ForeignKey(
        'colleges.AcademicYear',
        on_delete=models.CASCADE,
        related_name='timetable_entries',
    )
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'timetables'
        ordering = ['day', 'start_time']

    def clean(self):
        super().clean()
        if self.subject_id and self.college_id and self.subject.college_id != self.college_id:
            raise ValidationError({'subject': 'Subject must belong to the same college.'})
        if self.teacher_id and self.college_id and self.teacher.college_id != self.college_id:
            raise ValidationError({'teacher': 'Teacher must belong to the same college.'})
        if self.department_id and self.subject_id and self.subject.department_id != self.department_id:
            raise ValidationError({'department': 'Department must match the subject department.'})
        if self.academic_year_id and self.college_id and self.academic_year.college_id != self.college_id:
            raise ValidationError({'academic_year': 'Academic year must belong to the same college.'})

    def __str__(self):
        return f'{self.subject.name} — {self.day} {self.start_time}'
