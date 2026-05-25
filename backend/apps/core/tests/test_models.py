from __future__ import annotations

import uuid

import pytest

from apps.core.models import CoreSampleRecord, OrderedModel


@pytest.mark.django_db
def test_timestamped_model_uuid_and_defaults():
    record = CoreSampleRecord.objects.create(name='Sample')
    assert isinstance(record.id, uuid.UUID)
    assert record.is_active is True
    assert record.created_at is not None
    assert record.updated_at is not None


@pytest.mark.django_db
def test_timestamped_model_soft_active_flag():
    record = CoreSampleRecord.objects.create(name='Inactive')
    record.is_active = False
    record.save(update_fields=['is_active'])
    record.refresh_from_db()
    assert record.is_active is False


def test_ordered_model_meta_ordering():
    assert OrderedModel._meta.ordering == ['order', '-created_at']
