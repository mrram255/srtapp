import pytest
from rest_framework.test import APIClient
from apps.staff.models import Designation, Staff


def college(db):
    from apps.colleges.models import College
    return College.objects.create(name="Staff College", code="STC", is_active=True)

def department(db, college):
    from apps.colleges.models import Department
    return Department.objects.create(name="CS", college=college, is_active=True)

@pytest.fixture
def designation(db, college):
    return Designation.objects.create(
        name="Assistant Professor", category="teaching", level=1, college=college
    )

@pytest.fixture
def admin_user(db):
    from apps.accounts.models import User
    return User.objects.create_user(email="admin@staff.com", password="x", role="STAFF", phone="9000000011", first_name="Test", last_name="User")

def staff_user(db):
    from apps.accounts.models import User
    return User.objects.create_user(email="faculty@staff.com", password="x", role="STAFF", phone="9000000011", first_name="Test", last_name="User")

@pytest.fixture
def staff_member(db, staff_user, college, department, designation):
    return Staff.objects.create(
        user=staff_user, college=college, department=department,
        designation=designation, staff_type="teaching",
        appointment_type="regular", date_of_joining="2020-07-01",
    )

def auth_client(admin_user):
    client = APIClient()
    client.force_authenticate(user=admin_user)
    return client


class TestDesignation:
    def test_create_designation(self, db, college):
        d = Designation.objects.create(
            name="Professor", category="teaching", level=3, college=college
        )
        assert d.id is not None

    def test_designation_str(self, db, college):
        d = Designation.objects.create(
            name="Lecturer", category="teaching", level=1, college=college
        )
        assert "Lecturer" in str(d)

    def test_designation_unique_per_college(self, db, college):
        Designation.objects.create(name="Clerk", category="non_teaching", level=1, college=college)
        with pytest.raises(Exception):
            Designation.objects.create(name="Clerk", category="non_teaching", level=1, college=college)

    def test_designation_list_api(self, auth_client):
        r = auth_client.get("/api/v1/designations/")
        assert r.status_code == 200


class TestStaffModel:
    def test_employee_id_auto_generated(self, db, staff_member):
        assert staff_member.employee_id != ""

    def test_employee_id_starts_with_college_code(self, db, staff_member):
        assert staff_member.employee_id.startswith("STC")

    def test_staff_str(self, db, staff_member):
        assert staff_member.employee_id in str(staff_member)

    def test_staff_one_to_one_user(self, db, staff_user, college, department, designation):
        Staff.objects.create(
            user=staff_user, college=college, department=department,
            designation=designation, staff_type="teaching",
            appointment_type="regular", date_of_joining="2020-07-01",
        )
        with pytest.raises(Exception):
            Staff.objects.create(
                user=staff_user, college=college, department=department,
                staff_type="teaching", appointment_type="regular",
                date_of_joining="2021-07-01",
            )


class TestStaffAPI:
    def test_list_requires_auth(self):
        client = APIClient()
        assert client.get("/api/v1/staff/").status_code == 401

    def test_list_returns_200(self, auth_client, staff_member):
        assert auth_client.get("/api/v1/staff/").status_code == 200

    def test_retrieve_detail(self, auth_client, staff_member):
        r = auth_client.get(f"/api/v1/staff/{staff_member.id}/")
        assert r.status_code == 200
        assert r.data["employee_id"] == staff_member.employee_id

    def test_statistics_endpoint(self, auth_client, staff_member):
        r = auth_client.get("/api/v1/staff/statistics/")
        assert r.status_code == 200
        assert "total" in r.data

    def test_qualification_summary(self, auth_client):
        r = auth_client.get("/api/v1/staff/qualification-summary/")
        assert r.status_code == 200
        assert "phd_percentage" in r.data