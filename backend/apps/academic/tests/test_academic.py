from __future__ import annotations

from datetime import date

import pytest

from apps.academic.models import (
    AcademicEvent,
    Batch,
    CurriculumSubject,
    HolidayCalendar,
    Program,
    Regulation,
    Section,
    Semester,
)
from apps.colleges.models import AcademicYear
from apps.institutions.tests.conftest import auth_client


@pytest.mark.django_db
class TestAcademicYear:
    def test_list_academic_years(self, api_client, super_admin_user, college):
        AcademicYear.objects.create(
            college=college,
            year='2024-25',
            start_date=date(2024, 6, 1),
            end_date=date(2025, 5, 31),
        )
        client = auth_client(api_client, super_admin_user)
        response = client.get('/api/v1/academic-years/')
        assert response.status_code == 200
        assert len(response.data['data']) >= 1

    def test_create_academic_year(self, api_client, super_admin_user, college):
        client = auth_client(api_client, super_admin_user)
        response = client.post(
            '/api/v1/academic-years/',
            {
                'college': str(college.id),
                'year': '2025-26',
                'start_date': '2025-06-01',
                'end_date': '2026-05-31',
            },
            format='json',
        )
        assert response.status_code == 201
        assert AcademicYear.objects.filter(year='2025-26').exists()

    def test_activate_academic_year(self, api_client, super_admin_user, college):
        ay1 = AcademicYear.objects.create(
            college=college,
            year='2023-24',
            start_date=date(2023, 6, 1),
            end_date=date(2024, 5, 31),
            is_current=True,
        )
        ay2 = AcademicYear.objects.create(
            college=college,
            year='2024-25',
            start_date=date(2024, 6, 1),
            end_date=date(2025, 5, 31),
        )
        client = auth_client(api_client, super_admin_user)
        response = client.post(f'/api/v1/academic-years/{ay2.id}/activate/')
        assert response.status_code == 200
        ay1.refresh_from_db()
        ay2.refresh_from_db()
        assert ay2.is_current is True
        assert ay1.is_current is False


@pytest.mark.django_db
class TestDepartment:
    def test_list_departments(self, api_client, super_admin_user, department):
        client = auth_client(api_client, super_admin_user)
        response = client.get('/api/v1/departments/')
        assert response.status_code == 200
        assert any(d['code'] == 'CSE' for d in response.data['data'])

    def test_create_department(self, api_client, super_admin_user, college):
        client = auth_client(api_client, super_admin_user)
        response = client.post(
            '/api/v1/departments/',
            {'college': str(college.id), 'name': 'Mechanical', 'code': 'MECH'},
            format='json',
        )
        assert response.status_code == 201

    def test_department_programs(self, api_client, super_admin_user, college, department):
        Program.objects.create(
            college=college,
            department=department,
            name='B.Tech CSE',
            code='BTCSE',
        )
        client = auth_client(api_client, super_admin_user)
        response = client.get(f'/api/v1/departments/{department.id}/programs/')
        assert response.status_code == 200
        assert len(response.data['data']) >= 1

    def test_department_stats(self, api_client, super_admin_user, college, department):
        client = auth_client(api_client, super_admin_user)
        response = client.get(f'/api/v1/departments/{department.id}/stats/')
        assert response.status_code == 200
        assert 'programs' in response.data['data']


@pytest.mark.django_db
class TestProgram:
    def test_create_program(self, api_client, super_admin_user, college, department):
        client = auth_client(api_client, super_admin_user)
        response = client.post(
            '/api/v1/programs/',
            {
                'college': str(college.id),
                'department': str(department.id),
                'name': 'B.Tech',
                'code': 'BTECH',
                'level': 'ug',
            },
            format='json',
        )
        assert response.status_code == 201

    def test_program_subjects(self, api_client, super_admin_user, college, department):
        program = Program.objects.create(
            college=college,
            department=department,
            name='B.Tech',
            code='BTECH2',
        )
        CurriculumSubject.objects.create(
            college=college,
            program=program,
            name='DSA',
            code='CS301',
            semester_number=3,
        )
        client = auth_client(api_client, super_admin_user)
        response = client.get(f'/api/v1/programs/{program.id}/subjects/')
        assert response.status_code == 200
        assert len(response.data['data']) >= 1


@pytest.mark.django_db
class TestRegulation:
    def test_create_regulation(self, api_client, super_admin_user, college):
        client = auth_client(api_client, super_admin_user)
        response = client.post(
            '/api/v1/regulations/',
            {
                'college': str(college.id),
                'name': 'CBCS 2019',
                'code': 'R2019',
                'regulation_type': 'cbcs',
            },
            format='json',
        )
        assert response.status_code == 201
        assert Regulation.objects.filter(code='R2019').exists()


