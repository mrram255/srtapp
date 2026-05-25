from __future__ import annotations

import io

import pytest
from django.contrib.auth import get_user_model
from openpyxl import Workbook
from rest_framework.test import APIClient

from apps.users.models import Role, UserActivity
from apps.users.services import RoleService, UserService

User = get_user_model()


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def rbac_data(db):
    return {
        'super_admin': Role.objects.get(name='super_admin'),
        'teacher': Role.objects.get(name='teacher'),
        'student': Role.objects.get(name='student'),
    }


def auth_client(api_client, user):
    api_client.force_authenticate(user=user)
    return api_client


def create_user(role_name='teacher', email=None, **kwargs):
    role = Role.objects.filter(name=role_name).first()
    defaults = {
        'email': email or f'{role_name}_{User.objects.count()}@example.com',
        'phone': f'+9199{User.objects.count():08d}',
        'first_name': 'Test',
        'last_name': 'User',
        'role': role.name.upper() if role else role_name.upper(),
        'role_ref': role,
        'password': 'ValidPass1!',
    }
    defaults.update(kwargs)
    password = defaults.pop('password')
    user = User.objects.create_user(**defaults)
    user.set_password(password)
    user.save()
    return user


@pytest.mark.django_db
class TestUserCRUD:
    def test_list_users_as_super_admin(self, api_client, rbac_data):
        admin = create_user('super_admin', email='admin@example.com', phone='+919900000001')
        create_user('teacher', email='teacher@example.com', phone='+919900000002')
        client = auth_client(api_client, admin)
        response = client.get('/api/v1/users/')
        assert response.status_code == 200
        assert response.data['success'] is True
        assert len(response.data['data']) >= 2

    def test_create_user(self, api_client, rbac_data):
        admin = create_user('super_admin', email='admin2@example.com', phone='+919900000010')
        client = auth_client(api_client, admin)
        response = client.post(
            '/api/v1/users/',
            {
                'email': 'newuser@example.com',
                'phone': '+919900000011',
                'first_name': 'New',
                'last_name': 'User',
                'role_ref': rbac_data['teacher'].id,
                'password': 'ValidPass1!',
            },
            format='json',
        )
        assert response.status_code == 201
        assert User.objects.filter(email='newuser@example.com').exists()

    def test_get_user_detail(self, api_client, rbac_data):
        admin = create_user('super_admin', email='admin3@example.com', phone='+919900000020')
        target = create_user('teacher', email='detail@example.com', phone='+919900000021')
        client = auth_client(api_client, admin)
        response = client.get(f'/api/v1/users/{target.id}/')
        assert response.status_code == 200
        assert response.data['data']['email'] == 'detail@example.com'

    def test_update_user(self, api_client, rbac_data):
        admin = create_user('super_admin', email='admin4@example.com', phone='+919900000030')
        target = create_user('teacher', email='update@example.com', phone='+919900000031')
        client = auth_client(api_client, admin)
        response = client.patch(
            f'/api/v1/users/{target.id}/',
            {'first_name': 'Updated'},
            format='json',
        )
        assert response.status_code == 200
        target.refresh_from_db()
        assert target.first_name == 'Updated'

    def test_soft_delete_user(self, api_client, rbac_data):
        admin = create_user('super_admin', email='admin5@example.com', phone='+919900000040')
        target = create_user('teacher', email='delete@example.com', phone='+919900000041')
        client = auth_client(api_client, admin)
        response = client.delete(f'/api/v1/users/{target.id}/')
        assert response.status_code == 200
        target.refresh_from_db()
        assert target.is_deleted is True
        assert target.is_active is False

    def test_filter_users_by_role(self, api_client, rbac_data):
        admin = create_user('super_admin', email='admin6@example.com', phone='+919900000050')
        create_user('teacher', email='tfilter@example.com', phone='+919900000051')
        create_user('student', email='sfilter@example.com', phone='+919900000052')
        client = auth_client(api_client, admin)
        response = client.get('/api/v1/users/?role=STUDENT')
        assert response.status_code == 200
        emails = [row['email'] for row in response.data['data']]
        assert 'sfilter@example.com' in emails

    def test_reset_password(self, api_client, rbac_data):
        admin = create_user('super_admin', email='admin7@example.com', phone='+919900000060')
        target = create_user('teacher', email='reset@example.com', phone='+919900000061')
        client = auth_client(api_client, admin)
        response = client.post(f'/api/v1/users/{target.id}/reset-password/', {'password': 'NewPass1!'}, format='json')
        assert response.status_code == 200
        target.refresh_from_db()
        assert target.check_password('NewPass1!')

    def test_toggle_2fa(self, api_client, rbac_data):
        admin = create_user('super_admin', email='admin8@example.com', phone='+919900000070')
        target = create_user('teacher', email='2fa@example.com', phone='+919900000071')
        client = auth_client(api_client, admin)
        response = client.post(f'/api/v1/users/{target.id}/toggle-2fa/')
        assert response.status_code == 200
        target.refresh_from_db()
        assert target.two_factor_enabled is True


