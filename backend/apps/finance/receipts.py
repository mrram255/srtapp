from __future__ import annotations

import io
import uuid

from django.core.files.base import ContentFile
from django.core.files.storage import default_storage


def generate_fee_receipt_pdf(payment) -> str:
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.pdfgen import canvas
    except ImportError:
        return ''

    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    c.setFont('Helvetica-Bold', 16)
    c.drawString(72, 800, 'Fee Payment Receipt')
    c.setFont('Helvetica', 11)
    y = 760
    for label, value in [
        ('Receipt No', payment.receipt_number or 'N/A'),
        ('Student', payment.student.enrollment_number),
        ('Amount Paid', str(payment.amount_paid)),
        ('Status', payment.status),
        ('Date', str(payment.paid_date or '')),
        ('Transaction', payment.transaction_id or ''),
    ]:
        c.drawString(72, y, f'{label}: {value}')
        y -= 22
    c.showPage()
    c.save()

    if not payment.receipt_number:
        payment.receipt_number = f'RCP-{uuid.uuid4().hex[:8].upper()}'
        payment.save(update_fields=['receipt_number'])

    path = f'receipts/{payment.college_id}/{payment.receipt_number}.pdf'
    default_storage.save(path, ContentFile(buffer.getvalue()))
    return default_storage.url(path)
