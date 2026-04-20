"""Integration tests for the constitution enricher.

These replace the manual test plan (MT-001..MT-005 in the feature
test-report) with automated coverage for the deterministic portion of
``/doit.constitution``'s Step 2b enrichment behavior (spec FR-011..FR-014).

Scenarios:

- **MT-001** → :func:`test_enricher_detects_placeholders_and_enters_enrichment_mode`
- **MT-002** → :func:`test_enriched_file_passes_verify_memory_with_zero_warnings`
- **MT-003** → :func:`test_enrichment_preserves_body_byte_for_byte`
- **MT-004** → :func:`test_low_confidence_fields_remain_as_placeholders`
- **MT-005** → :func:`test_full_handoff_migrate_then_enrich_then_verify`
"""

from __future__ import annotations

import hashlib
from pathlib import Path

import pytest

from doit_cli.services.constitution_enricher import (
    EnrichmentAction,
    enrich_constitution,
)
from doit_cli.services.constitution_migrator import (
    MigrationAction,
    migrate_constitution,
)

LEGACY_BODY_RICH = """# Acme Widgets Constitution

## Purpose & Goals

### Project Purpose

Acme Widgets ships high-quality industrial widgets to enterprise customers with guaranteed 99.9% on-time delivery.

### Success Criteria

- 99.9% on-time delivery
- Zero defects per 10,000 units
- Sub-48-hour RMA turnaround
"""


LEGACY_BODY_SPARSE = """# Project

A very short file with no Purpose & Goals section.
"""


LEGACY_BODY_SERVICE_FLAVOURED = """# Event Bus Constitution

## Purpose & Goals

### Project Purpose

The Event Bus is a platform service consumed by other services for
asynchronous message delivery. It acts as a queue broker between
microservice producers and consumers.
"""


@pytest.fixture
def tmp_project(tmp_path: Path) -> Path:
    """Return the project root; .doit/memory/ prepared."""

    (tmp_path / ".doit" / "memory").mkdir(parents=True)
    return tmp_path


def _body_hash(body: str) -> bytes:
    return hashlib.sha256(body.encode("utf-8")).digest()


def _extract_body(source: str) -> str:
    if not source.startswith("---\n"):
        return source
    end = source.find("\n---\n", 4)
    if end == -1:
        return source
    return source[end + len("\n---\n") :]


# ---------------------------------------------------------------------------
# MT-001 — detect placeholders and enter enrichment mode


def test_enricher_detects_placeholders_and_enters_enrichment_mode(
    tmp_project: Path,
) -> None:
    """After doit update prepends a placeholder skeleton, the enricher
    recognizes the placeholders and runs."""

    constitution = tmp_project / ".doit" / "memory" / "constitution.md"
    constitution.write_text(LEGACY_BODY_RICH, encoding="utf-8")

    # Simulate the doit update step first.
    migrate_result = migrate_constitution(constitution)
    assert migrate_result.action is MigrationAction.PREPENDED

    enrich_result = enrich_constitution(constitution, project_dir="acme-widgets")

    assert enrich_result.action in {
        EnrichmentAction.ENRICHED,
        EnrichmentAction.PARTIAL,
    }
    assert enrich_result.enriched_fields, (
        "Enricher must replace at least one placeholder"
    )


# ---------------------------------------------------------------------------
# MT-002 — enriched file passes verify-memory with zero warnings


