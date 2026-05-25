import importlib

from django.utils import timezone

from apps.core.responses import APIResponse
from apps.core.views import BaseAPIView

from .models import Teacher, TeacherSubjectAssignment
from .serializers import (
    TeacherCreateSerializer,
    TeacherDashboardSerializer,
    TeacherSerializer,
    TeacherSubjectAssignmentSerializer,
)


def _teacher_dashboard_metrics(teacher):
    today_classes = 0
    pending_attendance = 0
    pending_assignments = 0
    total_students = 0
    recent_notifications = []

    try:
        acad = importlib.import_module('apps.academics.models')
        Timetable = getattr(acad, 'Timetable', None)
        if Timetable is not None:
            day = timezone.now().strftime('%A').upper()
            today_classes = Timetable.objects.filter(teacher=teacher, day=day, is_deleted=False).count()
    except Exception:
        pass

    try:
        attendance_mod = importlib.import_module('apps.attendance.models')
        Attendance = getattr(attendance_mod, 'Attendance', None)
        if Attendance is not None:
            pending_attendance = 0
    except Exception:
        pass

    try:
        assignments_mod = importlib.import_module('apps.assignments.models')
        AssignmentSubmission = getattr(assignments_mod, 'AssignmentSubmission', None)
        if AssignmentSubmission is not None:
            pending_assignments = AssignmentSubmission.objects.filter(
                assignment__teacher=teacher,
                status='SUBMITTED',
            ).count()
    except Exception:
        pass

    try:
        from apps.students.models import Student

        total_students = Student.objects.filter(
            college=teacher.college,
            is_deleted=False,
            is_active=True,
        ).count()
    except Exception:
        pass

    try:
        notifications_mod = importlib.import_module('apps.notifications.models')
        Notification = getattr(notifications_mod, 'Notification', None)
        if Notification is not None:
            qs = Notification.objects.filter(college=teacher.college).order_by('-created_at')[:5]
            recent_notifications = [
                {
                    'title': getattr(n, 'title', ''),
                    'message': getattr(n, 'message', ''),
                    'created_at': n.created_at.isoformat(),
                }
                for n in qs
            ]
    except Exception:
        pass

    return today_classes, pending_attendance, pending_assignments, total_students, recent_notifications


class TeacherListView(BaseAPIView):
    allowed_roles = ['SUPER_ADMIN', 'ADMIN', 'HOD']

    def get(self, request):
        queryset = Teacher.objects.filter(is_deleted=False).select_related('user', 'college', 'department')

        role = request.user.role
        if role == 'SUPER_ADMIN':
            pass
        elif role == 'ADMIN':
            queryset = queryset.filter(college=request.user.college)
        elif role == 'HOD':
            queryset = queryset.filter(college=request.user.college, department=request.user.department)
        else:
            queryset = queryset.none()

        department = request.query_params.get('department')
        designation = request.query_params.get('designation')
        is_active = request.query_params.get('is_active')

        if department:
            queryset = queryset.filter(department_id=department)
        if designation:
            queryset = queryset.filter(designation=designation)
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')

        return APIResponse.paginated(queryset, TeacherSerializer, request)

    def post(self, request):
        serializer = TeacherCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return APIResponse.error(message='Invalid input.', errors=serializer.errors)

        dept = serializer.validated_data['department']
        if request.user.role != 'SUPER_ADMIN':
            if request.user.college_id != dept.college_id:
                return APIResponse.error(message='Invalid department for your college.', status=403)

        teacher = serializer.save()
        return APIResponse.success(
            data=TeacherSerializer(teacher).data,
            message='Teacher created successfully.',
            status=201,
        )


