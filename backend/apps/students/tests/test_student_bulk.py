import pytest
from rest_framework import status
from rest_framework.test import APIClient


def college(db):
    from apps.colleges.models import College
    return College.objects.create(name="Bulk College", code="BLK", is_active=True)


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
        email="bulk_staff@t.com", password="x", role="STAFF"
    )


def auth_client(staff_user):
    client = APIClient()
    client.force_authenticate(user=staff_user)
    return client


def student(db, college, department, branch):
    from apps.accounts.models import User
    from apps.students.models import Student
    u = User.objects.create_user(email="bulk_stu@t.com", password="x", role="STUDENT")
    return Student.objects.create(
        user=u,
        college=college,
        department=department,
        branch=branch,
        enrollment_number="BLK001",
        roll_number="B01",
        admission_number="ABLK01",
        semester=1,
        batch_year=2024,
        date_of_birth="2000-01-01",
        gender="MALE",
        address="Addr",
        city="City",
        state="ST",
        pincode="400001",
        emergency_contact="9000000001",
        emergency_contact_name="Guardian",
        admission_date="2024-07-01",
    )


class TestStudentBulkImport:
    def test_bulk_import_requires_auth(self):
        client = APIClient()
        response = client.post("/api/v1/students/bulk-import/", {})
        assert response.status_code in [401, 404]

    def test_export_requires_auth(self):
        client = APIClient()
        response = client.get("/api/v1/students/export/")
        assert response.status_code in [401, 404]

    def test_category_wise_requires_auth(self):
        client = APIClient()
        response = client.get("/api/v1/students/category-wise/")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_category_wise_returns_200(self, auth_client, student):
        response = auth_client.get("/api/v1/students/category-wise/")
        assert response.status_code == status.HTTP_200_OK

    def test_category_wise_has_correct_keys(self, auth_client, student):
        response = auth_client.get("/api/v1/students/category-wise/")
        assert "category_distribution" in response.data
        assert "admission_type_distribution" in response.data
        assert "student_status_distribution" in response.data

    def test_category_wise_filter_by_college(self, auth_client, student, college):
        response = auth_client.get(
            f"/api/v1/students/category-wise/?college={college.id}"
        )
        assert response.status_code == status.HTTP_200_OK

    def test_statistics_returns_200(self, auth_client, student):
        response = auth_client.get("/api/v1/students/statistics/")
        assert response.status_code == status.HTTP_200_OK

    def test_statistics_has_correct_keys(self, auth_client, student):
        response = auth_client.get("/api/v1/students/statistics/")
        assert "total" in response.data
        assert "by_status" in response.data
        assert "by_category" in response.data

    def test_bulk_import_template_download(self, auth_client):
        response = auth_client.get("/api/v1/students/bulk-import/")
        assert response.status_code == status.HTTP_200_OK
        assert (
            response['Content-Type']
            == 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )

    def test_export_returns_excel(self, auth_client, student):
        response = auth_client.get("/api/v1/students/export/")
        assert response.status_code == status.HTTP_200_OK
        assert len(response.content) > 100
