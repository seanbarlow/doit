"""Provider exception hierarchy.

This module defines all exceptions that can be raised by git provider operations.
"""

from typing import Optional


class ProviderError(Exception):
    """Base exception for all provider errors."""

    def __init__(self, message: str, cause: Optional[Exception] = None):
        super().__init__(message)
        self.message = message
        self.cause = cause

    def __str__(self) -> str:
        if self.cause:
            return f"{self.message} (caused by: {self.cause})"
        return self.message


class AuthenticationError(ProviderError):
    """Raised when authentication fails.

    This error indicates that the provider credentials are missing,
    expired, or invalid.
    """

    def __init__(
        self,
        message: str = "Authentication failed",
        cause: Optional[Exception] = None,
        provider: Optional[str] = None,
    ):
        super().__init__(message, cause)
        self.provider = provider


class RateLimitError(ProviderError):
    """Raised when API rate limit is exceeded.

    This error indicates that the provider's API rate limit has been
    reached. The retry_after attribute indicates when to retry.
    """

    def __init__(
        self,
        message: str = "Rate limit exceeded",
        retry_after: Optional[int] = None,
        cause: Optional[Exception] = None,
    ):
        super().__init__(message, cause)
        self.retry_after = retry_after  # Seconds until rate limit resets

    def __str__(self) -> str:
        base = super().__str__()
        if self.retry_after:
            return f"{base} (retry after {self.retry_after} seconds)"
        return base


class ResourceNotFoundError(ProviderError):
    """Raised when a requested resource does not exist.

    This error indicates that the requested issue, PR, milestone,
    or other resource was not found.
    """

    def __init__(
        self,
        resource_type: str,
        resource_id: str,
        cause: Optional[Exception] = None,
    ):
        message = f"{resource_type} not found: {resource_id}"
        super().__init__(message, cause)
        self.resource_type = resource_type
        self.resource_id = resource_id


class ValidationError(ProviderError):
    """Raised when request validation fails.

    This error indicates that the request parameters are invalid
    or don't meet the provider's requirements.
    """

    def __init__(
        self,
        message: str,
        field: Optional[str] = None,
        cause: Optional[Exception] = None,
    ):
        super().__init__(message, cause)
        self.field = field

    def __str__(self) -> str:
        base = super().__str__()
        if self.field:
            return f"{base} (field: {self.field})"
        return base


class NetworkError(ProviderError):
    """Raised when a network operation fails.

    This error indicates connectivity issues, timeouts,
    or other network-related failures.
    """

    def __init__(
        self,
        message: str = "Network error",
        cause: Optional[Exception] = None,
        is_timeout: bool = False,
    ):
        super().__init__(message, cause)
        self.is_timeout = is_timeout


class ProviderNotConfiguredError(ProviderError):
    """Raised when no provider is configured.

    This error indicates that the user needs to configure
    a git provider before using provider features.
    """

    def __init__(
        self,
        message: str = "No git provider configured. Run 'doit provider configure' first.",
        cause: Optional[Exception] = None,
    ):
        super().__init__(message, cause)


class ProviderNotImplementedError(ProviderError):
    """Raised when a provider operation is not implemented.

    This is used for stub implementations (e.g., GitLab)
    to indicate the operation is not yet available.
    """

    def __init__(
        self,
        provider: str,
        operation: str,
        cause: Optional[Exception] = None,
    ):
        message = (
            f"{provider} provider does not support '{operation}' yet. "
            f"See https://github.com/seanbarlow/doit/issues for status."
        )
        super().__init__(message, cause)
        self.provider = provider
        self.operation = operation
