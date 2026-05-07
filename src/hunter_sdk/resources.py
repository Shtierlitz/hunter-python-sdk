"""Namespaced Hunter API endpoint groups."""

from hunter_sdk import constants as api_constants
from hunter_sdk.exceptions import HunterTransportError
from hunter_sdk.models import DomainSearchResult, EmailFinderResult, EmailVerificationResult
from hunter_sdk.protocols import HunterRequesterProtocol
from hunter_sdk.response_parsing import read_object, read_object_list, read_optional_int, read_str


class HunterDomains:
    """Hunter domain-related API operations."""

    def __init__(self, requester: HunterRequesterProtocol) -> None:
        """Create domain operations backed by a JSON requester."""
        self._requester = requester

    def search(
        self,
        domain: str,
        limit: int = api_constants.DEFAULT_DOMAIN_SEARCH_LIMIT,
    ) -> DomainSearchResult:
        """Search Hunter by company domain."""
        response_payload, _status_code = self._requester.request_json(
            "/domain-search",
            {api_constants.FIELD_DOMAIN: domain, "limit": limit},
        )
        result_payload = read_object(response_payload, "data", required=True)
        emails = read_object_list(result_payload, api_constants.FIELD_EMAILS)
        domain_name = read_str(result_payload, api_constants.FIELD_DOMAIN, required=True)
        if domain_name is None:
            raise HunterTransportError("Hunter returned invalid `domain` string")
        return DomainSearchResult(
            domain=domain_name,
            organization=read_str(result_payload, api_constants.FIELD_ORGANIZATION, required=False),
            pattern=read_str(result_payload, api_constants.FIELD_PATTERN, required=False),
            email_count=len(emails),
            raw_data=result_payload,
        )


class HunterEmails:
    """Hunter email-related API operations."""

    def __init__(self, requester: HunterRequesterProtocol) -> None:
        """Create email operations backed by a JSON requester."""
        self._requester = requester

    def find(
        self,
        domain: str,
        first_name: str,
        last_name: str,
    ) -> EmailFinderResult:
        """Find a likely email address for a person at a domain."""
        response_payload, _status_code = self._requester.request_json(
            "/email-finder",
            {
                api_constants.FIELD_DOMAIN: domain,
                api_constants.FIELD_FIRST_NAME: first_name,
                api_constants.FIELD_LAST_NAME: last_name,
            },
        )
        result_payload = read_object(response_payload, "data", required=True)
        return EmailFinderResult(
            email=read_str(result_payload, api_constants.FIELD_EMAIL, required=False),
            score=read_optional_int(result_payload, api_constants.FIELD_SCORE),
            domain=read_str(result_payload, api_constants.FIELD_DOMAIN, required=False),
            raw_data=result_payload,
        )

    def verify(self, email: str) -> EmailVerificationResult:
        """Verify whether an email address is deliverable."""
        response_payload, status_code = self._requester.request_json(
            "/email-verifier",
            {api_constants.FIELD_EMAIL: email},
            allowed_status_codes={
                api_constants.HTTP_STATUS_OK,
                api_constants.HTTP_STATUS_ACCEPTED,
            },
        )
        pending = status_code == api_constants.HTTP_STATUS_ACCEPTED
        result_payload = read_object(response_payload, "data", required=False)
        email_result = read_str(result_payload, api_constants.FIELD_EMAIL, required=False)
        return EmailVerificationResult(
            email=email_result or email,
            status=read_str(result_payload, api_constants.FIELD_STATUS, required=False),
            verification_result=read_str(result_payload, api_constants.FIELD_RESULT, required=False),
            score=read_optional_int(result_payload, api_constants.FIELD_SCORE),
            is_pending=pending,
            raw_data=result_payload,
        )
