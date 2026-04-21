"""Integration tests for the roadmap.md shape migrator and enricher.

US1 tests cover migrate_roadmap end-to-end against real filesystems.
US3 tests (appended later) cover enrich_roadmap — see the US3 section.
"""

from __future__ import annotations

import hashlib
from pathlib import Path

import pytest

from doit_cli.services.constitution_migrator import MigrationAction
from doit_cli.services.roadmap_migrator import (
    REQUIRED_ROADMAP_H3_UNDER_ACTIVE_REQS,
    migrate_roadmap,
)

LEGACY_ROADMAP_NO_ACTIVE_REQS = """# Acme Widgets Roadmap

## Vision

Ship widgets that customers love.

## Notes

Some legacy notes the user has been keeping.
"""


ROADMAP_WITH_ACTIVE_REQS_BUT_NO_P = """# Roadmap

## Active Requirements

<!-- content TBD -->
"""


ROADMAP_WITH_PARTIAL_PRIORITIES = """# Roadmap

## Active Requirements

### P1

- Ship widgets

### P3

- Refactor backend
"""


COMPLETE_ROADMAP = """# Roadmap

## Active Requirements

### P1

- Widget MVP

### P2

- Ordering flow

### P3

- Analytics dashboard

### P4

- Future experiments
"""


@pytest.fixture
def tmp_roadmap(tmp_path: Path) -> Path:
    memory = tmp_path / ".doit" / "memory"
    memory.mkdir(parents=True)
    return memory / "roadmap.md"


def _sha(text: str) -> bytes:
    return hashlib.sha256(text.encode("utf-8")).digest()


# ---------------------------------------------------------------------------
# US1 — shape migration


def test_missing_active_requirements_is_prepended(tmp_roadmap: Path) -> None:
    tmp_roadmap.write_text(LEGACY_ROADMAP_NO_ACTIVE_REQS, encoding="utf-8")
    result = migrate_roadmap(tmp_roadmap)

    assert result.action is MigrationAction.PREPENDED
    assert "Active Requirements" in result.added_fields
    for p in REQUIRED_ROADMAP_H3_UNDER_ACTIVE_REQS:
        assert p in result.added_fields

    post = tmp_roadmap.read_text(encoding="utf-8")
    assert "## Active Requirements" in post
    for p in REQUIRED_ROADMAP_H3_UNDER_ACTIVE_REQS:
        assert f"### {p}" in post
    # Preserve pre-existing content byte-for-byte
    assert "## Vision\n\nShip widgets that customers love." in post
    assert "## Notes\n\nSome legacy notes" in post


def test_active_requirements_without_priorities_patched(tmp_roadmap: Path) -> None:
    tmp_roadmap.write_text(ROADMAP_WITH_ACTIVE_REQS_BUT_NO_P, encoding="utf-8")
    result = migrate_roadmap(tmp_roadmap)

    assert result.action is MigrationAction.PATCHED
    assert set(result.added_fields) == set(REQUIRED_ROADMAP_H3_UNDER_ACTIVE_REQS)
    # H2 wasn't added — its absence from added_fields is the signal
    assert "Active Requirements" not in result.added_fields

    post = tmp_roadmap.read_text(encoding="utf-8")
    assert post.count("## Active Requirements") == 1
    for p in REQUIRED_ROADMAP_H3_UNDER_ACTIVE_REQS:
        assert f"### {p}" in post
    # Original user content under Active Requirements still present
    assert "<!-- content TBD -->" in post


def test_partial_priorities_only_adds_missing(tmp_roadmap: Path) -> None:
    tmp_roadmap.write_text(ROADMAP_WITH_PARTIAL_PRIORITIES, encoding="utf-8")
    result = migrate_roadmap(tmp_roadmap)

    assert result.action is MigrationAction.PATCHED
    assert set(result.added_fields) == {"P2", "P4"}

    post = tmp_roadmap.read_text(encoding="utf-8")
    # Pre-existing P1/P3 content preserved
    assert "### P1\n\n- Ship widgets" in post
    assert "### P3\n\n- Refactor backend" in post
    # New P2/P4 added
    assert "### P2" in post
    assert "### P4" in post
    # Exactly one of each
    for p in REQUIRED_ROADMAP_H3_UNDER_ACTIVE_REQS:
        assert post.count(f"### {p}") == 1


