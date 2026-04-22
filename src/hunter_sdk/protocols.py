"""Protocol interfaces for the service dependencies."""

from typing import Protocol

from hunter_sdk.constants import DEFAULT_DOMAIN_SEARCH_LIMIT
from hunter_sdk.models import DomainSearchResult, EmailFinderResult, EmailVerificationResult, StorageRecord


class HunterClientProtocol(Protocol):
    """Contract for the minimal client API used by the service."""

    def domain_search(
        self,
        domain: str,
        limit: int = DEFAULT_DOMAIN_SEARCH_LIMIT,
    ) -> DomainSearchResult:
        """Search by domain."""

    def email_finder(
        self,
        domain: str,
        first_name: str,
        last_name: str,
    ) -> EmailFinderResult:
        """Find an email address."""

    def email_verifier(self, email: str) -> EmailVerificationResult:
        """Verify an email address."""


class StorageProtocol(Protocol):
    """Contract for the minimal CRUD storage API used by the service."""

    def create(self, record: StorageRecord) -> StorageRecord:
        """Persist a record and return the stored value."""

    def get(self, record_id: str) -> StorageRecord | None:
        """Fetch a record by id."""

    def update(
        self,
        record_id: str,
        record: StorageRecord,
    ) -> StorageRecord:
        """Replace an existing record."""

    def delete(self, record_id: str) -> bool:
        """Delete a record by id."""

    def list(self) -> list[StorageRecord]:
        """Return all stored records."""
