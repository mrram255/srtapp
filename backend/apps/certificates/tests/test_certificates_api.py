import datetime

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework import status


@pytest.mark.django_db
def test_certificate_templates_list_requires_auth(api_client):
    response = api_client.get('/api/v1/certificates/')
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
def test_super_admin_can_create_certificate_template(api_client, super_admin_user, college, template_file):
    api_client.force_authenticate(user=super_admin_user)
    response = api_client.post(
        '/api/v1/certificates/templates/',
        data={
            'college': str(college.id),
            'name': 'Transcript',
            'code': 'TRANSCRIPT-001',
            'description': 'Official transcript',
            'certificate_type': 'transcript',
            'template_file': template_file,
            'is_active': True,
        },
        format='multipart',
    )
    assert response.status_code == status.HTTP_201_CREATED
    assert response.data['data']['name'] == 'Transcript'


@pytest.mark.django_db
def test_super_admin_can_issue_certificate(
    api_client, super_admin_user, student_record, certificate_template
):
    api_client.force_authenticate(user=super_admin_user)
    response = api_client.post(
        '/api/v1/certificates/issues/',
        data={
            'student': str(student_record.id),
            'template': str(certificate_template.id),
            'remarks': 'Issued for graduation',
        },
    )
    assert response.status_code == status.HTTP_201_CREATED
    data = response.data['data']
    assert data['status'] == 'issued'
    assert data['verification_code']
    assert data['blockchain_hash']
    assert data['pdf_url']
    assert data['qr_payload'].startswith('SRTAPP:CERT:')


@pytest.mark.django_db
def test_student_can_view_their_certificate_issues(
    api_client, student_record, super_admin_user, certificate_template
):
    from apps.certificates.models import CertificateIssue

    CertificateIssue.objects.create(
        student=student_record,
        template=certificate_template,
        issued_by=super_admin_user,
        status='issued',
        issued_at=datetime.datetime.now(),
        verification_code='ABC123VERIFY0001',
        blockchain_hash='a' * 64,
        qr_payload='SRTAPP:CERT:ABC123VERIFY0001',
        remarks='Test issue',
    )

    api_client.force_authenticate(user=student_record.user)
    response = api_client.get('/api/v1/certificates/issues/')
    assert response.status_code == status.HTTP_200_OK
    assert str(response.data['data'][0]['student']) == str(student_record.id)


@pytest.mark.django_db
def test_parent_can_view_ward_certificate_issues(
    api_client, student_record, super_admin_user, college, certificate_template
):
    from apps.accounts.models import ParentProfile, User
    from apps.certificates.models import CertificateIssue

    parent = User.objects.create_user(
        email='parent@test.com',
        phone='+933333333333',
        first_name='Test',
        last_name='Parent',
        role='PARENT',
        password='password',
        college=college,
    )
    profile = ParentProfile.objects.create(user=parent)
    profile.wards.add(student_record)

    CertificateIssue.objects.create(
        student=student_record,
        template=certificate_template,
        issued_by=super_admin_user,
        status='issued',
        issued_at=datetime.datetime.now(),
        verification_code='ABC123VERIFY0002',
        blockchain_hash='b' * 64,
        qr_payload='SRTAPP:CERT:ABC123VERIFY0002',
        remarks='Test parent view',
    )

    api_client.force_authenticate(user=parent)
    response = api_client.get('/api/v1/certificates/issues/')
    assert response.status_code == status.HTTP_200_OK
    assert str(response.data['data'][0]['student']) == str(student_record.id)
