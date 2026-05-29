import pytest
from rest_framework import status

from apps.core.services import CacheService
from apps.dashboard.services import DashboardService


@pytest.mark.django_db
def test_super_admin_dashboard_requires_auth(api_client):
    r = api_client.get('/api/v1/dashboard/super-admin/')
    assert r.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
def test_admin_gets_super_admin_dashboard(api_client, admin_user, college):
    api_client.force_authenticate(user=admin_user)
    r = api_client.get('/api/v1/dashboard/super-admin/')
    assert r.status_code == status.HTTP_200_OK
    data = r.data['data']
    assert 'kpis' in data
    assert 'naac_radar' in data
    assert 'heatmap' in data
    assert 'alerts' in data
    assert 'monthly_trends' in data
    assert len(data['monthly_trends']) == 12


@pytest.mark.django_db
def test_dashboard_uses_cache(api_client, admin_user, college):
    api_client.force_authenticate(user=admin_user)
    api_client.get('/api/v1/dashboard/super-admin/')
    cached = DashboardService.get_cached('super_admin', college)
    assert cached is not None
    assert 'kpis' in cached


@pytest.mark.django_db
def test_refresh_bypasses_cache(api_client, admin_user):
    api_client.force_authenticate(user=admin_user)
    r = api_client.get('/api/v1/dashboard/super-admin/?refresh=true')
    assert r.status_code == status.HTTP_200_OK
    assert r.data['data'].get('from_cache') is False


@pytest.mark.django_db
def test_principal_dashboard(api_client, principal_user):
    api_client.force_authenticate(user=principal_user)
    r = api_client.get('/api/v1/dashboard/principal/')
    assert r.status_code == status.HTTP_200_OK
    assert 'governance' in r.data['data']


@pytest.mark.django_db
def test_principal_dashboard_requires_college(api_client, college):
    from apps.accounts.models import User

    user = User.objects.create_user(
        email='noprincipal@college.edu',
        phone='+914444444444',
        first_name='No',
        last_name='College',
        role='PRINCIPAL',
        password='password',
    )
    api_client.force_authenticate(user=user)
    r = api_client.get('/api/v1/dashboard/principal/')
    assert r.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_dashboard_service_build_payload(college):
    payload = DashboardService.build_super_admin_payload(college)
    assert payload['kpis']['total_students'] == 0
    assert len(payload['naac_radar']) >= 5


@pytest.mark.django_db
def test_refresh_dashboard_cache_task(college):
    from apps.dashboard.tasks import refresh_dashboard_cache_task

    result = refresh_dashboard_cache_task(str(college.id))
    assert result['refreshed'] >= 1


@pytest.mark.django_db
def test_cache_service_roundtrip():
    CacheService.set('test:key', {'a': 1}, 60)
    assert CacheService.get('test:key') == {'a': 1}
