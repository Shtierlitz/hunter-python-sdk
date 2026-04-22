"""Service layer that persists SDK operation results."""

from collections.abc import Mapping
from datetime import UTC, datetime
from uuid import uuid4

from hunter_sdk.constants import (
    DEFAULT_DOMAIN_SEARCH_LIMIT,
    FIELD_DOMAIN,
    FIELD_EMAIL,
    FIELD_FIRST_NAME,
    FIELD_LAST_NAME,
)
from hunter_sdk.models import OperationResult, OperationType, StorageRecord
from hunter_sdk.protocols import HunterClientProtocol, StorageProtocol


class HunterService:
    """Service layer that persists Hunter API results."""

    def __init__(
        self,
        client: HunterClientProtocol,
        storage: StorageProtocol,
    ) -> None:
        """Create a service with an API client and storage backend."""
        self.client = client
        self.storage = storage

    def search_domain(
        self,
        domain: str,
        limit: int = DEFAULT_DOMAIN_SEARCH_LIMIT,
    ) -> StorageRecord:
        """Run domain search and persist the resulting record."""
        request_params: dict[str, str | int] = {FIELD_DOMAIN: domain, "limit": limit}
        operation_result = self.client.domain_search(domain=domain, limit=limit)
        return self._save_record(OperationType.domain_search, request_params, operation_result)

    def find_email(
        self,
        domain: str,
        first_name: str,
        last_name: str,
    ) -> StorageRecord:
        """Run email finder and persist the resulting record."""
        request_params: dict[str, str] = {
            FIELD_DOMAIN: domain,
            FIELD_FIRST_NAME: first_name,
            FIELD_LAST_NAME: last_name,
        }
        operation_result = self.client.email_finder(
            domain=domain,
            first_name=first_name,
            last_name=last_name,
        )
        return self._save_record(OperationType.email_finder, request_params, operation_result)

    def verify_email(self, email: str) -> StorageRecord:
        """Run email verification and persist the resulting record."""
        request_params: dict[str, str] = {FIELD_EMAIL: email}
        operation_result = self.client.email_verifier(email=email)
        return self._save_record(OperationType.email_verifier, request_params, operation_result)

    def _save_record(
        self,
        operation: OperationType,
        request_params: Mapping[str, str | int],
        operation_result: OperationResult,
    ) -> StorageRecord:
        record = StorageRecord(
            id=str(uuid4()),
            operation=operation,
            request_params=dict(request_params),
            operation_result=operation_result,
            created_at=datetime.now(tz=UTC),
        )
        return self.storage.create(record)
