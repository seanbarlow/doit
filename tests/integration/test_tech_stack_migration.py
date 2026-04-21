"""Integration tests for the tech-stack.md shape migrator and enricher.

US1 tests cover migrate_tech_stack end-to-end. US2 tests (appended later)
cover enrich_tech_stack — see the US2 section.
"""

from __future__ import annotations

import hashlib
from pathlib import Path

import pytest

from doit_cli.services.constitution_migrator import MigrationAction
from doit_cli.services.tech_stack_migrator import (
    REQUIRED_TECHSTACK_H3_UNDER_TECH_STACK,
    migrate_tech_stack,
)

LEGACY_NO_TECH_STACK = """# Project Technology

Some prose about our stack that predates the contract.

## History

Written back when everything was ad-hoc.
"""


TECH_STACK_WITHOUT_SUBHEADINGS = """# Tech

## Tech Stack

The section exists but has no subheadings yet.
"""


TECH_STACK_WITH_PARTIAL = """# Tech

## Tech Stack

### Languages

- Python 3.11+
"""


COMPLETE_TECH_STACK = """# Tech

## Tech Stack

### Languages

- Python 3.11+

### Frameworks

- Typer

### Libraries

- Rich
"""


@pytest.fixture
def tmp_tech_stack(tmp_path: Path) -> Path:
    memory = tmp_path / ".doit" / "memory"
    memory.mkdir(parents=True)
    return memory / "tech-stack.md"


def _sha(text: str) -> bytes:
    return hashlib.sha256(text.encode("utf-8")).digest()


# ---------------------------------------------------------------------------
# US1 — shape migration


def test_missing_tech_stack_section_is_prepended(tmp_tech_stack: Path) -> None:
    tmp_tech_stack.write_text(LEGACY_NO_TECH_STACK, encoding="utf-8")
    result = migrate_tech_stack(tmp_tech_stack)

    assert result.action is MigrationAction.PREPENDED
    assert "Tech Stack" in result.added_fields
    for group in REQUIRED_TECHSTACK_H3_UNDER_TECH_STACK:
        assert group in result.added_fields

    post = tmp_tech_stack.read_text(encoding="utf-8")
    assert "## Tech Stack" in post
    for group in REQUIRED_TECHSTACK_H3_UNDER_TECH_STACK:
        assert f"### {group}" in post
    # Legacy content preserved
    assert "## History\n\nWritten back when everything was ad-hoc." in post


def test_tech_stack_without_subheadings_is_patched(
    tmp_tech_stack: Path,
) -> None:
    tmp_tech_stack.write_text(TECH_STACK_WITHOUT_SUBHEADINGS, encoding="utf-8")
    result = migrate_tech_stack(tmp_tech_stack)

    assert result.action is MigrationAction.PATCHED
    assert set(result.added_fields) == set(REQUIRED_TECHSTACK_H3_UNDER_TECH_STACK)
    assert "Tech Stack" not in result.added_fields

    post = tmp_tech_stack.read_text(encoding="utf-8")
    assert post.count("## Tech Stack") == 1
    for group in REQUIRED_TECHSTACK_H3_UNDER_TECH_STACK:
        assert f"### {group}" in post
    assert "The section exists but has no subheadings yet." in post


def test_partial_tech_stack_only_adds_missing(tmp_tech_stack: Path) -> None:
    tmp_tech_stack.write_text(TECH_STACK_WITH_PARTIAL, encoding="utf-8")
    result = migrate_tech_stack(tmp_tech_stack)

    assert result.action is MigrationAction.PATCHED
    assert set(result.added_fields) == {"Frameworks", "Libraries"}

    post = tmp_tech_stack.read_text(encoding="utf-8")
    # Languages preserved verbatim
    assert "### Languages\n\n- Python 3.11+" in post
    for group in REQUIRED_TECHSTACK_H3_UNDER_TECH_STACK:
        assert post.count(f"### {group}") == 1


def test_complete_tech_stack_is_noop(tmp_tech_stack: Path) -> None:
    tmp_tech_stack.write_text(COMPLETE_TECH_STACK, encoding="utf-8")
    pre_bytes = tmp_tech_stack.read_bytes()

    result = migrate_tech_stack(tmp_tech_stack)
    assert result.action is MigrationAction.NO_OP
    assert tmp_tech_stack.read_bytes() == pre_bytes


def test_missing_file_is_noop(tmp_path: Path) -> None:
    missing = tmp_path / ".doit" / "memory" / "tech-stack.md"
    result = migrate_tech_stack(missing)
    assert result.action is MigrationAction.NO_OP
    assert not missing.exists()


