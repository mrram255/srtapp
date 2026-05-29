import datetime

import pytest
from rest_framework import status

from apps.finance.models import PayrollRun, Payslip, SalaryStructure


@pytest.fixture
def staff_member(college, department):
    from apps.accounts.models import User
    from apps.staff.models import Designation, Staff

    user = User.objects.create_user(
        email='payrollstaff@college.edu',
        phone='+915555555555',
        first_name='Pay',
        last_name='Roll',
        role='STAFF',
        password='password',
        college=college,
    )
    designation = Designation.objects.create(college=college, name='Lecturer', category='teaching')
    return Staff.objects.create(
        user=user,
        college=college,
        department=department,
        designation=designation,
        employee_id='EMP-PAY-001',
        date_of_joining=datetime.date(2020, 1, 1),
    )


@pytest.mark.django_db
def test_create_salary_structure(api_client, accountant_user, staff_member):
    api_client.force_authenticate(user=accountant_user)
    r = api_client.post(
        '/api/v1/finance/payroll/structures/',
        {
            'staff': str(staff_member.id),
            'designation': 'Lecturer',
            'basic_salary': '50000',
            'hra': '10000',
        },
        format='json',
    )
    assert r.status_code == status.HTTP_201_CREATED


@pytest.mark.django_db
def test_process_payroll_run(api_client, accountant_user, staff_member, college):
    SalaryStructure.objects.create(
        college=college,
        staff=staff_member,
        designation='Lecturer',
        basic_salary=50000,
        hra=10000,
    )
    api_client.force_authenticate(user=accountant_user)
    r = api_client.post(
        '/api/v1/finance/payroll/runs/',
        {'month': 5, 'year': 2026},
        format='json',
    )
    assert r.status_code == status.HTTP_201_CREATED
    assert PayrollRun.objects.filter(college=college, month=5, year=2026).exists()
    assert Payslip.objects.filter(payroll_run__month=5).exists()


@pytest.mark.django_db
def test_list_payslips(api_client, accountant_user, staff_member, college):
    SalaryStructure.objects.create(
        college=college, staff=staff_member, designation='L', basic_salary=40000, hra=5000,
    )
    api_client.force_authenticate(user=accountant_user)
    api_client.post('/api/v1/finance/payroll/runs/', {'month': 4, 'year': 2026}, format='json')
    r = api_client.get('/api/v1/finance/payroll/payslips/')
    assert r.status_code == status.HTTP_200_OK
    assert len(r.data['data']) >= 1


@pytest.mark.django_db
def test_list_payroll_runs(api_client, accountant_user, college):
    PayrollRun.objects.create(college=college, month=1, year=2026, status='draft')
    api_client.force_authenticate(user=accountant_user)
    r = api_client.get('/api/v1/finance/payroll/runs/')
    assert r.status_code == status.HTTP_200_OK
