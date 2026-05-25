from django.db import IntegrityError

from apps.core.responses import APIResponse
from apps.core.views import BaseAPIView

from .models import Company, JobPosting, PlacementApplication
from .serializers import (
    CompanySerializer,
    JobPostingSerializer,
    JobPostingWriteSerializer,
    PlacementApplicationSerializer,
    PlacementApplicationWriteSerializer,
)


def _scope_college_models(queryset, user):
    if user.role == 'SUPER_ADMIN':
        return queryset
    if getattr(user, 'college_id', None):
        return queryset.filter(college_id=user.college_id)
    return queryset.none()


def _scope_placement_applications(queryset, user):
    if user.role == 'SUPER_ADMIN':
        return queryset
    if user.role == 'ADMIN' and getattr(user, 'college_id', None):
        return queryset.filter(college_id=user.college_id)
    if user.role == 'STUDENT':
        return queryset.filter(student__user=user)
    return queryset.none()


class CompanyListView(BaseAPIView):
    allowed_roles = ['SUPER_ADMIN', 'ADMIN', 'STUDENT']

    def get(self, request):
        queryset = Company.objects.filter(is_deleted=False, is_active=True)
        queryset = _scope_college_models(queryset, request.user)
        return APIResponse.paginated(queryset, CompanySerializer, request)


class JobPostingListView(BaseAPIView):
    allowed_roles = ['SUPER_ADMIN', 'ADMIN', 'HOD', 'TEACHER', 'STUDENT']

    def get(self, request):
        queryset = JobPosting.objects.filter(is_deleted=False, is_active=True).select_related('company')
        queryset = _scope_college_models(queryset, request.user)

        status_param = request.query_params.get('status')
        company_id = request.query_params.get('company')

        if status_param:
            queryset = queryset.filter(status=status_param.upper())
        if company_id:
            queryset = queryset.filter(company_id=company_id)

        return APIResponse.paginated(queryset, JobPostingSerializer, request)

    def post(self, request):
        if request.user.role not in ('SUPER_ADMIN', 'ADMIN'):
            return APIResponse.error(message='Access denied.', status=403)

        serializer = JobPostingWriteSerializer(data=request.data, context={'request': request})
        if not serializer.is_valid():
            return APIResponse.error(message='Invalid input.', errors=serializer.errors)

        job = serializer.save()
        return APIResponse.success(
            data=JobPostingSerializer(job).data,
            message='Job posted.',
            status=201,
        )


class PlacementApplicationListView(BaseAPIView):
    allowed_roles = ['SUPER_ADMIN', 'ADMIN', 'STUDENT']

    def get(self, request):
        queryset = PlacementApplication.objects.filter(is_deleted=False).select_related('student', 'job')
        queryset = _scope_placement_applications(queryset, request.user)

        student_id = request.query_params.get('student')
        job_id = request.query_params.get('job')
        status_param = request.query_params.get('status')

        if student_id:
            queryset = queryset.filter(student_id=student_id)
        if job_id:
            queryset = queryset.filter(job_id=job_id)
        if status_param:
            queryset = queryset.filter(status=status_param.upper())

        return APIResponse.paginated(queryset, PlacementApplicationSerializer, request)

    def post(self, request):
        if request.user.role not in ('SUPER_ADMIN', 'ADMIN', 'STUDENT'):
            return APIResponse.error(message='Access denied.', status=403)

        payload = request.data.copy()
        if request.user.role == 'STUDENT':
            try:
                payload['student'] = str(request.user.student_profile.pk)
            except Exception:
                return APIResponse.error(message='Student profile required.', status=400)

        serializer = PlacementApplicationWriteSerializer(data=payload, context={'request': request})
        if not serializer.is_valid():
            return APIResponse.error(message='Invalid input.', errors=serializer.errors)

        try:
            application = serializer.save()
        except IntegrityError:
            return APIResponse.error(message='Already applied for this job.', status=400)

        return APIResponse.success(
            data=PlacementApplicationSerializer(application).data,
            message='Application submitted.',
            status=201,
        )
