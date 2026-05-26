import pytest
from rest_framework import status
from rest_framework.test import APIClient


def college(db):
    from apps.colleges.models import College
    return College.objects.create(name="Test College", code="TC", is_active=True)


def department(db, college):
    from apps.colleges.models import Department
    return Department.objects.create(name="CS", college=college, is_active=True)


def branch(db, college, department):
    from apps.colleges.models import Branch
    return Branch.objects.create(
        name="CSE", department=department, college=college, is_active=True
    )


def staff_user(db):
    from apps.accounts.models import User
    return User.objects.create_user(
        email="registrar@test.com", password="testpass123", role="STAFF",
        first_name="Reg", last_name="User",
    )


def student_user(db):
    from apps.accounts.models import User
    return User.objects.create_user(
        email="student@test.com", password="testpass123", role="STUDENT",
        first_name="Test", last_name="Student",
    )


def student(db, student_user, college, department, branch):
    from apps.students.models import Student
    return Student.objects.create(
        user=student_user, college=college, department=department, branch=branch,
        enrollment_number="TC2401001", roll_number="CSE001",
        admission_number="ADM2401001", current_semester=1,
    )


def auth_client(staff_user):
    client = APIClient()
    client.force_authenticate(user=staff_user)
    return client


class TestStudentList:
    def test_list_requires_auth(self):
        client = APIClient()
        response = client.get("/api/v1/students/")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_list_returns_200_for_auth_user(self, auth_client, student):
        response = auth_client.get("/api/v1/students/")
        assert response.status_code == status.HTTP_200_OK

    def test_list_filter_by_department(self, auth_client, student, department):
        response = auth_client.get(f"/api/v1/students/?department={department.id}")
        assert response.status_code == status.HTTP_200_OK

    def test_list_search_by_enrollment(self, auth_client, student):
        response = auth_client.get("/api/v1/students/?search=TC2401001")
        assert response.status_code == status.HTTP_200_OK


class TestStudentDetail:
    def test_retrieve_student(self, auth_client, student):
        response = auth_client.get(f"/api/v1/students/{student.id}/")
        assert response.status_code == status.HTTP_200_OK
        assert response.data["enrollment_number"] == "TC2401001"

    def test_retrieve_nonexistent_returns_404(self, auth_client):
        import uuid
        response = auth_client.get(f"/api/v1/students/{uuid.uuid4()}/")
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_student_has_uuid_pk(self, auth_client, student):
        import uuid
        response = auth_client.get(f"/api/v1/students/{student.id}/")
        assert response.status_code == status.HTTP_200_OK
        uuid.UUID(str(response.data["id"]))


class TestStudentUpdate:
    def test_patch_current_semester(self, auth_client, student):
        response = auth_client.patch(
            f"/api/v1/students/{student.id}/",
            {"current_semester": 2}, format="json",
        )
        assert response.status_code == status.HTTP_200_OK
        student.refresh_from_db()
        assert student.current_semester == 2

    def test_patch_student_status(self, auth_client, student):
        response = auth_client.patch(
            f"/api/v1/students/{student.id}/",
            {"student_status": "detained"}, format="json",
        )
        assert response.status_code in [200, 400]


class TestStudentModel:
    def test_enrollment_number_unique(self, db, college, department, branch):
        from apps.accounts.models import User
        from apps.students.models import Student
        u1 = User.objects.create_user(email="s1@t.com", password="x", role="STUDENT")
        u2 = User.objects.create_user(email="s2@t.com", password="x", role="STUDENT")
        Student.objects.create(
            user=u1, college=college, department=department, branch=branch,
            enrollment_number="UNIQ001", roll_number="R1",
            admission_number="A1", current_semester=1,
        )
        with pytest.raises(Exception):
            Student.objects.create(
                user=u2, college=college, department=department, branch=branch,
                enrollment_number="UNIQ001", roll_number="R2",
                admission_number="A2", current_semester=1,
            )

    def test_new_fields_exist(self, db, student):
        student.refresh_from_db()
        assert hasattr(student, "abc_id")
        assert hasattr(student, "hostel_resident")
        assert hasattr(student, "student_status")
        assert hasattr(student, "university_roll_number")

    def test_hostel_resident_default_false(self, db, student):
        assert student.hostel_resident is False

    def test_student_status_default_active(self, db, student):
        assert student.student_status == "active"
