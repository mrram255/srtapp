import pytest
from rest_framework import status

from apps.audit.models import AuditLog


@pytest.mark.django_db
def test_audit_export_csv(api_client, super_admin_user):
    AuditLog.objects.create(module='authentication', action='login', object_repr='test')
    api_client.force_authenticate(user=super_admin_user)
    r = api_client.get('/api/v1/audit/export/')
    assert r.status_code == status.HTTP_200_OK
    assert 'text/csv' in r['Content-Type']
    assert b'module' in r.content
