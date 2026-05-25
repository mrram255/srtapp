from rest_framework import serializers

from .models import Attendance, AttendanceSummary


class AttendanceSerializer(serializers.ModelSerializer):
    student_enrollment = serializers.CharField(source='student.enrollment_number', read_only=True)
    subject_name = serializers.CharField(source='subject.name', read_only=True)

    class Meta:
        model = Attendance
        fields = [
            'id',
            'college',
            'student',
            'student_enrollment',
            'subject',
            'subject_name',
            'teacher',
            'date',
            'status',
            'period',
            'remarks',
            'marked_at',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'college', 'marked_at', 'created_at', 'updated_at']


class AttendanceWriteSerializer(serializers.ModelSerializer):
    """Single attendance row for bulk marking."""

    class Meta:
        model = Attendance
        fields = ['student', 'subject', 'teacher', 'date', 'status', 'period', 'remarks']

    def validate(self, attrs):
        student = attrs['student']
        subject = attrs['subject']
        teacher = attrs['teacher']

        if student.college_id != subject.college_id or student.college_id != teacher.college_id:
            raise serializers.ValidationError('Student, subject, and teacher must belong to the same college.')

        attrs['college'] = student.college
        return attrs


class AttendanceSummarySerializer(serializers.ModelSerializer):
    student_enrollment = serializers.CharField(source='student.enrollment_number', read_only=True)
    subject_name = serializers.CharField(source='subject.name', read_only=True)

    class Meta:
        model = AttendanceSummary
        fields = [
            'id',
            'college',
            'student',
            'student_enrollment',
            'subject',
            'subject_name',
            'academic_year',
            'total_classes',
            'present_count',
            'absent_count',
            'late_count',
            'excused_count',
            'percentage',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'college', 'created_at', 'updated_at']
