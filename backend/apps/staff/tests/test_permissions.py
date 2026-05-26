import pytest
from rest_framework.test import APIClient
from apps.staff.models import Designation, Staff


def college(db):
    from apps.colleges.models import College
    return College.objects.create(name="Perm College", code="PRC", is_active=True)

def department(db, college):
    from apps.colleges.models import Department
    return Department.objects.create(name="Math", college=college, is_active=True)

@pytest.fixture
def designation(db, college):
    return Designation.objects.create(name="Lecturer", category="teaching", level=1, college=college)

def student_user(db):
    from apps.accounts.models import User
    return User.objects.create_user(email="perm_stu@t.com", password="x", role="STUDENT", phone="9000000001", first_name="Test", last_name="User")

@pytest.fixture
def staff_admin(db):
    from apps.accounts.models import User
    return User.objects.create_user(email="perm_admin@t.com", password="x", role="STAFF", phone="9000000001", first_name="Test", last_name="User")

@pytest.fixture
def staff_member(db, staff_admin, college, department, designation):
    return Staff.objects.create(
        user=staff_admin, college=college, department=department,
        designation=designation, staff_type="teaching",
        appointment_type="regular", date_of_joining="2020-01-01",
    )


class TestPermissions:
    def test_unauthenticated_cannot_list_students(self):
        assert APIClient().get("/api/v1/students/").status_code == 401

    def test_unauthenticated_cannot_list_staff(self):
        assert APIClient().get("/api/v1/staff/").status_code == 401

    def test_unauthenticated_cannot_access_statistics(self):
        assert APIClient().get("/api/v1/staff/statistics/").status_code == 401

    def test_unauthenticated_cannot_access_service_book(self, staff_member):
        assert APIClient().get(f"/api/v1/staff/{staff_member.id}/service-book/").status_code == 401

    def test_unauthenticated_cannot_access_designations(self):
        assert APIClient().get("/api/v1/designations/").status_code == 401

    def test_staff_can_list_staff(self, staff_admin, staff_member):
        client = APIClient()
        client.force_authenticate(user=staff_admin)
        assert client.get("/api/v1/staff/").status_code == 200

    def test_staff_can_access_designations(self, staff_admin):
        client = APIClient()
        client.force_authenticate(user=staff_admin)
        assert client.get("/api/v1/designations/").status_code == 200