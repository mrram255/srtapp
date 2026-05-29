import pytest
from rest_framework import status

from apps.certificates.models import CertificateIssue
from apps.certificates.services import CertificateService


@pytest.mark.django_db
class TestPublicCertificateVerify:
    def test_verify_valid_certificate(self, api_client, student_record, certificate_template, super_admin_user):
        issue = CertificateService.issue_direct(
            student=student_record,
            template=certificate_template,
            issued_by=super_admin_user,
        )
        response = api_client.get(f'/api/v1/certificates/verify/{issue.verification_code}/')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['data']['valid'] is True
        assert response.data['data']['enrollment_number'] == 'STU001'

    def test_verify_unknown_code(self, api_client):
        response = api_client.get('/api/v1/certificates/verify/UNKNOWNCODE99/')
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_verify_by_certificate_number(self, api_client, student_record, certificate_template, super_admin_user):
        issue = CertificateService.issue_direct(
            student=student_record,
            template=certificate_template,
            issued_by=super_admin_user,
        )
        response = api_client.get(f'/api/v1/certificates/verify/{issue.certificate_number}/')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['data']['valid'] is True

    def test_verify_tampered_hash(self, api_client, student_record, certificate_template, super_admin_user):
        issue = CertificateService.issue_direct(
            student=student_record,
            template=certificate_template,
            issued_by=super_admin_user,
        )
        CertificateIssue.objects.filter(pk=issue.pk).update(blockchain_hash='0' * 64)
        response = api_client.get(f'/api/v1/certificates/verify/{issue.verification_code}/')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['data']['valid'] is False
        assert response.data['data']['hash_valid'] is False

    def test_verify_no_auth_required(self, api_client, student_record, certificate_template, super_admin_user):
        issue = CertificateService.issue_direct(
            student=student_record,
            template=certificate_template,
            issued_by=super_admin_user,
        )
        api_client.logout()
        response = api_client.get(f'/api/v1/certificates/verify/{issue.verification_code}/')
        assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
class TestCertificateService:
    def test_blockchain_hash_is_deterministic(self):
        payload = {'a': 1, 'b': 2}
        assert CertificateService.blockchain_hash(payload) == CertificateService.blockchain_hash({'b': 2, 'a': 1})

    def test_qr_payload_format(self):
        assert CertificateService.qr_payload('ABC').startswith('SRTAPP:CERT:')
