"""Unit tests for :mod:`doit_cli.services.personas_enricher`.

Linter-mode enricher: detects ``{placeholder}`` tokens and reports
``PARTIAL`` with a deduplicated, sorted ``unresolved_fields`` tuple.
Never modifies the file on disk. See spec 062 contracts/migrators.md §2.
"""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

import pytest

from doit_cli.services.constitution_enricher import EnrichmentAction
from doit_cli.services.personas_enricher import enrich_personas


@pytest.fixture
def tmp_personas(tmp_path: Path) -> Path:
    memory = tmp_path / ".doit" / "memory"
    memory.mkdir(parents=True)
    return memory / "personas.md"


def test_missing_file_returns_no_op(tmp_path: Path) -> None:
    """FR-010: absent file → NO_OP, zero issues, exit-0-compatible."""

    missing = tmp_path / ".doit" / "memory" / "personas.md"
    result = enrich_personas(missing)

    assert result.action is EnrichmentAction.NO_OP
    assert result.enriched_fields == ()
    assert result.unresolved_fields == ()
    assert result.error is None
    assert not missing.exists()


def test_file_with_no_placeholders_returns_no_op(tmp_personas: Path) -> None:
    """FR-008, FR-009: no placeholders → NO_OP, bytes unchanged."""

    source = (
        "# Personas\n\n"
        "## Persona Summary\n\n"
        "| ID | Name |\n|----|------|\n| P-001 | Dana |\n\n"
        "## Detailed Profiles\n\n"
        "### Persona: P-001\n\n"
        "Dana the developer ships fast.\n"
    )
    tmp_personas.write_text(source, encoding="utf-8")
    pre_bytes = tmp_personas.read_bytes()

    result = enrich_personas(tmp_personas)

    assert result.action is EnrichmentAction.NO_OP
    assert result.enriched_fields == ()
    assert result.unresolved_fields == ()
    assert tmp_personas.read_bytes() == pre_bytes


def test_file_with_placeholders_returns_partial_with_unresolved_fields(
    tmp_personas: Path,
) -> None:
    """FR-008, FR-009: placeholders detected → PARTIAL, sorted + deduplicated."""

    source = (
        "# Personas: {FEATURE_NAME}\n\n"
        "## Persona Summary\n\n"
        "| ID | Name | Role | Archetype | Primary Goal |\n"
        "|----|------|------|-----------|--------------|\n"
        "| P-001 | {Persona Name} | {Role} | {Archetype} | {Primary Goal} |\n"
    )
    tmp_personas.write_text(source, encoding="utf-8")

    result = enrich_personas(tmp_personas)

    assert result.action is EnrichmentAction.PARTIAL
    assert result.enriched_fields == ()
    # Sorted alphabetically and deduplicated.
    assert result.unresolved_fields == (
        "Archetype",
        "FEATURE_NAME",
        "Persona Name",
        "Primary Goal",
        "Role",
    )


def test_enricher_never_modifies_file(tmp_personas: Path) -> None:
    """Linter-mode: disk bytes never change, even with PARTIAL result."""

    source = "# Personas\n\n{Persona Name} is a developer.\n"
    tmp_personas.write_text(source, encoding="utf-8")
    pre_bytes = tmp_personas.read_bytes()

    result = enrich_personas(tmp_personas)

    assert result.action is EnrichmentAction.PARTIAL
    assert tmp_personas.read_bytes() == pre_bytes


def test_enricher_handles_crlf_encoding(tmp_personas: Path) -> None:
    """CRLF source must not break the regex scan."""

    source_crlf = "# Personas\r\n\r\n{Persona Name}\r\n"
    tmp_personas.write_bytes(source_crlf.encode("utf-8"))

    result = enrich_personas(tmp_personas)

    assert result.action is EnrichmentAction.PARTIAL
    assert result.unresolved_fields == ("Persona Name",)
    # Bytes unchanged.
    assert tmp_personas.read_bytes() == source_crlf.encode("utf-8")


def test_enricher_handles_oserror(tmp_personas: Path) -> None:
    """ERROR path when read fails."""

    tmp_personas.write_text("# Personas\n", encoding="utf-8")

    def _raise_oserror(self: Path) -> bytes:
        raise OSError("simulated read failure")

    with patch.object(Path, "read_bytes", _raise_oserror):
        result = enrich_personas(tmp_personas)

    assert result.action is EnrichmentAction.ERROR
    assert result.error is not None
    assert "simulated read failure" in str(result.error)


def test_enricher_rejects_shell_variable_syntax(tmp_personas: Path) -> None:
    """``${VAR}`` is shell syntax, NOT a placeholder — must be ignored."""

    source = (
        "# Personas\n\n"
        "Example shell usage: ${VAR} and ${HOME}/docs.\n"
        "But {RealPlaceholder} IS a placeholder.\n"
    )
    tmp_personas.write_text(source, encoding="utf-8")

    result = enrich_personas(tmp_personas)

    assert result.action is EnrichmentAction.PARTIAL
    # Only the template-style token is reported.
    assert result.unresolved_fields == ("RealPlaceholder",)
    assert "VAR" not in result.unresolved_fields
    assert "HOME" not in result.unresolved_fields


def test_enricher_deduplicates_same_token(tmp_personas: Path) -> None:
    """Repeated ``{Persona Name}`` → single entry in unresolved_fields."""

    source = (
        "# Personas\n\n"
        "{Persona Name} is a developer.\n"
        "Again: {Persona Name}.\n"
        "Once more: {Persona Name}.\n"
    )
    tmp_personas.write_text(source, encoding="utf-8")

    result = enrich_personas(tmp_personas)

    assert result.action is EnrichmentAction.PARTIAL
    assert result.unresolved_fields == ("Persona Name",)