def test_migration_is_idempotent(tmp_tech_stack: Path) -> None:
    tmp_tech_stack.write_text(LEGACY_NO_TECH_STACK, encoding="utf-8")

    first = migrate_tech_stack(tmp_tech_stack)
    assert first.action is MigrationAction.PREPENDED
    after_first = tmp_tech_stack.read_bytes()

    second = migrate_tech_stack(tmp_tech_stack)
    assert second.action is MigrationAction.NO_OP
    assert tmp_tech_stack.read_bytes() == after_first


def test_migrated_file_has_placeholder_stubs(tmp_tech_stack: Path) -> None:
    tmp_tech_stack.write_text(LEGACY_NO_TECH_STACK, encoding="utf-8")
    migrate_tech_stack(tmp_tech_stack)

    post = tmp_tech_stack.read_text(encoding="utf-8")
    # Three subsections, one placeholder-token reference each.
    assert post.count("[PROJECT_NAME]") == 3


def test_body_outside_target_section_preserved(tmp_tech_stack: Path) -> None:
    source = (
        "# Tech\n\n"
        "## Background\n\nLegacy project notes.\n\n"
        "## References\n\n- external docs\n"
    )
    tmp_tech_stack.write_text(source, encoding="utf-8")
    migrate_tech_stack(tmp_tech_stack)

    post = tmp_tech_stack.read_text(encoding="utf-8")
    assert "## Background\n\nLegacy project notes.\n" in post
    assert "## References\n\n- external docs" in post


# ---------------------------------------------------------------------------
# US2 — tech-stack enrichment from the constitution


CONSTITUTION_WITH_TECH_STACK = """---
id: app-acme
name: Acme
kind: application
phase: 2
icon: AC
tagline: Ship widgets.
dependencies: []
---

# Acme Constitution

## Purpose & Goals

### Project Purpose

Ship widgets.

## Tech Stack

### Languages

- Python 3.11+
- TypeScript

### Frameworks

- Typer
- FastAPI

### Libraries

- Rich
- httpx

## Infrastructure

- AWS us-east-1
- Fargate

## Deployment

- GitHub Actions
- Manual promotion
"""


STUBBED_TECH_STACK = """# Tech Stack

## Tech Stack

### Languages

<!-- Add [PROJECT_NAME]'s Languages here.
     Populate from [PROJECT_PURPOSE] and [SUCCESS_CRITERIA] context. -->

### Frameworks

<!-- Add [PROJECT_NAME]'s Frameworks here.
     Populate from [PROJECT_PURPOSE] and [SUCCESS_CRITERIA] context. -->

### Libraries

<!-- Add [PROJECT_NAME]'s Libraries here.
     Populate from [PROJECT_PURPOSE] and [SUCCESS_CRITERIA] context. -->
"""


@pytest.fixture
def tmp_project(tmp_path: Path) -> Path:
    memory = tmp_path / ".doit" / "memory"
    memory.mkdir(parents=True)
    return tmp_path


def test_enrich_tech_stack_from_populated_constitution(tmp_project: Path) -> None:
    from doit_cli.services.constitution_enricher import EnrichmentAction
    from doit_cli.services.tech_stack_enricher import enrich_tech_stack

    memory = tmp_project / ".doit" / "memory"
    (memory / "constitution.md").write_text(CONSTITUTION_WITH_TECH_STACK, encoding="utf-8")
    ts = memory / "tech-stack.md"
    ts.write_text(STUBBED_TECH_STACK, encoding="utf-8")

    result = enrich_tech_stack(ts, project_root=tmp_project)

    assert result.action is EnrichmentAction.ENRICHED, (
        f"expected ENRICHED, got {result.action} with unresolved={result.unresolved_fields}"
    )
    post = ts.read_text(encoding="utf-8")
    # Verbatim bullets from constitution are now present
    assert "- Python 3.11+" in post
    assert "- Typer" in post
    assert "- Rich" in post
    # Placeholders gone
    assert "[PROJECT_NAME]" not in post


def test_enrich_tech_stack_infrastructure_and_deployment_auto_subsections(
    tmp_project: Path,
) -> None:
    from doit_cli.services.tech_stack_enricher import enrich_tech_stack

    memory = tmp_project / ".doit" / "memory"
    (memory / "constitution.md").write_text(CONSTITUTION_WITH_TECH_STACK, encoding="utf-8")
    ts = memory / "tech-stack.md"
    ts.write_text(STUBBED_TECH_STACK, encoding="utf-8")

    enrich_tech_stack(ts, project_root=tmp_project)

    post = ts.read_text(encoding="utf-8")
    # New subsections were auto-inserted for Infrastructure/Deployment
    assert "### Infrastructure" in post
    assert "- AWS us-east-1" in post
    assert "### Deployment" in post
    assert "- GitHub Actions" in post