@pytest.mark.django_db
class TestBulkCreate:
    def _build_excel(self, rows):
        wb = Workbook()
        ws = wb.active
        ws.append(['email', 'phone', 'first_name', 'last_name', 'role', 'password'])
        for row in rows:
            ws.append(row)
        buffer = io.BytesIO()
        wb.save(buffer)
        buffer.seek(0)
        return buffer

    def test_bulk_import_valid_rows(self, api_client, rbac_data):
        admin = create_user('super_admin', email='bulk@example.com', phone='+919900000080')
        client = auth_client(api_client, admin)
        excel = self._build_excel(
            [
                ['bulk1@example.com', '+919900000081', 'Bulk', 'One', 'teacher', 'ValidPass1!'],
                ['bulk2@example.com', '+919900000082', 'Bulk', 'Two', 'teacher', 'ValidPass1!'],
            ]
        )
        response = client.post('/api/v1/users/bulk-create/', {'file': excel}, format='multipart')
        assert response.status_code == 200
        assert response.data['data']['created'] == 2

    def test_bulk_import_invalid_header(self, api_client, rbac_data):
        admin = create_user('super_admin', email='bulkbad@example.com', phone='+919900000090')
        client = auth_client(api_client, admin)
        wb = Workbook()
        ws = wb.active
        ws.append(['email', 'phone'])
        buffer = io.BytesIO()
        wb.save(buffer)
        buffer.seek(0)
        response = client.post('/api/v1/users/bulk-create/', {'file': buffer}, format='multipart')
        assert response.status_code == 400


@pytest.mark.django_db
class TestRoles:
    def test_list_roles(self, api_client, rbac_data):
        admin = create_user('super_admin', email='roles@example.com', phone='+919900000100')
        client = auth_client(api_client, admin)
        response = client.get('/api/v1/roles/')
        assert response.status_code == 200
        assert response.data['meta']['total'] >= 28

    def test_create_custom_role(self, api_client, rbac_data):
        admin = create_user('super_admin', email='rolecreate@example.com', phone='+919900000101')
        client = auth_client(api_client, admin)
        response = client.post(
            '/api/v1/roles/',
            {'name': 'custom_role', 'display_name': 'Custom Role', 'permissions': []},
            format='json',
        )
        assert response.status_code == 201
        assert Role.objects.filter(name='custom_role').exists()

    def test_cannot_delete_system_role(self, api_client, rbac_data):
        admin = create_user('super_admin', email='roledelete@example.com', phone='+919900000102')
        role = rbac_data['super_admin']
        client = auth_client(api_client, admin)
        response = client.delete(f'/api/v1/roles/{role.id}/')
        assert response.status_code == 403

    def test_set_role_permissions(self, api_client, rbac_data):
        admin = create_user('super_admin', email='roleperm@example.com', phone='+919900000103')
        role = Role.objects.create(name='perm_role', display_name='Perm Role')
        perm_ids = list(rbac_data['teacher'].permissions.values_list('id', flat=True)[:3])
        client = auth_client(api_client, admin)
        response = client.post(f'/api/v1/roles/{role.id}/permissions/', {'permissions': perm_ids}, format='json')
        assert response.status_code == 200
        assert role.permissions.count() == 3

    def test_clone_role(self, api_client, rbac_data):
        admin = create_user('super_admin', email='roleclone@example.com', phone='+919900000104')
        source = rbac_data['teacher']
        client = auth_client(api_client, admin)
        response = client.post(
            f'/api/v1/roles/{source.id}/clone/',
            {'name': 'teacher_clone', 'display_name': 'Teacher Clone'},
            format='json',
        )
        assert response.status_code == 201
        assert Role.objects.filter(name='teacher_clone').exists()


