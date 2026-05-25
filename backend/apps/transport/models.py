from django.db import models

from apps.core.models import CollegeScopedModel


class BusRoute(CollegeScopedModel):
    route_number = models.CharField(max_length=20, db_index=True)
    name = models.CharField(max_length=200)
    start_point = models.CharField(max_length=255)
    end_point = models.CharField(max_length=255)
    total_stops = models.PositiveIntegerField(default=0)
    driver_name = models.CharField(max_length=200, blank=True)
    driver_phone = models.CharField(max_length=15, blank=True)
    vehicle_number = models.CharField(max_length=20, blank=True)
    capacity = models.PositiveIntegerField(default=50)
    occupied = models.PositiveIntegerField(default=0)
    monthly_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    is_active = models.BooleanField(default=True, db_index=True)

    class Meta:
        db_table = 'bus_routes'
        unique_together = [['college', 'route_number']]
        ordering = ['route_number']

    def __str__(self):
        return f'Route {self.route_number}: {self.name}'


class BusStop(CollegeScopedModel):
    route = models.ForeignKey(BusRoute, on_delete=models.CASCADE, related_name='stops')
    stop_name = models.CharField(max_length=255)
    stop_order = models.PositiveIntegerField()
    arrival_time = models.TimeField()
    departure_time = models.TimeField()
    landmark = models.CharField(max_length=255, blank=True)

    class Meta:
        db_table = 'bus_stops'
        unique_together = [['route', 'stop_order']]
        ordering = ['route', 'stop_order']

    def __str__(self):
        return f'{self.stop_name} (Route {self.route.route_number})'


class TransportAllocation(CollegeScopedModel):
    STATUS_CHOICES = [
        ('ACTIVE', 'Active'),
        ('INACTIVE', 'Inactive'),
        ('SUSPENDED', 'Suspended'),
    ]

    student = models.ForeignKey('students.Student', on_delete=models.CASCADE, related_name='transport_allocations')
    route = models.ForeignKey(BusRoute, on_delete=models.CASCADE, related_name='allocations')
    pickup_stop = models.ForeignKey(BusStop, on_delete=models.CASCADE, related_name='pickup_allocations')
    drop_stop = models.ForeignKey(BusStop, on_delete=models.CASCADE, related_name='drop_allocations')
    allocation_date = models.DateField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='ACTIVE')
    monthly_fee = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        db_table = 'transport_allocations'
        ordering = ['-allocation_date']

    def __str__(self):
        return f'{self.student.enrollment_number} - Route {self.route.route_number}'
