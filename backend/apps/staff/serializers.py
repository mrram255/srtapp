from rest_framework import serializers
from .models import Designation, Staff, StaffServiceBook


class DesignationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Designation
        fields = [
            'id', 'name', 'category', 'level', 'college',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class StaffServiceBookSerializer(serializers.ModelSerializer):
    old_designation_name = serializers.CharField(
        source='old_designation.name', read_only=True
    )
    new_designation_name = serializers.CharField(
        source='new_designation.name', read_only=True
    )

    class Meta:
        model = StaffServiceBook
        fields = [
            'id', 'staff', 'entry_type', 'effective_date',
            'order_number', 'order_date', 'description',
            'old_designation', 'old_designation_name',
            'new_designation', 'new_designation_name',
            'old_pay', 'new_pay', 'document',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class StaffListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for list views."""
    full_name = serializers.SerializerMethodField()
    email = serializers.EmailField(source='user.email', read_only=True)
    phone = serializers.CharField(source='user.phone', read_only=True, default='')
    designation_name = serializers.CharField(source='designation.name', read_only=True)
    department_name = serializers.CharField(source='department.name', read_only=True)

    class Meta:
        model = Staff
        fields = [
            'id', 'employee_id', 'full_name', 'email', 'phone',
            'staff_type', 'designation_name', 'department_name',
            'status', 'date_of_joining', 
        ]

    def get_full_name(self, obj):
        return obj.user.get_full_name()


class StaffDetailSerializer(serializers.ModelSerializer):
    """Full serializer for create/update/retrieve."""
    full_name = serializers.SerializerMethodField()
    email = serializers.EmailField(source='user.email', read_only=True)
    designation_name = serializers.CharField(source='designation.name', read_only=True)
    department_name = serializers.CharField(source='department.name', read_only=True)
    service_book_entries = StaffServiceBookSerializer(many=True, read_only=True)

    class Meta:
        model = Staff
        fields = [
            'id', 'employee_id', 'user', 'full_name', 'email',
            # Employment
            'staff_type', 'designation', 'designation_name',
            'department', 'department_name',
            'date_of_joining', 'date_of_retirement',
            'appointment_type', 'appointment_order_number',
            'appointment_order_date', 'appointment_order_file',
            # Qualification
            'highest_qualification', 'specialization',
            'phd_status', 'phd_university', 'phd_year', 'phd_thesis_title',
            'net_set_qualified', 'net_set_year', 'net_set_subject',
            'qualifications',
            # Experience
            'total_experience_years', 'teaching_experience_years',
            'industry_experience_years', 'previous_experiences',
            # Salary
            'pay_band', 'grade_pay', 'basic_pay',
            'bank_name', 'bank_account', 'bank_ifsc',
            'pf_number', 'esi_number', 'uan_number', 'pan_number',
            # Research
            'google_scholar_id', 'scopus_id', 'orcid_id',
            'vidwan_id', 'research_interests',
            # Documents
            'resume',
            # Status & Meta
            'status', 'college', 
            'created_at', 'updated_at',
            'service_book_entries',
        ]
        read_only_fields = ['id', 'employee_id', 'created_at', 'updated_at']

    def get_full_name(self, obj):
        return obj.user.get_full_name()
