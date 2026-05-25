from django.db import transaction

from apps.core.responses import APIResponse
from apps.core.views import BaseAPIView

from .models import Attendance, AttendanceSummary
from .serializers import AttendanceSerializer, AttendanceSummarySerializer, AttendanceWriteSerializer


def _scope_attendance(queryset, user):
    role = user.role
    if role == 'SUPER_ADMIN':
        return queryset
    if role == 'TEACHER':
        return queryset.filter(teacher__user=user)
    if role == 'STUDENT':
        return queryset.filter(student__user=user)
    if role == 'PARENT':
        try:
            wards = user.parent_profile.wards.values_list('pk', flat=True)
        except Exception:
            return queryset.none()
        return queryset.filter(student_id__in=wards)
    if role in ('ADMIN', 'ACCOUNTANT', 'LIBRARIAN', 'SECURITY'):
        return queryset.filter(college=user.college)
    if role == 'HOD':
        return queryset.filter(college=user.college, subject__department=user.department)
    return queryset.none()


def _scope_attendance_summary(queryset, user):
    role = user.role
    if role == 'SUPER_ADMIN':
        return queryset
    if role == 'STUDENT':
        return queryset.filter(student__user=user)
    if role == 'PARENT':
        try:
            wards = user.parent_profile.wards.values_list('pk', flat=True)
        except Exception:
            return queryset.none()
        return queryset.filter(student_id__in=wards)
    if role == 'TEACHER':
        return queryset.filter(subject__department=user.department)
    if role in ('ADMIN', 'ACCOUNTANT', 'LIBRARIAN', 'SECURITY'):
        return queryset.filter(college=user.college)
    if role == 'HOD':
        return queryset.filter(college=user.college, subject__department=user.department)
    return queryset.none()


class AttendanceListView(BaseAPIView):
    allowed_roles = ['SUPER_ADMIN', 'ADMIN', 'HOD', 'TEACHER', 'STUDENT', 'PARENT']

    def get(self, request):
        queryset = Attendance.objects.filter(is_deleted=False).select_related(
            'student', 'subject', 'teacher'
        )
        queryset = _scope_attendance(queryset, request.user)

        student_id = request.query_params.get('student')
        subject_id = request.query_params.get('subject')
        date = request.query_params.get('date')
        status = request.query_params.get('status')

        if student_id:
            queryset = queryset.filter(student_id=student_id)
        if subject_id:
            queryset = queryset.filter(subject_id=subject_id)
        if date:
            queryset = queryset.filter(date=date)
        if status:
            queryset = queryset.filter(status=status.upper())

        return APIResponse.paginated(queryset, AttendanceSerializer, request)

    def post(self, request):
        if request.user.role not in ('SUPER_ADMIN', 'ADMIN', 'HOD', 'TEACHER'):
            return APIResponse.error(message='Access denied.', status=403)

        rows = request.data
        if not isinstance(rows, list) or not rows:
            return APIResponse.error(message='Expected a non-empty JSON array of attendance rows.')

        errors = []
        created = 0

        with transaction.atomic():
            for index, row in enumerate(rows):
                serializer = AttendanceWriteSerializer(data=row)
                if not serializer.is_valid():
                    errors.append({'index': index, 'errors': serializer.errors})
                    continue

                validated = serializer.validated_data

                if request.user.role != 'SUPER_ADMIN':
                    college_id = validated['student'].college_id
                    if college_id != request.user.college_id:
                        errors.append({'index': index, 'errors': {'non_field_errors': ['College mismatch.']}})
                        continue
                    if request.user.role == 'TEACHER' and validated['teacher'].user_id != request.user.id:
                        errors.append({'index': index, 'errors': {'teacher': ['You may only mark your own attendance.']}})
                        continue

                Attendance.objects.update_or_create(
                    student=validated['student'],
                    subject=validated['subject'],
                    date=validated['date'],
                    period=validated['period'],
                    defaults={
                        'college': validated['college'],
                        'teacher': validated['teacher'],
                        'status': validated['status'],
                        'remarks': validated.get('remarks', ''),
                        'is_deleted': False,
                    },
                )
                created += 1

        if created == 0:
            return APIResponse.error(message='Validation failed.', errors=errors, status=400)

        return APIResponse.success(
            data={'created_or_updated': created, 'failed_rows': errors},
            message='Attendance processed.',
            status=201,
        )


class AttendanceSummaryView(BaseAPIView):
    allowed_roles = ['SUPER_ADMIN', 'ADMIN', 'HOD', 'TEACHER', 'STUDENT', 'PARENT']

    def get(self, request):
        queryset = AttendanceSummary.objects.filter(is_deleted=False).select_related(
            'student', 'subject', 'academic_year'
        )
        queryset = _scope_attendance_summary(queryset, request.user)

        student_id = request.query_params.get('student')
        subject_id = request.query_params.get('subject')

        if student_id:
            queryset = queryset.filter(student_id=student_id)
        if subject_id:
            queryset = queryset.filter(subject_id=subject_id)

        return APIResponse.paginated(queryset, AttendanceSummarySerializer, request)


class AttendanceMonthlyStatsView(BaseAPIView):
    allowed_roles = ['SUPER_ADMIN', 'ADMIN', 'HOD', 'TEACHER', 'STUDENT', 'PARENT']

    def get(self, request):
        import uuid
        from django.db.models import Count, Q

        student_id = request.query_params.get('student')
        subject_id = request.query_params.get('subject')
        year = request.query_params.get('year')
        month = request.query_params.get('month')

        if not student_id:
            return APIResponse.error(message='student param required.', status=400)

        try:
            uuid.UUID(str(student_id))
        except ValueError:
            return APIResponse.error(message='Invalid student UUID.', status=400)

        queryset = Attendance.objects.filter(
            student_id=student_id,
            is_deleted=False,
        )
        queryset = _scope_attendance(queryset, request.user)

        if subject_id:
            queryset = queryset.filter(subject_id=subject_id)
        if year:
            queryset = queryset.filter(date__year=year)
        if month:
            queryset = queryset.filter(date__month=month)

        stats = queryset.aggregate(
            total=Count('id'),
            present=Count('id', filter=Q(status='PRESENT')),
            absent=Count('id', filter=Q(status='ABSENT')),
            late=Count('id', filter=Q(status='LATE')),
            excused=Count('id', filter=Q(status='EXCUSED')),
        )

        total = stats['total'] or 0
        present = stats['present'] or 0
        stats['percentage'] = round((present / total) * 100, 2) if total > 0 else 0.00
        stats['is_low'] = stats['percentage'] < 75

        return APIResponse.success(data=stats)


class AttendanceAlertView(BaseAPIView):
    allowed_roles = ['SUPER_ADMIN', 'ADMIN', 'HOD', 'TEACHER']

    def get(self, request):
        queryset = AttendanceSummary.objects.filter(
            is_deleted=False,
            percentage__lt=75,
        ).select_related('student', 'subject', 'academic_year')

        queryset = _scope_attendance_summary(queryset, request.user)

        subject_id = request.query_params.get('subject')
        if subject_id:
            queryset = queryset.filter(subject_id=subject_id)

        return APIResponse.paginated(queryset, AttendanceSummarySerializer, request)
