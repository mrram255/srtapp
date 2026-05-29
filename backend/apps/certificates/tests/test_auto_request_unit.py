import pytest

from apps.certificates.models import CertificateRequest, CertificateTemplate
from apps.certificates.services import CertificateService


@pytest.mark.django_db
def test_request_certificate_auto_issue(student_record, college, template_file):
    template = CertificateTemplate.objects.create(
        college=college,
        name='Auto Bonafide',
        code='AUTO-UNIT',
        certificate_type='bonafide',
        template_file=template_file,
        requires_approval=False,
        auto_generate=True,
        is_active=True,
    )
    req = CertificateService.request_certificate(
        student=student_record,
        template=template,
        requested_by=student_record.user,
        purpose='Internship',
    )
    assert req.status == CertificateRequest.RequestStatus.ISSUED
    assert hasattr(req, 'certificate_issue')
    assert req.certificate_issue.pdf_url
