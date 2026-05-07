"""Typed result and storage models used by the SDK."""

from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
from typing import TypeAlias, Union

JsonPrimitive: TypeAlias = Union[str, int, float, bool, None]
JsonArray: TypeAlias = list["JsonValue"]
JsonObject: TypeAlias = dict[str, "JsonValue"]
JsonValue: TypeAlias = Union[JsonPrimitive, JsonArray, JsonObject]
RequestParamValue: TypeAlias = Union[str, int]
RequestParams: TypeAlias = dict[str, RequestParamValue]


class OperationType(StrEnum):
    """Supported service operations."""

    domain_search = "domain_search"
    email_finder = "email_finder"
    email_verifier = "email_verifier"


@dataclass(frozen=True)
class DomainSearchResult:
    """Normalized payload returned by domain search."""

    domain: str
    organization: str | None
    pattern: str | None
    email_count: int
    raw_data: JsonObject


@dataclass(frozen=True)
class EmailFinderResult:
    """Normalized payload returned by email finder."""

    email: str | None
    score: int | None
    domain: str | None
    raw_data: JsonObject


@dataclass(frozen=True)
class EmailVerificationResult:
    """Normalized payload returned by email verification."""

    email: str
    status: str | None
    verification_result: str | None
    score: int | None
    is_pending: bool
    raw_data: JsonObject


OperationResult = DomainSearchResult | EmailFinderResult | EmailVerificationResult


@dataclass(frozen=True)
class StorageRecord:
    """Persisted record for a completed service operation."""

    id: str
    operation: OperationType
    request_params: RequestParams
    operation_result: OperationResult
    created_at: datetime