class TeacherDetailView(BaseAPIView):
    allowed_roles = ['SUPER_ADMIN', 'ADMIN', 'HOD', 'TEACHER']

    def get(self, request, pk):
        try:
            teacher = Teacher.objects.select_related('user', 'college', 'department').get(id=pk, is_deleted=False)
        except Teacher.DoesNotExist:
            return APIResponse.error(message='Teacher not found.', status=404)

        if request.user.role == 'TEACHER' and teacher.user_id != request.user.id:
            return APIResponse.error(message='Access denied.', status=403)
        if request.user.role in ('ADMIN', 'HOD') and teacher.college_id != request.user.college_id:
            return APIResponse.error(message='Access denied.', status=403)

        return APIResponse.success(data=TeacherSerializer(teacher).data)

    def patch(self, request, pk):
        try:
            teacher = Teacher.objects.get(id=pk, is_deleted=False)
        except Teacher.DoesNotExist:
            return APIResponse.error(message='Teacher not found.', status=404)

        if request.user.role not in ('SUPER_ADMIN', 'ADMIN', 'HOD'):
            return APIResponse.error(message='Access denied.', status=403)
        if request.user.role in ('ADMIN', 'HOD') and teacher.college_id != request.user.college_id:
            return APIResponse.error(message='Access denied.', status=403)

        serializer = TeacherSerializer(teacher, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return APIResponse.success(data=serializer.data, message='Teacher updated successfully.')
        return APIResponse.error(message='Invalid input.', errors=serializer.errors)


class TeacherDashboardView(BaseAPIView):
    allowed_roles = ['TEACHER']

    def get(self, request):
        try:
            teacher = Teacher.objects.select_related('department').get(user=request.user, is_deleted=False)
        except Teacher.DoesNotExist:
            return APIResponse.error(message='Teacher profile not found.', status=404)

        (
            today_classes,
            pending_attendance,
            pending_assignments,
            total_students,
            recent_notifications,
        ) = _teacher_dashboard_metrics(teacher)

        dashboard_data = {
            'teacher_id': teacher.id,
            'name': teacher.full_name,
            'employee_id': teacher.employee_id,
            'department': teacher.department.name,
            'designation': teacher.designation,
            'today_classes': today_classes,
            'pending_attendance': pending_attendance,
            'pending_assignments': pending_assignments,
            'total_students': total_students,
            'recent_notifications': recent_notifications,
        }

        serializer = TeacherDashboardSerializer(data=dashboard_data)
        serializer.is_valid(raise_exception=True)
        return APIResponse.success(data=serializer.validated_data)


class TeacherSubjectAssignmentListView(BaseAPIView):
    allowed_roles = ['SUPER_ADMIN', 'ADMIN', 'HOD', 'TEACHER']

    def get(self, request):
        queryset = TeacherSubjectAssignment.objects.filter(is_deleted=False).select_related(
            'teacher',
            'teacher__user',
            'subject',
            'academic_year',
            'college',
        )

        role = request.user.role
        if role == 'SUPER_ADMIN':
            pass
        elif role == 'ADMIN':
            queryset = queryset.filter(college=request.user.college)
        elif role == 'HOD':
            queryset = queryset.filter(college=request.user.college, teacher__department=request.user.department)
        elif role == 'TEACHER':
            queryset = queryset.filter(teacher__user=request.user)
        else:
            queryset = queryset.none()

        teacher_id = request.query_params.get('teacher')
        subject_id = request.query_params.get('subject')
        semester = request.query_params.get('semester')

        if teacher_id:
            queryset = queryset.filter(teacher_id=teacher_id)
        if subject_id:
            queryset = queryset.filter(subject_id=subject_id)
        if semester:
            queryset = queryset.filter(semester=semester)

        return APIResponse.paginated(queryset, TeacherSubjectAssignmentSerializer, request)

    def post(self, request):
        if request.user.role == 'TEACHER':
            return APIResponse.error(message='Access denied.', status=403)

        serializer = TeacherSubjectAssignmentSerializer(data=request.data)
        if not serializer.is_valid():
            return APIResponse.error(message='Invalid input.', errors=serializer.errors)

        teacher = serializer.validated_data['teacher']
        if request.user.role != 'SUPER_ADMIN':
            if teacher.college_id != request.user.college_id:
                return APIResponse.error(message='Access denied.', status=403)
            if request.user.role == 'HOD' and teacher.department_id != request.user.department_id:
                return APIResponse.error(message='Access denied.', status=403)

        assignment = serializer.save(college=teacher.college)
        return APIResponse.success(
            data=TeacherSubjectAssignmentSerializer(assignment).data,
            message='Subject assigned successfully.',
            status=201,
        )
