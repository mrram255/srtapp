from __future__ import annotations

import base64
import hashlib
import io
import json
from typing import Any

from django.conf import settings
from django.db import transaction
from django.db.models import Count, Q
from django.template import Context, Template
from django.template.loader import render_to_string
from django.utils import timezone

from apps.core.services import FileUploadService
from apps.core.utils import generate_unique_code

from .models import CertificateIssue, CertificateRequest, CertificateTemplate


class CertificateService:
    @staticmethod
    def generate_request_number() -> str:
        year = timezone.now().year
        return generate_unique_code(f'CRT-{year}', length=6)

    @staticmethod
    def generate_certificate_number(template: CertificateTemplate) -> str:
        year = timezone.now().year
        prefix = template.code.split('-')[0][:6].upper() or 'CERT'
        return generate_unique_code(f'{prefix}-{year}', length=6)

    @staticmethod
    def student_snapshot(student) -> dict[str, Any]:
        user = student.user
        return {
            'student_id': str(student.id),
            'full_name': user.get_full_name(),
            'email': user.email,
            'enrollment_number': student.enrollment_number,
            'roll_number': student.roll_number,
            'department': student.department.name if student.department_id else '',
            'branch': student.branch.name if student.branch_id else '',
            'semester': student.semester,
            'college': student.college.name,
        }

    @staticmethod
    def issue_payload(issue: CertificateIssue) -> dict[str, Any]:
        return {
            'certificate_number': issue.certificate_number,
            'verification_code': issue.verification_code,
            'student_id': str(issue.student_id),
            'enrollment_number': issue.student.enrollment_number,
            'template_code': issue.template.code,
            'issued_at': issue.issued_at.isoformat() if issue.issued_at else None,
            'college_id': str(issue.student.college_id),
            'data_snapshot': issue.data_snapshot,
        }

    @staticmethod
    def blockchain_hash(payload: dict[str, Any]) -> str:
        canonical = json.dumps(payload, sort_keys=True, separators=(',', ':'), default=str)
        return hashlib.sha256(canonical.encode('utf-8')).hexdigest()

    @staticmethod
    def qr_payload(verification_code: str) -> str:
        return f'SRTAPP:CERT:{verification_code}'

    @staticmethod
    def verify_url(verification_code: str) -> str:
        base = getattr(settings, 'PUBLIC_APP_URL', 'http://localhost:3000')
        return f'{base.rstrip("/")}/verify/certificate/{verification_code}'

    @staticmethod
    def api_verify_url(verification_code: str) -> str:
        base = getattr(settings, 'PUBLIC_API_URL', 'http://localhost:8000')
        return f'{base.rstrip("/")}/api/v1/certificates/verify/{verification_code}/'

    @staticmethod
    def _qr_base64(data: str) -> str:
        import qrcode

        qr = qrcode.QRCode(version=1, box_size=8, border=2)
        qr.add_data(data)
        qr.make(fit=True)
        img = qr.make_image(fill_color='black', back_color='white')
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        return base64.b64encode(buffer.getvalue()).decode('utf-8')

    @staticmethod
    def _render_pdf_html(issue: CertificateIssue, context: dict[str, Any]) -> bytes:
        template = issue.template
        if template.html_body:
            html = Template(template.html_body).render(Context(context))
        else:
            html = render_to_string('certificates/certificate.html', context)
        try:
            from weasyprint import HTML

            return HTML(string=html).write_pdf()
        except Exception:
            return CertificateService._render_pdf_reportlab(context)

    @staticmethod
    def _render_pdf_reportlab(context: dict[str, Any]) -> bytes:
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.units import mm
        from reportlab.pdfgen import canvas

        buffer = io.BytesIO()
        c = canvas.Canvas(buffer, pagesize=A4)
        width, height = A4
        y = height - 40 * mm
        c.setFont('Helvetica-Bold', 18)
        c.drawCentredString(width / 2, y, context.get('college_name', 'SRTAPP College'))
        y -= 15 * mm
        c.setFont('Helvetica', 12)
        c.drawCentredString(width / 2, y, context.get('certificate_title', 'Certificate'))
        y -= 20 * mm
        c.drawString(30 * mm, y, f"Name: {context.get('student_name', '')}")
        y -= 10 * mm
        c.drawString(30 * mm, y, f"Enrollment: {context.get('enrollment_number', '')}")
        y -= 10 * mm
        c.drawString(30 * mm, y, f"Certificate No: {context.get('certificate_number', '')}")
        y -= 10 * mm
        c.drawString(30 * mm, y, f"Verification: {context.get('verification_code', '')}")
        c.drawString(30 * mm, 30 * mm, context.get('qr_payload', ''))
        c.showPage()
        c.save()
        buffer.seek(0)
        return buffer.getvalue()

    @staticmethod
    def _build_context(issue: CertificateIssue) -> dict[str, Any]:
        student = issue.student
        user = student.user
        return {
            'college_name': student.college.name,
            'certificate_title': issue.template.name,
            'certificate_type': issue.template.get_certificate_type_display(),
            'student_name': user.get_full_name(),
            'enrollment_number': student.enrollment_number,
            'certificate_number': issue.certificate_number,
            'department': student.department.name if student.department_id else '',
            'issued_date': issue.issued_at.strftime('%d %B %Y') if issue.issued_at else '',
            'verification_code': issue.verification_code,
            'blockchain_hash': issue.blockchain_hash,
            'qr_payload': issue.qr_payload,
            'qr_base64': CertificateService._qr_base64(issue.qr_payload),
            'verify_url': issue.qr_verification_url or CertificateService.verify_url(issue.verification_code),
            'purpose': issue.remarks,
            'data_snapshot': issue.data_snapshot,
        }

    @staticmethod
    def finalize_issue(issue: CertificateIssue, issued_by=None) -> CertificateIssue:
        if not issue.certificate_number:
            issue.certificate_number = CertificateService.generate_certificate_number(issue.template)
        issue.data_snapshot = CertificateService.student_snapshot(issue.student)
        issue.issued_at = timezone.now()
        issue.status = CertificateIssue.CertificateStatus.ISSUED
        if issued_by:
            issue.issued_by = issued_by
        issue.qr_payload = CertificateService.qr_payload(issue.verification_code)
        issue.qr_verification_url = CertificateService.verify_url(issue.verification_code)
        payload = CertificateService.issue_payload(issue)
        issue.blockchain_hash = CertificateService.blockchain_hash(payload)

        context = CertificateService._build_context(issue)
        pdf_bytes = CertificateService._render_pdf_html(issue, context)
        upload = io.BytesIO(pdf_bytes)
        upload.name = f'{issue.verification_code}.pdf'
        issue.pdf_url = FileUploadService.upload(upload, folder='certificates/pdf')
        issue.download_url = issue.pdf_url
        issue.save(
            update_fields=[
                'certificate_number',
                'data_snapshot',
                'issued_at',
                'status',
                'issued_by',
                'qr_payload',
                'qr_verification_url',
                'blockchain_hash',
                'pdf_url',
                'download_url',
            ]
        )
        if issue.request_id:
            CertificateRequest.objects.filter(pk=issue.request_id).update(
                status=CertificateRequest.RequestStatus.ISSUED,
                generated_at=timezone.now(),
            )
        return issue

    @staticmethod
    def issue_direct(*, student, template: CertificateTemplate, issued_by, remarks: str = '') -> CertificateIssue:
        issue = CertificateIssue(
            student=student,
            template=template,
            issued_by=issued_by,
            remarks=remarks,
            status=CertificateIssue.CertificateStatus.PENDING,
            certificate_number=CertificateService.generate_certificate_number(template),
        )
        issue.save()
        return CertificateService.finalize_issue(issue, issued_by=issued_by)

    @staticmethod
    @transaction.atomic
    def request_certificate(*, student, template: CertificateTemplate, requested_by, purpose: str = '', **extra) -> CertificateRequest:
        cert_request = CertificateRequest.objects.create(
            request_number=CertificateService.generate_request_number(),
            student=student,
            template=template,
            requested_by=requested_by,
            purpose=purpose,
            number_of_copies=extra.get('number_of_copies', 1),
            fee_amount=extra.get('fee_amount', 0),
            fee_paid=extra.get('fee_paid', False),
            remarks=extra.get('remarks', ''),
        )
        if not template.requires_approval:
            CertificateService.approve_request(
                cert_request,
                requested_by,
                remarks='Auto-approved',
                auto_issue=template.auto_generate,
            )
            cert_request.refresh_from_db()
        return cert_request

    @staticmethod
    def approve_request(request_obj: CertificateRequest, reviewer, remarks: str = '', auto_issue: bool = False) -> CertificateRequest:
        request_obj.status = CertificateRequest.RequestStatus.APPROVED
        request_obj.reviewed_by = reviewer
        request_obj.reviewed_at = timezone.now()
        request_obj.review_remarks = remarks
        request_obj.save(update_fields=['status', 'reviewed_by', 'reviewed_at', 'review_remarks'])
        if auto_issue or request_obj.template.auto_generate:
            CertificateService.generate_certificate(request_obj, issued_by=reviewer)
        return request_obj

    @staticmethod
    def reject_request(request_obj: CertificateRequest, reviewer, remarks: str = '') -> CertificateRequest:
        request_obj.status = CertificateRequest.RequestStatus.REJECTED
        request_obj.reviewed_by = reviewer
        request_obj.reviewed_at = timezone.now()
        request_obj.review_remarks = remarks
        request_obj.rejected_reason = remarks
        request_obj.save(
            update_fields=['status', 'reviewed_by', 'reviewed_at', 'review_remarks', 'rejected_reason']
        )
        return request_obj

    @staticmethod
    def generate_certificate(request_obj: CertificateRequest, issued_by) -> CertificateIssue:
        if request_obj.status not in (
            CertificateRequest.RequestStatus.APPROVED,
            CertificateRequest.RequestStatus.GENERATED,
        ):
            raise ValueError('Request must be approved before generation.')

        try:
            existing = request_obj.certificate_issue
        except CertificateIssue.DoesNotExist:
            existing = None

        if existing is not None:
            if existing.status == CertificateIssue.CertificateStatus.ISSUED and existing.pdf_url:
                return existing
            return CertificateService.finalize_issue(existing, issued_by=issued_by)

        issue = CertificateIssue(
            request=request_obj,
            student=request_obj.student,
            template=request_obj.template,
            issued_by=issued_by,
            remarks=request_obj.purpose,
            status=CertificateIssue.CertificateStatus.PENDING,
            certificate_number=CertificateService.generate_certificate_number(request_obj.template),
        )
        issue.save()
        issue = CertificateService.finalize_issue(issue, issued_by=issued_by)
        request_obj.status = CertificateRequest.RequestStatus.ISSUED
        request_obj.generated_at = timezone.now()
        request_obj.save(update_fields=['status', 'generated_at'])
        return issue

    @staticmethod
    def issue_from_request(request_obj: CertificateRequest, issued_by) -> CertificateIssue:
        return CertificateService.generate_certificate(request_obj, issued_by)

    @staticmethod
    def revoke_certificate(issue: CertificateIssue, revoked_by, reason: str = '') -> CertificateIssue:
        issue.is_revoked = True
        issue.revoked_reason = reason
        issue.revoked_at = timezone.now()
        issue.revoked_by = revoked_by
        issue.status = CertificateIssue.CertificateStatus.REVOKED
        issue.save(
            update_fields=['is_revoked', 'revoked_reason', 'revoked_at', 'revoked_by', 'status']
        )
        return issue

    @staticmethod
    def record_download(issue: CertificateIssue) -> CertificateIssue:
        issue.download_count += 1
        issue.save(update_fields=['download_count'])
        return issue

    @staticmethod
    def bulk_issue_requests(request_ids: list, issued_by) -> dict[str, Any]:
        issued = 0
        errors: list[dict] = []
        for request_id in request_ids:
            try:
                req = CertificateRequest.objects.select_related('student', 'template').get(pk=request_id)
                if req.status == CertificateRequest.RequestStatus.PENDING:
                    CertificateService.approve_request(req, issued_by, auto_issue=False)
                CertificateService.generate_certificate(req, issued_by)
                issued += 1
            except Exception as exc:
                errors.append({'request_id': str(request_id), 'error': str(exc)})
        return {'issued': issued, 'errors': errors}

    @staticmethod
    def bulk_generate_students(*, student_ids: list, template_id, issued_by) -> dict[str, Any]:
        template = CertificateTemplate.objects.get(pk=template_id, is_active=True)
        created = 0
        errors: list[dict] = []
        from apps.students.models import Student

        for student_id in student_ids:
            try:
                student = Student.objects.get(pk=student_id, is_deleted=False)
                if student.college_id != template.college_id:
                    raise ValueError('Student college mismatch.')
                req = CertificateService.request_certificate(
                    student=student,
                    template=template,
                    requested_by=issued_by,
                    purpose='Bulk generation',
                )
                if req.status != CertificateRequest.RequestStatus.ISSUED:
                    CertificateService.approve_request(req, issued_by, auto_issue=True)
                created += 1
            except Exception as exc:
                errors.append({'student_id': str(student_id), 'error': str(exc)})
        return {'created': created, 'errors': errors}

    @staticmethod
    def get_certificate_stats(*, college_id=None) -> dict[str, Any]:
        issues = CertificateIssue.objects.filter(is_active=True)
        requests = CertificateRequest.objects.filter(is_active=True)
        if college_id:
            issues = issues.filter(student__college_id=college_id)
            requests = requests.filter(student__college_id=college_id)
        return {
            'requests': {
                'pending': requests.filter(status=CertificateRequest.RequestStatus.PENDING).count(),
                'approved': requests.filter(status=CertificateRequest.RequestStatus.APPROVED).count(),
                'rejected': requests.filter(status=CertificateRequest.RequestStatus.REJECTED).count(),
                'issued': requests.filter(status=CertificateRequest.RequestStatus.ISSUED).count(),
            },
            'issued': {
                'total': issues.filter(status=CertificateIssue.CertificateStatus.ISSUED).count(),
                'revoked': issues.filter(is_revoked=True).count(),
            },
            'by_type': list(
                issues.filter(status=CertificateIssue.CertificateStatus.ISSUED)
                .values('template__certificate_type')
                .annotate(count=Count('id'))
                .order_by('-count')
            ),
        }

    @staticmethod
    def verify_public(code: str) -> dict[str, Any]:
        lookup = code.upper().strip()
        issue = (
            CertificateIssue.objects.filter(is_active=True)
            .filter(Q(verification_code=lookup) | Q(certificate_number=lookup))
            .select_related('student__user', 'student__college', 'student__department', 'template')
            .first()
        )
        if not issue or issue.status != CertificateIssue.CertificateStatus.ISSUED:
            return {'valid': False, 'message': 'Certificate not found.'}
        if issue.is_revoked:
            return {
                'valid': False,
                'message': 'Certificate has been revoked.',
                'revoked_reason': issue.revoked_reason,
            }

        payload = CertificateService.issue_payload(issue)
        hash_valid = CertificateService.blockchain_hash(payload) == issue.blockchain_hash
        return {
            'valid': hash_valid,
            'certificate_number': issue.certificate_number,
            'verification_code': issue.verification_code,
            'blockchain_hash': issue.blockchain_hash,
            'hash_valid': hash_valid,
            'student_name': issue.student.user.get_full_name(),
            'enrollment_number': issue.student.enrollment_number,
            'college': issue.student.college.name,
            'department': issue.student.department.name if issue.student.department_id else '',
            'certificate': issue.template.name,
            'certificate_type': issue.template.certificate_type,
            'issued_at': issue.issued_at,
            'pdf_url': issue.pdf_url,
            'is_revoked': issue.is_revoked,
        }