def test_complete_roadmap_is_noop(tmp_roadmap: Path) -> None:
    tmp_roadmap.write_text(COMPLETE_ROADMAP, encoding="utf-8")
    pre_bytes = tmp_roadmap.read_bytes()

    result = migrate_roadmap(tmp_roadmap)
    assert result.action is MigrationAction.NO_OP
    assert result.added_fields == ()
    assert tmp_roadmap.read_bytes() == pre_bytes


def test_missing_file_is_noop(tmp_path: Path) -> None:
    missing = tmp_path / ".doit" / "memory" / "roadmap.md"
    result = migrate_roadmap(missing)
    assert result.action is MigrationAction.NO_OP
    assert not missing.exists()


def test_migration_is_idempotent(tmp_roadmap: Path) -> None:
    tmp_roadmap.write_text(LEGACY_ROADMAP_NO_ACTIVE_REQS, encoding="utf-8")

    first = migrate_roadmap(tmp_roadmap)
    assert first.action is MigrationAction.PREPENDED
    after_first = tmp_roadmap.read_bytes()

    second = migrate_roadmap(tmp_roadmap)
    assert second.action is MigrationAction.NO_OP
    assert tmp_roadmap.read_bytes() == after_first


def test_body_outside_target_section_preserved(tmp_roadmap: Path) -> None:
    """Bytes outside the section the migrator modifies stay byte-identical."""

    source = (
        "# Acme Widgets Roadmap\n\n"
        "## Vision\n\nShip widgets.\n\n"
        "## Notes\n\nUse Python 3.11.\n"
    )
    tmp_roadmap.write_text(source, encoding="utf-8")
    result = migrate_roadmap(tmp_roadmap)

    assert result.action is MigrationAction.PREPENDED
    post = tmp_roadmap.read_text(encoding="utf-8")
    # The two unrelated sections should be byte-identical in the output
    assert "## Vision\n\nShip widgets.\n" in post
    assert "## Notes\n\nUse Python 3.11.\n" in post


def test_migrated_file_has_placeholder_stubs(tmp_roadmap: Path) -> None:
    """Stubs carry `[PROJECT_NAME]` so verify-memory warns on them."""

    tmp_roadmap.write_text(LEGACY_ROADMAP_NO_ACTIVE_REQS, encoding="utf-8")
    migrate_roadmap(tmp_roadmap)

    post = tmp_roadmap.read_text(encoding="utf-8")
    # Four priority subsections, one placeholder-token reference each.
    assert post.count("[PROJECT_NAME]") == 4


def test_missing_file_with_existing_directory_tree(tmp_path: Path) -> None:
    """When the path doesn't exist but the memory dir does, NO_OP."""

    memory = tmp_path / ".doit" / "memory"
    memory.mkdir(parents=True)
    missing = memory / "roadmap.md"

    result = migrate_roadmap(missing)
    assert result.action is MigrationAction.NO_OP
    assert not missing.exists()


def test_migrator_preserves_crlf_line_endings(tmp_roadmap: Path) -> None:
    """End-to-end CRLF preservation across read → mutate → atomic write.

    Users on Windows / in cross-platform repos depend on this — a silent
    CRLF → LF conversion shows up as a spurious diff on every run.
    """

    source = (
        b"# Acme Roadmap\r\n\r\n"
        b"## Vision\r\n\r\nShip widgets.\r\n"
    )
    tmp_roadmap.write_bytes(source)

    result = migrate_roadmap(tmp_roadmap)
    assert result.action is MigrationAction.PREPENDED

    post_bytes = tmp_roadmap.read_bytes()
    assert b"\r\n" in post_bytes, "CRLF line endings should survive round-trip"
    # No bare LFs (which would indicate mixed endings)
    bare_lf = post_bytes.count(b"\n") - post_bytes.count(b"\r\n")
    assert bare_lf == 0, f"Mixed line endings: {bare_lf} bare LFs"
    # Pre-existing content bytes preserved
    assert b"# Acme Roadmap\r\n" in post_bytes
    assert b"## Vision\r\n\r\nShip widgets.\r\n" in post_bytes


