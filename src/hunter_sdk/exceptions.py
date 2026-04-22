"""SDK-specific exception types."""

from typing import Any


class HunterError(Exception):
    """Base exception for the SDK."""


class HunterTransportError(HunterError):
    """Raised when an HTTP transport error occurs."""


class HunterApiError(HunterError):
    """Raised when Hunter returns an unsuccessful response."""

    def __init__(
        self,
        status_code: int,
        errors: list[dict[str, Any]],
    ) -> None:
        """Store API error details and build a readable message."""
        self.status_code = status_code
        self.errors = errors
        super().__init__(self._build_message())

    def _build_message(self) -> str:
        details = ", ".join(
            "{id}: {details}".format(
                id=error.get("id", "unknown_error"),
                details=error.get("details", "unknown error"),
            )
            for error in self.errors
        )
        return "Hunter API error {status_code}: {details}".format(
            status_code=self.status_code,
            details=details,
        )
