from django.http import HttpResponseRedirect
from django.utils import timezone
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView

from apps.core.responses import APIResponse
from apps.core.views import BaseAPIView

from .models import CertificateIssue, CertificateRequest, CertificateTemplate
from .serializers import (
    CertificateBulkIssueSerializer,
    CertificateBulkStudentsSerializer,
    CertificateIssueCreateSerializer,
    CertificateIssueSerializer,
    CertificateRequestCreateSerializer,
    CertificateRequestSerializer,
    CertificateRevokeSerializer,
    CertificateTemplateSerializer,
)
from .services import CertificateService


def _scope_templates(queryset, user):
    if user.role == 'SUPER_ADMIN':
        return queryset
    if getattr(user, 'college_id', None):
        return queryset.filter(college_id=user.college_id)
    return queryset.none()


def _scope_issues(queryset, user):
    if user.role == 'SUPER_ADMIN':
        return queryset
    if getattr(user, 'college_id', None):
        return queryset.filter(student__college_id=user.college_id)
    return queryset.none()


def _scope_requests(queryset, user):
    if user.role == 'SUPER_ADMIN':
        return queryset
    if getattr(user, 'college_id', None):
        return queryset.filter(student__college_id=user.college_id)
    return queryset.none()


def _get_issue_for_user(request, pk):
    queryset = CertificateIssue.objects.filter(is_active=True).select_related('student', 'template')
    if request.user.role == 'STUDENT':
        queryset = queryset.filter(student__user=request.user)
    elif request.user.role == 'PARENT':
        profile = getattr(request.user, 'parent_profile', None)
        if not profile:
            return None
        queryset = queryset.filter(student_id__in=profile.wards.values_list('pk', flat=True))
    else:
        queryset = _scope_issues(queryset, request.user)
    return queryset.filter(pk=pk).first()


class CertificateTemplateListView(BaseAPIView):
    allowed_roles = ['SUPER_ADMIN', 'ADMIN', 'PRINCIPAL', 'REGISTRAR', 'ACCOUNTANT', 'STUDENT']

    def get(self, request):
        queryset = CertificateTemplate.objects.filter(is_active=True).select_related('college')
        queryset = _scope_templates(queryset, request.user)
        cert_type = request.query_params.get('certificate_type')
        if cert_type:
            queryset = queryset.filter(certificate_type=cert_type)
        return APIResponse.paginated(queryset, CertificateTemplateSerializer, request)

    def post(self, request):
        if request.user.role not in ('SUPER_ADMIN', 'ADMIN', 'REGISTRAR', 'PRINCIPAL'):
            return APIResponse.error(message='Access denied.', status=403)

        serializer = CertificateTemplateSerializer(data=request.data, context={'request': request})
        if not serializer.is_valid():
            return APIResponse.error(message='Invalid input.', errors=serializer.errors)

        certificate = serializer.save()
        return APIResponse.success(
            data=CertificateTemplateSerializer(certificate).data,
            message='Template created.',
            status=201,
        )


class CertificateTemplateDetailView(BaseAPIView):
    allowed_roles = ['SUPER_ADMIN', 'ADMIN', 'REGISTRAR', 'PRINCIPAL']

    def get(self, request, pk):
        template = _scope_templates(CertificateTemplate.objects.filter(pk=pk, is_active=True), request.user).first()
        if not template:
            return APIResponse.error(message='Template not found.', status=404)
        return APIResponse.success(CertificateTemplateSerializer(template).data)

    def patch(self, request, pk):
        template = _scope_templates(CertificateTemplate.objects.filter(pk=pk), request.user).first()
        if not template:
            return APIResponse.error(message='Template not found.', status=404)
        serializer = CertificateTemplateSerializer(template, data=request.data, partial=True)
        if not serializer.is_valid():
            return APIResponse.error(message='Invalid input.', errors=serializer.errors)
        template = serializer.save()
        return APIResponse.success(CertificateTemplateSerializer(template).data, message='Template updated.')


