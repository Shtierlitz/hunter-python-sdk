"""Optional smoke demo for the Hunter SDK.

This script is not part of the required SDK implementation.
It exists as a runnable example that exercises the supported API calls.
"""

import os
from pathlib import Path
from pprint import pprint

from hunter_sdk.client import HunterClient
from hunter_sdk.exceptions import HunterApiError, HunterTransportError
from hunter_sdk.service import HunterService
from hunter_sdk.storage import InMemoryStorage


def _print_section(title: str) -> None:
    print(f"\n=== {title} ===")


def _get_env(name: str, default: str) -> str:
    value = os.getenv(name)
    if value:
        return value
    return default


def _load_dotenv(dotenv_path: Path) -> None:
    if not dotenv_path.exists():
        return

    for raw_line in dotenv_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        name, value = line.split("=", maxsplit=1)
        normalized_value = value.strip()
        if (
            len(normalized_value) >= 2
            and normalized_value[0] == normalized_value[-1]
            and normalized_value[0] in {'"', "'"}
        ):
            normalized_value = normalized_value[1:-1]
        os.environ.setdefault(name.strip(), normalized_value)


def main() -> int:
    """Run the three supported Hunter operations and print the results."""
    _load_dotenv(Path(".env"))
    api_key = _get_env("HUNTER_API_KEY", "test-api-key")
    domain = _get_env("HUNTER_DOMAIN", "stripe.com")
    first_name = _get_env("HUNTER_FIRST_NAME", "Patrick")
    last_name = _get_env("HUNTER_LAST_NAME", "Collison")
    email = _get_env("HUNTER_EMAIL", "patrick@stripe.com")

    storage = InMemoryStorage()
    client = HunterClient(api_key=api_key)
    service = HunterService(client=client, storage=storage)

    print("Running optional smoke demo for the Hunter SDK.")
    print(f"Domain: {domain}")
    print(f"Name: {first_name} {last_name}")
    print(f"Email: {email}")

    try:
        _print_section("Domain Search")
        domain_record = service.search_domain(domain=domain)
        pprint(domain_record)

        _print_section("Email Finder")
        finder_record = service.find_email(
            domain=domain,
            first_name=first_name,
            last_name=last_name,
        )
        pprint(finder_record)

        _print_section("Email Verifier")
        verifier_record = service.verify_email(email=email)
        pprint(verifier_record)
    except HunterApiError as api_error:
        print(f"Hunter API error: {api_error}")
        return 1
    except HunterTransportError as transport_error:
        print(f"Transport error: {transport_error}")
        return 1

    _print_section("Stored Records")
    pprint(storage.list())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
