"""Contract: roadmap validator ↔ migrator H3-matching bijection.

For every H3 title the memory validator accepts as a valid priority
subsection (``^p[1-4]\\b`` case-insensitive), the roadmap migrator must
treat that title as already present — i.e. must NOT add the priority
to ``MigrationResult.added_fields``.

Conversely, every H3 title the validator rejects must be treated as
absent by the migrator, so the canonical stub IS added.

This test locks the bidirectional invariant that spec 060's contract
tests missed. See spec 061 ``contracts/migrators.md`` §4.
"""

from __future__ import annotations

import re
import shutil
from pathlib import Path

import pytest

from doit_cli.services.constitution_migrator import MigrationAction
from doit_cli.services.memory_validator import (
    MemoryIssueSeverity,
    validate_project,
)
from doit_cli.services.roadmap_migrator import migrate_roadmap

# Authoritative regex from ``memory_validator._validate_roadmap``.
_PRIORITY_REGEX = re.compile(r"^p[1-4]\b", re.IGNORECASE)


# Minimal valid constitution and tech-stack so ``validate_project`` can
# run without tripping on unrelated files. The roadmap is the only file
# under test.
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


def _build_project(tmp_path: Path, roadmap_body: str) -> Path:
    """Create a minimal `.doit/memory/` tree under ``tmp_path`` and return it."""

    memory = tmp_path / ".doit" / "memory"
    memory.mkdir(parents=True)
    (memory / "constitution.md").write_text(_CONSTITUTION_MINIMAL, encoding="utf-8")
    (memory / "tech-stack.md").write_text(_TECH_STACK_MINIMAL, encoding="utf-8")
    (memory / "roadmap.md").write_text(roadmap_body, encoding="utf-8")
    return memory / "roadmap.md"


# Decoration forms the validator regex MUST accept. Each entry is a
# Python format string; the literal ``{p}`` is substituted per priority.
ACCEPTED_DECORATIONS = [
    "{p}",                          # bare
    "{p} - Critical",               # dash-decorated
    "{p}: Urgent",                  # colon-decorated
    "{p}. Must-Have",               # dot-decorated
    "{p} (MVP)",                    # paren-decorated
    "{p}   ",                       # trailing whitespace
    "{p} — Em-dashed",              # em-dash
]

# Decoration forms the validator regex MUST reject.
REJECTED_HEADINGS = [
    "Priority 1",
    "Critical",
    "p5",
    "1. P1",
    "P1A",          # no word boundary after the priority token
]


@pytest.mark.parametrize("priority", ["P1", "P2", "P3", "P4"])
@pytest.mark.parametrize("decoration", ACCEPTED_DECORATIONS)
def test_validator_accepted_forms_are_present_for_migrator(
    tmp_path: Path,
    priority: str,
    decoration: str,
) -> None:
    """Every priority H3 shape the validator accepts is present for the migrator.

    Builds a minimal roadmap with a single decorated priority H3 under
    ``## Active Requirements``. Asserts:

    1. The validator's regex accepts the heading (sanity check — this is
       the input to the bijection).
    2. ``validate_project`` emits no "no `### P1` / `### P2` / …" warning
       for roadmap.md (the heading IS recognized).
    3. The migrator returns NO_OP or PATCHED; either way, the decorated
       priority is NOT in ``added_fields``.
    """

    heading = decoration.format(p=priority)

    # (1) Validator regex sanity check — this is the contract input.
    assert _PRIORITY_REGEX.match(heading.strip()), (
        f"Validator regex does not accept {heading!r}; fixture is invalid."
    )

    # Build the minimal roadmap: only this decorated priority under H2.
    roadmap_body = (
        "# Roadmap\n\n"
        "## Active Requirements\n\n"
        f"### {heading}\n\n"
        "- Some content\n"
    )
    roadmap_path = _build_project(tmp_path, roadmap_body)

    # (2) Validator must not flag the priority-subsection warning.
    report = validate_project(tmp_path)
    priority_warnings = [
        i
        for i in report.issues
        if i.file.endswith("roadmap.md")
        and "no `### P1`" in i.message
    ]
    assert priority_warnings == [], (
        f"Validator emitted priority-missing warning for {heading!r}: "
        f"{priority_warnings}"
    )

    # (3) Migrator treats the decorated heading as present.
    result = migrate_roadmap(roadmap_path)
    assert result.action in {MigrationAction.NO_OP, MigrationAction.PATCHED}
    assert priority not in result.added_fields, (
        f"Migrator incorrectly marked {priority} as missing given existing "
        f"H3 '### {heading}'. added_fields={result.added_fields}"
    )


