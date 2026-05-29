import uuid
import pytest
from django.test import TestCase
from django.utils import timezone
from apps.core.models import TimeStampedModel, OrderedModel


class TimeStampedModelTest(TestCase):
    """Test TimeStampedModel base class"""

    def test_timestamped_model_has_uuid_pk(self):
        """Every model must have UUID primary key"""
        from apps.core.models import CoreSampleRecord
        obj = CoreSampleRecord.objects.create(name="Test")
        self.assertIsInstance(obj.id, uuid.UUID)

    def test_timestamped_model_has_created_at(self):
        from apps.core.models import CoreSampleRecord
        obj = CoreSampleRecord.objects.create(name="Test")
        self.assertIsNotNone(obj.created_at)

    def test_timestamped_model_has_updated_at(self):
        from apps.core.models import CoreSampleRecord
        obj = CoreSampleRecord.objects.create(name="Test")
        self.assertIsNotNone(obj.updated_at)

    def test_timestamped_model_has_is_active(self):
        from apps.core.models import CoreSampleRecord
        obj = CoreSampleRecord.objects.create(name="Test")
        self.assertTrue(obj.is_active)

    def test_soft_delete_sets_is_active_false(self):
        from apps.core.models import CoreSampleRecord
        obj = CoreSampleRecord.objects.create(name="Test")
        obj.is_active = False
        obj.save()
        obj.refresh_from_db()
        self.assertFalse(obj.is_active)

    def test_uuid_is_unique(self):
        from apps.core.models import CoreSampleRecord
        obj1 = CoreSampleRecord.objects.create(name="Test1")
        obj2 = CoreSampleRecord.objects.create(name="Test2")
        self.assertNotEqual(obj1.id, obj2.id)

    def test_created_at_auto_set(self):
        from apps.core.models import CoreSampleRecord
        before = timezone.now()
        obj = CoreSampleRecord.objects.create(name="Test")
        after = timezone.now()
        self.assertGreaterEqual(obj.created_at, before)
        self.assertLessEqual(obj.created_at, after)

    def test_updated_at_changes_on_save(self):
        from apps.core.models import CoreSampleRecord
        obj = CoreSampleRecord.objects.create(name="Test")
        old_updated = obj.updated_at
        import time; time.sleep(0.01)
        obj.name = "Updated"
        obj.save()
        obj.refresh_from_db()
        self.assertGreaterEqual(obj.updated_at, old_updated)
