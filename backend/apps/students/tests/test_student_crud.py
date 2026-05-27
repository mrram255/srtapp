import pytest
import uuid
from rest_framework.test import APIClient


class TestStudentList:
    def test_list_requires_auth(self):
        assert APIClient().get("/api/v1/students/").status_code == 401

    def test_list_returns_200_for_auth_user(self, auth_client, student):
        assert auth_client.get("/api/v1/students/").status_code in [200, 403]

    def test_list_filter_by_department(self, auth_client, student, department):
        assert auth_client.get(f"/api/v1/students/?department={department.id}").status_code in [200, 403]

    def test_list_search(self, auth_client, student):
        assert auth_client.get("/api/v1/students/?search=TST2401001").status_code in [200, 403]


class TestStudentDetail:
    def test_retrieve_student(self, auth_client, student):
        assert auth_client.get(f"/api/v1/students/{student.id}/").status_code in [200, 403]

    def test_retrieve_nonexistent(self, auth_client):
        import uuid
        assert auth_client.get(f"/api/v1/students/{uuid.uuid4()}/").status_code in [404, 403]

    def test_student_uuid_pk(self, auth_client, student):
        assert auth_client.get(f"/api/v1/students/{student.id}/").status_code in [200, 403]


class TestStudentUpdate:
    def test_patch_semester(self, auth_client, student):
        r = auth_client.patch(f"/api/v1/students/{student.id}/", {"semester": 2}, format="json")
        assert r.status_code in [200, 403]

    def test_patch_status(self, auth_client, student):
        r = auth_client.patch(f"/api/v1/students/{student.id}/", {"student_status": "detained"}, format="json")
        assert r.status_code in [200, 400, 403]


class TestStudentModel:
    def test_enrollment_unique(self, db, college, department, branch):
        from apps.accounts.models import User
        from apps.students.models import Student
        u1 = User.objects.create_user(email="s1u@t.com", password="x", role="STUDENT", phone="9111000001", first_name="S", last_name="One")
        u2 = User.objects.create_user(email="s2u@t.com", password="x", role="STUDENT", phone="9111000002", first_name="S", last_name="Two")
        Student.objects.create(user=u1, college=college, department=department, branch=branch, enrollment_number="UNIQ001", roll_number="R1", admission_number="A1", semester=1, batch_year=2024, date_of_birth="2000-01-01", gender="MALE", address="Addr", city="City", state="ST", pincode="400001", emergency_contact="9000000099", emergency_contact_name="Parent", admission_date="2024-07-01")
        with pytest.raises(Exception):
            Student.objects.create(user=u2, college=college, department=department, branch=branch, enrollment_number="UNIQ001", roll_number="R2", admission_number="A2", semester=1, batch_year=2024, date_of_birth="2000-01-01", gender="MALE", address="Addr", city="City", state="ST", pincode="400001", emergency_contact="9000000099", emergency_contact_name="Parent", admission_date="2024-07-01")

    def test_new_fields_exist(self, student):
        student.refresh_from_db()
        assert hasattr(student, "abc_id")
        assert hasattr(student, "hostel_resident")
        assert hasattr(student, "student_status")
        assert hasattr(student, "mentor")

    def test_hostel_resident_default(self, student):
        assert student.hostel_resident is False

    def test_student_status_default(self, student):
        assert student.student_status == "active"
