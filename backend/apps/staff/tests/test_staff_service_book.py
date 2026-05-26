import pytest
from rest_framework.test import APIClient
from apps.staff.models import Designation, Staff, StaffServiceBook


def college(db):
    from apps.colleges.models import College
    return College.objects.create(name="SB College", code="SBC", is_active=True)

def department(db, college):
    from apps.colleges.models import Department
    return Department.objects.create(name="Physics", college=college, is_active=True)

@pytest.fixture
def designation_ap(db, college):
    return Designation.objects.create(name="Asst Prof", category="teaching", level=1, college=college)

@pytest.fixture
def designation_assoc(db, college):
    return Designation.objects.create(name="Assoc Prof", category="teaching", level=2, college=college)

@pytest.fixture
def admin_user(db):
    from apps.accounts.models import User
    return User.objects.create_user(email="sb_admin@t.com", password="x", role="STAFF", phone="9000000001", first_name="Test", last_name="User")

@pytest.fixture
def staff_member(db, admin_user, college, department, designation_ap):
    return Staff.objects.create(
        user=admin_user, college=college, department=department,
        designation=designation_ap, staff_type="teaching",
        appointment_type="regular", date_of_joining="2018-07-01",
    )

def auth_client(admin_user):
    client = APIClient()
    client.force_authenticate(user=admin_user)
    return client


class TestStaffServiceBook:
    def test_create_joining_entry(self, db, staff_member, designation_ap):
        entry = StaffServiceBook.objects.create(
            staff=staff_member, entry_type="joining",
            effective_date="2018-07-01",
            description="Initial joining",
            new_designation=designation_ap, new_pay=50000,
        )
        assert entry.id is not None
        assert entry.entry_type == "joining"

    def test_create_promotion_entry(self, db, staff_member, designation_ap, designation_assoc):
        entry = StaffServiceBook.objects.create(
            staff=staff_member, entry_type="promotion",
            effective_date="2023-01-01",
            description="Promoted",
            old_designation=designation_ap,
            new_designation=designation_assoc,
            old_pay=60000, new_pay=75000,
        )
        assert entry.new_designation == designation_assoc

    def test_service_book_str(self, db, staff_member):
        entry = StaffServiceBook.objects.create(
            staff=staff_member, entry_type="increment",
            effective_date="2022-01-01", description="Annual increment",
        )
        assert "increment" in str(entry)

    def test_entries_ordered_by_date(self, db, staff_member):
        StaffServiceBook.objects.create(
            staff=staff_member, entry_type="joining",
            effective_date="2018-07-01", description="Joined",
        )
        StaffServiceBook.objects.create(
            staff=staff_member, entry_type="increment",
            effective_date="2019-01-01", description="Increment",
        )
        entries = list(staff_member.service_book_entries.all())
        assert entries[0].effective_date > entries[1].effective_date

    def test_service_book_get_api(self, auth_client, staff_member):
        StaffServiceBook.objects.create(
            staff=staff_member, entry_type="joining",
            effective_date="2018-07-01", description="Joined",
        )
        r = auth_client.get(f"/api/v1/staff/{staff_member.id}/service-book/")
        assert r.status_code == 200
        assert len(r.data) >= 1

    def test_service_book_post_api(self, auth_client, staff_member):
        r = auth_client.post(
            f"/api/v1/staff/{staff_member.id}/service-book/",
            {"entry_type": "increment", "effective_date": "2024-01-01",
             "description": "Increment 2024"},
            format="json",
        )
        assert r.status_code == 201

    def test_service_book_post_missing_fields(self, auth_client, staff_member):
        r = auth_client.post(
            f"/api/v1/staff/{staff_member.id}/service-book/",
            {}, format="json",
        )
        assert r.status_code == 400

    def test_minio_path_field(self, db, staff_member):
        entry = StaffServiceBook.objects.create(
            staff=staff_member, entry_type="promotion",
            effective_date="2023-06-01", description="Promotion order",
            document="staff/orders/promo_2023.pdf",
        )
        assert "staff/orders" in entry.document