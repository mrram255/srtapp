from __future__ import annotations

import io
import logging
import uuid
from typing import Any

from django.conf import settings
from django.core.cache import cache
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.utils import timezone

logger = logging.getLogger(__name__)


class FileUploadService:
    """Upload files to configured storage (MinIO in production)."""

    @staticmethod
    def upload(file_obj, folder: str = 'uploads') -> str:
        extension = ''
        if getattr(file_obj, 'name', None) and '.' in file_obj.name:
            extension = file_obj.name.rsplit('.', 1)[-1]
        filename = f'{folder}/{uuid.uuid4()}.{extension}' if extension else f'{folder}/{uuid.uuid4()}'
        saved_name = default_storage.save(filename, file_obj)
        return default_storage.url(saved_name)

    @staticmethod
    def delete(path: str) -> bool:
        if default_storage.exists(path):
            default_storage.delete(path)
            return True
        return False


class CacheService:
    """Redis cache helpers with key prefixing."""

    prefix = 'srtapp'

    @classmethod
    def _key(cls, key: str) -> str:
        return f'{cls.prefix}:{key}'

    @classmethod
    def get(cls, key: str, default=None):
        return cache.get(cls._key(key), default)

    @classmethod
    def set(cls, key: str, value: Any, timeout: int = 300) -> None:
        cache.set(cls._key(key), value, timeout)

    @classmethod
    def delete(cls, key: str) -> None:
        cache.delete(cls._key(key))


class SearchService:
    """Meilisearch index/search/delete helpers."""

    @staticmethod
    def _client():
        try:
            import meilisearch
        except ImportError as exc:
            raise RuntimeError('meilisearch package is not installed.') from exc

        config = getattr(settings, 'MEILISEARCH', {})
        host = config.get('HOST')
        api_key = config.get('API_KEY')
        if not host:
            raise RuntimeError('MEILISEARCH host is not configured.')
        return meilisearch.Client(host, api_key)

    @classmethod
    def index(cls, index_name: str, documents: list[dict[str, Any]]) -> dict[str, Any]:
        client = cls._client()
        index = client.index(index_name)
        return index.add_documents(documents)

    @classmethod
    def search(cls, index_name: str, query: str, limit: int = 20) -> dict[str, Any]:
        client = cls._client()
        index = client.index(index_name)
        return index.search(query, {'limit': limit})

    @classmethod
    def delete(cls, index_name: str, document_ids: list[str]) -> dict[str, Any]:
        client = cls._client()
        index = client.index(index_name)
        return index.delete_documents(document_ids)


class NotificationService:
    """Send notifications via configured channels."""

    @staticmethod
    def send_email(to: str, subject: str, body: str, attachments=None) -> bool:
        from django.core.mail import send_mail

        try:
            send_mail(
                subject=subject,
                message=body,
                from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', None),
                recipient_list=[to],
                fail_silently=False,
            )
            return True
        except Exception:
            logger.exception('email_send_failed', extra={'to': to})
            return False

    @staticmethod
    def send_sms(to: str, message: str) -> bool:
        logger.info('sms_send_stub', extra={'to': to, 'message': message[:160]})
        return True

    @staticmethod
    def send_whatsapp(to: str, message: str, template_id: str | None = None) -> bool:
        logger.info(
            'whatsapp_send_stub',
            extra={'to': to, 'template_id': template_id, 'message': message[:160]},
        )
        return True

    @staticmethod
    def send_push(user_id: str, title: str, body: str, data: dict[str, Any] | None = None) -> bool:
        logger.info('push_send_stub', extra={'user_id': user_id, 'title': title})
        return True

    @classmethod
    def send_notification(
        cls,
        user,
        title: str,
        message: str,
        channels: list[str] | None = None,
    ) -> bool:
        channels = channels or ['in_app']
        success = False
        email = getattr(user, 'email', None)
        phone = getattr(user, 'phone', None)
        user_id = str(getattr(user, 'pk', ''))

        if 'email' in channels and email:
            success = cls.send_email(email, title, message) or success
        if 'sms' in channels and phone:
            success = cls.send_sms(phone, message) or success
        if 'whatsapp' in channels and phone:
            success = cls.send_whatsapp(phone, message) or success
        if 'push' in channels and user_id:
            success = cls.send_push(user_id, title, message) or success
        if 'in_app' in channels:
            success = True
        return success


class PDFService:
    """Generate PDF documents."""

    @staticmethod
    def generate_simple_pdf(title: str, lines: list[str]) -> bytes:
        from reportlab.lib.pagesizes import A4
        from reportlab.pdfgen import canvas

        buffer = io.BytesIO()
        pdf = canvas.Canvas(buffer, pagesize=A4)
        pdf.setTitle(title)
        y = 800
        pdf.drawString(50, y, title)
        y -= 30
        for line in lines:
            pdf.drawString(50, y, line[:120])
            y -= 20
            if y < 50:
                pdf.showPage()
                y = 800
        pdf.save()
        buffer.seek(0)
        return buffer.read()


class ExcelService:
    """Generate Excel workbooks."""

    @staticmethod
    def generate_workbook(sheet_name: str, rows: list[dict[str, Any]]) -> bytes:
        from openpyxl import Workbook

        workbook = Workbook()
        worksheet = workbook.active
        worksheet.title = sheet_name[:31]
        if rows:
            headers = list(rows[0].keys())
            worksheet.append(headers)
            for row in rows:
                worksheet.append([row.get(header) for header in headers])
        stream = io.BytesIO()
        workbook.save(stream)
        stream.seek(0)
        return stream.read()


class QRCodeService:
    """Generate QR code images."""

    @staticmethod
    def generate(data: str) -> bytes:
        import qrcode

        qr = qrcode.QRCode(version=1, box_size=8, border=2)
        qr.add_data(data)
        qr.make(fit=True)
        image = qr.make_image(fill_color='black', back_color='white')
        stream = io.BytesIO()
        image.save(stream, format='PNG')
        stream.seek(0)
        return stream.read()

    @classmethod
    def generate_and_upload(cls, data: str, folder: str = 'qr-codes') -> str:
        content = ContentFile(cls.generate(data), name=f'{uuid.uuid4()}.png')
        return FileUploadService.upload(content, folder=folder)
