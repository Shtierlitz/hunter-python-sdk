"""Tests for package-level public exports."""

from hunter_sdk import HunterClient, HunterService, InMemoryStorage


def test_package_reexports_public_classes() -> None:
    """Top-level package should expose the public SDK classes."""
    assert HunterClient.__name__ == "HunterClient"
    assert HunterService.__name__ == "HunterService"
    assert InMemoryStorage.__name__ == "InMemoryStorage"
