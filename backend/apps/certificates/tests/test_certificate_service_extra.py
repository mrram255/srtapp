import pytest

from apps.certificates.services import CertificateService


@pytest.mark.django_db
def test_render_pdf_returns_bytes(student_record, certificate_template, super_admin_user):
    issue = CertificateService.issue_direct(
        student=student_record,
        template=certificate_template,
        issued_by=super_admin_user,
    )
    context = CertificateService._build_context(issue)
    pdf = CertificateService._render_pdf_html(issue, context)
    assert isinstance(pdf, bytes)
    assert len(pdf) > 100
    assert pdf[:4] == b'%PDF'


@pytest.mark.django_db
def test_issue_payload_contains_required_keys(student_record, certificate_template, super_admin_user):
    issue = CertificateService.issue_direct(
        student=student_record,
        template=certificate_template,
        issued_by=super_admin_user,
    )
    payload = CertificateService.issue_payload(issue)
    assert 'verification_code' in payload
    assert 'enrollment_number' in payload
    assert 'template_code' in payload