# ---------------------------------------------------------------------------
# US3 — roadmap Vision + completed-items enrichment


CONSTITUTION_WITH_PURPOSE = """---
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

Acme Widgets ships industrial widgets to enterprise customers with 99.9% on-time delivery.

### Success Criteria

- 99.9% on-time delivery
"""


COMPLETED_ROADMAP = """# Completed Roadmap Items

**Project**: Acme Widgets
**Created**: 2026-01-01

## Recently Completed

| Item | Original Priority | Completed Date | Feature Branch | Notes |
|------|-------------------|----------------|----------------|-------|
| User authentication | P1 | 2026-02-10 | 001-user-auth | |
| Widget catalog | P1 | 2026-02-20 | 002-catalog | |
| Order tracking | P2 | 2026-03-05 | 003-orders | |
"""


STUBBED_ROADMAP = """# Project Roadmap

## Vision

<!-- [PROJECT_NAME]'s vision will go here -->

## Active Requirements

### P1

<!-- Add [PROJECT_NAME]'s P1 items here.
     See [PROJECT_PURPOSE] and [SUCCESS_CRITERIA] for guidance. -->

### P2

<!-- Add [PROJECT_NAME]'s P2 items here.
     See [PROJECT_PURPOSE] and [SUCCESS_CRITERIA] for guidance. -->

### P3

<!-- Add [PROJECT_NAME]'s P3 items here.
     See [PROJECT_PURPOSE] and [SUCCESS_CRITERIA] for guidance. -->

### P4

<!-- Add [PROJECT_NAME]'s P4 items here.
     See [PROJECT_PURPOSE] and [SUCCESS_CRITERIA] for guidance. -->
"""


@pytest.fixture
def tmp_project(tmp_path: Path) -> Path:
    (tmp_path / ".doit" / "memory").mkdir(parents=True)
    return tmp_path


def test_enrich_roadmap_replaces_vision_from_project_purpose(
    tmp_project: Path,
) -> None:
    from doit_cli.services.constitution_enricher import EnrichmentAction
    from doit_cli.services.roadmap_enricher import enrich_roadmap

    memory = tmp_project / ".doit" / "memory"
    (memory / "constitution.md").write_text(CONSTITUTION_WITH_PURPOSE, encoding="utf-8")
    roadmap = memory / "roadmap.md"
    roadmap.write_text(STUBBED_ROADMAP, encoding="utf-8")

    result = enrich_roadmap(roadmap, project_root=tmp_project)

    assert result.action in {EnrichmentAction.ENRICHED, EnrichmentAction.PARTIAL}
    assert "Vision" in result.enriched_fields

    post = roadmap.read_text(encoding="utf-8")
    assert (
        "Acme Widgets ships industrial widgets to enterprise customers"
        in post
    ), f"Expected Vision to contain the Project Purpose's first sentence.\nGot:\n{post}"
    # Vision placeholder token is gone
    vision_body = post.split("## Vision", 1)[1].split("##", 1)[0]
    assert "[PROJECT_NAME]" not in vision_body


def test_enrich_roadmap_inserts_completed_items_hint(tmp_project: Path) -> None:
    from doit_cli.services.roadmap_enricher import enrich_roadmap

    memory = tmp_project / ".doit" / "memory"
    (memory / "constitution.md").write_text(CONSTITUTION_WITH_PURPOSE, encoding="utf-8")
    (memory / "completed_roadmap.md").write_text(COMPLETED_ROADMAP, encoding="utf-8")
    roadmap = memory / "roadmap.md"
    roadmap.write_text(STUBBED_ROADMAP, encoding="utf-8")

    enrich_roadmap(roadmap, project_root=tmp_project)

    post = roadmap.read_text(encoding="utf-8")
    assert "User authentication" in post
    assert "Widget catalog" in post
    assert "Order tracking" in post
    # The hint is inside an HTML comment (rendered markdown hides it)
    assert "<!-- [060] completed-items-hint START" in post