def test_enrich_tech_stack_preserves_existing_non_placeholder_content(
    tmp_project: Path,
) -> None:
    from doit_cli.services.tech_stack_enricher import enrich_tech_stack

    memory = tmp_project / ".doit" / "memory"
    (memory / "constitution.md").write_text(CONSTITUTION_WITH_TECH_STACK, encoding="utf-8")
    ts = memory / "tech-stack.md"
    ts.write_text(
        "# Tech Stack\n\n"
        "## Tech Stack\n\n"
        "### Languages\n\n- Go  # hand-authored\n\n"
        "### Frameworks\n\n"
        "<!-- Add [PROJECT_NAME]'s Frameworks here. -->\n\n"
        "### Libraries\n\n"
        "<!-- Add [PROJECT_NAME]'s Libraries here. -->\n",
        encoding="utf-8",
    )

    enrich_tech_stack(ts, project_root=tmp_project)

    post = ts.read_text(encoding="utf-8")
    # Hand-authored Languages preserved verbatim
    assert "- Go  # hand-authored" in post
    # Python etc. NOT substituted for Go
    assert post.count("- Python 3.11+") == 0
    # Frameworks and Libraries were enriched
    assert "- Typer" in post
    assert "- Rich" in post


def test_enrich_tech_stack_no_source_returns_partial(tmp_project: Path) -> None:
    from doit_cli.services.constitution_enricher import EnrichmentAction
    from doit_cli.services.tech_stack_enricher import enrich_tech_stack

    memory = tmp_project / ".doit" / "memory"
    # Constitution without any Tech Stack / Infrastructure / Deployment content
    (memory / "constitution.md").write_text(
        "---\nid: app-acme\nname: Acme\nkind: application\nphase: 1\n"
        "icon: AC\ntagline: Ship.\ndependencies: []\n---\n"
        "# Acme Constitution\n\n## Purpose & Goals\n\n### Project Purpose\n\nShip.\n",
        encoding="utf-8",
    )
    ts = memory / "tech-stack.md"
    ts.write_text(STUBBED_TECH_STACK, encoding="utf-8")
    pre_bytes = ts.read_bytes()

    result = enrich_tech_stack(ts, project_root=tmp_project)

    assert result.action is EnrichmentAction.PARTIAL
    assert set(result.unresolved_fields) == {"Languages", "Frameworks", "Libraries"}
    # No write performed (all unresolved)
    assert ts.read_bytes() == pre_bytes


def test_enrich_tech_stack_noop_when_no_placeholders(tmp_project: Path) -> None:
    from doit_cli.services.constitution_enricher import EnrichmentAction
    from doit_cli.services.tech_stack_enricher import enrich_tech_stack

    memory = tmp_project / ".doit" / "memory"
    (memory / "constitution.md").write_text(CONSTITUTION_WITH_TECH_STACK, encoding="utf-8")
    ts = memory / "tech-stack.md"
    ts.write_text(COMPLETE_TECH_STACK, encoding="utf-8")
    pre_bytes = ts.read_bytes()

    result = enrich_tech_stack(ts, project_root=tmp_project)
    assert result.action is EnrichmentAction.NO_OP
    assert ts.read_bytes() == pre_bytes


def test_cli_memory_enrich_tech_stack_success(tmp_project: Path) -> None:
    from typer.testing import CliRunner

    from doit_cli.main import app as doit_app

    memory = tmp_project / ".doit" / "memory"
    (memory / "constitution.md").write_text(CONSTITUTION_WITH_TECH_STACK, encoding="utf-8")
    (memory / "tech-stack.md").write_text(STUBBED_TECH_STACK, encoding="utf-8")

    runner = CliRunner()
    result = runner.invoke(
        doit_app,
        ["memory", "enrich", "tech-stack", str(tmp_project), "--json"],
    )
    assert result.exit_code == 0, result.stdout

    import json as jsonlib

    payload = jsonlib.loads(result.stdout)
    assert payload["action"] == "enriched"
    assert set(payload["enriched_fields"]) >= {"Languages", "Frameworks", "Libraries"}


def test_cli_memory_enrich_tech_stack_partial_exits_1(tmp_project: Path) -> None:
    from typer.testing import CliRunner

    from doit_cli.main import app as doit_app

    memory = tmp_project / ".doit" / "memory"
    (memory / "constitution.md").write_text(
        "---\nid: app-acme\nname: Acme\nkind: application\nphase: 1\n"
        "icon: AC\ntagline: Ship.\ndependencies: []\n---\n"
        "# Acme Constitution\n\n## Purpose & Goals\n\n### Project Purpose\n\nShip.\n",
        encoding="utf-8",
    )
    (memory / "tech-stack.md").write_text(STUBBED_TECH_STACK, encoding="utf-8")

    runner = CliRunner()
    result = runner.invoke(
        doit_app,
        ["memory", "enrich", "tech-stack", str(tmp_project), "--json"],
    )
    assert result.exit_code == 1, result.stdout
