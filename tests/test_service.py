"""Tests for the persistence-aware service layer."""

from typing import cast

from hunter_sdk.models import (
    DomainSearchResult,
    EmailFinderResult,
    EmailVerificationResult,
)
from hunter_sdk.models import OperationType
from hunter_sdk.service import HunterService

from conftest import assert_record_saved


def test_search_domain_saves_record(service: HunterService) -> None:
    """Domain search should be persisted in storage."""
    record = service.search_domain(domain="durmstrang.com")
    domain_search_result = cast(DomainSearchResult, record.operation_result)

    assert record.operation is OperationType.domain_search
    assert record.request_params == {"domain": "durmstrang.com", "limit": 10}
    assert domain_search_result.domain == "durmstrang.com"
    assert_record_saved(service.storage, record)


def test_find_email_saves_record(service: HunterService) -> None:
    """Email finder should be persisted in storage."""
    record = service.find_email(
        domain="durmstrang.com",
        first_name="Igor",
        last_name="Karkarov",
    )
    email_finder_result = cast(EmailFinderResult, record.operation_result)

    assert record.operation is OperationType.email_finder
    assert record.request_params == {
        "domain": "durmstrang.com",
        "first_name": "Igor",
        "last_name": "Karkarov",
    }
    assert email_finder_result.email == "igor@durmstrang.com"
    assert_record_saved(service.storage, record)


def test_verify_email_saves_record(service: HunterService) -> None:
    """Email verification should be persisted in storage."""
    record = service.verify_email(email="igor@durmstrang.com")
    email_verification_result = cast(EmailVerificationResult, record.operation_result)

    assert record.operation is OperationType.email_verifier
    assert record.request_params == {"email": "igor@durmstrang.com"}
    assert email_verification_result.email == "igor@durmstrang.com"
    assert_record_saved(service.storage, record)
