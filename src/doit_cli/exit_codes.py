"""Canonical exit codes for the doit CLI.

Keep every `typer.Exit(code=…)` call site and every `sys.exit(…)` call
site in this codebase pointing at one of these constants. Ad-hoc
integers (`raise typer.Exit(code=2)`) obscure intent and make it
impossible to reason about CLI contract compatibility across versions.

Values follow POSIX-ish conventions: 0 success, 1 generic failure,
2 usage/validation error, higher numbers for specific categories so
shell scripts can branch on them.
"""

from __future__ import annotations

from enum import IntEnum


class ExitCode(IntEnum):
    """Exit codes emitted by doit CLI commands."""

    SUCCESS = 0
    """Command completed successfully."""

    FAILURE = 1
    """Generic failure: a condition the user asked about was false, or
    an operation could not complete but the reason doesn't merit a
    dedicated code."""

    VALIDATION_ERROR = 2
    """Input was syntactically or semantically invalid before any
    remote call was made. Includes missing required args, malformed
    YAML/JSON the user supplied, and spec files that fail validation."""

    PROVIDER_ERROR = 3
    """A remote provider (GitHub, GitLab, Azure DevOps) returned an
    error or was unreachable. Distinct from FAILURE so CI scripts can
    retry selectively."""

    AUTH_ERROR = 4
    """Authentication with a remote provider failed or is missing
    (e.g. `gh` not logged in, token expired)."""

    STATE_ERROR = 5
    """Persisted workflow state in `.doit/state/` is corrupt or
    incompatible; user must reset or repair."""

    USER_CANCEL = 130
    """User aborted (Ctrl+C or explicit decline at an interactive prompt).
    Matches the conventional SIGINT-terminated exit code (128 + 2)."""