@pytest.mark.django_db
class TestBatchSection:
    def test_batch_and_section(self, api_client, super_admin_user, college, department):
        program = Program.objects.create(
            college=college,
            department=department,
            name='B.Tech',
            code='BTCH',
        )
        ay = AcademicYear.objects.create(
            college=college,
            year='2024-25',
            start_date=date(2024, 6, 1),
            end_date=date(2025, 5, 31),
        )
        client = auth_client(api_client, super_admin_user)
        batch_resp = client.post(
            '/api/v1/batches/',
            {
                'program': str(program.id),
                'academic_year': str(ay.id),
                'name': '2024-28 CSE',
                'start_year': 2024,
                'end_year': 2028,
            },
            format='json',
        )
        assert batch_resp.status_code == 201
        batch_id = batch_resp.data['data']['id']
        section_resp = client.post(
            '/api/v1/sections/',
            {'batch': batch_id, 'name': 'A', 'max_students': 60},
            format='json',
        )
        assert section_resp.status_code == 201
        assert Section.objects.filter(batch_id=batch_id, name='A').exists()

    def test_program_batches_action(self, api_client, super_admin_user, college, department):
        program = Program.objects.create(college=college, department=department, name='P', code='PB1')
        ay = AcademicYear.objects.create(
            college=college,
            year='2024-25',
            start_date=date(2024, 6, 1),
            end_date=date(2025, 5, 31),
        )
        Batch.objects.create(program=program, academic_year=ay, name='B1', start_year=2024, end_year=2028)
        client = auth_client(api_client, super_admin_user)
        response = client.get(f'/api/v1/programs/{program.id}/batches/')
        assert response.status_code == 200
        assert len(response.data['data']) >= 1


@pytest.mark.django_db
class TestSemester:
    def test_create_semester(self, api_client, super_admin_user, college, department):
        program = Program.objects.create(college=college, department=department, name='P', code='PS1')
        ay = AcademicYear.objects.create(
            college=college,
            year='2024-25',
            start_date=date(2024, 6, 1),
            end_date=date(2025, 5, 31),
        )
        batch = Batch.objects.create(program=program, academic_year=ay, name='B', start_year=2024, end_year=2028)
        client = auth_client(api_client, super_admin_user)
        response = client.post(
            '/api/v1/semesters/',
            {
                'academic_year': str(ay.id),
                'batch': str(batch.id),
                'semester_number': 1,
                'status': 'ongoing',
            },
            format='json',
        )
        assert response.status_code == 201
        assert Semester.objects.filter(batch=batch, semester_number=1).exists()


@pytest.mark.django_db
class TestSubject:
    def test_create_subject(self, api_client, super_admin_user, college, department):
        program = Program.objects.create(college=college, department=department, name='P', code='SUBP')
        client = auth_client(api_client, super_admin_user)
        response = client.post(
            '/api/v1/subjects/',
            {
                'college': str(college.id),
                'program': str(program.id),
                'name': 'Data Structures',
                'code': 'CS301',
                'semester_number': 3,
                'credits': 4,
            },
            format='json',
        )
        assert response.status_code == 201

    def test_filter_subjects_by_semester(self, api_client, super_admin_user, college, department):
        program = Program.objects.create(college=college, department=department, name='P', code='FILP')
        CurriculumSubject.objects.create(
            college=college, program=program, name='S1', code='S101', semester_number=1
        )
        CurriculumSubject.objects.create(
            college=college, program=program, name='S3', code='S301', semester_number=3
        )
        client = auth_client(api_client, super_admin_user)
        response = client.get('/api/v1/subjects/?semester_number=3')
        assert response.status_code == 200
        codes = [s['code'] for s in response.data['data']]
        assert 'S301' in codes
        assert 'S101' not in codes


@pytest.mark.django_db
class TestHoliday:
    def test_create_holiday(self, api_client, super_admin_user, college):
        ay = AcademicYear.objects.create(
            college=college,
            year='2024-25',
            start_date=date(2024, 6, 1),
            end_date=date(2025, 5, 31),
        )
        client = auth_client(api_client, super_admin_user)
        response = client.post(
            '/api/v1/holidays/',
            {
                'academic_year': str(ay.id),
                'date': '2025-01-26',
                'name': 'Republic Day',
                'holiday_type': 'national',
            },
            format='json',
        )
        assert response.status_code == 201
        assert HolidayCalendar.objects.filter(name='Republic Day').exists()

    def test_department_specific_holiday(self, api_client, super_admin_user, college, department):
        ay = AcademicYear.objects.create(
            college=college,
            year='2024-25',
            start_date=date(2024, 6, 1),
            end_date=date(2025, 5, 31),
        )
        client = auth_client(api_client, super_admin_user)
        response = client.post(
            '/api/v1/holidays/',
            {
                'academic_year': str(ay.id),
                'date': '2025-03-15',
                'name': 'Dept Event',
                'holiday_type': 'college',
                'applicable_to': 'specific_dept',
                'departments': [str(department.id)],
            },
            format='json',
        )
        assert response.status_code == 201
        holiday = HolidayCalendar.objects.get(name='Dept Event')
        assert holiday.departments.filter(id=department.id).exists()


