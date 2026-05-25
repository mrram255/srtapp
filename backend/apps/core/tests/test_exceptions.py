from __future__ import annotations

import pytest
from rest_framework.exceptions import NotFound, PermissionDenied, ValidationError
from rest_framework.test import APIRequestFactory

from apps.core.exceptions import custom_exception_handler
from apps.core.pagination import LargePagination, SmallPagination, StandardPagination


def test_standard_pagination_defaults():
    pagination = StandardPagination()
    assert pagination.page_size == 20
    assert pagination.max_page_size == 100


def test_large_and_small_pagination_defaults():
    assert LargePagination().page_size == 50
    assert LargePagination().max_page_size == 500
    assert SmallPagination().page_size == 10


def test_custom_exception_handler_validation_error():
    exc = ValidationError({'email': ['Invalid email']})
    response = custom_exception_handler(exc, {'request': None, 'view': None})
    assert response.status_code == 400
    assert response.data['success'] is False
    assert response.data['error_code'] == 'VALIDATION_ERROR'
    assert 'email' in response.data['errors']


def test_custom_exception_handler_not_found():
    exc = NotFound('Missing')
    response = custom_exception_handler(exc, {'request': None, 'view': None})
    assert response.status_code == 404
    assert response.data['error_code'] == 'NOT_FOUND'


def test_custom_exception_handler_permission_denied():
    exc = PermissionDenied('Nope')
    response = custom_exception_handler(exc, {'request': None, 'view': None})
    assert response.status_code == 403
    assert response.data['error_code'] == 'PERMISSION_DENIED'
