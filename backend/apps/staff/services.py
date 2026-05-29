from typing import Dict, Any
from django.db import transaction
from apps.staff.models import Staff, Designation

class StaffService:
    """Service layer for Staff management logic."""
    
    @staticmethod
    @transaction.atomic
    def create_staff(data: Dict[str, Any]) -> Staff:
        return Staff.objects.create(**data)
        
    @staticmethod
    @transaction.atomic
    def update_staff(staff: Staff, data: Dict[str, Any]) -> Staff:
        for attr, value in data.items():
            setattr(staff, attr, value)
        staff.save()
        return staff
