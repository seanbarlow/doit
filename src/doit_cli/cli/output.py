"""Shared `--format` option plumbing for doit CLI commands.

Every command that produces a report to stdout should accept the same
`--format / -f` flag with the same set of values, so scripts piping
between doit commands don't need to learn per-command dialects.

The existing `doit_cli.formatters` package already contains Rich/JSON/
Markdown `StatusFormatter` implementations for the status command;
this module adds the surrounding convention (Typer Option factory +
enum) without replacing those formatters.
"""

from __future__ import annotations

from enum import Enum

import typer


class OutputFormat(str, Enum):
    """Canonical `--format` values accepted across doit commands.

    Individual commands pick the subset they support and pass it as
    the `allowed` argument to `format_option()`. Using a shared enum
    prevents drift like `table|json` vs `rich|json|table` vs
    `rich|json|markdown` popping up across the tree.
    """

    RICH = "rich"
    """Human-readable output using Rich console styling (default)."""

    JSON = "json"
    """Machine-readable JSON. Use this when piping to jq, another doit
    command, or CI."""

    MARKDOWN = "markdown"
    """GitHub-flavored markdown suitable for PR bodies or docs."""

    TABLE = "table"
    """Plain text tabular output. Use for reports where Rich styling
    would confuse a downstream tool."""

    YAML = "yaml"
    """YAML output for commands that emit config-shaped data."""

    CSV = "csv"
    """Comma-separated values for analytics reports."""


def format_option(
    *,
    default: OutputFormat = OutputFormat.RICH,
    allowed: tuple[OutputFormat, ...] | None = None,
    help_text: str | None = None,
) -> typer.models.OptionInfo:
    """Return a Typer Option configured with the shared `--format/-f` convention.

    Pass the set of formats a command supports via `allowed`; Typer will
    reject any other value at parse time. If `allowed` is None, every
    OutputFormat is accepted.

    Use like:

        format: OutputFormat = format_option(
            default=OutputFormat.RICH,
            allowed=(OutputFormat.RICH, OutputFormat.JSON, OutputFormat.MARKDOWN),
        )
    """
    accepted = allowed if allowed is not None else tuple(OutputFormat)
    accepted_list = ", ".join(f.value for f in accepted)

    return typer.Option(
        default.value,
        "--format",
        "-f",
        help=help_text or f"Output format. One of: {accepted_list}.",
        case_sensitive=False,
    )


def resolve_format(value: str, allowed: tuple[OutputFormat, ...]) -> OutputFormat:
    """Validate a raw `--format` string against `allowed`, returning the enum.

    Raises `typer.BadParameter` if the value isn't one of the allowed
    formats for this command. Call this at the top of command functions
    that want the enum value rather than the raw string.
    """
    try:
        fmt = OutputFormat(value.lower())
    except ValueError as exc:
        accepted = ", ".join(f.value for f in allowed)
        raise typer.BadParameter(
            f"Unknown format '{value}'. Supported: {accepted}.",
        ) from exc

    if fmt not in allowed:
        accepted = ", ".join(f.value for f in allowed)
        raise typer.BadParameter(
            f"Format '{fmt.value}' not supported by this command. Supported: {accepted}.",
        )

    return fmt
