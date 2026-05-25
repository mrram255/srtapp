from django.db import models

from apps.core.models import CollegeScopedModel


def default_empty_list():
    return []


class MessMenu(CollegeScopedModel):
    DAYS = [
        ('MONDAY', 'Monday'),
        ('TUESDAY', 'Tuesday'),
        ('WEDNESDAY', 'Wednesday'),
        ('THURSDAY', 'Thursday'),
        ('FRIDAY', 'Friday'),
        ('SATURDAY', 'Saturday'),
        ('SUNDAY', 'Sunday'),
    ]

    MEAL_TYPES = [
        ('BREAKFAST', 'Breakfast'),
        ('LUNCH', 'Lunch'),
        ('SNACKS', 'Snacks'),
        ('DINNER', 'Dinner'),
    ]

    day = models.CharField(max_length=10, choices=DAYS)
    meal_type = models.CharField(max_length=10, choices=MEAL_TYPES)
    items = models.JSONField(default=default_empty_list)
    special_items = models.JSONField(default=default_empty_list, blank=True)
    calories_estimate = models.PositiveIntegerField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'mess_menus'
        unique_together = [['college', 'day', 'meal_type']]
        ordering = ['day', 'meal_type']

    def __str__(self):
        return f'{self.day} {self.meal_type}'


class MessFeedback(CollegeScopedModel):
    RATING_CHOICES = [(i, str(i)) for i in range(1, 6)]

    student = models.ForeignKey('students.Student', on_delete=models.CASCADE, related_name='mess_feedbacks')
    menu = models.ForeignKey(MessMenu, on_delete=models.CASCADE, related_name='feedbacks')
    rating = models.PositiveIntegerField(choices=RATING_CHOICES)
    comment = models.TextField(blank=True)
    date = models.DateField()

    class Meta:
        db_table = 'mess_feedbacks'
        ordering = ['-date']

    def __str__(self):
        return f'{self.student.enrollment_number} - {self.rating}/5'
