from rest_framework import serializers

from apps.colleges.models import College

from .models import Book, BookBorrowing


class BookSerializer(serializers.ModelSerializer):
    subject_name = serializers.CharField(source='subject.name', read_only=True)

    class Meta:
        model = Book
        fields = [
            'id',
            'college',
            'title',
            'author',
            'isbn',
            'publisher',
            'publication_year',
            'edition',
            'category',
            'subject',
            'subject_name',
            'description',
            'total_copies',
            'available_copies',
            'shelf_location',
            'cover_image',
            'is_active',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'college', 'available_copies', 'created_at', 'updated_at']


class BookWriteSerializer(serializers.ModelSerializer):
    college = serializers.PrimaryKeyRelatedField(queryset=College.objects.all(), required=False)

    class Meta:
        model = Book
        fields = [
            'college',
            'title',
            'author',
            'isbn',
            'publisher',
            'publication_year',
            'edition',
            'category',
            'subject',
            'description',
            'total_copies',
            'available_copies',
            'shelf_location',
            'cover_image',
            'is_active',
        ]

    def validate(self, attrs):
        request = self.context.get('request')
        user = getattr(request, 'user', None)
        subject = attrs.get('subject')

        if user and user.role != 'SUPER_ADMIN':
            attrs['college'] = user.college
        elif not attrs.get('college'):
            if subject is not None:
                attrs['college'] = subject.college
            else:
                raise serializers.ValidationError({'college': 'This field is required.'})

        college = attrs['college']
        if subject and subject.college_id != college.id:
            raise serializers.ValidationError({'subject': 'Subject must belong to the same college.'})

        total = attrs.get('total_copies', 1)
        avail = attrs.get('available_copies', total)
        if avail > total:
            attrs['available_copies'] = total
        return attrs


class BookBorrowingSerializer(serializers.ModelSerializer):
    book_title = serializers.CharField(source='book.title', read_only=True)
    student_enrollment = serializers.CharField(source='student.enrollment_number', read_only=True)

    class Meta:
        model = BookBorrowing
        fields = [
            'id',
            'college',
            'book',
            'book_title',
            'student',
            'student_enrollment',
            'borrowed_date',
            'due_date',
            'returned_date',
            'status',
            'fine_amount',
            'remarks',
            'issued_by',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'college', 'issued_by', 'created_at', 'updated_at']


class BookBorrowingWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = BookBorrowing
        fields = ['book', 'student', 'borrowed_date', 'due_date', 'remarks']

    def validate(self, attrs):
        book = attrs['book']
        student = attrs['student']
        if book.college_id != student.college_id:
            raise serializers.ValidationError('Book and student must belong to the same college.')
        if book.available_copies < 1:
            raise serializers.ValidationError({'book': 'No copies available.'})
        attrs['college'] = student.college
        return attrs

    def create(self, validated_data):
        request = self.context.get('request')
        user = getattr(request, 'user', None)
        validated_data['issued_by'] = user if user and user.is_authenticated else None
        borrowing = super().create(validated_data)
        book = borrowing.book
        book.available_copies = max(0, book.available_copies - 1)
        book.save(update_fields=['available_copies'])
        return borrowing
