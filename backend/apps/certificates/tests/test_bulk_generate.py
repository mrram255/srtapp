import pytest
from rest_framework import status

from apps.certificates.models import CertificateRequest


@pytest.mark.django_db
class TestBulkGenerate:
    def test_bulk_students(self, api_client, registrar_user, student_record, certificate_template):
        api_client.force_authenticate(user=registrar_user)
        response = api_client.post(
            '/api/v1/certificates/bulk-generate-students/',
            {
                'student_ids': [str(student_record.id)],
                'template_id': str(certificate_template.id),
            },
            format='json',
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.data['data']['created'] == 1

    def test_download_increments_count(
        self, api_client, student_record, certificate_template, super_admin_user
    ):
        from apps.certificates.services import CertificateService

        issue = CertificateService.issue_direct(
            student=student_record,
            template=certificate_template,
            issued_by=super_admin_user,
        )
        api_client.force_authenticate(user=student_record.user)
        api_client.get(f'/api/v1/certificates/download/{issue.id}/')
        issue.refresh_from_db()
        assert issue.download_count == 1

    def test_my_certificates_student(self, api_client, student_record, certificate_template, super_admin_user):
        from apps.certificates.services import CertificateService

        CertificateService.issue_direct(
            student=student_record,
            template=certificate_template,
            issued_by=super_admin_user,
        )
        api_client.force_authenticate(user=student_record.user)
        response = api_client.get('/api/v1/certificates/my-certificates/')
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['data']) >= 1

    def test_request_via_spec_path(self, api_client, student_record, certificate_template):
        api_client.force_authenticate(user=student_record.user)
        response = api_client.post(
            '/api/v1/certificates/request/',
            {
                'student': str(student_record.id),
                'template': str(certificate_template.id),
                'purpose': 'Visa',
            },
        )
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['data']['request_number'].startswith('CRT-')
