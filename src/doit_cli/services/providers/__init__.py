"""Git provider implementations.

This package contains the provider abstraction layer for git hosting platforms
including GitHub, Azure DevOps, and GitLab.
"""

from __future__ import annotations

from .base import GitProvider, ProviderType
from .exceptions import (
    AuthenticationError,
    NetworkError,
    ProviderError,
    RateLimitError,
    ResourceNotFoundError,
    ValidationError,
)

__all__ = [
    "AuthenticationError",
    "GitProvider",
    "NetworkError",
    "ProviderError",
    "ProviderType",
    "RateLimitError",
    "ResourceNotFoundError",
    "ValidationError",
]