def test_enrich_roadmap_preserves_priority_subsections(tmp_project: Path) -> None:
    """Priority subsection bodies are deliberately left as placeholders."""

    from doit_cli.services.roadmap_enricher import enrich_roadmap

    memory = tmp_project / ".doit" / "memory"
    (memory / "constitution.md").write_text(CONSTITUTION_WITH_PURPOSE, encoding="utf-8")
    roadmap = memory / "roadmap.md"
    roadmap.write_text(STUBBED_ROADMAP, encoding="utf-8")

    enrich_roadmap(roadmap, project_root=tmp_project)

    post = roadmap.read_text(encoding="utf-8")
    # Each priority subsection still contains its [PROJECT_NAME] placeholder
    for priority in ("P1", "P2", "P3", "P4"):
        section = post.split(f"### {priority}", 1)[1].split("### ", 1)[0]
        assert "[PROJECT_NAME]" in section, (
            f"{priority} should still contain placeholder — enricher should not "
            "auto-fill priority items."
        )


def test_enrich_roadmap_noop_when_no_placeholders_and_no_completed(
    tmp_project: Path,
) -> None:
    from doit_cli.services.constitution_enricher import EnrichmentAction
    from doit_cli.services.roadmap_enricher import enrich_roadmap

    memory = tmp_project / ".doit" / "memory"
    # No constitution, no completed_roadmap
    roadmap = memory / "roadmap.md"
    # Roadmap with real Vision content (no placeholder)
    roadmap.write_text(
        "# Roadmap\n\n## Vision\n\nShip widgets with style.\n\n"
        "## Active Requirements\n\n### P1\n\n- real content\n",
        encoding="utf-8",
    )
    pre_bytes = roadmap.read_bytes()

    result = enrich_roadmap(roadmap, project_root=tmp_project)
    assert result.action is EnrichmentAction.NO_OP
    assert roadmap.read_bytes() == pre_bytes


def test_enrich_roadmap_missing_constitution_returns_partial(
    tmp_project: Path,
) -> None:
    """Placeholder Vision with no constitution source → Vision unresolved."""

    from doit_cli.services.constitution_enricher import EnrichmentAction
    from doit_cli.services.roadmap_enricher import enrich_roadmap

    memory = tmp_project / ".doit" / "memory"
    roadmap = memory / "roadmap.md"
    roadmap.write_text(STUBBED_ROADMAP, encoding="utf-8")
    pre_bytes = roadmap.read_bytes()

    result = enrich_roadmap(roadmap, project_root=tmp_project)

    assert result.action is EnrichmentAction.PARTIAL
    assert "Vision" in result.unresolved_fields
    # No write performed (no successful enrichment path)
    assert roadmap.read_bytes() == pre_bytes


def test_enrich_roadmap_re_run_is_idempotent(tmp_project: Path) -> None:
    from doit_cli.services.constitution_enricher import EnrichmentAction
    from doit_cli.services.roadmap_enricher import enrich_roadmap

    memory = tmp_project / ".doit" / "memory"
    (memory / "constitution.md").write_text(CONSTITUTION_WITH_PURPOSE, encoding="utf-8")
    (memory / "completed_roadmap.md").write_text(COMPLETED_ROADMAP, encoding="utf-8")
    roadmap = memory / "roadmap.md"
    roadmap.write_text(STUBBED_ROADMAP, encoding="utf-8")

    enrich_roadmap(roadmap, project_root=tmp_project)
    after_first = roadmap.read_bytes()

    second = enrich_roadmap(roadmap, project_root=tmp_project)
    # Second run should NO_OP (Vision is now real, completed block exists)
    assert second.action is EnrichmentAction.NO_OP
    assert roadmap.read_bytes() == after_first


def test_cli_memory_enrich_roadmap(tmp_project: Path) -> None:
    from typer.testing import CliRunner

    from doit_cli.main import app as doit_app

    memory = tmp_project / ".doit" / "memory"
    (memory / "constitution.md").write_text(CONSTITUTION_WITH_PURPOSE, encoding="utf-8")
    (memory / "completed_roadmap.md").write_text(COMPLETED_ROADMAP, encoding="utf-8")
    (memory / "roadmap.md").write_text(STUBBED_ROADMAP, encoding="utf-8")

    runner = CliRunner()
    result = runner.invoke(
        doit_app, ["memory", "enrich", "roadmap", str(tmp_project), "--json"]
    )
    assert result.exit_code == 0, result.stdout

    import json as jsonlib

    payload = jsonlib.loads(result.stdout)
    assert payload["action"] == "enriched"
    assert "Vision" in payload["enriched_fields"]


