"""Protocol interfaces for the service dependencies."""

from collections.abc import Mapping
from typing import Protocol

from hunter_sdk.constants import DEFAULT_DOMAIN_SEARCH_LIMIT
from hunter_sdk.models import (
    DomainSearchResult,
    EmailFinderResult,
    EmailVerificationResult,
    JsonObject,
    RequestParamValue,
    StorageRecord,
)


class HunterRequesterProtocol(Protocol):
    """Contract for sending typed JSON requests to Hunter."""

    def request_json(
        self,
        path: str,
        query_params: Mapping[str, RequestParamValue],
        allowed_status_codes: set[int] | None = None,
    ) -> tuple[JsonObject, int]:
        """Send a request and return a JSON object with the HTTP status."""


class HunterDomainsProtocol(Protocol):
    """Contract for Hunter domain operations used by the service."""

    def search(
        self,
        domain: str,
        limit: int = DEFAULT_DOMAIN_SEARCH_LIMIT,
    ) -> DomainSearchResult:
        """Search by domain."""


class HunterEmailsProtocol(Protocol):
    """Contract for Hunter email operations used by the service."""

    def find(
        self,
        domain: str,
        first_name: str,
        last_name: str,
    ) -> EmailFinderResult:
        """Find an email address."""

    def verify(self, email: str) -> EmailVerificationResult:
        """Verify an email address."""


class HunterClientProtocol(Protocol):
    """Contract for the minimal client API used by the service."""

    domains: HunterDomainsProtocol
    emails: HunterEmailsProtocol


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
