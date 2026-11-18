"""Exceptions for aioopenmeteo."""

from __future__ import annotations


class OpenMeteoError(Exception):
    """Base class for all aioopenmeteo errors."""


class OpenMeteoConnectionError(OpenMeteoError):
    """Network problem or timeout talking to Open-Meteo."""


class OpenMeteoRequestError(OpenMeteoError):
    """Open-Meteo answered with an HTTP error."""

    def __init__(self, status: int, reason: str) -> None:
        super().__init__(f"HTTP {status}: {reason}")
        self.status = status
        self.reason = reason


class OpenMeteoInvalidLocationError(OpenMeteoRequestError):
    """The selected model has no data for this location (regional model elsewhere)."""


class OpenMeteoRateLimitError(OpenMeteoRequestError):
    """The free API limit was hit (HTTP 429)."""

    def __init__(self, reason: str, retry_after: float | None = None) -> None:
        super().__init__(429, reason)
        self.retry_after = retry_after


class OpenMeteoParseError(OpenMeteoError):
    """The response could not be understood."""
