"""Tests for the in-memory storage backend."""

from datetime import UTC, datetime

import pytest

from hunter_sdk.models import OperationType, StorageRecord
from hunter_sdk.storage import InMemoryStorage


def make_record(record_id: str = "record-1") -> StorageRecord:
    """Build a sample storage record for tests."""
    return StorageRecord(
        id=record_id,
        operation=OperationType.domain_search,
        request_params={"domain": "durmstrang.com"},
        operation_result={"status": "ok"},
        created_at=datetime(2026, 4, 21, tzinfo=UTC),
    )


def test_create_and_get_returns_stored_record() -> None:
    """Create should persist a record retrievable by id."""
    storage = InMemoryStorage()
    record = make_record()

    created = storage.create(record)

    assert created == record
    assert storage.get(record.id) == record


def test_update_replaces_existing_record() -> None:
    """Update should replace an existing stored record."""
    storage = InMemoryStorage()
    created = storage.create(make_record())
    updated_record = StorageRecord(
        id=created.id,
        operation=OperationType.email_finder,
        request_params={"domain": "durmstrang.com", "first_name": "Igor", "last_name": "Karkarov"},
        operation_result={"email": "igor@durmstrang.com"},
        created_at=created.created_at,
    )

    updated = storage.update(created.id, updated_record)

    assert updated == updated_record
    assert storage.get(created.id) == updated_record


def test_delete_removes_record() -> None:
    """Delete should remove a stored record."""
    storage = InMemoryStorage()
    record = storage.create(make_record())

    deleted = storage.delete(record.id)

    assert deleted is True
    assert storage.get(record.id) is None


def test_list_returns_all_records() -> None:
    """List should return every stored record."""
    storage = InMemoryStorage()
    first = storage.create(make_record("record-1"))
    second = storage.create(make_record("record-2"))

    records = storage.list()

    assert records == [first, second]


def test_update_missing_record_raises_key_error() -> None:
    """Updating a missing record should fail with ``KeyError``."""
    storage = InMemoryStorage()

    with pytest.raises(KeyError):
        storage.update("missing", make_record("missing"))


def test_update_rejects_record_with_mismatched_id() -> None:
    """Update should reject a payload with a mismatched record id."""
    storage = InMemoryStorage()
    created = storage.create(make_record("record-1"))

    with pytest.raises(ValueError):
        storage.update(created.id, make_record("record-2"))
