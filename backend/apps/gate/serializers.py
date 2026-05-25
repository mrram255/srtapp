from rest_framework import serializers

from .models import GateLog


class GateLogSerializer(serializers.ModelSerializer):
    person_email = serializers.SerializerMethodField()
    student_enrollment = serializers.SerializerMethodField()
    meeting_with_email = serializers.SerializerMethodField()

    class Meta:
        model = GateLog
        fields = [
            'id',
            'college',
            'entry_type',
            'person_type',
            'person',
            'person_email',
            'student',
            'student_enrollment',
            'visitor_name',
            'visitor_phone',
            'visitor_id_type',
            'visitor_id_number',
            'purpose',
            'meeting_with',
            'meeting_with_email',
            'vehicle_number',
            'vehicle_type',
            'timestamp',
            'expected_return',
            'actual_return',
            'security_guard',
            'gate_number',
            'verified_by',
            'remarks',
            'created_at',
            'updated_at',
        ]
        read_only_fields = fields

    def get_person_email(self, obj):
        return obj.person.email if obj.person_id else None

    def get_student_enrollment(self, obj):
        return obj.student.enrollment_number if obj.student_id else None

    def get_meeting_with_email(self, obj):
        return obj.meeting_with.email if obj.meeting_with_id else None


class GateLogWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = GateLog
        fields = [
            'entry_type',
            'person_type',
            'person',
            'student',
            'visitor_name',
            'visitor_phone',
            'visitor_id_type',
            'visitor_id_number',
            'purpose',
            'meeting_with',
            'vehicle_number',
            'vehicle_type',
            'expected_return',
            'actual_return',
            'security_guard',
            'gate_number',
            'verified_by',
            'remarks',
        ]

    def validate_student(self, student):
        college = self.context.get('college')
        if student and college and student.college_id != college.id:
            raise serializers.ValidationError('Invalid student.')
        return student

    def validate_person(self, person):
        college = self.context.get('college')
        if person and college and getattr(person, 'college_id', None) and person.college_id != college.id:
            raise serializers.ValidationError('Invalid person.')
        return person

    def validate_meeting_with(self, user):
        college = self.context.get('college')
        if user and college and getattr(user, 'college_id', None) and user.college_id != college.id:
            raise serializers.ValidationError('Invalid meeting contact.')
        return user

    def validate_security_guard(self, guard):
        if guard is None:
            return guard
        if guard.role != 'SECURITY':
            raise serializers.ValidationError('security_guard must be a SECURITY role user.')
        college = self.context.get('college')
        if college and getattr(guard, 'college_id', None) and guard.college_id != college.id:
            raise serializers.ValidationError('Invalid security guard.')
        return guard

    def validate(self, attrs):
        person_type = attrs.get('person_type')
        if person_type == 'STUDENT' and not attrs.get('student'):
            raise serializers.ValidationError({'student': 'Required for student entries.'})
        if person_type in ('VISITOR', 'VENDOR', 'OTHER'):
            name = (attrs.get('visitor_name') or '').strip()
            if not name:
                raise serializers.ValidationError({'visitor_name': 'Required for this person type.'})
        return attrs

    def create(self, validated_data):
        college = self.context['college']
        request = self.context['request']
        if request.user.role == 'SECURITY' and validated_data.get('security_guard') is None:
            validated_data['security_guard'] = request.user
        return GateLog.objects.create(college=college, **validated_data)
