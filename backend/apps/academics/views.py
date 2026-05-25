from django.utils import timezone

from apps.core.responses import APIResponse
from apps.core.views import BaseAPIView
from apps.students.models import Student
from .models import Course, Subject, Timetable
from .serializers import CourseSerializer, SubjectSerializer, TimetableSerializer, TimetableWriteSerializer


def _scope_academic_queryset(queryset, request):
    user = request.user
    if user.role == 'SUPER_ADMIN':
        return queryset
    if not getattr(user, 'college_id', None):
        return queryset.none()
    qs = queryset.filter(college=user.college)
    if user.role == 'HOD' and getattr(user, 'department_id', None):
        model = queryset.model
        if model is Subject:
            qs = qs.filter(department_id=user.department_id)
        elif model is Timetable:
            qs = qs.filter(department_id=user.department_id)
        elif model is Course:
            qs = qs.filter(subjects__department_id=user.department_id).distinct()
    return qs


def _apply_student_timetable_scope(queryset, user):
    if user.role == 'STUDENT':
        try:
            sp = user.student_profile
        except Student.DoesNotExist:
            return queryset.none()
        queryset = queryset.filter(
            college_id=sp.college_id,
            semester=sp.semester,
            section__iexact=sp.section,
        )
        if sp.academic_year_id:
            queryset = queryset.filter(academic_year_id=sp.academic_year_id)
    elif user.role == 'TEACHER':
        queryset = queryset.filter(teacher__user=user)
    return queryset


class CourseListView(BaseAPIView):
    allowed_roles = ['SUPER_ADMIN', 'ADMIN', 'HOD', 'TEACHER', 'STUDENT']

    def get(self, request):
        queryset = Course.objects.filter(is_deleted=False, is_active=True)
        queryset = _scope_academic_queryset(queryset, request)
        return APIResponse.paginated(queryset, CourseSerializer, request)


class SubjectListView(BaseAPIView):
    allowed_roles = ['SUPER_ADMIN', 'ADMIN', 'HOD', 'TEACHER', 'STUDENT']

    def get(self, request):
        queryset = Subject.objects.filter(is_deleted=False, is_active=True).select_related(
            'course', 'department'
        )
        queryset = _scope_academic_queryset(queryset, request)
        semester = request.query_params.get('semester')
        department = request.query_params.get('department')
        if semester:
            queryset = queryset.filter(semester=semester)
        if department:
            queryset = queryset.filter(department_id=department)
        return APIResponse.paginated(queryset, SubjectSerializer, request)


class TimetableListView(BaseAPIView):
    allowed_roles = ['SUPER_ADMIN', 'ADMIN', 'HOD', 'TEACHER', 'STUDENT']

    def get(self, request):
        queryset = Timetable.objects.filter(is_deleted=False, is_active=True).select_related(
            'subject', 'teacher', 'teacher__user', 'department', 'academic_year',
        )
        queryset = _scope_academic_queryset(queryset, request)
        queryset = _apply_student_timetable_scope(queryset, request.user)

        day = request.query_params.get('day')
        semester = request.query_params.get('semester')
        section = request.query_params.get('section')
        teacher_id = request.query_params.get('teacher')

        if day:
            queryset = queryset.filter(day=day.upper())
        if semester:
            queryset = queryset.filter(semester=semester)
        if section:
            queryset = queryset.filter(section__iexact=section)
        if teacher_id:
            queryset = queryset.filter(teacher_id=teacher_id)

        return APIResponse.paginated(queryset, TimetableSerializer, request)

    def post(self, request):
        if request.user.role not in ('SUPER_ADMIN', 'ADMIN', 'HOD'):
            return APIResponse.error(message='Access denied.', status=403)

        serializer = TimetableWriteSerializer(data=request.data)
        if not serializer.is_valid():
            return APIResponse.error(message='Invalid input.', errors=serializer.errors)

        validated = serializer.validated_data
        if request.user.role != 'SUPER_ADMIN':
            if validated['subject'].college_id != request.user.college_id:
                return APIResponse.error(message='College mismatch.', status=403)

        entry = serializer.save(college=validated['subject'].college)
        return APIResponse.success(
            data=TimetableSerializer(entry).data,
            message='Timetable entry created.',
            status=201,
        )


class TimetableDetailView(BaseAPIView):
    allowed_roles = ['SUPER_ADMIN', 'ADMIN', 'HOD']

    def _get_entry(self, pk, user):
        try:
            entry = Timetable.objects.get(pk=pk, is_deleted=False)
        except Timetable.DoesNotExist:
            return None
        if user.role != 'SUPER_ADMIN' and entry.college_id != user.college_id:
            return None
        return entry

    def put(self, request, pk):
        entry = self._get_entry(pk, request.user)
        if not entry:
            return APIResponse.error(message='Not found.', status=404)

        serializer = TimetableWriteSerializer(entry, data=request.data, partial=True)
        if not serializer.is_valid():
            return APIResponse.error(message='Invalid input.', errors=serializer.errors)

        updated = serializer.save()
        return APIResponse.success(
            data=TimetableSerializer(updated).data,
            message='Timetable entry updated.',
        )

    def delete(self, request, pk):
        entry = self._get_entry(pk, request.user)
        if not entry:
            return APIResponse.error(message='Not found.', status=404)

        entry.is_deleted = True
        entry.save(update_fields=['is_deleted'])
        return APIResponse.success(message='Timetable entry deleted.')


class TimetableTodayView(BaseAPIView):
    allowed_roles = ['SUPER_ADMIN', 'ADMIN', 'HOD', 'TEACHER', 'STUDENT']

    def get(self, request):
        today = timezone.localdate().strftime('%A').upper()

        queryset = Timetable.objects.filter(
            is_deleted=False,
            is_active=True,
            day=today,
        ).select_related('subject', 'teacher', 'teacher__user', 'department', 'academic_year')

        queryset = _scope_academic_queryset(queryset, request)
        queryset = _apply_student_timetable_scope(queryset, request.user)
        queryset = queryset.order_by('start_time')

        return APIResponse.success(data=TimetableSerializer(queryset, many=True).data)


class TimetableWeekView(BaseAPIView):
    allowed_roles = ['SUPER_ADMIN', 'ADMIN', 'HOD', 'TEACHER', 'STUDENT']

    DAYS_ORDER = ['MONDAY', 'TUESDAY', 'WEDNESDAY', 'THURSDAY', 'FRIDAY', 'SATURDAY']

    def get(self, request):
        queryset = Timetable.objects.filter(
            is_deleted=False,
            is_active=True,
        ).select_related('subject', 'teacher', 'teacher__user', 'department', 'academic_year')

        queryset = _scope_academic_queryset(queryset, request)
        queryset = _apply_student_timetable_scope(queryset, request.user)
        queryset = queryset.order_by('start_time')

        week = {day: [] for day in self.DAYS_ORDER}
        for entry in queryset:
            if entry.day in week:
                week[entry.day].append(TimetableSerializer(entry).data)

        return APIResponse.success(data=week)
