from rest_framework import serializers

from apps.students.models import Student

from .models import MessFeedback, MessMenu


class MessMenuSerializer(serializers.ModelSerializer):
    class Meta:
        model = MessMenu
        fields = [
            'id',
            'college',
            'day',
            'meal_type',
            'items',
            'special_items',
            'calories_estimate',
            'is_active',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'college', 'created_at', 'updated_at']


class MessMenuWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = MessMenu
        fields = ['day', 'meal_type', 'items', 'special_items', 'calories_estimate', 'is_active']

    def validate_items(self, value):
        if not isinstance(value, list):
            raise serializers.ValidationError('Must be a list.')
        return value

    def create(self, validated_data):
        validated_data['college'] = self.context['college']
        return super().create(validated_data)


class MessFeedbackSerializer(serializers.ModelSerializer):
    student_enrollment = serializers.CharField(source='student.enrollment_number', read_only=True)

    class Meta:
        model = MessFeedback
        fields = [
            'id',
            'college',
            'student',
            'student_enrollment',
            'menu',
            'rating',
            'comment',
            'date',
            'created_at',
            'updated_at',
        ]
        read_only_fields = fields


class MessFeedbackWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = MessFeedback
        fields = ['student', 'menu', 'rating', 'comment', 'date']

    def validate_student(self, student: Student):
        req = self.context.get('request')
        if req and req.user.role == 'STUDENT':
            try:
                profile = req.user.student_profile
            except Student.DoesNotExist as exc:
                raise serializers.ValidationError('Student profile required.') from exc
            if student.pk != profile.pk:
                raise serializers.ValidationError('Invalid student.')
        return student

    def validate_menu(self, menu: MessMenu):
        req = self.context.get('request')
        if req and req.user.role == 'ADMIN' and getattr(req.user, 'college_id', None):
            if menu.college_id != req.user.college_id:
                raise serializers.ValidationError('Invalid menu.')
        return menu

    def validate(self, attrs):
        student = attrs['student']
        menu = attrs['menu']
        if student.college_id != menu.college_id:
            raise serializers.ValidationError('Student and menu must belong to the same college.')
        attrs['college'] = student.college
        return attrs
