"""Tests for the persistence-aware service layer."""

from hunter_sdk.models import (
    DomainSearchResult,
    EmailFinderResult,
    EmailVerificationResult,
)
from hunter_sdk.models import OperationType
from hunter_sdk.service import HunterRecordsGateway

from conftest import assert_record_saved


def test_search_domain_saves_record(service: HunterRecordsGateway) -> None:
    """Domain search should be persisted in storage."""
    record = service.search_domain(domain="durmstrang.com")

    assert record.operation is OperationType.domain_search
    assert isinstance(record.operation_result, DomainSearchResult)
    assert record.request_params == {"domain": "durmstrang.com", "limit": 10}
    assert record.operation_result.domain == "durmstrang.com"
    assert_record_saved(service.storage, record)


def test_find_email_saves_record(service: HunterRecordsGateway) -> None:
    """Email finder should be persisted in storage."""
    record = service.find_email(
        domain="durmstrang.com",
        first_name="Igor",
        last_name="Karkarov",
    )

    assert record.operation is OperationType.email_finder
    assert isinstance(record.operation_result, EmailFinderResult)
    assert record.request_params == {
        "domain": "durmstrang.com",
        "first_name": "Igor",
        "last_name": "Karkarov",
    }
    assert record.operation_result.email == "igor@durmstrang.com"
    assert_record_saved(service.storage, record)


def test_verify_email_saves_record(service: HunterRecordsGateway) -> None:
    """Email verification should be persisted in storage."""
    record = service.verify_email(email="igor@durmstrang.com")

    assert record.operation is OperationType.email_verifier
    assert isinstance(record.operation_result, EmailVerificationResult)
    assert record.request_params == {"email": "igor@durmstrang.com"}
    assert record.operation_result.email == "igor@durmstrang.com"
    assert_record_saved(service.storage, record)
