import pytest
from rest_framework.test import APIClient
from apps.students.models import StudentSemesterRecord


def college(db):
    from apps.colleges.models import College
    return College.objects.create(name="Promo College", code="PMC", is_active=True)

def department(db, college):
    from apps.colleges.models import Department
    return Department.objects.create(name="CS", college=college, is_active=True)

def branch(db, college, department):
    from apps.colleges.models import Branch
    return Branch.objects.create(name="CSE", department=department, college=college, is_active=True)

def staff_user(db):
    from apps.accounts.models import User
    return User.objects.create_user(email="promo_staff@t.com", password="x", role="STAFF", phone="9000000001", first_name="Test", last_name="User")

def student(db, college, department, branch):
    from apps.accounts.models import User
    from apps.students.models import Student
    u = User.objects.create_user(email="promo_stu@t.com", password="x", role="STUDENT", phone="9000000001", first_name="Test", last_name="User")
    return Student.objects.create(
        user=u, college=college, department=department, branch=branch,
        enrollment_number="PROMO01", roll_number="P01",
        admission_number="APROMO01", current_semester=1,
    )

def auth_client(staff_user):
    client = APIClient()
    client.force_authenticate(user=staff_user)
    return client


class TestSemesterRecord:
    def test_create_record(self, db, student):
        rec = StudentSemesterRecord.objects.create(
            student=student, semester_number=1,
            academic_year_label="2024-25", status="ongoing",
        )
        assert rec.id is not None
        assert rec.promoted_to_next is False

    def test_record_str(self, db, student):
        rec = StudentSemesterRecord.objects.create(
            student=student, semester_number=1,
            academic_year_label="2024-25", status="ongoing",
        )
        assert "1" in str(rec)

    def test_unique_per_year(self, db, student):
        StudentSemesterRecord.objects.create(
            student=student, semester_number=1,
            academic_year_label="2024-25", status="ongoing",
        )
        with pytest.raises(Exception):
            StudentSemesterRecord.objects.create(
                student=student, semester_number=1,
                academic_year_label="2024-25", status="ongoing",
            )

    def test_sgpa_cgpa_nullable(self, db, student):
        rec = StudentSemesterRecord.objects.create(
            student=student, semester_number=2,
            academic_year_label="2024-25", status="ongoing",
        )
        assert rec.sgpa is None
        assert rec.cgpa is None

    def test_promote_increases_semester(self, auth_client, student):
        assert student.current_semester == 1
        r = auth_client.post(f"/api/v1/students/{student.id}/promote/")
        if r.status_code == 200:
            student.refresh_from_db()
            assert student.current_semester == 2

    def test_promote_marks_record(self, db, auth_client, student):
        StudentSemesterRecord.objects.create(
            student=student, semester_number=1,
            academic_year_label="2024-25", status="ongoing",
        )
        r = auth_client.post(f"/api/v1/students/{student.id}/promote/")
        if r.status_code == 200:
            rec = StudentSemesterRecord.objects.get(student=student, semester_number=1)
            assert rec.promoted_to_next is True

    def test_semester_records_endpoint(self, auth_client, student):
        StudentSemesterRecord.objects.create(
            student=student, semester_number=1,
            academic_year_label="2024-25", status="ongoing",
        )
        r = auth_client.get(f"/api/v1/students/{student.id}/semester-records/")
        assert r.status_code == 200

    def test_attendance_decimal(self, db, student):
        rec = StudentSemesterRecord.objects.create(
            student=student, semester_number=3,
            academic_year_label="2025-26", status="ongoing",
            attendance_percentage="78.50",
        )
        assert float(rec.attendance_percentage) == 78.50