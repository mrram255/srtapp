from rest_framework import serializers

from .models import ApprovalRequest, Meeting, StrategicPlanItem


class ApprovalRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = ApprovalRequest
        fields = [
            'id',
            'college',
            'title',
            'description',
            'request_type',
            'status',
            'requested_by',
            'reviewed_by',
            'reviewed_at',
            'remarks',
            'metadata',
            'created_at',
        ]
        read_only_fields = ['id', 'reviewed_by', 'reviewed_at', 'created_at']


class ApprovalRequestWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = ApprovalRequest
        fields = ['title', 'description', 'request_type', 'metadata']


class MeetingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Meeting
        fields = [
            'id',
            'college',
            'title',
            'agenda',
            'location',
            'scheduled_at',
            'duration_minutes',
            'status',
            'organizer',
            'minutes',
            'created_at',
        ]
        read_only_fields = ['id', 'organizer', 'created_at']


class MeetingWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Meeting
        fields = ['title', 'agenda', 'location', 'scheduled_at', 'duration_minutes']


class StrategicPlanItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = StrategicPlanItem
        fields = [
            'id',
            'college',
            'title',
            'description',
            'target_year',
            'quarter',
            'status',
            'progress_percent',
            'owner',
            'created_at',
        ]
        read_only_fields = ['id', 'created_at']