class CertificateIssueListView(BaseAPIView):
    allowed_roles = ['SUPER_ADMIN', 'ADMIN', 'REGISTRAR', 'PRINCIPAL', 'STUDENT', 'PARENT']

    def get(self, request):
        queryset = CertificateIssue.objects.filter(is_active=True).select_related(
            'student__user', 'template', 'issued_by', 'request'
        )
        if request.user.role == 'STUDENT':
            queryset = queryset.filter(student__user=request.user)
        elif request.user.role == 'PARENT':
            profile = getattr(request.user, 'parent_profile', None)
            if profile:
                queryset = queryset.filter(student_id__in=profile.wards.values_list('pk', flat=True))
            else:
                queryset = queryset.none()
        else:
            queryset = _scope_issues(queryset, request.user)

        for param in ('status', 'template', 'student'):
            value = request.query_params.get(param)
            if value:
                queryset = queryset.filter(**{param: value})

        return APIResponse.paginated(queryset, CertificateIssueSerializer, request)

    def post(self, request):
        if request.user.role not in ('SUPER_ADMIN', 'ADMIN', 'REGISTRAR', 'PRINCIPAL'):
            return APIResponse.error(message='Access denied.', status=403)

        serializer = CertificateIssueCreateSerializer(data=request.data, context={'request': request})
        if not serializer.is_valid():
            return APIResponse.error(message='Invalid input.', errors=serializer.errors)

        issue = serializer.save()
        return APIResponse.success(
            data=CertificateIssueSerializer(issue).data,
            message='Certificate issued.',
            status=201,
        )


class CertificateRequestListView(BaseAPIView):
    allowed_roles = ['SUPER_ADMIN', 'ADMIN', 'REGISTRAR', 'PRINCIPAL', 'STUDENT', 'PARENT']

    def get(self, request):
        queryset = CertificateRequest.objects.filter(is_active=True).select_related(
            'student__user', 'template', 'requested_by', 'reviewed_by', 'certificate_issue'
        )
        if request.user.role == 'STUDENT':
            queryset = queryset.filter(student__user=request.user)
        elif request.user.role == 'PARENT':
            profile = getattr(request.user, 'parent_profile', None)
            if profile:
                queryset = queryset.filter(student_id__in=profile.wards.values_list('pk', flat=True))
            else:
                queryset = queryset.none()
        else:
            queryset = _scope_requests(queryset, request.user)

        status_param = request.query_params.get('status')
        if status_param:
            queryset = queryset.filter(status=status_param)
        template_param = request.query_params.get('template')
        if template_param:
            queryset = queryset.filter(template_id=template_param)

        return APIResponse.paginated(queryset, CertificateRequestSerializer, request)

    def post(self, request):
        if request.user.role not in ('SUPER_ADMIN', 'ADMIN', 'REGISTRAR', 'PRINCIPAL', 'STUDENT'):
            return APIResponse.error(message='Access denied.', status=403)
        serializer = CertificateRequestCreateSerializer(data=request.data, context={'request': request})
        if not serializer.is_valid():
            return APIResponse.error(message='Invalid input.', errors=serializer.errors)
        cert_request = serializer.save()
        return APIResponse.success(
            data=CertificateRequestSerializer(cert_request).data,
            message='Certificate request submitted.',
            status=201,
        )


class StudentCertificateRequestView(BaseAPIView):
    """POST /certificates/request/ — student or staff submits a certificate request."""

    allowed_roles = ['SUPER_ADMIN', 'ADMIN', 'REGISTRAR', 'PRINCIPAL', 'STUDENT']

    def post(self, request):
        serializer = CertificateRequestCreateSerializer(data=request.data, context={'request': request})
        if not serializer.is_valid():
            return APIResponse.error(message='Invalid input.', errors=serializer.errors)
        cert_request = serializer.save()
        return APIResponse.success(
            data=CertificateRequestSerializer(cert_request).data,
            message='Certificate request submitted.',
            status=201,
        )


