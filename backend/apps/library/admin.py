from django.contrib import admin

from .models import Book, BookBorrowing


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'isbn', 'available_copies', 'total_copies', 'is_active']
    search_fields = ['title', 'author', 'isbn']
    raw_id_fields = ['college', 'subject']


@admin.register(BookBorrowing)
class BookBorrowingAdmin(admin.ModelAdmin):
    list_display = ['book', 'student', 'borrowed_date', 'due_date', 'status']
    list_filter = ['status']
    raw_id_fields = ['college', 'book', 'student', 'issued_by']
