"""Tests for package-level public exports."""

from hunter_sdk import HunterApiClient, HunterRecordsGateway, InMemoryStorage


def test_package_reexports_public_classes() -> None:
    """Top-level package should expose the public SDK classes."""
    assert HunterApiClient.__name__ == "HunterApiClient"
    assert HunterRecordsGateway.__name__ == "HunterRecordsGateway"
    assert InMemoryStorage.__name__ == "InMemoryStorage"
