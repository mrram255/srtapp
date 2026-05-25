from rest_framework import serializers

from .models import BusRoute, BusStop, TransportAllocation


class BusRouteSerializer(serializers.ModelSerializer):
    class Meta:
        model = BusRoute
        fields = [
            'id',
            'college',
            'route_number',
            'name',
            'start_point',
            'end_point',
            'total_stops',
            'driver_name',
            'driver_phone',
            'vehicle_number',
            'capacity',
            'occupied',
            'monthly_fee',
            'is_active',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'college', 'occupied', 'created_at', 'updated_at']


class BusStopSerializer(serializers.ModelSerializer):
    route_number = serializers.CharField(source='route.route_number', read_only=True)

    class Meta:
        model = BusStop
        fields = [
            'id',
            'college',
            'route',
            'route_number',
            'stop_name',
            'stop_order',
            'arrival_time',
            'departure_time',
            'landmark',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'college', 'created_at', 'updated_at']


class TransportAllocationSerializer(serializers.ModelSerializer):
    student_enrollment = serializers.CharField(source='student.enrollment_number', read_only=True)

    class Meta:
        model = TransportAllocation
        fields = [
            'id',
            'college',
            'student',
            'student_enrollment',
            'route',
            'pickup_stop',
            'drop_stop',
            'allocation_date',
            'status',
            'monthly_fee',
            'created_at',
            'updated_at',
        ]
        read_only_fields = fields
