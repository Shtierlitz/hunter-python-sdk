"""Shared fixtures and helpers for SDK tests."""

from typing import Any

import httpx
import pytest

from hunter_sdk.client import HunterClient
from hunter_sdk.models import (
    DomainSearchResult,
    EmailFinderResult,
    EmailVerificationResult,
    StorageRecord,
)
from hunter_sdk.service import HunterService
from hunter_sdk.protocols import StorageProtocol
from hunter_sdk.storage import InMemoryStorage


@pytest.fixture
def api_key() -> str:
    """Return a static API key for tests."""
    return "test-api-key"


@pytest.fixture
def client(api_key: str) -> HunterClient:
    """Create a real Hunter client for HTTP-level tests."""
    return HunterClient(api_key=api_key)


@pytest.fixture
def storage() -> InMemoryStorage:
    """Create an empty in-memory storage backend."""
    return InMemoryStorage()


@pytest.fixture
def service(client: HunterClient, storage: InMemoryStorage) -> HunterService:
    """Create a service wired to a stubbed client and real storage."""
    class StubHunterClient:
        def domain_search(self, domain: str, limit: int = 10) -> DomainSearchResult:
            return DomainSearchResult(
                domain=domain,
                organization="Example",
                pattern="{first}",
                email_count=1,
                raw_data={"domain": domain, "limit": limit},
            )

        def email_finder(
            self,
            domain: str,
            first_name: str,
            last_name: str,
        ) -> EmailFinderResult:
            return EmailFinderResult(
                email="igor@durmstrang.com",
                score=97,
                domain=domain,
                raw_data={
                    "domain": domain,
                    "first_name": first_name,
                    "last_name": last_name,
                },
            )

        def email_verifier(self, email: str) -> EmailVerificationResult:
            return EmailVerificationResult(
                email=email,
                status="valid",
                verification_result="deliverable",
                score=99,
                is_pending=False,
                raw_data={"email": email},
            )

    return HunterService(client=StubHunterClient(), storage=storage)


@pytest.fixture
def response_headers() -> dict[str, str]:
    """Return default JSON response headers."""
    return {"Content-Type": "application/json"}


def build_response(
    status_code: int,
    payload: dict[str, Any],
) -> httpx.Response:
    """Build a JSON response for mocked HTTP calls."""
    return httpx.Response(status_code=status_code, json=payload)


def assert_record_saved(
    storage: StorageProtocol,
    record: StorageRecord,
) -> None:
    """Assert that a record was written to storage."""
    saved_record = storage.get(record.id)
    assert saved_record == record