class MyCertificateRequestsView(BaseAPIView):
    allowed_roles = ['STUDENT', 'PARENT']

    def get(self, request):
        queryset = CertificateRequest.objects.filter(is_active=True).select_related(
            'student__user', 'template', 'certificate_issue'
        )
        if request.user.role == 'STUDENT':
            queryset = queryset.filter(student__user=request.user)
        else:
            profile = getattr(request.user, 'parent_profile', None)
            if not profile:
                return APIResponse.paginated(CertificateRequest.objects.none(), CertificateRequestSerializer, request)
            queryset = queryset.filter(student_id__in=profile.wards.values_list('pk', flat=True))
        return APIResponse.paginated(queryset, CertificateRequestSerializer, request)


class MyCertificatesView(BaseAPIView):
    allowed_roles = ['STUDENT', 'PARENT']

    def get(self, request):
        queryset = CertificateIssue.objects.filter(
            is_active=True,
            status=CertificateIssue.CertificateStatus.ISSUED,
        ).select_related('student__user', 'template')
        if request.user.role == 'STUDENT':
            queryset = queryset.filter(student__user=request.user)
        else:
            profile = getattr(request.user, 'parent_profile', None)
            if not profile:
                return APIResponse.paginated(CertificateIssue.objects.none(), CertificateIssueSerializer, request)
            queryset = queryset.filter(student_id__in=profile.wards.values_list('pk', flat=True))
        return APIResponse.paginated(queryset, CertificateIssueSerializer, request)


class CertificateDownloadView(BaseAPIView):
    allowed_roles = ['SUPER_ADMIN', 'ADMIN', 'REGISTRAR', 'PRINCIPAL', 'STUDENT', 'PARENT']

    def get(self, request, pk):
        issue = _get_issue_for_user(request, pk)
        if not issue:
            return APIResponse.error(message='Certificate not found.', status=404)
        if issue.is_revoked:
            return APIResponse.error(message='Certificate has been revoked.', status=410)
        if not issue.pdf_url:
            return APIResponse.error(message='PDF not available.', status=404)

        CertificateService.record_download(issue)
        if issue.pdf_url.startswith('http'):
            return HttpResponseRedirect(issue.pdf_url)
        return APIResponse.success(
            {'download_url': issue.pdf_url, 'download_count': issue.download_count},
            message='Use download_url to fetch the PDF.',
        )


class CertificateRequestDetailView(BaseAPIView):
    allowed_roles = ['SUPER_ADMIN', 'ADMIN', 'REGISTRAR', 'PRINCIPAL', 'STUDENT', 'PARENT']

    def get_object(self, request, pk):
        queryset = CertificateRequest.objects.filter(is_active=True).select_related(
            'student__user', 'template', 'certificate_issue'
        )
        if request.user.role == 'STUDENT':
            queryset = queryset.filter(student__user=request.user)
        elif request.user.role == 'PARENT':
            profile = getattr(request.user, 'parent_profile', None)
            if profile:
                queryset = queryset.filter(student_id__in=profile.wards.values_list('pk', flat=True))
            else:
                return None
        else:
            queryset = _scope_requests(queryset, request.user)
        return queryset.filter(pk=pk).first()


class CertificateRequestApproveView(CertificateRequestDetailView):
    allowed_roles = ['SUPER_ADMIN', 'ADMIN', 'REGISTRAR', 'PRINCIPAL']

    def post(self, request, pk):
        cert_request = self.get_object(request, pk)
        if not cert_request:
            return APIResponse.error(message='Request not found.', status=404)
        if cert_request.status != CertificateRequest.RequestStatus.PENDING:
            return APIResponse.error(message='Only pending requests can be approved.', status=400)

        remarks = request.data.get('remarks', '')
        auto_issue = request.data.get('auto_issue', cert_request.template.auto_generate)
        CertificateService.approve_request(cert_request, request.user, remarks=remarks, auto_issue=bool(auto_issue))
        cert_request.refresh_from_db()
        return APIResponse.success(
            data=CertificateRequestSerializer(cert_request).data,
            message='Request approved.',
        )