@pytest.mark.django_db
class TestAcademicCalendar:
    def test_combined_calendar(self, api_client, super_admin_user, college):
        ay = AcademicYear.objects.create(
            college=college,
            year='2024-25',
            start_date=date(2024, 6, 1),
            end_date=date(2025, 5, 31),
        )
        HolidayCalendar.objects.create(
            academic_year=ay, date=date(2025, 1, 26), name='Republic Day'
        )
        AcademicEvent.objects.create(
            academic_year=ay,
            title='Semester Start',
            event_type='semester_start',
            start_date=date(2024, 7, 1),
            end_date=date(2024, 7, 1),
        )
        client = auth_client(api_client, super_admin_user)
        response = client.get(f'/api/v1/academic-calendar/?academic_year={ay.id}')
        assert response.status_code == 200
        assert len(response.data['data']['holidays']) >= 1
        assert len(response.data['data']['events']) >= 1

    def test_update_department_hod(self, api_client, super_admin_user, department, db):
        from django.contrib.auth import get_user_model
        from apps.users.models import Role

        User = get_user_model()
        hod_role = Role.objects.filter(name='hod').first()
        hod_user = User.objects.create_user(
            email='hod_s4@example.com',
            phone='+919933333333',
            first_name='HOD',
            last_name='User',
            role='HOD',
            role_ref=hod_role,
            password='ValidPass1!',
        )
        client = auth_client(api_client, super_admin_user)
        response = client.patch(
            f'/api/v1/departments/{department.id}/',
            {'hod': str(hod_user.id)},
            format='json',
        )
        assert response.status_code == 200
        department.refresh_from_db()
        assert department.hod_id == hod_user.id

    def test_update_program(self, api_client, super_admin_user, college, department):
        program = Program.objects.create(college=college, department=department, name='P', code='UPRG')
        client = auth_client(api_client, super_admin_user)
        response = client.patch(
            f'/api/v1/programs/{program.id}/',
            {'intake_capacity': 120},
            format='json',
        )
        assert response.status_code == 200
        program.refresh_from_db()
        assert program.intake_capacity == 120

    def test_subject_credit_fields(self, api_client, super_admin_user, college, department):
        program = Program.objects.create(college=college, department=department, name='P', code='CRP')
        subject = CurriculumSubject.objects.create(
            college=college,
            program=program,
            name='Math',
            code='MA101',
            semester_number=1,
            credits=3,
            lecture_hours=3,
            tutorial_hours=1,
            practical_hours=0,
        )
        total_weekly = subject.lecture_hours + subject.tutorial_hours + subject.practical_hours
        assert subject.credits == 3
        assert total_weekly == 4

    def test_regulation_with_grading_scale(self, api_client, super_admin_user, college):
        client = auth_client(api_client, super_admin_user)
        response = client.post(
            '/api/v1/regulations/',
            {
                'college': str(college.id),
                'name': 'NEP 2020',
                'code': 'NEP20',
                'regulation_type': 'nep',
                'grading_scale': {'O': [90, 100], 'A+': [80, 89]},
            },
            format='json',
        )
        assert response.status_code == 201
        reg = Regulation.objects.get(code='NEP20')
        assert reg.grading_scale['O'] == [90, 100]

    def test_deactivate_academic_year(self, api_client, super_admin_user, college):
        ay = AcademicYear.objects.create(
            college=college,
            year='2022-23',
            start_date=date(2022, 6, 1),
            end_date=date(2023, 5, 31),
        )
        client = auth_client(api_client, super_admin_user)
        response = client.delete(f'/api/v1/academic-years/{ay.id}/')
        assert response.status_code == 200
        ay.refresh_from_db()
        assert ay.is_active is False

    def test_create_academic_event(self, api_client, super_admin_user, college):
        ay = AcademicYear.objects.create(
            college=college,
            year='2024-25',
            start_date=date(2024, 6, 1),
            end_date=date(2025, 5, 31),
        )
        client = auth_client(api_client, super_admin_user)
        response = client.post(
            '/api/v1/academic-events/',
            {
                'academic_year': str(ay.id),
                'title': 'Exam Week',
                'event_type': 'exam_start',
                'start_date': '2025-04-01',
                'end_date': '2025-04-15',
            },
            format='json',
        )
        assert response.status_code == 201
