"""Integration tests for ``.doit/memory/personas.md`` migration.

Covers the behavioural contract in
``specs/062-personas-migration/contracts/migrators.md`` and the quickstart
scenarios 1-5 and 12. US1 (existing file shape-migrated) and US2 (absent
file is opt-in NO_OP) live together here — the same ``migrate_personas``
function handles both paths.

CLI tests for ``doit memory migrate`` and ``doit memory enrich personas``
are appended later by T007 and T010.
"""

from __future__ import annotations

import hashlib
from pathlib import Path

import pytest

from doit_cli.services.constitution_migrator import MigrationAction
from doit_cli.services.personas_migrator import (
    REQUIRED_PERSONAS_H2,
    migrate_personas,
)

MINIMAL_COMPLETE_PERSONAS = """# Personas

## Persona Summary

| ID | Name | Role | Archetype | Primary Goal |
|----|------|------|-----------|--------------|
| P-001 | Dana | Developer | Power User | Ship fast |

## Detailed Profiles

### Persona: P-001

Dana the developer works on cross-functional teams.
"""


ONLY_PERSONA_SUMMARY = """# Personas

## Persona Summary

| ID | Name | Role | Archetype | Primary Goal |
|----|------|------|-----------|--------------|
| P-001 | Dana | Developer | Power User | Ship fast |
"""


ONLY_DETAILED_PROFILES = """# Personas

## Detailed Profiles

### Persona: P-001

Dana the developer.
"""


LEGACY_PERSONAS_NO_REQUIRED_H2 = """# Old notes

Some unrelated prose about personas in general.

## Intro

Random content that pre-dates the 0.4.0 memory contract.
"""


@pytest.fixture
def tmp_personas(tmp_path: Path) -> Path:
    memory = tmp_path / ".doit" / "memory"
    memory.mkdir(parents=True)
    return memory / "personas.md"


def _sha(text: str) -> bytes:
    return hashlib.sha256(text.encode("utf-8")).digest()


# ---------------------------------------------------------------------------
# US2 — opt-in semantic: absent file is a valid NO_OP.


def test_missing_file_is_noop(tmp_path: Path) -> None:
    """FR-002, SC-001: personas.md absent → NO_OP, no file created."""

    missing = tmp_path / ".doit" / "memory" / "personas.md"
    result = migrate_personas(missing)

    assert result.action is MigrationAction.NO_OP
    assert result.added_fields == ()
    assert result.error is None
    # Opt-in: the migrator MUST NOT create the file.
    assert not missing.exists()


# ---------------------------------------------------------------------------
# US1 — shape migration for existing files.


def test_missing_persona_summary_is_patched(tmp_personas: Path) -> None:
    """FR-004: ## Persona Summary missing → PATCHED, added_fields includes it."""

    tmp_personas.write_text(ONLY_DETAILED_PROFILES, encoding="utf-8")
    result = migrate_personas(tmp_personas)

    assert result.action is MigrationAction.PATCHED
    assert "Persona Summary" in result.added_fields
    assert "Detailed Profiles" not in result.added_fields

    post = tmp_personas.read_text(encoding="utf-8")
    assert post.count("## Persona Summary") == 1
    # Original content byte-preserved.
    assert "### Persona: P-001" in post
    assert "Dana the developer." in post


def test_missing_detailed_profiles_is_patched(tmp_personas: Path) -> None:
    """FR-004: ## Detailed Profiles missing → PATCHED with just that H2."""

    tmp_personas.write_text(ONLY_PERSONA_SUMMARY, encoding="utf-8")
    result = migrate_personas(tmp_personas)

    assert result.action is MigrationAction.PATCHED
    assert result.added_fields == ("Detailed Profiles",)

    post = tmp_personas.read_text(encoding="utf-8")
    assert post.count("## Detailed Profiles") == 1
    # Original Persona Summary table preserved.
    assert "| P-001 | Dana | Developer | Power User | Ship fast |" in post


def test_both_h2s_missing_patches_both(tmp_personas: Path) -> None:
    """FR-004: both required H2s absent but file exists → both stubs added."""

    tmp_personas.write_text(LEGACY_PERSONAS_NO_REQUIRED_H2, encoding="utf-8")
    result = migrate_personas(tmp_personas)

    assert result.action is MigrationAction.PATCHED
    assert set(result.added_fields) == set(REQUIRED_PERSONAS_H2)

    post = tmp_personas.read_text(encoding="utf-8")
    # Pre-existing unrelated prose must survive.
    assert "## Intro" in post
    assert "Random content that pre-dates" in post
    # Both required H2s now present.
    assert "## Persona Summary" in post
    assert "## Detailed Profiles" in post


