"""Contract tests for the roadmap + tech-stack migrators.

Behavioural tests that ensure the migrators' `REQUIRED_*` constants stay
in sync with what `memory_validator` actually enforces. If the validator
adds a required section and this test keeps passing, the migrators will
silently leave users in a broken state — the job of these tests is to
fail loudly when that drift happens.
"""

from __future__ import annotations

from pathlib import Path

from doit_cli.models.memory_contract import MemoryIssueSeverity
from doit_cli.services.constitution_migrator import MigrationAction
from doit_cli.services.roadmap_migrator import (
    REQUIRED_ROADMAP_H2,
    REQUIRED_ROADMAP_H3_UNDER_ACTIVE_REQS,
    migrate_roadmap,
)
from doit_cli.services.tech_stack_migrator import (
    REQUIRED_TECHSTACK_H2,
    REQUIRED_TECHSTACK_H3_UNDER_TECH_STACK,
    migrate_tech_stack,
)

# ---------------------------------------------------------------------------
# Constant shape


def test_roadmap_required_h2_matches_validator() -> None:
    """`REQUIRED_ROADMAP_H2` covers the H2 `_validate_roadmap` looks for."""

    assert REQUIRED_ROADMAP_H2 == ("Active Requirements",)


def test_roadmap_required_h3_covers_priority_range() -> None:
    """All four priorities are enforced so stubs render predictably."""

    assert REQUIRED_ROADMAP_H3_UNDER_ACTIVE_REQS == ("P1", "P2", "P3", "P4")


def test_tech_stack_required_h2_matches_validator() -> None:
    assert REQUIRED_TECHSTACK_H2 == ("Tech Stack",)


def test_tech_stack_required_h3_covers_canonical_groups() -> None:
    assert REQUIRED_TECHSTACK_H3_UNDER_TECH_STACK == (
        "Languages",
        "Frameworks",
        "Libraries",
    )


# ---------------------------------------------------------------------------
# Shared result types (no duplicate class definitions)


def test_roadmap_migrator_reuses_constitution_migration_types() -> None:
    """Both migrators return the same MigrationResult type used by spec 059.

    This matters because the init hook handles all three migrators through
    a single `isinstance(result.action, MigrationAction)` branch.
    """

    from doit_cli.services.constitution_migrator import (
        MigrationAction as CM_Action,
    )
    from doit_cli.services.constitution_migrator import (
        MigrationResult as CM_Result,
    )

    # Build a throwaway result to confirm the class is shared.
    result = migrate_roadmap(Path("/nonexistent-file.md"))
    assert isinstance(result, CM_Result)
    assert isinstance(result.action, CM_Action)


def test_tech_stack_migrator_reuses_constitution_migration_types() -> None:
    from doit_cli.services.constitution_migrator import (
        MigrationAction as CM_Action,
    )
    from doit_cli.services.constitution_migrator import (
        MigrationResult as CM_Result,
    )

    result = migrate_tech_stack(Path("/nonexistent-file.md"))
    assert isinstance(result, CM_Result)
    assert isinstance(result.action, CM_Action)


# ---------------------------------------------------------------------------
# Behavioural bijection: migrated output passes the validator


def _write_memory(tmp_path: Path, *, constitution_frontmatter: bool = True) -> Path:
    memory = tmp_path / ".doit" / "memory"
    memory.mkdir(parents=True)

    if constitution_frontmatter:
        (memory / "constitution.md").write_text(
            "---\n"
            "id: app-test\n"
            "name: Test\n"
            "kind: application\n"
            "phase: 1\n"
            "icon: TS\n"
            "tagline: Test.\n"
            "dependencies: []\n"
            "---\n"
            "# Test Constitution\n\n"
            "## Purpose & Goals\n\n"
            "### Project Purpose\n\nTest.\n",
            encoding="utf-8",
        )
    return memory


def test_migrated_roadmap_passes_validator(tmp_path: Path) -> None:
    """After migrate_roadmap runs on an empty roadmap, the validator
    no longer emits an ERROR for the `## Active Requirements` section."""

    memory = _write_memory(tmp_path)
    # Minimal tech-stack so the validator doesn't emit *other* errors
    (memory / "tech-stack.md").write_text(
        "# Tech\n\n## Tech Stack\n\n### Languages\n\nPython\n",
        encoding="utf-8",
    )
    roadmap = memory / "roadmap.md"
    roadmap.write_text("# Project Roadmap\n\n## Vision\n\nShip it.\n", encoding="utf-8")

    result = migrate_roadmap(roadmap)
    assert result.action is MigrationAction.PREPENDED

    from doit_cli.services.memory_validator import validate_project

    report = validate_project(tmp_path)
    roadmap_errors = [
        i
        for i in report.issues
        if i.severity is MemoryIssueSeverity.ERROR and i.file.endswith("roadmap.md")
    ]
    assert roadmap_errors == [], (
        f"Expected validator to stop erroring on roadmap after migration; got {roadmap_errors}"
    )


def test_migrated_tech_stack_passes_validator(tmp_path: Path) -> None:
    memory = _write_memory(tmp_path)
    # Minimal roadmap so the validator doesn't emit *other* errors
    (memory / "roadmap.md").write_text(
        "# Roadmap\n\n## Active Requirements\n\n### P1\n\n- ship it\n",
        encoding="utf-8",
    )
    tech_stack = memory / "tech-stack.md"
    tech_stack.write_text("# Technology\n\nLegacy prose.\n", encoding="utf-8")

    result = migrate_tech_stack(tech_stack)
    assert result.action is MigrationAction.PREPENDED

    from doit_cli.services.memory_validator import validate_project

    report = validate_project(tmp_path)
    ts_errors = [
        i
        for i in report.issues
        if i.severity is MemoryIssueSeverity.ERROR and i.file.endswith("tech-stack.md")
    ]
    assert ts_errors == [], (
        f"Expected validator to stop erroring on tech-stack after migration; got {ts_errors}"
    )
