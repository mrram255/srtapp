from __future__ import annotations

from rest_framework import serializers

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
from apps.colleges.models import AcademicYear, Department


class AcademicYearListSerializer(serializers.ModelSerializer):
    college_name = serializers.CharField(source='college.name', read_only=True)

    class Meta:
        model = AcademicYear
        fields = ['id', 'year', 'start_date', 'end_date', 'is_current', 'is_active', 'college', 'college_name']


class AcademicYearWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = AcademicYear
        fields = ['id', 'college', 'year', 'start_date', 'end_date', 'is_current', 'is_active']
        read_only_fields = ['id']


class DepartmentListSerializer(serializers.ModelSerializer):
    college_name = serializers.CharField(source='college.name', read_only=True)
    hod_name = serializers.SerializerMethodField()
    program_count = serializers.IntegerField(read_only=True, default=0)

    class Meta:
        model = Department
        fields = [
            'id', 'name', 'code', 'college', 'college_name', 'hod', 'hod_name',
            'is_active', 'program_count',
        ]

    def get_hod_name(self, obj):
        if obj.hod_id:
            return obj.hod.get_full_name() or obj.hod.email
        return None


class DepartmentDetailSerializer(serializers.ModelSerializer):
    college_name = serializers.CharField(source='college.name', read_only=True)
    hod_name = serializers.SerializerMethodField()

    class Meta:
        model = Department
        fields = [
            'id', 'college', 'college_name', 'name', 'code', 'description',
            'hod', 'hod_name', 'is_active', 'created_at', 'updated_at',
        ]

    def get_hod_name(self, obj):
        if obj.hod_id:
            return obj.hod.get_full_name() or obj.hod.email
        return None


class DepartmentWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = ['college', 'name', 'code', 'description', 'hod', 'is_active']


class RegulationListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Regulation
        fields = ['id', 'name', 'code', 'regulation_type', 'college', 'is_active']


class RegulationDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Regulation
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']


class ProgramListSerializer(serializers.ModelSerializer):
    department_name = serializers.CharField(source='department.name', read_only=True)
    subject_count = serializers.IntegerField(read_only=True, default=0)
    batch_count = serializers.IntegerField(read_only=True, default=0)

    class Meta:
        model = Program
        fields = [
            'id', 'name', 'code', 'level', 'department', 'department_name',
            'duration_years', 'total_semesters', 'subject_count', 'batch_count', 'is_active',
        ]


class ProgramDetailSerializer(serializers.ModelSerializer):
    department_name = serializers.CharField(source='department.name', read_only=True)
    regulation_name = serializers.CharField(source='regulation.name', read_only=True, allow_null=True)

    class Meta:
        model = Program
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']


class ProgramWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Program
        exclude = ['created_at', 'updated_at', 'created_by', 'updated_by']


class BatchListSerializer(serializers.ModelSerializer):
    program_name = serializers.CharField(source='program.name', read_only=True)
    section_count = serializers.IntegerField(read_only=True, default=0)

    class Meta:
        model = Batch
        fields = [
            'id', 'name', 'program', 'program_name', 'academic_year',
            'start_year', 'end_year', 'current_semester', 'section_count', 'is_active',
        ]


class BatchDetailSerializer(serializers.ModelSerializer):
    sections = serializers.SerializerMethodField()

    class Meta:
        model = Batch
        fields = '__all__'

    def get_sections(self, obj):
        return SectionListSerializer(obj.sections.filter(is_active=True), many=True).data


class SectionListSerializer(serializers.ModelSerializer):
    class_teacher_name = serializers.SerializerMethodField()

    class Meta:
        model = Section
        fields = ['id', 'batch', 'name', 'max_students', 'class_teacher', 'class_teacher_name', 'is_active']

    def get_class_teacher_name(self, obj):
        if obj.class_teacher_id:
            return obj.class_teacher.get_full_name() or obj.class_teacher.email
        return None


class SectionWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Section
        fields = ['batch', 'name', 'max_students', 'class_teacher', 'is_active']


class SemesterSerializer(serializers.ModelSerializer):
    batch_name = serializers.CharField(source='batch.name', read_only=True)

    class Meta:
        model = Semester
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']


class SubjectListSerializer(serializers.ModelSerializer):
    program_name = serializers.CharField(source='program.name', read_only=True)

    class Meta:
        model = CurriculumSubject
        fields = [
            'id', 'name', 'code', 'program', 'program_name', 'semester_number',
            'subject_type', 'category', 'credits', 'is_active',
        ]


class SubjectDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = CurriculumSubject
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']


class SubjectWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = CurriculumSubject
        exclude = ['created_at', 'updated_at', 'created_by', 'updated_by']


class HolidaySerializer(serializers.ModelSerializer):
    class Meta:
        model = HolidayCalendar
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']


class AcademicEventSerializer(serializers.ModelSerializer):
    created_by_name = serializers.CharField(source='created_by.email', read_only=True, allow_null=True)

    class Meta:
        model = AcademicEvent
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at', 'created_by']