def test_enriched_file_passes_verify_memory_with_zero_warnings(
    tmp_project: Path,
) -> None:
    """A rich body should yield a fully enriched constitution with no
    placeholder warnings reported by the memory validator."""

    memory_dir = tmp_project / ".doit" / "memory"
    constitution = memory_dir / "constitution.md"
    constitution.write_text(LEGACY_BODY_RICH, encoding="utf-8")

    # Tech-stack and roadmap need valid shape so the validator doesn't
    # emit unrelated warnings that pollute this assertion.
    (memory_dir / "tech-stack.md").write_text(
        "# Tech\n\n## Tech Stack\n\n### Languages\n\nPython\n",
        encoding="utf-8",
    )
    (memory_dir / "roadmap.md").write_text(
        "# Roadmap\n\n## Active Requirements\n\n### P1\n\n- ship widgets\n",
        encoding="utf-8",
    )

    migrate_constitution(constitution)
    result = enrich_constitution(constitution, project_dir="acme-widgets")

    assert result.action is EnrichmentAction.ENRICHED, (
        f"Expected full enrichment, got {result.action} with "
        f"unresolved={result.unresolved_fields}"
    )
    assert result.unresolved_fields == ()

    from doit_cli.services.memory_validator import validate_project

    report = validate_project(tmp_project)
    placeholder_warnings = [
        i
        for i in report.issues
        if i.severity.value == "warning"
        and i.file.endswith("constitution.md")
        and i.field_name in {
            "id", "name", "kind", "phase", "icon", "tagline", "dependencies",
        }
    ]
    errors = [i for i in report.issues if i.severity.value == "error"]

    assert placeholder_warnings == [], (
        f"Expected zero placeholder warnings, got: {placeholder_warnings}"
    )
    assert errors == [], f"Expected zero errors, got: {errors}"


# ---------------------------------------------------------------------------
# MT-003 — body preservation byte-for-byte


def test_enrichment_preserves_body_byte_for_byte(tmp_project: Path) -> None:
    constitution = tmp_project / ".doit" / "memory" / "constitution.md"
    constitution.write_text(LEGACY_BODY_RICH, encoding="utf-8")

    # migrate first so the enricher has a frontmatter to act on
    migrate_constitution(constitution)
    pre_body = _extract_body(constitution.read_text(encoding="utf-8"))
    pre_hash = _body_hash(pre_body)

    result = enrich_constitution(constitution, project_dir="acme-widgets")

    assert result.action is not EnrichmentAction.ERROR

    post_body = _extract_body(constitution.read_text(encoding="utf-8"))
    post_hash = _body_hash(post_body)

    assert pre_hash == post_hash, "Body SHA-256 must be identical before/after enrichment"
    assert pre_body == post_body, "Body bytes must be byte-identical"
    assert result.preserved_body_hash == post_hash


def test_enrichment_preserves_body_with_unicode(tmp_project: Path) -> None:
    constitution = tmp_project / ".doit" / "memory" / "constitution.md"
    body = (
        "# Café Resumé Constitution\n\n"
        "## Purpose & Goals\n\n"
        "### Project Purpose\n\n"
        "Build high-quality café management tools for small businesses — "
        "with 日本語 / émoji (☕) support in every field.\n"
    )
    constitution.write_text(body, encoding="utf-8")

    migrate_constitution(constitution)
    pre_body = _extract_body(constitution.read_text(encoding="utf-8"))

    result = enrich_constitution(constitution, project_dir="cafe-resume")

    assert result.action is not EnrichmentAction.ERROR
    post_body = _extract_body(constitution.read_text(encoding="utf-8"))
    assert pre_body == post_body, "unicode body must survive enrichment byte-for-byte"


# ---------------------------------------------------------------------------
# MT-004 — low-confidence fields remain as placeholders


def test_low_confidence_fields_remain_as_placeholders(tmp_project: Path) -> None:
    """When the body is too sparse, fields that can't be inferred stay as
    placeholders and appear in unresolved_fields."""

    constitution = tmp_project / ".doit" / "memory" / "constitution.md"
    constitution.write_text(LEGACY_BODY_SPARSE, encoding="utf-8")

    migrate_constitution(constitution)
    result = enrich_constitution(constitution, project_dir="")  # no dir hint

    assert result.action is EnrichmentAction.PARTIAL
    # tagline needs a Purpose & Goals section — the sparse body has none
    assert "tagline" in result.unresolved_fields, (
        f"Expected 'tagline' to be unresolved in sparse body; got "
        f"unresolved={result.unresolved_fields}"
    )
    # File contents still carry the tagline placeholder token
    post = constitution.read_text(encoding="utf-8")
    assert "[PROJECT_TAGLINE]" in post