def test_complete_personas_is_noop(tmp_personas: Path) -> None:
    """FR-003, SC-003: complete file → NO_OP, byte-identical."""

    tmp_personas.write_text(MINIMAL_COMPLETE_PERSONAS, encoding="utf-8")
    pre_bytes = tmp_personas.read_bytes()

    result = migrate_personas(tmp_personas)

    assert result.action is MigrationAction.NO_OP
    assert result.added_fields == ()
    assert tmp_personas.read_bytes() == pre_bytes
    # SHA-256 populated on NO_OP (matches spec 060 convention).
    assert result.preserved_body_hash == _sha(MINIMAL_COMPLETE_PERSONAS)


def test_migration_is_idempotent(tmp_personas: Path) -> None:
    """SC-002: rerun after PATCHED → NO_OP, no further byte changes."""

    tmp_personas.write_text(ONLY_PERSONA_SUMMARY, encoding="utf-8")

    first = migrate_personas(tmp_personas)
    assert first.action is MigrationAction.PATCHED
    after_first = tmp_personas.read_bytes()

    second = migrate_personas(tmp_personas)
    assert second.action is MigrationAction.NO_OP
    assert tmp_personas.read_bytes() == after_first


def test_migrator_preserves_crlf_line_endings(tmp_personas: Path) -> None:
    """CRLF regression guard — mirrors spec 060's guard in test_roadmap_migration.

    The migrator uses ``read_bytes().decode("utf-8")`` + ``_detect_newline``
    (via the shared helper) to preserve CRLF round-trips.
    """

    # Write CRLF bytes explicitly via write_bytes to avoid Python's universal-
    # newline translation.
    source_crlf = ONLY_PERSONA_SUMMARY.replace("\n", "\r\n")
    tmp_personas.write_bytes(source_crlf.encode("utf-8"))

    result = migrate_personas(tmp_personas)
    assert result.action is MigrationAction.PATCHED
    assert "Detailed Profiles" in result.added_fields

    post_bytes = tmp_personas.read_bytes()
    # Must still be predominantly CRLF after migration.
    assert b"\r\n" in post_bytes
    # A bare LF would signal line-ending corruption — check there are NO
    # bare-LF runs (any \n must be preceded by \r).
    for i, byte in enumerate(post_bytes):
        if byte == 0x0A and (i == 0 or post_bytes[i - 1] != 0x0D):
            raise AssertionError(
                f"bare LF detected at offset {i} — CRLF preservation regressed"
            )


def test_body_outside_required_sections_preserved(tmp_personas: Path) -> None:
    """Bytes outside the inserted H2 stubs stay byte-identical."""

    source = (
        "# Personas\n\n"
        "## Persona Summary\n\n"
        "| ID | Name |\n|----|------|\n| P-001 | Dana |\n\n"
        "## Glossary\n\n"
        "Some glossary text.\n"
    )
    tmp_personas.write_text(source, encoding="utf-8")

    result = migrate_personas(tmp_personas)
    assert result.action is MigrationAction.PATCHED
    assert result.added_fields == ("Detailed Profiles",)

    post = tmp_personas.read_text(encoding="utf-8")
    assert "## Glossary\n\nSome glossary text.\n" in post
    assert "| P-001 | Dana |" in post


# ---------------------------------------------------------------------------
# CLI integration: doit memory enrich personas (T007) + umbrella (T010).


def test_cli_memory_enrich_personas_partial(tmp_path: Path) -> None:
    """FR-011: `doit memory enrich personas` reports PARTIAL with exit 1."""

    from typer.testing import CliRunner

    from doit_cli.main import app as doit_app

    memory = tmp_path / ".doit" / "memory"
    memory.mkdir(parents=True)
    (memory / "personas.md").write_text(
        "# Personas\n\n{Persona Name} works here.\n",
        encoding="utf-8",
    )

    runner = CliRunner()
    result = runner.invoke(
        doit_app,
        ["memory", "enrich", "personas", str(tmp_path), "--json"],
    )
    assert result.exit_code == 1, result.stdout

    import json as jsonlib

    payload = jsonlib.loads(result.stdout)
    assert payload["action"] == "partial"
    assert payload["unresolved_fields"] == ["Persona Name"]


def test_cli_memory_enrich_personas_no_op_when_absent(tmp_path: Path) -> None:
    """FR-010: absent personas.md → exit 0 NO_OP."""

    from typer.testing import CliRunner

    from doit_cli.main import app as doit_app

    memory = tmp_path / ".doit" / "memory"
    memory.mkdir(parents=True)
    # No personas.md

    runner = CliRunner()
    result = runner.invoke(
        doit_app,
        ["memory", "enrich", "personas", str(tmp_path), "--json"],
    )
    assert result.exit_code == 0, result.stdout

    import json as jsonlib

    payload = jsonlib.loads(result.stdout)
    assert payload["action"] == "no_op"
    assert payload["unresolved_fields"] == []
    # File must still not exist.
    assert not (memory / "personas.md").exists()
