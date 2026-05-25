from django.db import models

from apps.core.models import CollegeScopedModel


class Hostel(CollegeScopedModel):
    name = models.CharField(max_length=200)
    code = models.CharField(max_length=20, db_index=True)
    address = models.TextField(blank=True)
    warden = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='hostels_warden',
        limit_choices_to={'role': 'ADMIN'},
    )
    total_rooms = models.PositiveIntegerField(default=0)
    occupied_rooms = models.PositiveIntegerField(default=0)
    capacity = models.PositiveIntegerField(default=0)
    occupied_beds = models.PositiveIntegerField(default=0)
    type = models.CharField(
        max_length=10,
        choices=[('BOYS', 'Boys'), ('GIRLS', 'Girls'), ('MIXED', 'Mixed')],
        default='BOYS',
    )
    is_active = models.BooleanField(default=True, db_index=True)

    class Meta:
        db_table = 'hostels'
        ordering = ['name']
        unique_together = [['college', 'code']]

    def __str__(self):
        return f'{self.name} ({self.type})'


class Room(CollegeScopedModel):
    hostel = models.ForeignKey(Hostel, on_delete=models.CASCADE, related_name='rooms')
    room_number = models.CharField(max_length=20)
    floor = models.PositiveIntegerField(default=1)
    capacity = models.PositiveIntegerField(default=2)
    occupied = models.PositiveIntegerField(default=0)
    room_type = models.CharField(
        max_length=15,
        choices=[
            ('SINGLE', 'Single'),
            ('DOUBLE', 'Double'),
            ('TRIPLE', 'Triple'),
            ('DORMITORY', 'Dormitory'),
        ],
        default='DOUBLE',
    )
    has_ac = models.BooleanField(default=False)
    has_attached_bath = models.BooleanField(default=False)
    monthly_rent = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    is_active = models.BooleanField(default=True, db_index=True)

    class Meta:
        db_table = 'rooms'
        unique_together = [['hostel', 'room_number']]
        ordering = ['hostel', 'floor', 'room_number']

    def __str__(self):
        return f'Room {self.room_number} - {self.hostel.name}'

    @property
    def is_full(self):
        return self.occupied >= self.capacity


class HostelAllocation(CollegeScopedModel):
    STATUS_CHOICES = [
        ('ACTIVE', 'Active'),
        ('VACATED', 'Vacated'),
        ('SUSPENDED', 'Suspended'),
    ]

    student = models.ForeignKey('students.Student', on_delete=models.CASCADE, related_name='hostel_allocations')
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='allocations')
    hostel = models.ForeignKey(Hostel, on_delete=models.CASCADE, related_name='allocations')
    allocation_date = models.DateField()
    vacated_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='ACTIVE')
    monthly_rent = models.DecimalField(max_digits=10, decimal_places=2)
    security_deposit = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    remarks = models.TextField(blank=True)

    class Meta:
        db_table = 'hostel_allocations'
        ordering = ['-allocation_date']

    def __str__(self):
        return f'{self.student.enrollment_number} - {self.room.room_number}'
