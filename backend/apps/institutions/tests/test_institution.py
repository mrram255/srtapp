from __future__ import annotations

import pytest

from apps.institutions.models import Institution, InstitutionSettings
from apps.institutions.tests.conftest import auth_client


@pytest.mark.django_db
class TestInstitutionCRUD:
    def test_list_institutions(self, api_client, super_admin_user):
        Institution.objects.create(name='Test College', code='TC01')
        client = auth_client(api_client, super_admin_user)
        response = client.get('/api/v1/institutions/')
        assert response.status_code == 200
        assert response.data['success'] is True
        assert len(response.data['data']) >= 1

    def test_create_institution(self, api_client, super_admin_user, college):
        client = auth_client(api_client, super_admin_user)
        response = client.post(
            '/api/v1/institutions/',
            {
                'name': 'SRT Institute',
                'code': 'SRTI',
                'college': str(college.id),
                'institution_type': 'affiliated',
                'city': 'Dhmari',
                'state': 'Maharashtra',
            },
            format='json',
        )
        assert response.status_code == 201
        assert Institution.objects.filter(code='SRTI').exists()
        assert InstitutionSettings.objects.filter(institution__code='SRTI').exists()

    def test_retrieve_institution(self, api_client, super_admin_user):
        inst = Institution.objects.create(name='Retrieve Test', code='RT01')
        client = auth_client(api_client, super_admin_user)
        response = client.get(f'/api/v1/institutions/{inst.id}/')
        assert response.status_code == 200
        assert response.data['data']['code'] == 'RT01'

    def test_update_institution(self, api_client, super_admin_user):
        inst = Institution.objects.create(name='Old Name', code='UP01')
        client = auth_client(api_client, super_admin_user)
        response = client.patch(
            f'/api/v1/institutions/{inst.id}/',
            {'name': 'New Name'},
            format='json',
        )
        assert response.status_code == 200
        inst.refresh_from_db()
        assert inst.name == 'New Name'

    def test_deactivate_institution(self, api_client, super_admin_user):
        inst = Institution.objects.create(name='Delete Test', code='DL01')
        client = auth_client(api_client, super_admin_user)
        response = client.delete(f'/api/v1/institutions/{inst.id}/')
        assert response.status_code == 200
        inst.refresh_from_db()
        assert inst.is_active is False

    def test_search_institutions(self, api_client, super_admin_user):
        Institution.objects.create(name='Alpha College', code='ALP')
        Institution.objects.create(name='Beta College', code='BET')
        client = auth_client(api_client, super_admin_user)
        response = client.get('/api/v1/institutions/?search=Alpha')
        assert response.status_code == 200
        codes = [row['code'] for row in response.data['data']]
        assert 'ALP' in codes
        assert 'BET' not in codes


@pytest.mark.django_db
class TestInstitutionSettings:
    def test_get_settings(self, api_client, super_admin_user):
        inst = Institution.objects.create(name='Settings College', code='SC01')
        InstitutionSettings.objects.create(institution=inst)
        client = auth_client(api_client, super_admin_user)
        response = client.get('/api/v1/institutions/settings/')
        assert response.status_code == 200
        assert response.data['data']['grading_system'] == 'CGPA_10'

    def test_patch_settings(self, api_client, super_admin_user):
        inst = Institution.objects.create(name='Patch College', code='PC01')
        InstitutionSettings.objects.create(institution=inst, attendance_minimum_percentage=75)
        client = auth_client(api_client, super_admin_user)
        response = client.patch(
            '/api/v1/institutions/settings/',
            {'attendance_minimum_percentage': '80.00'},
            format='json',
        )
        assert response.status_code == 200
        settings = InstitutionSettings.objects.get(institution=inst)
        assert float(settings.attendance_minimum_percentage) == 80.0

    def test_institution_detail_settings_action(self, api_client, super_admin_user):
        inst = Institution.objects.create(name='Action College', code='AC01')
        settings = InstitutionSettings.objects.create(institution=inst)
        client = auth_client(api_client, super_admin_user)
        response = client.get(f'/api/v1/institutions/{inst.id}/settings/')
        assert response.status_code == 200
        assert response.data['data']['id'] == str(settings.id)

    def test_create_institution_requires_super_admin(self, api_client, db, college):
        from apps.institutions.tests.conftest import auth_client as _auth
        from django.contrib.auth import get_user_model
        from apps.users.models import Role

        User = get_user_model()
        role = Role.objects.filter(name='teacher').first()
        teacher = User.objects.create_user(
            email='teacher_inst@example.com',
            phone='+919944444444',
            first_name='T',
            last_name='User',
            role='TEACHER',
            role_ref=role,
            password='ValidPass1!',
        )
        client = _auth(api_client, teacher)
        response = client.post(
            '/api/v1/institutions/',
            {'name': 'Blocked', 'code': 'BLK'},
            format='json',
        )
        assert response.status_code == 403

    def test_settings_requires_super_admin_for_patch(self, api_client, db):
        from apps.institutions.tests.conftest import auth_client as _auth
        from django.contrib.auth import get_user_model
        from apps.users.models import Role

        User = get_user_model()
        role = Role.objects.filter(name='teacher').first()
        teacher = User.objects.create_user(
            email='teacher_s4@example.com',
            phone='+919922222222',
            first_name='T',
            last_name='User',
            role='TEACHER',
            role_ref=role,
            password='ValidPass1!',
        )
        inst = Institution.objects.create(name='Perm College', code='PR01')
        InstitutionSettings.objects.create(institution=inst)
        client = _auth(api_client, teacher)
        response = client.patch('/api/v1/institutions/settings/', {'sms_enabled': True}, format='json')
        assert response.status_code == 403
