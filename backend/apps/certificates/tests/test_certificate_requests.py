import pytest
from rest_framework import status

from apps.certificates.models import CertificateRequest


@pytest.mark.django_db
class TestCertificateRequests:
    def test_student_can_create_request(self, api_client, student_record, certificate_template):
        api_client.force_authenticate(user=student_record.user)
        response = api_client.post(
            '/api/v1/certificates/requests/',
            {
                'student': str(student_record.id),
                'template': str(certificate_template.id),
                'purpose': 'For internship',
            },
        )
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['data']['status'] == 'pending'

    def test_student_cannot_request_for_other(
        self, api_client, student_record, certificate_template, college, department, branch, academic_year
    ):
        from apps.accounts.models import User
        from apps.students.models import Student

        other_user = User.objects.create_user(
            email='other@test.com',
            phone='+955555555555',
            first_name='Other',
            last_name='Student',
            role='STUDENT',
            password='password',
            college=college,
        )
        other = Student.objects.create(
            user=other_user,
            college=college,
            department=department,
            branch=branch,
            academic_year=academic_year,
            enrollment_number='STU999',
            roll_number='R999',
            semester=1,
            batch_year=2025,
            date_of_birth='2005-01-01',
            gender='MALE',
            address='x',
            city='x',
            state='x',
            pincode='1',
            emergency_contact='1',
            emergency_contact_name='g',
            admission_date='2023-07-01',
            admission_number='A999',
        )
        api_client.force_authenticate(user=student_record.user)
        response = api_client.post(
            '/api/v1/certificates/requests/',
            {
                'student': str(other.id),
                'template': str(certificate_template.id),
                'purpose': 'Bad',
            },
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_registrar_lists_requests(self, api_client, registrar_user, student_record, certificate_template):
        CertificateRequest.objects.create(
            student=student_record,
            template=certificate_template,
            requested_by=student_record.user,
            request_number='CRT-LIST-001',
            purpose='Bonafide',
        )
        api_client.force_authenticate(user=registrar_user)
        response = api_client.get('/api/v1/certificates/requests/?status=pending')
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['data']) >= 1

    def test_approve_reject_issue_flow(
        self, api_client, registrar_user, student_record, certificate_template
    ):
        cert_request = CertificateRequest.objects.create(
            student=student_record,
            template=certificate_template,
            requested_by=student_record.user,
            request_number='CRT-FLOW-001',
            purpose='Placement',
        )
        api_client.force_authenticate(user=registrar_user)

        reject_resp = api_client.post(
            f'/api/v1/certificates/requests/{cert_request.id}/reject/',
            {'remarks': 'Incomplete docs'},
        )
        assert reject_resp.status_code == status.HTTP_200_OK
        assert reject_resp.data['data']['status'] == 'rejected'

        cert_request.status = CertificateRequest.RequestStatus.PENDING
        cert_request.save(update_fields=['status'])

        approve_resp = api_client.post(
            f'/api/v1/certificates/requests/{cert_request.id}/approve/',
            {'remarks': 'OK'},
        )
        assert approve_resp.status_code == status.HTTP_200_OK
        assert approve_resp.data['data']['status'] == 'approved'

        issue_resp = api_client.post(f'/api/v1/certificates/requests/{cert_request.id}/generate/')
        assert issue_resp.status_code == status.HTTP_201_CREATED
        assert issue_resp.data['data']['issue']['verification_code']
        assert issue_resp.data['data']['issue']['certificate_number']
        cert_request.refresh_from_db()
        assert cert_request.status == 'issued'

    def test_cannot_issue_pending_request(self, api_client, registrar_user, student_record, certificate_template):
        cert_request = CertificateRequest.objects.create(
            student=student_record,
            template=certificate_template,
            requested_by=student_record.user,
            request_number='CRT-PEND-001',
            status=CertificateRequest.RequestStatus.PENDING,
        )
        api_client.force_authenticate(user=registrar_user)
        response = api_client.post(f'/api/v1/certificates/requests/{cert_request.id}/issue/')
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_student_cannot_approve(self, api_client, student_record, certificate_template):
        cert_request = CertificateRequest.objects.create(
            student=student_record,
            template=certificate_template,
            requested_by=student_record.user,
            request_number='CRT-STU-001',
        )
        api_client.force_authenticate(user=student_record.user)
        response = api_client.post(f'/api/v1/certificates/requests/{cert_request.id}/approve/')
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_bulk_generate(self, api_client, registrar_user, student_record, certificate_template):
        req1 = CertificateRequest.objects.create(
            student=student_record,
            template=certificate_template,
            requested_by=student_record.user,
            request_number='CRT-BULK-001',
            status=CertificateRequest.RequestStatus.APPROVED,
        )
        api_client.force_authenticate(user=registrar_user)
        response = api_client.post(
            '/api/v1/certificates/bulk-generate/',
            {'request_ids': [str(req1.id)]},
            format='json',
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.data['data']['issued'] == 1
