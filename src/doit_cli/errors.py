"""Shared error hierarchy for the doit CLI.

Every error raised at a domain boundary should subclass one of the types
below so callers can catch by category rather than the bare `Exception`.
Legacy module-local hierarchies (TeamError, WorkflowError, GitHubServiceError)
are being re-parented to these categories as each service is modernized.
"""

from __future__ import annotations


class DoitError(Exception):
    """Base class for all doit-originated errors.

    Catch this at the CLI entry point to turn any unexpected failure into a
    user-facing Rich message with a non-zero exit code. Internal code should
    raise a more specific subclass.
    """


class DoitConfigError(DoitError):
    """Configuration is missing, malformed, or inconsistent.

    Raised by loaders that parse YAML/JSON/TOML in `.doit/config/`,
    constitution files, team configs, or project-level settings.
    """


class DoitStateError(DoitError):
    """Persisted workflow state is corrupt, stale, or from an incompatible version.

    Raised when reading/writing `.doit/state/` files. A `DoitStateError` implies
    the user's state directory needs repair or reset — never a recoverable
    condition.
    """


class DoitTemplateError(DoitError):
    """A bundled template or rendered command output is invalid.

    Raised by template readers, skill validators, and the sync/prompt
    generators. Typically indicates a packaging bug rather than user error.
    """


class DoitProviderError(DoitError):
    """A remote provider (GitHub, GitLab, Azure DevOps) failed a request.

    Wraps `subprocess.CalledProcessError`, `httpx.HTTPError`, and provider-
    specific CLI errors. Subclass for auth- vs API- vs rate-limit distinctions.
    """


class DoitAuthError(DoitProviderError):
    """Authentication with a remote provider failed or is missing."""


class DoitValidationError(DoitError):
    """User-supplied input failed validation.

    Raised when CLI arguments, interactive prompts, or file contents violate
    a documented contract. Always carry a message fit to show the user.
    """