def test_low_confidence_returns_placeholder_not_garbage(tmp_project: Path) -> None:
    """Never infer a value when confidence is low — always keep the
    placeholder and report it as unresolved."""

    constitution = tmp_project / ".doit" / "memory" / "constitution.md"
    # Body with no headings at all
    constitution.write_text("Just plain text, nothing else.\n", encoding="utf-8")

    migrate_constitution(constitution)
    result = enrich_constitution(constitution, project_dir="")

    # Without any headings AND without a project_dir hint, name/id/icon/tagline
    # can't be inferred.
    assert "name" in result.unresolved_fields
    assert "tagline" in result.unresolved_fields
    assert "id" in result.unresolved_fields
    assert "icon" in result.unresolved_fields


# ---------------------------------------------------------------------------
# MT-005 — full handoff: migrate → enrich → verify


def test_full_handoff_migrate_then_enrich_then_verify(tmp_project: Path) -> None:
    """Execute the whole pipeline end-to-end on a realistic fixture."""

    memory_dir = tmp_project / ".doit" / "memory"
    constitution = memory_dir / "constitution.md"
    constitution.write_text(LEGACY_BODY_RICH, encoding="utf-8")
    (memory_dir / "tech-stack.md").write_text(
        "# Tech\n\n## Tech Stack\n\n### Languages\n\nPython\n",
        encoding="utf-8",
    )
    (memory_dir / "roadmap.md").write_text(
        "# Roadmap\n\n## Active Requirements\n\n### P1\n\n- ship widgets\n",
        encoding="utf-8",
    )

    # Step 1: doit update (migrator)
    m = migrate_constitution(constitution)
    assert m.action is MigrationAction.PREPENDED

    # Step 2: /doit.constitution enricher
    e = enrich_constitution(constitution, project_dir="acme-widgets")
    assert e.action is EnrichmentAction.ENRICHED
    assert e.unresolved_fields == ()

    # Step 3: doit verify-memory — zero errors, zero placeholder warnings
    from doit_cli.services.memory_validator import validate_project

    report = validate_project(tmp_project)
    errors = [i for i in report.issues if i.severity.value == "error"]
    placeholder_warnings = [
        i
        for i in report.issues
        if i.severity.value == "warning" and "placeholder" in i.message
    ]
    assert errors == []
    assert placeholder_warnings == []


# ---------------------------------------------------------------------------
# Inference quality — per-field checks


def test_kind_service_inferred_from_body_keywords(tmp_project: Path) -> None:
    constitution = tmp_project / ".doit" / "memory" / "constitution.md"
    constitution.write_text(LEGACY_BODY_SERVICE_FLAVOURED, encoding="utf-8")

    migrate_constitution(constitution)
    result = enrich_constitution(constitution, project_dir="event-bus")

    post = constitution.read_text(encoding="utf-8")
    assert "kind: service" in post, (
        f"Body mentions 'service'/'broker' → kind should be 'service'. Got:\n{post}"
    )
    assert "platform-event-bus" in post, (
        "service kind should produce platform-* id"
    )
    assert "kind" in result.enriched_fields


def test_kind_application_is_default(tmp_project: Path) -> None:
    constitution = tmp_project / ".doit" / "memory" / "constitution.md"
    constitution.write_text(LEGACY_BODY_RICH, encoding="utf-8")

    migrate_constitution(constitution)
    result = enrich_constitution(constitution, project_dir="acme-widgets")

    post = constitution.read_text(encoding="utf-8")
    assert "kind: application" in post
    assert "app-acme-widgets" in post
    assert "kind" in result.enriched_fields


def test_dependencies_inferred_from_body_component_references(
    tmp_project: Path,
) -> None:
    constitution = tmp_project / ".doit" / "memory" / "constitution.md"
    body = (
        "# Cloud Control Constitution\n\n"
        "## Purpose & Goals\n\n"
        "### Project Purpose\n\n"
        "Cloud Control manages virtual desktops.\n\n"
        "## Dependencies\n\n"
        "- platform-event-bus for async messaging\n"
        "- app-cloud-control-frontend for UI\n"
        "- external: Azure Virtual Desktop REST API\n"
    )
    constitution.write_text(body, encoding="utf-8")

    migrate_constitution(constitution)
    result = enrich_constitution(constitution, project_dir="cloud-control")

    post = constitution.read_text(encoding="utf-8")
    assert "platform-event-bus" in post
    assert "app-cloud-control-frontend" in post
    assert "dependencies" in result.enriched_fields


