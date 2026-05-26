import pytest


@pytest.fixture
def college(db):
    from apps.colleges.models import College
    return College.objects.create(
        name="Test College", code="TST",
        address="123 Main St", city="Mumbai",
        state="Maharashtra", pincode="400001",
        phone="9999999999", email="college@test.com",
        established_year=2000, is_active=True,
    )


@pytest.fixture
def department(db, college):
    from apps.colleges.models import Department
    return Department.objects.create(
        name="Computer Science", code="CS",
        college=college, is_active=True,
    )


@pytest.fixture
def branch(db, college, department):
    from apps.colleges.models import Branch
    return Branch.objects.create(
        name="CSE", code="CSE",
        department=department, college=college,
        duration_years=4, total_semesters=8,
        is_active=True,
    )


def make_user(email, role, n=1):
    from apps.accounts.models import User
    return User.objects.create_user(
        email=email, password="testpass123", role=role,
        phone=f"900000{n:04d}",
        first_name="Test", last_name="User",
    )


@pytest.fixture
def staff_user(db):
    return make_user("staff@test.com", "STAFF", n=1)


@pytest.fixture
def student_user(db):
    return make_user("student@test.com", "STUDENT", n=2)


@pytest.fixture
def student(db, student_user, college, department, branch):
    from apps.students.models import Student
    return Student.objects.create(
        user=student_user, college=college,
        department=department, branch=branch,
        enrollment_number="TST2401001", roll_number="CSE001",
        admission_number="ADM2401001", current_semester=1,
    )


@pytest.fixture
def auth_client(staff_user):
    from rest_framework.test import APIClient
    client = APIClient()
    client.force_authenticate(user=staff_user)
    return client