@pytest.mark.django_db
class TestPermissions:
    def test_super_admin_has_all_permissions(self, rbac_data):
        admin = create_user('super_admin', email='permadmin@example.com', phone='+919900000110')
        assert admin.has_module_permission('users', 'delete') is True
        assert admin.has_module_permission('finance', 'approve') is True

    def test_teacher_limited_permissions(self, rbac_data):
        teacher = create_user('teacher', email='permteacher@example.com', phone='+919900000111')
        assert teacher.has_module_permission('attendance', 'edit') is True
        assert teacher.has_module_permission('users', 'create') is False

    def test_student_read_only_modules(self, rbac_data):
        student = create_user('student', email='permstudent@example.com', phone='+919900000112')
        assert student.has_module_permission('dashboard', 'view') is True
        assert student.has_module_permission('students', 'create') is False

    def test_user_service_accessible_modules(self, rbac_data):
        teacher = create_user('teacher', email='modules@example.com', phone='+919900000113')
        modules = UserService.get_accessible_modules(teacher)
        names = {item['name'] for item in modules}
        assert 'dashboard' in names
        assert 'attendance' in names


@pytest.mark.django_db
class TestRBAC:
    def test_teacher_cannot_list_users(self, api_client, rbac_data):
        teacher = create_user('teacher', email='rbac1@example.com', phone='+919900000120')
        client = auth_client(api_client, teacher)
        response = client.get('/api/v1/users/')
        assert response.status_code == 403

    def test_super_admin_can_list_users(self, api_client, rbac_data):
        admin = create_user('super_admin', email='rbac2@example.com', phone='+919900000121')
        client = auth_client(api_client, admin)
        response = client.get('/api/v1/users/')
        assert response.status_code == 200

    def test_student_cannot_create_users(self, api_client, rbac_data):
        student = create_user('student', email='rbac3@example.com', phone='+919900000122')
        client = auth_client(api_client, student)
        response = client.post(
            '/api/v1/users/',
            {
                'email': 'blocked@example.com',
                'phone': '+919900000123',
                'first_name': 'Blocked',
                'last_name': 'User',
                'role_ref': rbac_data['student'].id,
            },
            format='json',
        )
        assert response.status_code == 403


@pytest.mark.django_db
class TestProfile:
    def test_get_profile(self, api_client, rbac_data):
        user = create_user('teacher', email='profile@example.com', phone='+919900000130')
        client = auth_client(api_client, user)
        response = client.get('/api/v1/profile/')
        assert response.status_code == 200
        assert response.data['data']['email'] == 'profile@example.com'

    def test_update_profile(self, api_client, rbac_data):
        user = create_user('teacher', email='profile2@example.com', phone='+919900000131')
        client = auth_client(api_client, user)
        response = client.patch('/api/v1/profile/', {'city': 'Delhi'}, format='json')
        assert response.status_code == 200
        user.refresh_from_db()
        assert user.city == 'Delhi'