def test_icon_derived_from_name_initials(tmp_project: Path) -> None:
    constitution = tmp_project / ".doit" / "memory" / "constitution.md"
    body = (
        "# Cloud Control Constitution\n\n"
        "## Purpose & Goals\n\n"
        "### Project Purpose\n\n"
        "ML-powered Azure Virtual Desktop management platform.\n"
    )
    constitution.write_text(body, encoding="utf-8")

    migrate_constitution(constitution)
    result = enrich_constitution(constitution, project_dir="cloud-control")

    post = constitution.read_text(encoding="utf-8")
    # Cloud Control → CC
    assert "icon: CC" in post
    assert "icon" in result.enriched_fields


def test_name_from_h1_constitution_heading(tmp_project: Path) -> None:
    constitution = tmp_project / ".doit" / "memory" / "constitution.md"
    constitution.write_text(
        "# Acme Widgets Constitution\n\n"
        "## Purpose & Goals\n\n"
        "### Project Purpose\n\n"
        "Ship widgets.\n",
        encoding="utf-8",
    )

    migrate_constitution(constitution)
    enrich_constitution(constitution, project_dir="unrelated-dir")

    post = constitution.read_text(encoding="utf-8")
    assert "name: Acme Widgets" in post, (
        "Name should come from the H1 'X Constitution' heading, not project_dir"
    )


def test_idempotent_enrich_is_noop_on_second_run(tmp_project: Path) -> None:
    constitution = tmp_project / ".doit" / "memory" / "constitution.md"
    constitution.write_text(LEGACY_BODY_RICH, encoding="utf-8")
    migrate_constitution(constitution)

    first = enrich_constitution(constitution, project_dir="acme-widgets")
    assert first.action is EnrichmentAction.ENRICHED
    first_bytes = constitution.read_bytes()

    second = enrich_constitution(constitution, project_dir="acme-widgets")
    assert second.action is EnrichmentAction.NO_OP
    assert constitution.read_bytes() == first_bytes


def test_missing_file_is_noop(tmp_path: Path) -> None:
    missing = tmp_path / ".doit" / "memory" / "constitution.md"
    result = enrich_constitution(missing)
    assert result.action is EnrichmentAction.NO_OP
    assert not missing.exists()


# ---------------------------------------------------------------------------
# CLI subcommand coverage — make sure doit constitution enrich wires up


def test_cli_constitution_enrich(tmp_project: Path) -> None:
    from typer.testing import CliRunner

    from doit_cli.main import app as doit_app

    constitution = tmp_project / ".doit" / "memory" / "constitution.md"
    constitution.write_text(LEGACY_BODY_RICH, encoding="utf-8")
    migrate_constitution(constitution)

    runner = CliRunner()
    result = runner.invoke(
        doit_app,
        ["constitution", "enrich", str(tmp_project), "--json"],
    )

    assert result.exit_code == 0, result.stdout
    import json as jsonlib

    payload = jsonlib.loads(result.stdout)
    assert payload["action"] in {"enriched", "partial"}
    assert set(payload["enriched_fields"])


def test_cli_constitution_enrich_partial_exits_1(tmp_project: Path) -> None:
    from typer.testing import CliRunner

    from doit_cli.main import app as doit_app

    constitution = tmp_project / ".doit" / "memory" / "constitution.md"
    constitution.write_text(LEGACY_BODY_SPARSE, encoding="utf-8")
    migrate_constitution(constitution)

    runner = CliRunner()
    result = runner.invoke(
        doit_app,
        ["constitution", "enrich", str(tmp_project), "--json"],
    )

    # Sparse body ⇒ PARTIAL ⇒ exit code 1.
    assert result.exit_code == 1, result.stdout
