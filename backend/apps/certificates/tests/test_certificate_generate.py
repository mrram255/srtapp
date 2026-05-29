import pytest
from rest_framework import status

from apps.certificates.models import CertificateRequest
from apps.certificates.services import CertificateService


@pytest.mark.django_db
class TestCertificateGenerate:
    def test_generate_endpoint(self, api_client, registrar_user, student_record, certificate_template):
        cert_request = CertificateRequest.objects.create(
            student=student_record,
            template=certificate_template,
            requested_by=student_record.user,
            request_number='CRT-GEN-001',
            status=CertificateRequest.RequestStatus.APPROVED,
        )
        api_client.force_authenticate(user=registrar_user)
        response = api_client.post(f'/api/v1/certificates/requests/{cert_request.id}/generate/')
        assert response.status_code == status.HTTP_201_CREATED
        data = response.data['data']['issue']
        assert data['certificate_number']
        assert data['pdf_url']
        assert data['data_snapshot']['enrollment_number'] == 'STU001'

    def test_auto_generate_template(self, api_client, student_record, college, template_file):
        from apps.certificates.models import CertificateTemplate

        template = CertificateTemplate.objects.create(
            college=college,
            name='Auto Bonafide',
            code='AUTO-BON',
            certificate_type='bonafide',
            template_file=template_file,
            requires_approval=False,
            auto_generate=True,
            is_active=True,
        )
        api_client.force_authenticate(user=student_record.user)
        response = api_client.post(
            '/api/v1/certificates/request/',
            {
                'student': str(student_record.id),
                'template': str(template.id),
                'purpose': 'Internship',
            },
        )
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['data']['status'] == 'issued'

    def test_revoked_not_valid(self, api_client, student_record, certificate_template, super_admin_user):
        issue = CertificateService.issue_direct(
            student=student_record,
            template=certificate_template,
            issued_by=super_admin_user,
        )
        CertificateService.revoke_certificate(issue, super_admin_user, reason='Fraud')
        response = api_client.get(f'/api/v1/certificates/verify/{issue.verification_code}/')
        assert response.status_code == status.HTTP_404_NOT_FOUND
