"""HTTP client for the supported Hunter API endpoints."""

import json
from typing import Any, Self

import httpx

from hunter_sdk import constants as api_constants
from hunter_sdk.exceptions import HunterApiError, HunterTransportError
from hunter_sdk.models import DomainSearchResult, EmailFinderResult, EmailVerificationResult


class BaseHttpClient:
    """Reusable wrapper around ``httpx.Client`` lifecycle."""

    def __init__(self, http_client: httpx.Client) -> None:
        """Wrap an existing ``httpx.Client`` instance."""
        self._http_client = http_client

    @property
    def is_closed(self) -> bool:
        """Return whether the underlying HTTP client is closed."""
        return self._http_client.is_closed

    def close(self) -> None:
        """Close the underlying HTTP client."""
        self._http_client.close()

    def __enter__(self) -> Self:
        """Return the client itself for context-managed use."""
        return self

    def __exit__(self, *_args: object) -> None:
        """Close the underlying HTTP client on context exit."""
        self.close()


class HunterClient(BaseHttpClient):
    """Small sync client for Hunter.io API v2."""

    def __init__(
        self,
        api_key: str,
        base_url: str = api_constants.BASE_URL,
        timeout: float = api_constants.DEFAULT_TIMEOUT,
    ) -> None:
        """Create a sync Hunter API client."""
        self._http_client = httpx.Client(
            base_url=base_url,
            timeout=timeout,
            headers={"X-API-KEY": api_key},
        )
        super().__init__(self._http_client)

    def domain_search(
        self,
        domain: str,
        limit: int = 10,
    ) -> DomainSearchResult:
        """Search Hunter by company domain."""
        response_payload = self._get(
            "/domain-search",
            {api_constants.FIELD_DOMAIN: domain, "limit": limit},
        )
        result_payload = response_payload["data"]
        emails = result_payload.get(api_constants.FIELD_EMAILS, [])
        return DomainSearchResult(
            domain=result_payload[api_constants.FIELD_DOMAIN],
            organization=result_payload.get(api_constants.FIELD_ORGANIZATION),
            pattern=result_payload.get(api_constants.FIELD_PATTERN),
            email_count=len(emails),
            raw_data=result_payload,
        )

    def email_finder(
        self,
        domain: str,
        first_name: str,
        last_name: str,
    ) -> EmailFinderResult:
        """Find a likely email address for a person at a domain."""
        response_payload = self._get(
            "/email-finder",
            {
                api_constants.FIELD_DOMAIN: domain,
                api_constants.FIELD_FIRST_NAME: first_name,
                api_constants.FIELD_LAST_NAME: last_name,
            },
        )
        result_payload = response_payload["data"]
        return EmailFinderResult(
            email=result_payload.get(api_constants.FIELD_EMAIL),
            score=result_payload.get(api_constants.FIELD_SCORE),
            domain=result_payload.get(api_constants.FIELD_DOMAIN),
            raw_data=result_payload,
        )

    def email_verifier(self, email: str) -> EmailVerificationResult:
        """Verify whether an email address is deliverable."""
        response_payload = self._get(
            "/email-verifier",
            {api_constants.FIELD_EMAIL: email},
            allowed_status_codes={
                api_constants.HTTP_STATUS_OK,
                api_constants.HTTP_STATUS_ACCEPTED,
            },
        )
        pending = response_payload["status_code"] == api_constants.HTTP_STATUS_ACCEPTED
        result_payload = response_payload.get("data", {})
        return EmailVerificationResult(
            email=result_payload.get(api_constants.FIELD_EMAIL, email),
            status=result_payload.get(api_constants.FIELD_STATUS),
            verification_result=result_payload.get(api_constants.FIELD_RESULT),
            score=result_payload.get(api_constants.FIELD_SCORE),
            is_pending=pending,
            raw_data=result_payload,
        )

    def _get(
        self,
        path: str,
        query_params: dict[str, Any],
        allowed_status_codes: set[int] | None = None,
    ) -> dict[str, Any]:
        """Perform a GET request and validate the response status."""
        statuses = allowed_status_codes or {api_constants.HTTP_STATUS_OK}
        try:
            response = self._http_client.get(path, params=query_params)
        except httpx.HTTPError as transport_error:
            raise HunterTransportError(str(transport_error)) from transport_error
        try:
            response_payload = response.json()
        except json.JSONDecodeError as decode_error:
            raise HunterTransportError("Hunter returned a non-JSON response") from decode_error
        if response.status_code not in statuses:
            errors = response_payload.get("errors", [])
            raise HunterApiError(response.status_code, errors)
        response_payload["status_code"] = response.status_code
        return response_payload
