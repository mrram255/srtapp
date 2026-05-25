from rest_framework import serializers
from apps.teachers.models import Teacher
from .models import StudyMaterial


class StudyMaterialSerializer(serializers.ModelSerializer):
    subject_name = serializers.CharField(source='subject.name', read_only=True)
    teacher_name = serializers.CharField(source='teacher.user.full_name', read_only=True)
    department_name = serializers.CharField(source='department.name', read_only=True)
    tags_list = serializers.SerializerMethodField()

    class Meta:
        model = StudyMaterial
        fields = [
            'id', 'college', 'title', 'description',
            'subject', 'subject_name', 'teacher', 'teacher_name',
            'department', 'department_name',
            'material_type', 'file_url', 'external_link',
            'file_size', 'version', 'semester', 'section',
            'access_level', 'is_published', 'download_count',
            'tags', 'tags_list', 'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'college', 'download_count', 'created_at', 'updated_at']

    def get_tags_list(self, obj):
        return [t.strip() for t in obj.tags.split(',') if t.strip()] if obj.tags else []


class StudyMaterialWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudyMaterial
        fields = [
            'title', 'description', 'subject', 'teacher', 'department',
            'material_type', 'file_url', 'external_link', 'file_size',
            'version', 'semester', 'section', 'access_level', 'is_published', 'tags',
        ]
        extra_kwargs = {
            'teacher': {'required': False},
            'department': {'required': False},
        }

    def validate(self, attrs):
        request = self.context.get('request')
        user = getattr(request, 'user', None)

        if user and user.role == 'TEACHER':
            try:
                teacher = Teacher.objects.select_related('department', 'college').get(user=user)
            except Teacher.DoesNotExist:
                raise serializers.ValidationError({'teacher': 'Teacher profile not found.'})
            attrs['teacher'] = teacher
            attrs['department'] = teacher.department
            attrs['college'] = teacher.college

        teacher = attrs.get('teacher')
        if not teacher:
            raise serializers.ValidationError({'teacher': 'This field is required.'})

        attrs.setdefault('department', teacher.department)
        attrs.setdefault('college', teacher.college)

        if not attrs.get('file_url') and not attrs.get('external_link'):
            raise serializers.ValidationError('Either file_url or external_link is required.')

        return attrs
