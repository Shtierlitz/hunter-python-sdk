"""In-memory storage implementation for saved SDK results."""

from hunter_sdk.models import StorageRecord


class InMemoryStorage:
    """Dictionary-backed storage for operation records."""

    def __init__(self) -> None:
        """Initialize empty in-memory storage."""
        self._records: dict[str, StorageRecord] = {}

    def create(self, record: StorageRecord) -> StorageRecord:
        """Persist a new record."""
        self._records[record.id] = record
        return record

    def get(self, record_id: str) -> StorageRecord | None:
        """Return a stored record by id if present."""
        return self._records.get(record_id)

    def update(
        self,
        record_id: str,
        record: StorageRecord,
    ) -> StorageRecord:
        """Replace an existing stored record."""
        if record_id not in self._records:
            raise KeyError(record_id)
        if record.id != record_id:
            raise ValueError("record.id must match record_id")
        self._records[record_id] = record
        return record

    def delete(self, record_id: str) -> bool:
        """Delete a stored record by id."""
        deleted = self._records.pop(record_id, None)
        return deleted is not None

    def list(self) -> list[StorageRecord]:
        """Return all stored records."""
        return list(self._records.values())
