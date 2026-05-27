import pytest
from django.utils import timezone
from rest_framework.test import APIClient
from apps.students.models import StudentDocumentVerification


def college(db):
    from apps.colleges.models import College
    return College.objects.create(name="Doc College", code="DTC", is_active=True)

def department(db, college):
    from apps.colleges.models import Department
    return Department.objects.create(name="CS", college=college, is_active=True)

def branch(db, college, department):
    from apps.colleges.models import Branch
    return Branch.objects.create(name="CSE", department=department, college=college, is_active=True)

def staff_user(db):
    from apps.accounts.models import User
    return User.objects.create_user(email="doc_staff@t.com", password="x", role="STAFF")

def student(db, college, department, branch):
    from apps.accounts.models import User
    from apps.students.models import Student
    u = User.objects.create_user(email="doc_stu@t.com", password="x", role="STUDENT")
    return Student.objects.create(
        user=u, college=college, department=department, branch=branch,
        enrollment_number="DOC001", roll_number="D01",
        admission_number="ADOC01", semester=1, batch_year=2024, date_of_birth="2000-01-01", gender="MALE", address="Addr", city="Mumbai", state="MH", pincode="400001", emergency_contact="9000000099", emergency_contact_name="Parent", admission_date="2024-07-01",
    )

def auth_client(staff_user):
    client = APIClient()
    client.force_authenticate(user=staff_user)
    return client


class TestStudentDocuments:
    def test_create_pending(self, db, student):
        doc = StudentDocumentVerification.objects.create(
            student=student, document_type="photo", status="pending"
        )
        assert doc.status == "pending"

    def test_verify_document(self, db, student, staff_user):
        doc = StudentDocumentVerification.objects.create(
            student=student, document_type="aadhaar", status="pending"
        )
        doc.status = "verified"
        doc.verified_by = staff_user
        doc.verified_at = timezone.now()
        doc.save()
        doc.refresh_from_db()
        assert doc.status == "verified"
        assert doc.verified_by == staff_user

    def test_reject_document(self, db, student, staff_user):
        doc = StudentDocumentVerification.objects.create(
            student=student, document_type="caste_cert", status="pending"
        )
        doc.status = "rejected"
        doc.remarks = "Blurry image"
        doc.verified_by = staff_user
        doc.verified_at = timezone.now()
        doc.save()
        assert doc.status == "rejected"

    def test_re_upload_requested(self, db, student):
        doc = StudentDocumentVerification.objects.create(
            student=student, document_type="ssc_marksheet", status="pending"
        )
        doc.status = "re_upload_requested"
        doc.save()
        assert doc.status == "re_upload_requested"

    def test_unique_per_student_type(self, db, student):
        StudentDocumentVerification.objects.create(
            student=student, document_type="photo", status="pending"
        )
        with pytest.raises(Exception):
            StudentDocumentVerification.objects.create(
                student=student, document_type="photo", status="pending"
            )

    def test_multiple_doc_types(self, db, student):
        for dt in ["photo", "aadhaar", "ssc_marksheet"]:
            StudentDocumentVerification.objects.create(
                student=student, document_type=dt, status="pending"
            )
        assert StudentDocumentVerification.objects.filter(student=student).count() == 3

    def test_doc_str(self, db, student):
        doc = StudentDocumentVerification.objects.create(
            student=student, document_type="photo", status="pending"
        )
        assert "photo" in str(doc)

    def test_verify_endpoint(self, auth_client, student):
        r = auth_client.post(
            f"/api/v1/students/{student.id}/documents/verify/",
            {"document_type": "photo", "status": "verified", "remarks": "OK"},
            format="json",
        )
        assert r.status_code in [200, 201]

    def test_documents_list_endpoint(self, auth_client, student):
        StudentDocumentVerification.objects.create(
            student=student, document_type="photo", status="pending"
        )
        r = auth_client.get(f"/api/v1/students/{student.id}/documents/")
        assert r.status_code == 200

    def test_verify_missing_fields(self, auth_client, student):
        r = auth_client.post(
            f"/api/v1/students/{student.id}/documents/verify/",
            {}, format="json",
        )
        assert r.status_code == 400