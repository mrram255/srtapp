from apps.core.responses import APIResponse
from apps.core.views import BaseAPIView

from .models import GeneratedReport, ReportTemplate
from .serializers import (
    GeneratedReportSerializer,
    GeneratedReportWriteSerializer,
    ReportTemplateSerializer,
)


def _scope_college_models(queryset, user):
    if user.role == 'SUPER_ADMIN':
        return queryset
    if getattr(user, 'college_id', None):
        return queryset.filter(college_id=user.college_id)
    return queryset.none()


class ReportTemplateListView(BaseAPIView):
    allowed_roles = ['SUPER_ADMIN', 'ADMIN', 'HOD']

    def get(self, request):
        queryset = ReportTemplate.objects.filter(is_deleted=False, is_active=True)
        queryset = _scope_college_models(queryset, request.user)

        report_type = request.query_params.get('report_type')
        if report_type:
            queryset = queryset.filter(report_type=report_type.upper())

        return APIResponse.paginated(queryset, ReportTemplateSerializer, request)


class GeneratedReportListView(BaseAPIView):
    allowed_roles = ['SUPER_ADMIN', 'ADMIN', 'HOD', 'ACCOUNTANT']

    def get(self, request):
        queryset = GeneratedReport.objects.filter(is_deleted=False).select_related(
            'template',
            'generated_by',
        )
        queryset = _scope_college_models(queryset, request.user)

        template_id = request.query_params.get('template')
        status_param = request.query_params.get('status')

        if template_id:
            queryset = queryset.filter(template_id=template_id)
        if status_param:
            queryset = queryset.filter(status=status_param.upper())

        return APIResponse.paginated(queryset, GeneratedReportSerializer, request)

    def post(self, request):
        serializer = GeneratedReportWriteSerializer(data=request.data, context={'request': request})
        if not serializer.is_valid():
            return APIResponse.error(message='Invalid input.', errors=serializer.errors)

        report = serializer.save()
        return APIResponse.success(
            data=GeneratedReportSerializer(report).data,
            message='Report generation started.',
            status=202,
        )
