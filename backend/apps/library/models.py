from django.db import models

from apps.core.models import CollegeScopedModel


class Book(CollegeScopedModel):
    title = models.CharField(max_length=500)
    author = models.CharField(max_length=255)
    isbn = models.CharField(max_length=20, db_index=True)
    publisher = models.CharField(max_length=255, blank=True)
    publication_year = models.PositiveIntegerField(null=True, blank=True)
    edition = models.CharField(max_length=50, blank=True)
    category = models.CharField(max_length=100, blank=True)
    subject = models.ForeignKey(
        'academics.Subject',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='books',
    )
    description = models.TextField(blank=True)
    total_copies = models.PositiveIntegerField(default=1)
    available_copies = models.PositiveIntegerField(default=1)
    shelf_location = models.CharField(max_length=50, blank=True)
    cover_image = models.CharField(max_length=500, blank=True)
    is_active = models.BooleanField(default=True, db_index=True)

    class Meta:
        db_table = 'books'
        ordering = ['title']

    def __str__(self):
        return f'{self.title} by {self.author}'


class BookBorrowing(CollegeScopedModel):
    STATUS_CHOICES = [
        ('BORROWED', 'Borrowed'),
        ('RETURNED', 'Returned'),
        ('OVERDUE', 'Overdue'),
        ('LOST', 'Lost'),
        ('DAMAGED', 'Damaged'),
    ]

    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='borrowings')
    student = models.ForeignKey(
        'students.Student',
        on_delete=models.CASCADE,
        related_name='book_borrowings',
    )
    borrowed_date = models.DateField()
    due_date = models.DateField()
    returned_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='BORROWED')
    fine_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    remarks = models.TextField(blank=True)
    issued_by = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='+',
    )

    class Meta:
        db_table = 'book_borrowings'
        ordering = ['-borrowed_date']

    def __str__(self):
        return f'{self.student.enrollment_number} — {self.book.title}'
