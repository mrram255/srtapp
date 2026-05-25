from django.db.models import Q

from apps.core.responses import APIResponse
from apps.core.views import BaseAPIView

from .models import Book, BookBorrowing
from .serializers import (
    BookBorrowingSerializer,
    BookBorrowingWriteSerializer,
    BookSerializer,
    BookWriteSerializer,
)


def _scope_books(queryset, user):
    role = user.role
    if role == 'SUPER_ADMIN':
        return queryset
    if not getattr(user, 'college_id', None):
        return queryset.none()
    return queryset.filter(college=user.college)


def _scope_borrowings(queryset, user):
    role = user.role
    if role == 'SUPER_ADMIN':
        return queryset
    if role == 'STUDENT':
        return queryset.filter(student__user=user)
    if role in ('ADMIN', 'LIBRARIAN'):
        return queryset.filter(college=user.college)
    return queryset.none()


class BookListView(BaseAPIView):
    allowed_roles = ['SUPER_ADMIN', 'ADMIN', 'LIBRARIAN', 'TEACHER', 'STUDENT']

    def get(self, request):
        queryset = Book.objects.filter(is_deleted=False, is_active=True).select_related('subject')
        queryset = _scope_books(queryset, request.user)

        search = request.query_params.get('search')
        category = request.query_params.get('category')
        subject_id = request.query_params.get('subject')
        available = request.query_params.get('available')

        if search:
            queryset = queryset.filter(Q(title__icontains=search) | Q(author__icontains=search))
        if category:
            queryset = queryset.filter(category__iexact=category)
        if subject_id:
            queryset = queryset.filter(subject_id=subject_id)
        if available and available.lower() == 'true':
            queryset = queryset.filter(available_copies__gt=0)

        return APIResponse.paginated(queryset, BookSerializer, request)

    def post(self, request):
        if request.user.role not in ('SUPER_ADMIN', 'ADMIN', 'LIBRARIAN'):
            return APIResponse.error(message='Access denied.', status=403)

        serializer = BookWriteSerializer(data=request.data, context={'request': request})
        if not serializer.is_valid():
            return APIResponse.error(message='Invalid input.', errors=serializer.errors)

        validated = serializer.validated_data
        if request.user.role != 'SUPER_ADMIN':
            if validated['college'].id != request.user.college_id:
                return APIResponse.error(message='Invalid college.', status=403)

        book = serializer.save()
        return APIResponse.success(data=BookSerializer(book).data, message='Book added.', status=201)


class BookBorrowingListView(BaseAPIView):
    allowed_roles = ['SUPER_ADMIN', 'ADMIN', 'LIBRARIAN', 'STUDENT']

    def get(self, request):
        queryset = BookBorrowing.objects.filter(is_deleted=False).select_related('book', 'student')
        queryset = _scope_borrowings(queryset, request.user)

        book_id = request.query_params.get('book')
        student_id = request.query_params.get('student')
        status = request.query_params.get('status')

        if book_id:
            queryset = queryset.filter(book_id=book_id)
        if student_id:
            queryset = queryset.filter(student_id=student_id)
        if status:
            queryset = queryset.filter(status=status.upper())

        return APIResponse.paginated(queryset, BookBorrowingSerializer, request)

    def post(self, request):
        if request.user.role not in ('SUPER_ADMIN', 'ADMIN', 'LIBRARIAN'):
            return APIResponse.error(message='Access denied.', status=403)

        serializer = BookBorrowingWriteSerializer(data=request.data, context={'request': request})
        if not serializer.is_valid():
            return APIResponse.error(message='Invalid input.', errors=serializer.errors)

        validated = serializer.validated_data
        if request.user.role != 'SUPER_ADMIN':
            if validated['student'].college_id != request.user.college_id:
                return APIResponse.error(message='Invalid student.', status=403)

        borrowing = serializer.save()
        return APIResponse.success(
            data=BookBorrowingSerializer(borrowing).data,
            message='Borrowing recorded.',
            status=201,
        )
