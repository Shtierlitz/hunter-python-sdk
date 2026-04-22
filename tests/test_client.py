"""Tests for the HTTP client layer."""

import httpx
import pytest
import respx

from hunter_sdk.client import HunterClient
from hunter_sdk.exceptions import HunterApiError, HunterTransportError

from conftest import build_response


@respx.mock
def test_domain_search_returns_typed_result(
    client: HunterClient,
    response_headers: dict[str, str],
) -> None:
    """Domain search should return a normalized typed result."""
    respx.get("https://api.hunter.io/v2/domain-search").mock(
        return_value=build_response(
            200,
            {
                "data": {
                    "domain": "durmstrang.com",
                    "organization": "Example",
                    "pattern": "{first}",
                    "emails": [{"value": "viktor@durmstrang.com"}],
                },
                "meta": {"results": 1},
            },
        ),
    )

    domain_search_result = client.domain_search(domain="durmstrang.com")

    assert domain_search_result.domain == "durmstrang.com"
    assert domain_search_result.organization == "Example"
    assert domain_search_result.email_count == 1
    assert domain_search_result.raw_data["pattern"] == "{first}"


@respx.mock
def test_email_finder_returns_typed_result(client: HunterClient) -> None:
    """Email finder should return a normalized typed result."""
    respx.get("https://api.hunter.io/v2/email-finder").mock(
        return_value=build_response(
            200,
            {
                "data": {
                    "email": "igor@durmstrang.com",
                    "score": 97,
                    "domain": "durmstrang.com",
                    "position": "CEO",
                },
            },
        ),
    )

    email_finder_result = client.email_finder(
        domain="example.com",
        first_name="Igor",
        last_name="Karkarov",
    )

    assert email_finder_result.email == "igor@durmstrang.com"
    assert email_finder_result.score == 97
    assert email_finder_result.domain == "durmstrang.com"


@respx.mock
def test_email_verifier_returns_typed_result(client: HunterClient) -> None:
    """Email verifier should return a normalized typed result."""
    respx.get("https://api.hunter.io/v2/email-verifier").mock(
        return_value=build_response(
            200,
            {
                "data": {
                    "email": "igor@durmstrang.com",
                    "status": "valid",
                    "result": "deliverable",
                    "score": 99,
                },
            },
        ),
    )

    email_verification_result = client.email_verifier(email="igor@durmstrang.com")

    assert email_verification_result.email == "igor@durmstrang.com"
    assert email_verification_result.status == "valid"
    assert email_verification_result.verification_result == "deliverable"


@respx.mock
def test_email_verifier_maps_accepted_response(client: HunterClient) -> None:
    """Accepted verification responses should be marked as pending."""
    respx.get("https://api.hunter.io/v2/email-verifier").mock(
        return_value=build_response(
            202,
            {
                "data": {
                    "email": "igor@durmstrang.com",
                },
            },
        ),
    )

    email_verification_result = client.email_verifier(email="igor@durmstrang.com")

    assert email_verification_result.email == "igor@durmstrang.com"
    assert email_verification_result.is_pending is True


@respx.mock
def test_email_verifier_handles_accepted_response_without_data(
    client: HunterClient,
) -> None:
    """Accepted responses without ``data`` should still map to pending result."""
    respx.get("https://api.hunter.io/v2/email-verifier").mock(
        return_value=build_response(
            202,
            {
                "errors": [
                    {
                        "id": "verification_in_progress",
                        "code": 202,
                        "details": "Verification still in progress",
                    },
                ],
            },
        ),
    )

    email_verification_result = client.email_verifier(email="igor@durmstrang.com")

    assert (
        email_verification_result.email,
        email_verification_result.status,
        email_verification_result.verification_result,
        email_verification_result.score,
        email_verification_result.is_pending,
    ) == ("igor@durmstrang.com", None, None, None, True)
    assert not email_verification_result.raw_data


@respx.mock
def test_client_raises_api_error_for_failed_response(client: HunterClient) -> None:
    """Client should raise API error for non-success responses."""
    respx.get("https://api.hunter.io/v2/domain-search").mock(
        return_value=build_response(
            400,
            {
                "errors": [
                    {
                        "id": "wrong_params",
                        "code": 400,
                        "details": "You are missing the domain parameter",
                    },
                ],
            },
        ),
    )

    with pytest.raises(HunterApiError) as error_info:
        client.domain_search(domain="")

    assert error_info.value.status_code == 400
    assert "wrong_params" in str(error_info.value)


@respx.mock
def test_client_raises_transport_error(client: HunterClient) -> None:
    """Client should wrap transport exceptions."""
    respx.get("https://api.hunter.io/v2/domain-search").mock(
        side_effect=httpx.ConnectError("boom"),
    )

    with pytest.raises(HunterTransportError):
        client.domain_search(domain="durmstrang.com")


@respx.mock
def test_client_wraps_non_json_response(client: HunterClient) -> None:
    """Client should wrap invalid JSON responses as transport errors."""
    respx.get("https://api.hunter.io/v2/domain-search").mock(
        return_value=httpx.Response(
            502,
            text="bad gateway",
            headers={"Content-Type": "text/plain"},
        ),
    )

    with pytest.raises(HunterTransportError):
        client.domain_search(domain="durmstrang.com")


def test_client_can_be_closed_explicitly() -> None:
    """Client should expose explicit close support."""
    client = HunterClient(api_key="test-api-key")

    client.close()

    assert client.is_closed is True


def test_client_closes_on_context_manager_exit() -> None:
    """Context manager exit should close the client."""
    with HunterClient(api_key="test-api-key") as client:
        assert client.is_closed is False

    assert client.is_closed is True
