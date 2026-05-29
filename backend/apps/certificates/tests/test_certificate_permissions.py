import pytest
from rest_framework import status


@pytest.mark.django_db
class TestCertificatePermissions:
    def test_student_cannot_approve(self, api_client, student_record, certificate_template):
        from apps.certificates.models import CertificateRequest

        req = CertificateRequest.objects.create(
            student=student_record,
            template=certificate_template,
            requested_by=student_record.user,
            request_number='CRT-TEST-001',
        )
        api_client.force_authenticate(user=student_record.user)
        response = api_client.post(f'/api/v1/certificates/requests/{req.id}/approve/')
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_student_cannot_revoke(self, api_client, student_record, certificate_template, super_admin_user):
        from apps.certificates.services import CertificateService

        issue = CertificateService.issue_direct(
            student=student_record,
            template=certificate_template,
            issued_by=super_admin_user,
        )
        api_client.force_authenticate(user=student_record.user)
        response = api_client.post(f'/api/v1/certificates/issues/{issue.id}/revoke/', {'reason': 'x'})
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_registrar_can_view_stats(self, api_client, registrar_user):
        api_client.force_authenticate(user=registrar_user)
        response = api_client.get('/api/v1/certificates/stats/')
        assert response.status_code == status.HTTP_200_OK
        assert 'requests' in response.data['data']

    def test_student_cannot_view_stats(self, api_client, student_record):
        api_client.force_authenticate(user=student_record.user)
        response = api_client.get('/api/v1/certificates/stats/')
        assert response.status_code == status.HTTP_403_FORBIDDEN
