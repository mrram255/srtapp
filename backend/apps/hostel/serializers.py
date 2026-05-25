from django.db import transaction
from django.db.models import F
from rest_framework import serializers

from .models import Hostel, HostelAllocation, Room


class HostelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Hostel
        fields = [
            'id',
            'college',
            'name',
            'code',
            'address',
            'warden',
            'total_rooms',
            'occupied_rooms',
            'capacity',
            'occupied_beds',
            'type',
            'is_active',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'college', 'created_at', 'updated_at']


class RoomSerializer(serializers.ModelSerializer):
    hostel_name = serializers.CharField(source='hostel.name', read_only=True)
    is_full = serializers.ReadOnlyField()

    class Meta:
        model = Room
        fields = [
            'id',
            'college',
            'hostel',
            'hostel_name',
            'room_number',
            'floor',
            'capacity',
            'occupied',
            'room_type',
            'has_ac',
            'has_attached_bath',
            'monthly_rent',
            'is_active',
            'is_full',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'college', 'occupied', 'created_at', 'updated_at']


class HostelAllocationSerializer(serializers.ModelSerializer):
    student_enrollment = serializers.CharField(source='student.enrollment_number', read_only=True)

    class Meta:
        model = HostelAllocation
        fields = [
            'id',
            'college',
            'student',
            'student_enrollment',
            'room',
            'hostel',
            'allocation_date',
            'vacated_date',
            'status',
            'monthly_rent',
            'security_deposit',
            'remarks',
            'created_at',
            'updated_at',
        ]
        read_only_fields = fields


class HostelAllocationWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = HostelAllocation
        fields = [
            'student',
            'room',
            'allocation_date',
            'monthly_rent',
            'security_deposit',
            'remarks',
            'status',
        ]

    def validate(self, attrs):
        student = attrs['student']
        room = attrs['room']
        if student.college_id != room.college_id:
            raise serializers.ValidationError('Student and room must belong to the same college.')
        hostel = room.hostel

        active_exists = HostelAllocation.objects.filter(
            student=student,
            status='ACTIVE',
            is_deleted=False,
        ).exclude(pk=getattr(self.instance, 'pk', None)).exists()
        if active_exists and attrs.get('status', 'ACTIVE') == 'ACTIVE':
            raise serializers.ValidationError('Student already has an active hostel allocation.')

        attrs['hostel'] = hostel
        attrs['college'] = student.college

        req = self.context.get('request')
        if req and req.user.role == 'ADMIN' and getattr(req.user, 'college_id', None):
            if student.college_id != req.user.college_id:
                raise serializers.ValidationError({'student': 'Invalid student for your college.'})

        return attrs

    @transaction.atomic
    def create(self, validated_data):
        room = validated_data['room']
        status = validated_data.get('status', 'ACTIVE')

        locked_room = Room.objects.select_for_update().get(pk=room.pk)
        if status == 'ACTIVE' and locked_room.occupied >= locked_room.capacity:
            raise serializers.ValidationError({'room': 'Room is full.'})

        allocation = HostelAllocation.objects.create(**validated_data)

        if status == 'ACTIVE':
            Room.objects.filter(pk=locked_room.pk).update(occupied=F('occupied') + 1)
            Hostel.objects.filter(pk=locked_room.hostel_id).update(occupied_beds=F('occupied_beds') + 1)

        return allocation
