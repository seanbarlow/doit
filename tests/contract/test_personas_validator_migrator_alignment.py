"""Contract: personas validator ↔ migrator ID bijection.

Mirrors the spec 061 ``test_roadmap_validator_migrator_alignment.py``
pattern. Every persona ID the validator accepts (``P-\\d{3}``) must be
treated as valid by the migrator and produce zero issues from
``validate_project``. Conversely, every malformed ID must be flagged by
the validator.

Also locks the umbrella migrate output order (4 rows: constitution →
roadmap → tech-stack → personas).
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

_PERSONA_ID_RE = re.compile(r"^P-\d{3}$")


_CONSTITUTION_MINIMAL = """---
id: app-contract
name: Contract Test App
kind: application
phase: 1
icon: CT
tagline: Minimal app for contract-test fixtures.
dependencies: []
---
# Contract Test

## Purpose & Goals

### Project Purpose

Exercise validator-migrator alignment.
"""


_TECH_STACK_MINIMAL = """# Tech Stack

## Tech Stack

### Languages

Python 3.11

### Frameworks

Typer

### Libraries

Rich
"""


_ROADMAP_MINIMAL = """# Roadmap

## Active Requirements

### P1

- Ship fast
"""


def _build_project_with_personas(tmp_path: Path, personas_body: str | None) -> Path:
    """Build a minimal valid project tree. personas_body=None → no personas.md."""

    memory = tmp_path / ".doit" / "memory"
    memory.mkdir(parents=True)
    (memory / "constitution.md").write_text(_CONSTITUTION_MINIMAL, encoding="utf-8")
    (memory / "tech-stack.md").write_text(_TECH_STACK_MINIMAL, encoding="utf-8")
    (memory / "roadmap.md").write_text(_ROADMAP_MINIMAL, encoding="utf-8")
    if personas_body is not None:
        (memory / "personas.md").write_text(personas_body, encoding="utf-8")
    return memory / "personas.md"


def _minimal_valid_personas(persona_id: str) -> str:
    return (
        "# Personas\n\n"
        "## Persona Summary\n\n"
        "| ID | Name | Role | Archetype | Primary Goal |\n"
        "|----|------|------|-----------|--------------|\n"
        f"| {persona_id} | Alex | Engineer | Power User | Ship |\n\n"
        "## Detailed Profiles\n\n"
        f"### Persona: {persona_id}\n\n"
        "Alex the engineer.\n"
    )


# ---------------------------------------------------------------------------
# Positive corpus — validator accepts these IDs.


@pytest.mark.parametrize(
    "persona_id", ["P-001", "P-042", "P-099", "P-100", "P-500", "P-999"]
)
def test_validator_accepted_ids_round_trip(tmp_path: Path, persona_id: str) -> None:
    """Every canonical `P-NNN` ID is accepted by validator AND migrator.

    Builds a minimal valid project, runs ``validate_project`` and
    ``migrate_personas``, asserts zero personas.md ERRORs and NO_OP.
    """

    from doit_cli.services.constitution_migrator import MigrationAction
    from doit_cli.services.memory_validator import (
        MemoryIssueSeverity,
        validate_project,
    )
    from doit_cli.services.personas_migrator import migrate_personas

    # Sanity: fixture corpus really does match the regex.
    assert _PERSONA_ID_RE.match(persona_id), f"test fixture invalid: {persona_id!r}"

    personas_path = _build_project_with_personas(
        tmp_path, _minimal_valid_personas(persona_id)
    )

    report = validate_project(tmp_path)
    persona_errors = [
        i
        for i in report.issues
        if i.file.endswith("personas.md")
        and i.severity is MemoryIssueSeverity.ERROR
    ]
    assert persona_errors == [], (
        f"Validator unexpectedly errored for {persona_id!r}: {persona_errors}"
    )

    result = migrate_personas(personas_path)
    assert result.action is MigrationAction.NO_OP
    assert result.added_fields == ()


# ---------------------------------------------------------------------------
# Negative corpus — validator rejects these.


@pytest.mark.parametrize(
    "bad_id",
    [
        "P-1",        # missing leading zeros
        "P-01",       # only two digits
        "P-1000",     # four digits
        "p-001",      # lowercase
        "Persona-001",  # wrong prefix
        "X-001",      # wrong prefix
        "P001",       # missing dash
        "P 001",      # space instead of dash
    ],
)
def test_validator_rejected_ids_error(tmp_path: Path, bad_id: str) -> None:
    """Validator rejects every non-canonical ID with an ERROR."""

    from doit_cli.services.memory_validator import (
        MemoryIssueSeverity,
        validate_project,
    )

    # Sanity: fixture corpus really fails the regex.
    assert not _PERSONA_ID_RE.match(bad_id), (
        f"test fixture accidentally valid: {bad_id!r}"
    )

    personas_body = (
        "# Personas\n\n"
        "## Persona Summary\n\n"
        "| ID | Name |\n|----|------|\n"
        f"| {bad_id} | Alex |\n\n"
        "## Detailed Profiles\n\n"
        f"### Persona: {bad_id}\n\n"
        "Alex the engineer.\n"
    )
    _build_project_with_personas(tmp_path, personas_body)

    report = validate_project(tmp_path)
    persona_errors = [
        i
        for i in report.issues
        if i.file.endswith("personas.md")
        and i.severity is MemoryIssueSeverity.ERROR
        and bad_id in i.message
    ]
    assert len(persona_errors) >= 1, (
        f"Validator did not flag malformed ID {bad_id!r}. "
        f"All issues: {report.issues}"
    )


# ---------------------------------------------------------------------------
# Opt-in semantic: absent personas.md produces zero issues.


def test_personas_absent_emits_no_issues(tmp_path: Path) -> None:
    """FR-014: missing personas.md is a valid state, zero issues."""

    from doit_cli.services.memory_validator import validate_project

    _build_project_with_personas(tmp_path, personas_body=None)

    report = validate_project(tmp_path)
    persona_issues = [i for i in report.issues if i.file.endswith("personas.md")]
    assert persona_issues == [], f"Unexpected personas.md issues: {persona_issues}"


# ---------------------------------------------------------------------------
# Umbrella CLI output order: constitution → roadmap → tech-stack → personas.


def test_umbrella_migrator_output_order(tmp_path: Path) -> None:
    """FR-012: `doit memory migrate` emits four rows in canonical order."""

    import json as jsonlib

    from typer.testing import CliRunner

    from doit_cli.main import app as doit_app

    _build_project_with_personas(tmp_path, _minimal_valid_personas("P-001"))

    runner = CliRunner()
    result = runner.invoke(
        doit_app, ["memory", "migrate", str(tmp_path), "--json"]
    )
    assert result.exit_code == 0, result.stdout

    payload = jsonlib.loads(result.stdout)
    files = [row["file"] for row in payload]
    assert files == [
        "constitution.md",
        "roadmap.md",
        "tech-stack.md",
        "personas.md",
    ], f"Unexpected output order: {files}"


def test_umbrella_includes_personas_row_when_absent(tmp_path: Path) -> None:
    """FR-012: personas.md row present even when the file is absent."""

    import json as jsonlib

    from typer.testing import CliRunner

    from doit_cli.main import app as doit_app

    _build_project_with_personas(tmp_path, personas_body=None)

    runner = CliRunner()
    result = runner.invoke(
        doit_app, ["memory", "migrate", str(tmp_path), "--json"]
    )
    assert result.exit_code == 0, result.stdout

    payload = jsonlib.loads(result.stdout)
    personas_rows = [row for row in payload if row["file"] == "personas.md"]
    assert len(personas_rows) == 1
    assert personas_rows[0]["action"] == "no_op"
    assert personas_rows[0]["added_fields"] == []


# ---------------------------------------------------------------------------
# Spec 062 SC-11: shape-valid-but-content-empty → WARNING (not ERROR).


def test_validator_warns_on_empty_detailed_profiles_section(tmp_path: Path) -> None:
    """Shape-correct personas.md with zero ``### Persona: P-NNN`` entries.

    SC-11 from ``specs/062-personas-migration/quickstart.md``: the file
    has both required H2s but no persona entries under
    ``## Detailed Profiles``. Validator emits a WARNING (not an ERROR) —
    shape is valid, content is empty.
    """

    from doit_cli.services.memory_validator import (
        MemoryIssueSeverity,
        validate_project,
    )

    personas_body = (
        "# Personas\n\n"
        "## Persona Summary\n\n"
        "| ID | Name |\n|----|------|\n"
        "\n"
        "## Detailed Profiles\n\n"
        "<!-- No personas defined yet -->\n"
    )
    _build_project_with_personas(tmp_path, personas_body)

    report = validate_project(tmp_path)

    # Zero ERROR-severity issues for personas.md (shape is valid).
    errors = [
        i
        for i in report.issues
        if i.file.endswith("personas.md")
        and i.severity is MemoryIssueSeverity.ERROR
    ]
    assert errors == [], f"Unexpected ERROR for shape-valid empty file: {errors}"

    # Exactly one WARNING citing "no" persona entries.
    warnings = [
        i
        for i in report.issues
        if i.file.endswith("personas.md")
        and i.severity is MemoryIssueSeverity.WARNING
        and "no `### Persona: P-NNN` entries" in i.message
    ]
    assert len(warnings) == 1, (
        "Expected exactly one WARNING for empty Detailed Profiles; "
        f"got: {warnings}"
    )
