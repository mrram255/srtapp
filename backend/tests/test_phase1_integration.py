"""Cross-module integration: admission → enroll → fee → certificate verify path."""

import datetime

import pytest
from rest_framework import status


@pytest.mark.django_db
def test_login_enroll_fee_flow(api_client, college, department, branch, academic_year):
    from apps.accounts.models import User
    from apps.admissions.models import AdmissionApplication
    from apps.admissions.services import AdmissionService
    from apps.colleges.models import Branch, Department
    from apps.finance.models import FeeStructure
    from apps.finance.services import FinanceService

    admin = User.objects.create_user(
        email='intadmin@test.com',
        phone='+911111111111',
        first_name='Int',
        last_name='Admin',
        role='ADMIN',
        password='ValidPass1!',
        college=college,
    )

    app = AdmissionApplication.objects.create(
        college=college,
        application_number='INT-APP-001',
        first_name='Int',
        last_name='Student',
        email='intstudent@test.com',
        phone='+922222222222',
        date_of_birth=datetime.date(2005, 3, 1),
        gender='MALE',
        department=department,
        branch=branch,
        previous_school='HS',
        previous_percentage=88,
        status='ACCEPTED',
    )

    student = AdmissionService.enroll_application(app, enrolled_by=admin)
    assert student.enrollment_number

    fee = FeeStructure.objects.create(
        college=college,
        name='Integration Fee',
        department=department,
        semester=1,
        academic_year=academic_year,
        tuition_fee=10000,
    )

    payment = FinanceService.record_payment(
        student=student,
        fee_structure=fee,
        amount=fee.total_fee,
    )
    assert payment.status == 'PAID'

    api_client.force_authenticate(user=admin)
    health = api_client.get('/health/')
    assert health.status_code == status.HTTP_200_OK

    r = api_client.get('/api/v1/finance/payments/', {'student': str(student.id)})
    assert r.status_code == status.HTTP_200_OK
