from django.utils import timezone
from rest_framework.permissions import AllowAny

from apps.core.responses import APIResponse
from apps.core.views import BaseAPIView

from .models import AdmissionApplication, AdmissionCycle, AdmissionInquiry, MeritList
from .serializers import (
    AdmissionApplicationSerializer,
    AdmissionApplicationWriteSerializer,
    AdmissionCycleSerializer,
    AdmissionInquirySerializer,
    MeritListSerializer,
)
from .services import AdmissionService


def _scope_admissions(queryset, user):
    if user.role == 'SUPER_ADMIN':
        return queryset
    if user.role in ('ADMIN',) and getattr(user, 'college_id', None):
        return queryset.filter(college_id=user.college_id)
    return queryset.none()


class AdmissionListView(BaseAPIView):
    allowed_roles = ['SUPER_ADMIN', 'ADMIN']

    def get(self, request):
        queryset = AdmissionApplication.objects.filter(is_deleted=False).select_related(
            'department',
            'branch',
        )
        queryset = _scope_admissions(queryset, request.user)

        status_param = request.query_params.get('status')
        department_id = request.query_params.get('department')

        if status_param:
            queryset = queryset.filter(status=status_param.upper())
        if department_id:
            queryset = queryset.filter(department_id=department_id)

        return APIResponse.paginated(queryset, AdmissionApplicationSerializer, request)

    def post(self, request):
        serializer = AdmissionApplicationWriteSerializer(data=request.data, context={'request': request})
        if not serializer.is_valid():
            return APIResponse.error(message='Invalid input.', errors=serializer.errors)

        app = serializer.save()
        return APIResponse.success(
            data=AdmissionApplicationSerializer(app).data,
            message='Application submitted.',
            status=201,
        )


class AdmissionDetailView(BaseAPIView):
    allowed_roles = ['SUPER_ADMIN', 'ADMIN']

    def get(self, request, pk):
        queryset = _scope_admissions(
            AdmissionApplication.objects.filter(pk=pk, is_deleted=False).select_related('department', 'branch'),
            request.user,
        )
        app = queryset.first()
        if not app:
            return APIResponse.error(message='Application not found.', status=404)
        return APIResponse.success(data=AdmissionApplicationSerializer(app).data)

    def patch(self, request, pk):
        queryset = _scope_admissions(AdmissionApplication.objects.filter(pk=pk, is_deleted=False), request.user)
        app = queryset.first()
        if not app:
            return APIResponse.error(message='Application not found.', status=404)
        serializer = AdmissionApplicationWriteSerializer(app, data=request.data, partial=True, context={'request': request})
        if not serializer.is_valid():
            return APIResponse.error(message='Invalid input.', errors=serializer.errors)
        app = serializer.save()
        if 'status' in request.data:
            app.reviewed_by = request.user
            app.reviewed_at = timezone.now()
            app.save(update_fields=['reviewed_by', 'reviewed_at'])
        return APIResponse.success(data=AdmissionApplicationSerializer(app).data)


class AdmissionEnrollView(BaseAPIView):
    allowed_roles = ['SUPER_ADMIN', 'ADMIN']

    def post(self, request, pk):
        queryset = _scope_admissions(AdmissionApplication.objects.filter(pk=pk, is_deleted=False), request.user)
        app = queryset.first()
        if not app:
            return APIResponse.error(message='Application not found.', status=404)
        if app.status == 'ENROLLED':
            return APIResponse.error(message='Already enrolled.', status=400)
        try:
            student = AdmissionService.enroll_application(app, enrolled_by=request.user)
        except ValueError as exc:
            return APIResponse.error(message=str(exc), status=400)
        return APIResponse.success(
            data={'student_id': str(student.id), 'enrollment_number': student.enrollment_number},
            message='Student enrolled.',
        )


