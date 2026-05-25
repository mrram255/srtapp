from decimal import Decimal

from django.db import models

from apps.core.models import CollegeScopedModel


class ExamSchedule(CollegeScopedModel):
    EXAM_TYPES = [
        ('INTERNAL_1', 'Internal Assessment 1'),
        ('INTERNAL_2', 'Internal Assessment 2'),
        ('INTERNAL_3', 'Internal Assessment 3'),
        ('SEMESTER', 'Semester Exam'),
        ('PRACTICAL', 'Practical Exam'),
        ('VIVA', 'Viva Voce'),
        ('QUIZ', 'Quiz'),
    ]

    name = models.CharField(max_length=255)
    exam_type = models.CharField(max_length=15, choices=EXAM_TYPES)
    subject = models.ForeignKey(
        'academics.Subject',
        on_delete=models.CASCADE,
        related_name='exam_schedules',
    )
    department = models.ForeignKey(
        'colleges.Department',
        on_delete=models.CASCADE,
        related_name='exam_schedules',
    )
    semester = models.PositiveIntegerField()
    section = models.CharField(max_length=10, blank=True)
    exam_date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    duration_minutes = models.PositiveIntegerField(default=180)
    room_number = models.CharField(max_length=50, blank=True)
    max_marks = models.PositiveIntegerField(default=100)
    passing_marks = models.PositiveIntegerField(default=40)
    instructions = models.TextField(blank=True)
    is_active = models.BooleanField(default=True, db_index=True)

    class Meta:
        db_table = 'exam_schedules'
        ordering = ['exam_date', 'start_time']

    def __str__(self):
        return f'{self.name} — {self.subject.name} ({self.exam_date})'


class ExamResult(CollegeScopedModel):
    exam = models.ForeignKey(
        ExamSchedule,
        on_delete=models.CASCADE,
        related_name='results',
    )
    student = models.ForeignKey(
        'students.Student',
        on_delete=models.CASCADE,
        related_name='exam_results',
    )
    marks_obtained = models.DecimalField(max_digits=6, decimal_places=2)
    grade = models.CharField(max_length=5, blank=True)
    percentage = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    status = models.CharField(
        max_length=10,
        choices=[
            ('PASS', 'Pass'),
            ('FAIL', 'Fail'),
            ('ABSENT', 'Absent'),
            ('PENDING', 'Pending'),
        ],
        default='PENDING',
    )
    remarks = models.TextField(blank=True)
    evaluated_by = models.ForeignKey(
        'teachers.Teacher',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='evaluated_results',
    )
    evaluated_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'exam_results'
        unique_together = [['exam', 'student']]
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.student.enrollment_number} — {self.exam.name} — {self.marks_obtained}'

    def save(self, *args, **kwargs):
        if self.status != 'ABSENT' and self.marks_obtained is not None and self.exam_id:
            exam = self.exam
            if exam.max_marks > 0:
                self.percentage = (self.marks_obtained / Decimal(exam.max_marks)) * Decimal('100')
                if self.status == 'PENDING':
                    pm = Decimal(exam.passing_marks)
                    self.status = 'PASS' if self.percentage >= pm else 'FAIL'
        super().save(*args, **kwargs)


class MCQQuestion(CollegeScopedModel):
    """MCQ Question bank."""
    exam = models.ForeignKey(
        ExamSchedule,
        on_delete=models.CASCADE,
        related_name='questions',
    )
    question_text = models.TextField()
    option_a = models.CharField(max_length=500)
    option_b = models.CharField(max_length=500)
    option_c = models.CharField(max_length=500)
    option_d = models.CharField(max_length=500)
    correct_option = models.CharField(
        max_length=1,
        choices=[('A', 'A'), ('B', 'B'), ('C', 'C'), ('D', 'D')],
    )
    marks = models.PositiveIntegerField(default=1)
    negative_marks = models.DecimalField(max_digits=4, decimal_places=2, default=0)
    order = models.PositiveIntegerField(default=0)
    explanation = models.TextField(blank=True)

    class Meta:
        db_table = 'mcq_questions'
        ordering = ['order', 'id']

    def __str__(self):
        return f'Q{self.order}: {self.question_text[:60]}'


class ExamAttempt(CollegeScopedModel):
    """Tracks student exam session."""
    STATUS_CHOICES = [
        ('IN_PROGRESS', 'In Progress'),
        ('SUBMITTED', 'Submitted'),
        ('TIMED_OUT', 'Timed Out'),
        ('DISQUALIFIED', 'Disqualified'),
    ]

    exam = models.ForeignKey(
        ExamSchedule,
        on_delete=models.CASCADE,
        related_name='attempts',
    )
    student = models.ForeignKey(
        'students.Student',
        on_delete=models.CASCADE,
        related_name='exam_attempts',
    )
    started_at = models.DateTimeField(auto_now_add=True)
    submitted_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='IN_PROGRESS')
    tab_switch_count = models.PositiveIntegerField(default=0)
    question_order = models.JSONField(default=list)  # shuffled question IDs

    class Meta:
        db_table = 'exam_attempts'
        unique_together = [['exam', 'student']]
        ordering = ['-started_at']

    def __str__(self):
        return f'{self.student.enrollment_number} — {self.exam.name} — {self.status}'


class StudentAnswer(CollegeScopedModel):
    """Student answer for each MCQ question."""
    attempt = models.ForeignKey(
        ExamAttempt,
        on_delete=models.CASCADE,
        related_name='answers',
    )
    question = models.ForeignKey(
        MCQQuestion,
        on_delete=models.CASCADE,
        related_name='student_answers',
    )
    selected_option = models.CharField(
        max_length=1,
        choices=[('A', 'A'), ('B', 'B'), ('C', 'C'), ('D', 'D')],
        null=True,
        blank=True,
    )
    is_correct = models.BooleanField(null=True, blank=True)
    marks_awarded = models.DecimalField(max_digits=5, decimal_places=2, default=0)

    class Meta:
        db_table = 'student_answers'
        unique_together = [['attempt', 'question']]

    def save(self, *args, **kwargs):
        if self.selected_option and self.question_id:
            self.is_correct = self.selected_option == self.question.correct_option
            if self.is_correct:
                self.marks_awarded = self.question.marks
            elif self.selected_option and not self.is_correct:
                self.marks_awarded = -self.question.negative_marks
            else:
                self.marks_awarded = 0
        super().save(*args, **kwargs)


class AdmitCard(CollegeScopedModel):
    """Student admit card for exam."""
    exam = models.ForeignKey(
        ExamSchedule,
        on_delete=models.CASCADE,
        related_name='admit_cards',
    )
    student = models.ForeignKey(
        'students.Student',
        on_delete=models.CASCADE,
        related_name='admit_cards',
    )
    roll_number = models.CharField(max_length=50)
    seat_number = models.CharField(max_length=50, blank=True)
    is_issued = models.BooleanField(default=False)
    issued_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'admit_cards'
        unique_together = [['exam', 'student']]

    def __str__(self):
        return f'{self.student.enrollment_number} — {self.exam.name}'
