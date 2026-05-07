"""HTTP client for the supported Hunter API endpoints."""

import json
from collections.abc import Mapping

import httpx

from hunter_sdk import constants as api_constants
from hunter_sdk.exceptions import HunterApiError, HunterTransportError
from hunter_sdk.models import JsonObject, RequestParamValue
from hunter_sdk.resources import HunterDomains, HunterEmails
from hunter_sdk.response_parsing import ensure_json_object, read_object_list


class HunterApiClient:
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
        self.domains = HunterDomains(requester=self)
        self.emails = HunterEmails(requester=self)

    def close(self) -> None:
        """Close the underlying HTTP client."""
        self._http_client.close()

    def request_json(
        self,
        path: str,
        query_params: Mapping[str, RequestParamValue],
        allowed_status_codes: set[int] | None = None,
    ) -> tuple[JsonObject, int]:
        """Perform a GET request and validate the response status."""
        statuses = allowed_status_codes or {api_constants.HTTP_STATUS_OK}
        self._ensure_open()
        try:
            response = self._http_client.get(path, params=query_params)
        except httpx.HTTPError as transport_error:
            raise HunterTransportError(str(transport_error)) from transport_error
        try:
            decoded_payload: object = response.json()
        except json.JSONDecodeError as decode_error:
            raise HunterTransportError("Hunter returned a non-JSON response") from decode_error
        response_payload = ensure_json_object(decoded_payload)
        if response.status_code not in statuses:
            errors = read_object_list(response_payload, "errors")
            raise HunterApiError(response.status_code, errors)
        return response_payload, response.status_code

    def _ensure_open(self) -> None:
        """Fail before sending requests through a closed HTTP client."""
        if self._http_client.is_closed:
            raise HunterTransportError("Hunter API client is closed")
