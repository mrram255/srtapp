import pytest
from rest_framework import status


@pytest.mark.django_db
class TestStudentProfileFields:
    def test_create_with_family_and_education_json(self, auth_client, department, branch):
        payload = {
            'email': 'family.stu@test.com',
            'password': 'SecurePass123!',
            'first_name': 'Ravi',
            'last_name': 'Kumar',
            'phone': '9876543210',
            'enrollment_number': 'ENR-FAM-001',
            'roll_number': 'ROLL-FAM-001',
            'department': str(department.id),
            'branch': str(branch.id),
            'semester': 1,
            'batch_year': 2024,
            'date_of_birth': '2002-05-15',
            'gender': 'MALE',
            'address': 'Line 1',
            'city': 'Pune',
            'state': 'MH',
            'pincode': '411001',
            'emergency_contact': '9876543211',
            'emergency_contact_name': 'Mother',
            'admission_date': '2024-07-01',
            'abc_id': 'ABC-12345',
            'family_details': {
                'father_name': 'Father',
                'mother_name': 'Mother',
                'guardian_phone': '9876543212',
            },
            'education_details': {
                'ssc_percentage': 92.5,
                'hsc_percentage': 88.0,
            },
            'permanent_address': {'line1': 'Perm', 'city': 'Pune'},
            'correspondence_address': {'line1': 'Corr', 'city': 'Pune'},
            'is_address_same': False,
        }
        response = auth_client.post('/api/v1/students/', payload, format='json')
        assert response.status_code == status.HTTP_201_CREATED, response.data
        from apps.students.models import Student

        student = Student.objects.get(enrollment_number='ENR-FAM-001')
        assert student.abc_id == 'ABC-12345'
        assert student.family_details['father_name'] == 'Father'
        assert student.education_details['ssc_percentage'] == 92.5
        assert student.permanent_address['city'] == 'Pune'
        assert student.is_address_same is False