class AdmissionCycleListView(BaseAPIView):
    allowed_roles = ['SUPER_ADMIN', 'ADMIN']

    def get(self, request):
        queryset = _scope_admissions(AdmissionCycle.objects.filter(is_deleted=False), request.user)
        return APIResponse.paginated(queryset, AdmissionCycleSerializer, request)

    def post(self, request):
        college = request.user.college
        if college is None:
            return APIResponse.error(message='College context required.', status=400)
        serializer = AdmissionCycleSerializer(data=request.data)
        if not serializer.is_valid():
            return APIResponse.error(message='Invalid input.', errors=serializer.errors)
        obj = serializer.save(college=college)
        return APIResponse.success(data=AdmissionCycleSerializer(obj).data, status=201)


class AdmissionInquiryListView(BaseAPIView):
    allowed_roles = ['SUPER_ADMIN', 'ADMIN']

    def get(self, request):
        queryset = _scope_admissions(AdmissionInquiry.objects.filter(is_deleted=False), request.user)
        status_param = request.query_params.get('status')
        if status_param:
            queryset = queryset.filter(status=status_param.lower())
        return APIResponse.paginated(queryset, AdmissionInquirySerializer, request)

    def post(self, request):
        college = request.user.college
        if college is None:
            return APIResponse.error(message='College context required.', status=400)
        serializer = AdmissionInquirySerializer(data=request.data)
        if not serializer.is_valid():
            return APIResponse.error(message='Invalid input.', errors=serializer.errors)
        obj = serializer.save(college=college, assigned_to=request.user)
        return APIResponse.success(data=AdmissionInquirySerializer(obj).data, status=201)


class PublicAdmissionApplyView(BaseAPIView):
    """Public application submission (no auth)."""

    permission_classes = [AllowAny]
    allowed_roles = []

    def post(self, request):
        import uuid

        from apps.colleges.models import Branch, College, Department

        college_id = request.data.get('college')
        if not college_id:
            return APIResponse.error(message='college is required.', status=400)

        college = College.objects.filter(pk=college_id, is_deleted=False).first()
        if not college:
            return APIResponse.error(message='Invalid college.', status=400)

        required = [
            'first_name', 'last_name', 'email', 'phone', 'date_of_birth',
            'gender', 'department', 'branch', 'previous_school', 'previous_percentage',
        ]
        missing = [f for f in required if not request.data.get(f)]
        if missing:
            return APIResponse.error(message=f'Missing fields: {", ".join(missing)}', status=400)

        from apps.colleges.models import Branch, Department

        dept = Department.objects.filter(pk=request.data['department'], college=college).first()
        branch = Branch.objects.filter(pk=request.data['branch'], college=college, department=dept).first()
        if not dept or not branch:
            return APIResponse.error(message='Invalid department or branch.', status=400)

        app = AdmissionApplication.objects.create(
            college=college,
            application_number=f'APP-{uuid.uuid4().hex[:12].upper()}',
            status='SUBMITTED',
            first_name=request.data['first_name'],
            last_name=request.data['last_name'],
            email=request.data['email'],
            phone=request.data['phone'],
            date_of_birth=request.data['date_of_birth'],
            gender=request.data['gender'],
            department=dept,
            branch=branch,
            previous_school=request.data['previous_school'],
            previous_percentage=request.data['previous_percentage'],
            entrance_exam_score=request.data.get('entrance_exam_score'),
        )
        return APIResponse.success(
            data={'application_number': app.application_number, 'id': str(app.id)},
            message='Application submitted.',
            status=201,
        )


class AdmissionKanbanView(BaseAPIView):
    allowed_roles = ['SUPER_ADMIN', 'ADMIN']

    def get(self, request):
        queryset = _scope_admissions(AdmissionApplication.objects.filter(is_deleted=False), request.user)
        columns = {status: [] for status, _ in AdmissionApplication.STATUS_CHOICES}
        for app in queryset.select_related('department', 'branch')[:500]:
            if app.status in columns:
                columns[app.status].append(AdmissionApplicationSerializer(app).data)
        return APIResponse.success(data=columns)


class MeritListView(BaseAPIView):
    allowed_roles = ['SUPER_ADMIN', 'ADMIN']

    def get(self, request):
        queryset = _scope_admissions(MeritList.objects.filter(is_deleted=False), request.user)
        return APIResponse.paginated(queryset, MeritListSerializer, request)
