"""Smoke tests — extend per module as features land."""

from __future__ import annotations

import json

import pytest
from django.test import Client

from apps.accounts.models import User
from apps.core.pagination import StandardPagination


@pytest.mark.django_db
def test_admin_endpoint_responds() -> None:
    client = Client()
    response = client.get('/manage-portal/')
    assert response.status_code in {200, 302}


def test_health_endpoint_is_public(client: Client) -> None:
    response = client.get('/health/')
    assert response.status_code == 200
    payload = response.json()
    assert payload.get('status') == 'healthy'
    assert payload.get('version') == '2.0.0'


@pytest.mark.django_db
def test_create_user_with_required_fields() -> None:
    user = User.objects.create_user(
        email='student@example.com',
        phone='+15555555555',
        first_name='Test',
        last_name='Student',
        role='STUDENT',
        password='longsecurepass',
    )
    assert user.pk is not None
    assert user.email == 'student@example.com'


@pytest.mark.django_db
def test_login_success_returns_envelope_with_tokens(client: Client) -> None:
    """POST /api/v1/auth/login/ with valid credentials returns APIResponse + JWT."""
    User.objects.create_user(
        email='api_login_smoke@example.com',
        phone='+15559876543',
        first_name='Smok',
        last_name='Test',
        role='ADMIN',
        password='ValidPass2025!ab',
    )
    response = client.post(
        '/api/v1/auth/login/',
        data=json.dumps(
            {
                'email': 'api_login_smoke@example.com',
                'password': 'ValidPass2025!ab',
            }
        ),
        content_type='application/json',
    )
    assert response.status_code == 200
    body = response.json()
    assert body.get('success') is True
    assert 'data' in body
    assert 'access' in body['data']
    assert 'refresh' in body['data']
    assert 'user' in body['data']


@pytest.mark.django_db
def test_api_v1_root_lists_prefixes(client: Client) -> None:
    response = client.get('/api/v1/')
    assert response.status_code == 200
    body = response.json()
    assert body.get('success') is True
    assert '/api/v1/auth/' in body['data']['paths']


@pytest.mark.django_db
def test_login_endpoint_validation_errors(client: Client) -> None:
    response = client.post('/api/v1/auth/login/', {}, content_type='application/json')
    assert response.status_code == 400


def test_standard_pagination_limit_matches_spec() -> None:
    pagination = StandardPagination()
    assert pagination.page_size == 20
    assert pagination.max_page_size == 100