class CertificateRequestRejectView(CertificateRequestDetailView):
    allowed_roles = ['SUPER_ADMIN', 'ADMIN', 'REGISTRAR', 'PRINCIPAL']

    def post(self, request, pk):
        cert_request = self.get_object(request, pk)
        if not cert_request:
            return APIResponse.error(message='Request not found.', status=404)
        if cert_request.status != CertificateRequest.RequestStatus.PENDING:
            return APIResponse.error(message='Only pending requests can be rejected.', status=400)

        remarks = request.data.get('remarks', '') or request.data.get('reason', '')
        CertificateService.reject_request(cert_request, request.user, remarks=remarks)
        return APIResponse.success(
            data=CertificateRequestSerializer(cert_request).data,
            message='Request rejected.',
        )


class CertificateRequestGenerateView(CertificateRequestDetailView):
    allowed_roles = ['SUPER_ADMIN', 'ADMIN', 'REGISTRAR', 'PRINCIPAL']

    def post(self, request, pk):
        cert_request = self.get_object(request, pk)
        if not cert_request:
            return APIResponse.error(message='Request not found.', status=404)
        try:
            issue = CertificateService.generate_certificate(cert_request, request.user)
        except ValueError as exc:
            return APIResponse.error(message=str(exc), status=400)

        cert_request.refresh_from_db()
        return APIResponse.success(
            data={
                'request': CertificateRequestSerializer(cert_request).data,
                'issue': CertificateIssueSerializer(issue).data,
            },
            message='Certificate generated.',
            status=201,
        )


class CertificateRequestIssueView(CertificateRequestGenerateView):
    """Alias: /issue/ same as /generate/."""


class CertificateIssueRevokeView(BaseAPIView):
    allowed_roles = ['SUPER_ADMIN', 'ADMIN', 'REGISTRAR', 'PRINCIPAL']

    def post(self, request, pk):
        issue = _scope_issues(CertificateIssue.objects.filter(pk=pk), request.user).first()
        if not issue:
            return APIResponse.error(message='Certificate not found.', status=404)
        serializer = CertificateRevokeSerializer(data=request.data)
        if not serializer.is_valid():
            return APIResponse.error(message='Invalid input.', errors=serializer.errors)
        issue = CertificateService.revoke_certificate(issue, request.user, serializer.validated_data['reason'])
        return APIResponse.success(CertificateIssueSerializer(issue).data, message='Certificate revoked.')


class CertificateBulkGenerateView(BaseAPIView):
    allowed_roles = ['SUPER_ADMIN', 'ADMIN', 'REGISTRAR', 'PRINCIPAL']

    def post(self, request):
        serializer = CertificateBulkIssueSerializer(data=request.data)
        if not serializer.is_valid():
            return APIResponse.error(message='Invalid input.', errors=serializer.errors)

        result = CertificateService.bulk_issue_requests(
            serializer.validated_data['request_ids'],
            request.user,
        )
        return APIResponse.success(result, message='Bulk issue completed.')


class CertificateBulkStudentsView(BaseAPIView):
    allowed_roles = ['SUPER_ADMIN', 'ADMIN', 'REGISTRAR', 'PRINCIPAL']

    def post(self, request):
        serializer = CertificateBulkStudentsSerializer(data=request.data)
        if not serializer.is_valid():
            return APIResponse.error(message='Invalid input.', errors=serializer.errors)

        result = CertificateService.bulk_generate_students(
            student_ids=serializer.validated_data['student_ids'],
            template_id=serializer.validated_data['template_id'],
            issued_by=request.user,
        )
        return APIResponse.success(result, message='Bulk generation completed.')


class CertificateStatsView(BaseAPIView):
    allowed_roles = ['SUPER_ADMIN', 'ADMIN', 'REGISTRAR', 'PRINCIPAL']

    def get(self, request):
        college_id = request.query_params.get('college') or (
            None if request.user.role == 'SUPER_ADMIN' else request.user.college_id
        )
        if request.user.role == 'SUPER_ADMIN' and request.query_params.get('college'):
            college_id = request.query_params.get('college')
        return APIResponse.success(CertificateService.get_certificate_stats(college_id=college_id))


class PublicCertificateVerifyView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    def get(self, request, code):
        data = CertificateService.verify_public(code)
        if data.get('message') and not data.get('certificate_number'):
            return APIResponse.error(message=data['message'], status=404)
        return APIResponse.success(data)