def test_enrich_roadmap_handles_escaped_pipes_in_completed_items(
    tmp_project: Path,
) -> None:
    """GFM-escaped pipes (``\\|``) inside completed-item cells should be
    preserved literally. Naive `|`-split would shift column indices."""

    from doit_cli.services.roadmap_enricher import enrich_roadmap

    memory = tmp_project / ".doit" / "memory"
    (memory / "constitution.md").write_text(CONSTITUTION_WITH_PURPOSE, encoding="utf-8")
    (memory / "completed_roadmap.md").write_text(
        "# Completed\n\n## Recently Completed\n\n"
        "| Item | Priority | Date |\n"
        "|------|----------|------|\n"
        "| API \\| REST layer | P1 | 2026-01-01 |\n"
        "| Plain feature | P2 | 2026-01-02 |\n",
        encoding="utf-8",
    )
    (memory / "roadmap.md").write_text(STUBBED_ROADMAP, encoding="utf-8")

    enrich_roadmap(memory / "roadmap.md", project_root=tmp_project)

    post = (memory / "roadmap.md").read_text(encoding="utf-8")
    # The pipe character inside the Item cell should survive (unescaped).
    assert "API | REST layer" in post
    assert "Plain feature" in post


def test_enrich_roadmap_truncates_long_vision_without_breaking_markdown(
    tmp_project: Path,
) -> None:
    """A Project Purpose with inline markdown should truncate cleanly."""

    from doit_cli.services.roadmap_enricher import enrich_roadmap

    memory = tmp_project / ".doit" / "memory"
    (memory / "constitution.md").write_text(
        "---\nid: app-acme\nname: Acme\nkind: application\nphase: 1\n"
        "icon: AC\ntagline: t\ndependencies: []\n---\n"
        "# Acme Constitution\n\n"
        "## Purpose & Goals\n\n"
        "### Project Purpose\n\n"
        "Ship widgets with `code-fenced` terms and [links](https://example.com) "
        "and *emphasis* that should not leave dangling markers when truncated "
        "because this sentence is quite long and certainly over one hundred "
        "forty characters total including the rest of the sentence that follows.\n",
        encoding="utf-8",
    )
    (memory / "roadmap.md").write_text(STUBBED_ROADMAP, encoding="utf-8")

    enrich_roadmap(memory / "roadmap.md", project_root=tmp_project)

    post = (memory / "roadmap.md").read_text(encoding="utf-8")
    vision = post.split("## Vision", 1)[1].split("##", 1)[0]
    # No dangling markdown markers
    assert "`" not in vision, f"Vision contains unclosed backtick: {vision!r}"
    assert "](" not in vision, f"Vision contains unclosed link: {vision!r}"
    # Still contains meaningful content
    assert "Ship widgets" in vision


def test_cli_memory_migrate_umbrella(tmp_project: Path) -> None:
    """`doit memory migrate` runs all three migrators and reports."""

    from typer.testing import CliRunner

    from doit_cli.main import app as doit_app

    memory = tmp_project / ".doit" / "memory"
    # Legacy files across all three file types
    (memory / "constitution.md").write_text(
        "# Constitution\n\n## Purpose & Goals\n\n### Project Purpose\n\nShip.\n",
        encoding="utf-8",
    )
    (memory / "roadmap.md").write_text("# Roadmap\n", encoding="utf-8")
    (memory / "tech-stack.md").write_text("# Tech\n", encoding="utf-8")

    runner = CliRunner()
    result = runner.invoke(
        doit_app, ["memory", "migrate", str(tmp_project), "--json"]
    )
    assert result.exit_code == 0, result.stdout

    import json as jsonlib

    payload = jsonlib.loads(result.stdout)
    files = {row["file"]: row["action"] for row in payload}
    assert files["constitution.md"] == "prepended"
    assert files["roadmap.md"] == "prepended"
    assert files["tech-stack.md"] == "prepended"
