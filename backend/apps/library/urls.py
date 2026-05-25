from django.urls import path

from .views import BookBorrowingListView, BookListView

urlpatterns = [
    path('books/', BookListView.as_view(), name='book_list'),
    path('borrowings/', BookBorrowingListView.as_view(), name='book_borrowing_list'),
]
