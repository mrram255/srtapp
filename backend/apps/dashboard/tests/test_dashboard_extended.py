import pytest
from rest_framework import status

from apps.dashboard.services import DashboardService


@pytest.mark.django_db
def test_student_cannot_access_super_admin_dashboard(api_client, college):
    from apps.accounts.models import User

    user = User.objects.create_user(
        email='stu@dash.edu',
        phone='+911111111111',
        first_name='S',
        last_name='T',
        role='STUDENT',
        password='password',
        college=college,
    )
    api_client.force_authenticate(user=user)
    r = api_client.get('/api/v1/dashboard/super-admin/')
    assert r.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_monthly_trends_structure(api_client, admin_user):
    api_client.force_authenticate(user=admin_user)
    r = api_client.get('/api/v1/dashboard/super-admin/')
    trend = r.data['data']['monthly_trends'][0]
    assert 'month' in trend
    assert 'fees_collected' in trend
    assert 'admissions' in trend


@pytest.mark.django_db
def test_fee_by_status_in_payload(api_client, admin_user):
    api_client.force_authenticate(user=admin_user)
    r = api_client.get('/api/v1/dashboard/super-admin/')
    assert 'fee_by_status' in r.data['data']


@pytest.mark.django_db
def test_principal_governance_counts(api_client, principal_user, college):
    from apps.governance.models import ApprovalRequest

    ApprovalRequest.objects.create(
        college=college,
        title='Pending',
        requested_by=principal_user,
        status='pending',
    )
    api_client.force_authenticate(user=principal_user)
    r = api_client.get('/api/v1/dashboard/principal/')
    assert r.data['data']['governance']['pending_approvals'] >= 1


@pytest.mark.django_db
def test_set_and_get_cache(college):
    DashboardService.set_cached('super_admin', college, {'test': True})
    assert DashboardService.get_cached('super_admin', college)['test'] is True


@pytest.mark.django_db
def test_alerts_when_defaulters(api_client, admin_user, college, department):
    from apps.accounts.models import User
    from apps.colleges.models import AcademicYear, Branch
    from apps.finance.models import FeePayment, FeeStructure
    from apps.students.models import Student

    ay = AcademicYear.objects.create(
        college=college,
        year='2025-2026',
        start_date='2025-06-01',
        end_date='2026-05-31',
        is_current=True,
    )
    br = Branch.objects.create(
        college=college, department=department, name='CSE', code='CSE', duration_years=4, total_semesters=8,
    )
    user = User.objects.create_user(
        email='def@college.edu', phone='+917777777777', first_name='D', last_name='F',
        role='STUDENT', password='p', college=college,
    )
    student = Student.objects.create(
        user=user, college=college, department=department, branch=br, academic_year=ay,
        enrollment_number='DEF001', roll_number='R1', semester=1, section='A', batch_year=2025,
        date_of_birth='2005-01-01', gender='MALE', address='A', city='C', state='S', pincode='1',
        emergency_contact='+91', emergency_contact_name='P', admission_date='2023-07-01', admission_number='A1',
    )
    fee = FeeStructure.objects.create(
        college=college, name='F', department=department, semester=1, academic_year=ay, tuition_fee=50000,
    )
    FeePayment.objects.create(
        college=college,
        student=student,
        fee_structure=fee,
        amount_due=50000,
        amount_paid=0,
        due_date='2026-06-01',
        status='PENDING',
    )
    payload = DashboardService.build_super_admin_payload(college)
    assert any(a['id'] == 'fee-defaulters' for a in payload['alerts'])


@pytest.mark.django_db
def test_generated_at_timestamp(api_client, admin_user):
    api_client.force_authenticate(user=admin_user)
    r = api_client.get('/api/v1/dashboard/super-admin/')
    assert 'generated_at' in r.data['data']
