from rest_framework import serializers

from .models import AcademicYear, Branch, College, Department


class CollegeSerializer(serializers.ModelSerializer):
    class Meta:
        model = College
        fields = [
            'id',
            'name',
            'code',
            'address',
            'city',
            'state',
            'country',
            'pincode',
            'phone',
            'email',
            'website',
            'logo',
            'established_year',
            'affiliation',
            'accreditation',
            'principal_name',
            'is_active',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class DepartmentSerializer(serializers.ModelSerializer):
    college_name = serializers.CharField(source='college.name', read_only=True)
    hod_name = serializers.CharField(source='hod.full_name', read_only=True)

    class Meta:
        model = Department
        fields = [
            'id',
            'college',
            'college_name',
            'name',
            'code',
            'description',
            'hod',
            'hod_name',
            'is_active',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class BranchSerializer(serializers.ModelSerializer):
    college_name = serializers.CharField(source='college.name', read_only=True)
    department_name = serializers.CharField(source='department.name', read_only=True)

    class Meta:
        model = Branch
        fields = [
            'id',
            'college',
            'college_name',
            'department',
            'department_name',
            'name',
            'code',
            'duration_years',
            'total_semesters',
            'is_active',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class AcademicYearSerializer(serializers.ModelSerializer):
    college_name = serializers.CharField(source='college.name', read_only=True)

    class Meta:
        model = AcademicYear
        fields = [
            'id',
            'college',
            'college_name',
            'year',
            'start_date',
            'end_date',
            'is_current',
            'is_active',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
