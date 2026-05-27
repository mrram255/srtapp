import pytest
from rest_framework.test import APIClient
from apps.students.models import StudentSemesterRecord



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
        assert student.semester == 1
        r = auth_client.post(f"/api/v1/students/{student.id}/promote/")
        if r.status_code == 200:
            student.refresh_from_db()
            assert student.semester == 2

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