@pytest.mark.parametrize("heading", REJECTED_HEADINGS)
def test_validator_rejected_forms_are_absent_for_migrator(
    tmp_path: Path,
    heading: str,
) -> None:
    """Every H3 the validator rejects is treated as absent by the migrator.

    Builds a roadmap containing only a rejected H3 under ``## Active
    Requirements``. Asserts:

    1. The validator's regex rejects the heading.
    2. The migrator adds the canonical P1..P4 stubs because none of the
       existing H3s satisfy any priority matcher.
    """

    # (1) Validator regex rejects the heading.
    assert not _PRIORITY_REGEX.match(heading.strip()), (
        f"Validator regex unexpectedly accepts {heading!r}; fixture is invalid."
    )

    roadmap_body = (
        "# Roadmap\n\n"
        "## Active Requirements\n\n"
        f"### {heading}\n\n"
        "- Some content\n"
    )
    roadmap_path = _build_project(tmp_path, roadmap_body)

    # (2) Migrator adds all four canonical priority stubs.
    result = migrate_roadmap(roadmap_path)
    assert result.action is MigrationAction.PATCHED
    assert set(result.added_fields) == {"P1", "P2", "P3", "P4"}


def test_validator_warning_coverage_marker(tmp_path: Path) -> None:
    """Guard: ``memory_validator`` still emits the priority-missing warning.

    If the validator's message text changes, the substring match in
    :func:`test_validator_accepted_forms_are_present_for_migrator` goes
    stale — silently. This guard surfaces that drift: a roadmap with NO
    priority subsections MUST trigger the warning containing ``no `###
    P1```.
    """

    roadmap_body = (
        "# Roadmap\n\n"
        "## Active Requirements\n\n"
        "<!-- empty on purpose -->\n"
    )

    _build_project(tmp_path, roadmap_body)
    report = validate_project(tmp_path)

    warnings = [
        i
        for i in report.issues
        if i.file.endswith("roadmap.md")
        and i.severity is MemoryIssueSeverity.WARNING
        and "no `### P1`" in i.message
    ]
    assert len(warnings) == 1, (
        "memory_validator no longer emits the expected priority-missing "
        "warning — update the substring check in the alignment test."
    )


# ---------------------------------------------------------------------------
# Dogfood regression guard — the exact case that drove spec 061.
#
# Before the fix, ``doit memory migrate .`` on this repo spuriously PATCHED
# duplicate empty stubs into ``.doit/memory/roadmap.md`` because its
# priority headings are decorated (``### P1 - Critical (Must Have for MVP)``
# etc.). This test runs the migrator on a SAFE COPY of the committed
# roadmap — never the original — and asserts ``NO_OP`` with byte-for-byte
# equality.


def test_roadmap_migrator_is_noop_on_doit_own_repo(tmp_path: Path) -> None:
    """The doit repo's own decorated roadmap must be NO_OP under its migrator.

    Automates SC-9 from ``specs/061-fix-roadmap-h3-matching/quickstart.md``.
    If someone later reverts the prefix-matcher fix or decorates a priority
    heading in a way the matcher rejects, this test fails fast.
    """

    # tests/contract/test_file.py → tests/contract/ → tests/ → repo root
    repo_root = Path(__file__).resolve().parent.parent.parent
    roadmap_source = repo_root / ".doit" / "memory" / "roadmap.md"

    if not roadmap_source.exists():
        pytest.skip(
            f"{roadmap_source} not found — test is doit-repo-specific and "
            "only runs when the repo's own memory files are present."
        )

    # Copy to tmp_path so the test NEVER modifies the real committed file
    # even if it regresses. The migrator writes atomically, so a regression
    # against the original would dirty the working tree.
    tmp_roadmap = tmp_path / "roadmap.md"
    shutil.copy2(roadmap_source, tmp_roadmap)
    pre_bytes = tmp_roadmap.read_bytes()

    result = migrate_roadmap(tmp_roadmap)

    assert result.action is MigrationAction.NO_OP, (
        f"Dogfood regression: doit's own roadmap.md is no longer NO_OP. "
        f"action={result.action}, added_fields={result.added_fields}"
    )
    assert result.added_fields == ()
    assert tmp_roadmap.read_bytes() == pre_bytes, (
        "roadmap.md bytes changed despite NO_OP — atomic-write regression."
    )
