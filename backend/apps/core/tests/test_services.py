from __future__ import annotations

from io import BytesIO
from unittest.mock import MagicMock, patch

import pytest
from django.core.cache import cache
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage

from apps.core.services import (
    CacheService,
    ExcelService,
    FileUploadService,
    NotificationService,
    PDFService,
    QRCodeService,
    SearchService,
)


@pytest.mark.django_db
def test_file_upload_service_stores_file():
    upload = ContentFile(b'hello', name='hello.txt')
    url = FileUploadService.upload(upload, folder='tests')
    assert url


def test_cache_service_prefix():
    cache.clear()
    CacheService.set('dashboard', {'ok': True}, timeout=60)
    assert CacheService.get('dashboard') == {'ok': True}
    CacheService.delete('dashboard')
    assert CacheService.get('dashboard') is None


def test_excel_service_generates_workbook():
    content = ExcelService.generate_workbook('Sheet1', [{'name': 'Alice', 'score': 90}])
    assert content.startswith(b'PK')


def test_pdf_service_generates_pdf():
    content = PDFService.generate_simple_pdf('Report', ['Line 1', 'Line 2'])
    assert content.startswith(b'%PDF')


def test_qr_code_service_generates_png():
    content = QRCodeService.generate('verify:123')
    assert content.startswith(b'\x89PNG')


def test_notification_service_email(monkeypatch):
    sent = {}

    def fake_send_mail(*args, **kwargs):
        sent['args'] = args
        sent['kwargs'] = kwargs
        return 1

    monkeypatch.setattr('django.core.mail.send_mail', fake_send_mail)
    user = MagicMock(email='user@example.com', phone='+919999999999', pk='1')
    assert NotificationService.send_notification(user, 'Hello', 'Body', channels=['email']) is True


@patch('apps.core.services.SearchService._client')
def test_search_service_index_and_search(mock_client):
    index = MagicMock()
    index.add_documents.return_value = {'taskUid': 1}
    index.search.return_value = {'hits': []}
    index.delete_documents.return_value = {'taskUid': 2}
    mock_client.return_value.index.return_value = index

    SearchService.index('students', [{'id': '1', 'name': 'A'}])
    SearchService.search('students', 'A')
    SearchService.delete('students', ['1'])
    assert index.add_documents.called
    assert index.search.called
    assert index.delete_documents.called
