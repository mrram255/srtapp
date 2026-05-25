"""Unauthenticated API smoke — must not leak data without credentials."""

from __future__ import annotations

import uuid

import pytest
from django.test import Client


@pytest.mark.django_db
def test_colleges_list_requires_authentication(client: Client) -> None:
    response = client.get('/api/v1/colleges/')
    assert response.status_code == 401


@pytest.mark.django_db
def test_students_list_requires_authentication(client: Client) -> None:
    response = client.get('/api/v1/students/')
    assert response.status_code == 401


@pytest.mark.django_db
def test_student_me_requires_authentication(client: Client) -> None:
    response = client.get('/api/v1/students/me/')
    assert response.status_code == 401


@pytest.mark.django_db
def test_students_dashboard_requires_authentication(client: Client) -> None:
    response = client.get('/api/v1/students/dashboard/')
    assert response.status_code == 401


@pytest.mark.django_db
def test_student_documents_requires_authentication(client: Client) -> None:
    response = client.get('/api/v1/students/documents/')
    assert response.status_code == 401


@pytest.mark.django_db
def test_teachers_list_requires_authentication(client: Client) -> None:
    response = client.get('/api/v1/teachers/')
    assert response.status_code == 401


@pytest.mark.django_db
def test_teacher_dashboard_requires_authentication(client: Client) -> None:
    response = client.get('/api/v1/teachers/dashboard/')
    assert response.status_code == 401


@pytest.mark.django_db
def test_teacher_subject_assignments_requires_authentication(client: Client) -> None:
    response = client.get('/api/v1/teachers/assignments/')
    assert response.status_code == 401


@pytest.mark.django_db
def test_academics_course_list_requires_authentication(client: Client) -> None:
    response = client.get('/api/v1/academics/courses/')
    assert response.status_code == 401


@pytest.mark.django_db
def test_academics_subject_list_requires_authentication(client: Client) -> None:
    response = client.get('/api/v1/academics/subjects/')
    assert response.status_code == 401


@pytest.mark.django_db
def test_academics_timetable_requires_authentication(client: Client) -> None:
    response = client.get('/api/v1/academics/timetable/')
    assert response.status_code == 401


@pytest.mark.django_db
def test_attendance_list_requires_authentication(client: Client) -> None:
    response = client.get('/api/v1/attendance/')
    assert response.status_code == 401


@pytest.mark.django_db
def test_attendance_summary_requires_authentication(client: Client) -> None:
    response = client.get('/api/v1/attendance/summary/')
    assert response.status_code == 401


@pytest.mark.django_db
def test_assignments_list_requires_authentication(client: Client) -> None:
    response = client.get('/api/v1/assignments/')
    assert response.status_code == 401


@pytest.mark.django_db
def test_assignment_submissions_requires_authentication(client: Client) -> None:
    response = client.get('/api/v1/assignments/submissions/')
    assert response.status_code == 401


@pytest.mark.django_db
def test_exam_schedules_requires_authentication(client: Client) -> None:
    response = client.get('/api/v1/exams/')
    assert response.status_code == 401


@pytest.mark.django_db
def test_exam_results_requires_authentication(client: Client) -> None:
    response = client.get('/api/v1/exams/results/')
    assert response.status_code == 401


@pytest.mark.django_db
def test_fee_structures_requires_authentication(client: Client) -> None:
    response = client.get('/api/v1/finance/structures/')
    assert response.status_code == 401


@pytest.mark.django_db
def test_fee_payments_requires_authentication(client: Client) -> None:
    response = client.get('/api/v1/finance/payments/')
    assert response.status_code == 401


@pytest.mark.django_db
def test_library_books_requires_authentication(client: Client) -> None:
    response = client.get('/api/v1/library/books/')
    assert response.status_code == 401


@pytest.mark.django_db
def test_library_borrowings_requires_authentication(client: Client) -> None:
    response = client.get('/api/v1/library/borrowings/')
    assert response.status_code == 401


_PROTECTED_EXTENDED_ROUTES = (
    '/api/v1/hostel/',
    '/api/v1/hostel/rooms/',
    '/api/v1/hostel/allocations/',
    '/api/v1/transport/',
    '/api/v1/transport/routes/',
    '/api/v1/transport/stops/',
    '/api/v1/transport/allocations/',
    '/api/v1/placements/',
    '/api/v1/placements/companies/',
    '/api/v1/placements/jobs/',
    '/api/v1/placements/applications/',
    '/api/v1/mess/',
    '/api/v1/mess/menu/',
    '/api/v1/mess/feedback/',
    '/api/v1/events/',
    '/api/v1/events/registrations/',
    '/api/v1/reports/templates/',
    '/api/v1/reports/generated/',
    '/api/v1/gate/',
)


@pytest.mark.django_db
def test_notifications_requires_authentication(client: Client) -> None:
    response = client.get('/api/v1/notifications/')
    assert response.status_code == 401


@pytest.mark.django_db
def test_notifications_mark_read_requires_authentication(client: Client) -> None:
    rid = uuid.uuid4()
    response = client.post(f'/api/v1/notifications/{rid}/read/')
    assert response.status_code == 401


@pytest.mark.django_db
def test_messaging_threads_requires_authentication(client: Client) -> None:
    response = client.get('/api/v1/messages/threads/')
    assert response.status_code == 401


@pytest.mark.django_db
def test_messaging_messages_requires_authentication(client: Client) -> None:
    response = client.get(f'/api/v1/messages/?thread={uuid.uuid4()}')
    assert response.status_code == 401


@pytest.mark.django_db
def test_admissions_requires_authentication(client: Client) -> None:
    response = client.get('/api/v1/admissions/')
    assert response.status_code == 401


@pytest.mark.parametrize('path', _PROTECTED_EXTENDED_ROUTES)
@pytest.mark.django_db
def test_extended_api_routes_require_authentication(client: Client, path: str) -> None:
    response = client.get(path)
    assert response.status_code == 401
