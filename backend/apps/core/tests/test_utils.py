from __future__ import annotations

from datetime import date
from decimal import Decimal
from io import BytesIO

import pytest
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile

from apps.core import utils


def test_generate_unique_code_prefix_and_length():
    code = utils.generate_unique_code('ENR', length=6)
    assert code.startswith('ENR-')
    assert len(code.split('-', 1)[1]) == 6


def test_get_client_ip_from_forwarded_header(rf):
    request = rf.get('/api/v1/', HTTP_X_FORWARDED_FOR='203.0.113.1, 198.51.100.2')
    assert utils.get_client_ip(request) == '203.0.113.1'


def test_get_client_ip_remote_addr(rf):
    request = rf.get('/api/v1/')
    request.META['REMOTE_ADDR'] = '127.0.0.1'
    assert utils.get_client_ip(request) == '127.0.0.1'


def test_validate_file_size_rejects_large_file():
    upload = SimpleUploadedFile('doc.pdf', b'12345', content_type='application/pdf')
    with pytest.raises(ValidationError):
        utils.validate_file_size(upload, max_size_mb=0)


def test_validate_file_extension_rejects_invalid_type():
    upload = SimpleUploadedFile('doc.exe', b'12345', content_type='application/octet-stream')
    with pytest.raises(ValidationError):
        utils.validate_file_extension(upload, allowed_extensions=['pdf', 'jpg'])


def test_format_indian_currency():
    assert utils.format_indian_currency(Decimal('123456.7')) == '₹1,23,456.70'
    assert utils.format_indian_currency('-1000') == '-₹1,000.00'


def test_calculate_age():
    today = date.today()
    dob = date(today.year - 20, today.month, today.day)
    assert utils.calculate_age(dob) == 20


def test_mask_aadhaar():
    assert utils.mask_aadhaar('1234-5678-9012') == 'XXXX-XXXX-9012'


def test_mask_aadhaar_invalid():
    with pytest.raises(ValidationError):
        utils.mask_aadhaar('123')


def test_generate_qr_code_returns_png_bytes():
    payload = utils.generate_qr_code('https://example.com/verify/abc')
    assert payload.startswith(b'\x89PNG')


def test_send_notification_delegates(monkeypatch):
    called = {}

    def fake_send(user, title, message, channels):
        called['user'] = user
        called['title'] = title
        called['channels'] = channels
        return True

    monkeypatch.setattr('apps.core.services.NotificationService.send_notification', fake_send)
    assert utils.send_notification(object(), 'Title', 'Body', channel='email') is True
    assert called['channels'] == ['email']