@pytest.mark.django_db
class TestActivity:
    def test_create_user_logs_activity(self, rbac_data):
        admin = create_user('super_admin', email='activity@example.com', phone='+919900000140')
        UserService.create_user(
            {
                'email': 'logged@example.com',
                'phone': '+919900000141',
                'first_name': 'Logged',
                'last_name': 'User',
                'role_ref': rbac_data['teacher'],
                'password': 'ValidPass1!',
            },
            created_by=admin,
        )
        assert UserActivity.objects.filter(user=admin, action='create', module='users').exists()

    def test_user_activity_endpoint(self, api_client, rbac_data):
        admin = create_user('super_admin', email='activity2@example.com', phone='+919900000142')
        target = create_user('teacher', email='activitytarget@example.com', phone='+919900000143')
        UserService.log_activity(admin, 'view', module='users', description='Viewed user', request=None)
        client = auth_client(api_client, admin)
        response = client.get(f'/api/v1/users/{target.id}/activity/')
        assert response.status_code == 200


@pytest.mark.django_db
class TestModules:
    def test_list_modules(self, api_client, rbac_data):
        admin = create_user('super_admin', email='modules@example.com', phone='+919900000150')
        client = auth_client(api_client, admin)
        response = client.get('/api/v1/modules/')
        assert response.status_code == 200
        assert len(response.data['data']) >= 10

    def test_export_users(self, api_client, rbac_data):
        admin = create_user('super_admin', email='export@example.com', phone='+919900000151')
        create_user('teacher', email='exportt@example.com', phone='+919900000152')
        client = auth_client(api_client, admin)
        response = client.get('/api/v1/users/export/')
        assert response.status_code == 200
        assert response['Content-Type'].startswith('application/vnd.openxmlformats')

    def test_import_template(self, api_client, rbac_data):
        admin = create_user('super_admin', email='template@example.com', phone='+919900000153')
        client = auth_client(api_client, admin)
        response = client.get('/api/v1/users/import-template/')
        assert response.status_code == 200


@pytest.mark.django_db
class TestRoleService:
    def test_permission_matrix(self, rbac_data):
        matrix = RoleService.get_role_permissions_matrix(rbac_data['teacher'])
        assert len(matrix) > 0
        assert any(row['assigned'] for row in matrix)

    def test_change_role_via_api(self, api_client, rbac_data):
        admin = create_user('super_admin', email='changerole@example.com', phone='+919900000160')
        target = create_user('teacher', email='changerolet@example.com', phone='+919900000161')
        client = auth_client(api_client, admin)
        response = client.post(
            f'/api/v1/users/{target.id}/change-role/',
            {'role_id': rbac_data['student'].id},
            format='json',
        )
        assert response.status_code == 200
        target.refresh_from_db()
        assert target.role_ref_id == rbac_data['student'].id

    def test_bulk_activate_deactivate(self, api_client, rbac_data):
        admin = create_user('super_admin', email='bulkact@example.com', phone='+919900000170')
        u1 = create_user('teacher', email='bulkact1@example.com', phone='+919900000171')
        u2 = create_user('teacher', email='bulkact2@example.com', phone='+919900000172')
        client = auth_client(api_client, admin)
        deactivate = client.post('/api/v1/users/bulk-deactivate/', {'user_ids': [str(u1.id), str(u2.id)]}, format='json')
        assert deactivate.status_code == 200
        activate = client.post('/api/v1/users/bulk-activate/', {'user_ids': [str(u1.id), str(u2.id)]}, format='json')
        assert activate.status_code == 200

    def test_masked_aadhaar_on_user(self, rbac_data):
        user = create_user('teacher', email='aadhaar@example.com', phone='+919900000180')
        user.aadhaar_number = '123456789012'
        assert '9012' in user.get_masked_aadhaar() or user.get_masked_aadhaar().endswith('9012')

    def test_field_permission_super_admin(self, rbac_data):
        admin = create_user('super_admin', email='field@example.com', phone='+919900000181')
        assert admin.has_field_permission('users', 'aadhaar_number', 'edit') is True
