from django.utils import timezone
from rest_framework import serializers

from apps.accounts.models import User

from .models import Event, EventRegistration


class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = [
            'id',
            'college',
            'title',
            'description',
            'event_type',
            'start_datetime',
            'end_datetime',
            'venue',
            'organizer',
            'department',
            'banner_image',
            'max_participants',
            'registration_required',
            'registration_deadline',
            'is_public',
            'is_active',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'college', 'created_at', 'updated_at']


class EventWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = [
            'title',
            'description',
            'event_type',
            'start_datetime',
            'end_datetime',
            'venue',
            'organizer',
            'department',
            'banner_image',
            'max_participants',
            'registration_required',
            'registration_deadline',
            'is_public',
            'is_active',
        ]

    def validate_department(self, dept):
        if dept is None:
            return dept
        college = self.context.get('college')
        if college and dept.college_id != college.id:
            raise serializers.ValidationError('Department must belong to the target college.')
        return dept

    def validate(self, attrs):
        start = attrs.get('start_datetime')
        end = attrs.get('end_datetime')
        if start and end and end <= start:
            raise serializers.ValidationError({'end_datetime': 'Must be after start_datetime.'})
        return attrs

    def create(self, validated_data):
        validated_data['college'] = self.context['college']
        return super().create(validated_data)


class EventRegistrationSerializer(serializers.ModelSerializer):
    user_email = serializers.EmailField(source='user.email', read_only=True)

    class Meta:
        model = EventRegistration
        fields = [
            'id',
            'college',
            'event',
            'user',
            'user_email',
            'status',
            'registered_at',
            'attended_at',
            'feedback',
            'rating',
            'created_at',
            'updated_at',
        ]
        read_only_fields = fields


class EventRegistrationWriteSerializer(serializers.ModelSerializer):
    user_id = serializers.UUIDField(write_only=True, required=False)

    class Meta:
        model = EventRegistration
        fields = ['event', 'user_id', 'feedback', 'rating']

    def validate_event(self, event: Event):
        if getattr(event, 'is_deleted', False) or not event.is_active:
            raise serializers.ValidationError('Invalid event.')
        return event

    def validate(self, attrs):
        request = self.context['request']
        event = attrs['event']
        raw_uid = attrs.pop('user_id', None)

        if raw_uid:
            if request.user.role not in ('SUPER_ADMIN', 'ADMIN'):
                raise serializers.ValidationError({'user_id': 'Not permitted.'})
            user_obj = User.objects.filter(pk=raw_uid, is_deleted=False).first()
            if not user_obj:
                raise serializers.ValidationError({'user_id': 'Invalid user.'})
        else:
            user_obj = request.user

        uc = getattr(user_obj, 'college_id', None)
        ec = event.college_id
        if uc is not None and uc != ec:
            raise serializers.ValidationError('User must belong to the same college as the event.')

        if event.registration_required:
            deadline = event.registration_deadline
            if deadline and timezone.now() > deadline:
                raise serializers.ValidationError('Registration deadline has passed.')

        attrs['user'] = user_obj
        attrs['college'] = event.college
        return attrs

    def create(self, validated_data):
        return EventRegistration.objects.create(**validated_data)
