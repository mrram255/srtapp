import base64
import io
import qrcode
from reportlab.lib import colors
from reportlab.lib.pagesizes import A6, landscape
from reportlab.lib.units import mm
from reportlab.lib.utils import ImageReader


def generate_qr_base64(data: str) -> str:
    qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_H, box_size=10, border=2)
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)
    return base64.b64encode(buffer.getvalue()).decode('utf-8')


def generate_id_card_pdf(card_data: dict) -> bytes:
    buffer = io.BytesIO()
    width, height = landscape(A6)
    c = canvas.Canvas(buffer, pagesize=(width, height))
    from reportlab.pdfgen import canvas as cv
    c = cv.Canvas(buffer, pagesize=(width, height))

    c.setFillColor(colors.HexColor('#1e40af'))
    c.rect(0, 0, width, height, fill=1, stroke=0)
    c.setFillColor(colors.white)
    c.roundRect(10*mm, 8*mm, width - 20*mm, height - 16*mm, 5*mm, fill=1, stroke=0)
    c.setFillColor(colors.HexColor('#1e40af'))
    c.rect(10*mm, height - 22*mm, width - 20*mm, 14*mm, fill=1, stroke=0)
    c.setFillColor(colors.white)
    c.setFont('Helvetica-Bold', 10)
    c.drawCentredString(width / 2, height - 15*mm, card_data.get('college_name', 'SRTAPP').upper())
    c.setFont('Helvetica', 7)
    c.drawCentredString(width / 2, height - 20*mm, f"{card_data.get('role_label', 'STAFF')} IDENTITY CARD")

    right_col = width - 45*mm
    qr_base64 = card_data.get('qr_code', '')
    if qr_base64:
        qr_bytes = base64.b64decode(qr_base64)
        qr_img = ImageReader(io.BytesIO(qr_bytes))
        c.drawImage(qr_img, right_col, 15*mm, 32*mm, 32*mm)

    left_col = 20*mm
    c.setFillColor(colors.HexColor('#1e293b'))
    c.setFont('Helvetica-Bold', 11)
    c.drawString(left_col, height - 30*mm, card_data.get('name', '').upper())

    details = [
        ('ID / Enrollment', card_data.get('id_number', '')),
        ('Role', card_data.get('role_label', '')),
        ('Department', card_data.get('department', 'N/A')),
        ('Email', card_data.get('email', '')),
        ('Valid Till', card_data.get('valid_till', '2025-26')),
    ]

    y = height - 38*mm
    for label, value in details:
        c.setFont('Helvetica', 6)
        c.setFillColor(colors.HexColor('#64748b'))
        c.drawString(left_col, y, label.upper())
        c.setFont('Helvetica-Bold', 8)
        c.setFillColor(colors.HexColor('#1e293b'))
        c.drawString(left_col, y - 4*mm, str(value)[:40])
        y -= 10*mm

    c.setFillColor(colors.HexColor('#1e40af'))
    c.rect(10*mm, 8*mm, width - 20*mm, 6*mm, fill=1, stroke=0)
    c.setFillColor(colors.white)
    c.setFont('Helvetica', 6)
    c.drawCentredString(width / 2, 10*mm, 'Official Identity Card — Non-transferable')
    c.save()
    buffer.seek(0)
    return buffer.getvalue()
