"""Integration tests for the constitution frontmatter migrator.

These exercise :func:`doit_cli.services.constitution_migrator.migrate_constitution`
end-to-end against a real filesystem, matching the scenarios in the
feature quickstart. Scenario 2 (AI enrichment via ``/doit.constitution``)
is not covered here — it requires an AI assistant and is run manually.
"""

from __future__ import annotations

import hashlib
from pathlib import Path

import pytest

from doit_cli.services.constitution_migrator import (
    REQUIRED_FIELDS,
    MigrationAction,
    migrate_constitution,
)

LEGACY_BODY = """# Acme Widgets Constitution

## Purpose & Goals

### Project Purpose

Ship widgets to happy customers.

### Success Criteria

- 99.9% on-time delivery
"""


COMPLETE_FRONTMATTER = """---
id: app-acme-widgets
name: Acme Widgets
kind: application
phase: 3
icon: AW
tagline: Ship widgets to happy customers.
dependencies:
  - platform-github
---

# Acme Widgets Constitution

## Purpose & Goals

### Project Purpose

Ship widgets to happy customers.
"""


MALFORMED_YAML = """---
id: app-broken
name: "Broken: unclosed quotes
---
# Body content
"""


@pytest.fixture
def tmp_constitution(tmp_path: Path) -> Path:
    """Return the path where a constitution.md should live for this test."""

    memory_dir = tmp_path / ".doit" / "memory"
    memory_dir.mkdir(parents=True)
    return memory_dir / "constitution.md"


def _body_hash(body: str) -> bytes:
    return hashlib.sha256(body.encode("utf-8")).digest()


def _extract_body(source: str) -> str:
    """Return everything after the closing ``---\\n`` of a frontmatter block,
    or the whole source when no block is present."""

    if not source.startswith("---\n"):
        return source
    end = source.find("\n---\n", 4)
    if end == -1:
        return source
    return source[end + len("\n---\n"):]


# ---------------------------------------------------------------------------
# US1: Legacy project upgrades cleanly


def test_no_frontmatter_is_prepended(tmp_constitution: Path) -> None:
    tmp_constitution.write_text(LEGACY_BODY, encoding="utf-8")
    pre_hash = _body_hash(LEGACY_BODY)

    result = migrate_constitution(tmp_constitution)

    assert result.action is MigrationAction.PREPENDED
    assert set(result.added_fields) == set(REQUIRED_FIELDS)
    assert result.preserved_body_hash == pre_hash
    assert result.error is None

    post = tmp_constitution.read_text(encoding="utf-8")
    assert post.startswith("---\n")
    assert _extract_body(post) == LEGACY_BODY


def test_prepended_file_passes_verify_memory(tmp_path: Path) -> None:
    """verify-memory returns warnings (not errors) for a freshly-migrated
    constitution with placeholder values."""

    memory_dir = tmp_path / ".doit" / "memory"
    memory_dir.mkdir(parents=True)
    constitution = memory_dir / "constitution.md"
    constitution.write_text(LEGACY_BODY, encoding="utf-8")

    # Tech-stack and roadmap need to exist so the validator doesn't emit
    # unrelated warnings that would distract from this test's assertions.
    (memory_dir / "tech-stack.md").write_text(
        "# Tech\n\n## Tech Stack\n\n### Languages\n\nPython\n",
        encoding="utf-8",
    )
    (memory_dir / "roadmap.md").write_text(
        "# Roadmap\n\n## Active Requirements\n\n### P1\n\n- build it\n",
        encoding="utf-8",
    )

    assert migrate_constitution(constitution).action is MigrationAction.PREPENDED

    from doit_cli.services.memory_validator import validate_project

    report = validate_project(tmp_path)
    errors = [
        i
        for i in report.issues
        if i.severity.value == "error" and i.file.endswith("constitution.md")
    ]
    warnings = [
        i
        for i in report.issues
        if i.severity.value == "warning" and i.file.endswith("constitution.md")
    ]

    assert errors == [], f"Expected zero constitution errors, got: {errors}"
    assert len(warnings) >= len(REQUIRED_FIELDS), (
        f"Expected at least {len(REQUIRED_FIELDS)} placeholder warnings, "
        f"got {len(warnings)}: {warnings}"
    )


def test_complete_frontmatter_is_noop(tmp_constitution: Path) -> None:
    tmp_constitution.write_text(COMPLETE_FRONTMATTER, encoding="utf-8")
    pre_bytes = tmp_constitution.read_bytes()

    result = migrate_constitution(tmp_constitution)

    assert result.action is MigrationAction.NO_OP
    assert result.added_fields == ()
    assert result.error is None
    assert tmp_constitution.read_bytes() == pre_bytes, (
        "NO_OP must not touch the file on disk"
    )


def test_malformed_yaml_errors_and_preserves_bytes(
    tmp_constitution: Path,
) -> None:
    tmp_constitution.write_text(MALFORMED_YAML, encoding="utf-8")
    pre_bytes = tmp_constitution.read_bytes()

    result = migrate_constitution(tmp_constitution)

    assert result.action is MigrationAction.ERROR
    assert result.error is not None
    assert "invalid YAML" in str(result.error) or "could not be parsed" in str(
        result.error
    )
    assert tmp_constitution.read_bytes() == pre_bytes, (
        "ERROR must not rewrite the file"
    )


def test_missing_file_is_noop(tmp_path: Path) -> None:
    missing = tmp_path / ".doit" / "memory" / "constitution.md"
    result = migrate_constitution(missing)

    assert result.action is MigrationAction.NO_OP
    assert result.error is None
    assert not missing.exists(), "NO_OP must not create the file"


def test_migration_is_idempotent(tmp_constitution: Path) -> None:
    tmp_constitution.write_text(LEGACY_BODY, encoding="utf-8")

    first = migrate_constitution(tmp_constitution)
    assert first.action is MigrationAction.PREPENDED

    after_first = tmp_constitution.read_bytes()

    second = migrate_constitution(tmp_constitution)
    assert second.action is MigrationAction.NO_OP
    assert tmp_constitution.read_bytes() == after_first, (
        "Second run must produce a zero-byte diff"
    )


# ---------------------------------------------------------------------------
# Body preservation guarantees


def test_body_with_unicode_is_preserved(tmp_constitution: Path) -> None:
    body = "# Café Résumé 日本語\n\nBody content with unicode.\n"
    tmp_constitution.write_text(body, encoding="utf-8")

    result = migrate_constitution(tmp_constitution)

    assert result.action is MigrationAction.PREPENDED
    assert result.preserved_body_hash == _body_hash(body)
    assert _extract_body(tmp_constitution.read_text(encoding="utf-8")) == body


def test_body_without_trailing_newline_is_preserved(
    tmp_constitution: Path,
) -> None:
    body = "# No trailing newline"
    tmp_constitution.write_text(body, encoding="utf-8")

    result = migrate_constitution(tmp_constitution)

    assert result.action is MigrationAction.PREPENDED
    post_body = _extract_body(tmp_constitution.read_text(encoding="utf-8"))
    assert post_body == body


# ---------------------------------------------------------------------------
# US3: Partial frontmatter is completed, not overwritten


def test_partial_frontmatter_is_patched(tmp_constitution: Path) -> None:
    """Only missing required fields are added; existing values preserved."""

    source = """---
id: app-acme-widgets
name: Acme Widgets
---

# Acme Widgets Constitution

## Purpose & Goals

### Project Purpose

Ship widgets.
"""
    tmp_constitution.write_text(source, encoding="utf-8")

    result = migrate_constitution(tmp_constitution)

    assert result.action is MigrationAction.PATCHED
    assert set(result.added_fields) == {
        "kind",
        "phase",
        "icon",
        "tagline",
        "dependencies",
    }
    # Existing values must be unchanged
    post = tmp_constitution.read_text(encoding="utf-8")
    assert "id: app-acme-widgets" in post
    assert "name: Acme Widgets" in post
    # Added placeholders
    assert "[PROJECT_KIND]" in post
    assert "[PROJECT_PHASE]" in post
    assert "[PROJECT_ICON]" in post
    assert "[PROJECT_TAGLINE]" in post
    assert "[PROJECT_DEPENDENCIES]" in post


def test_unknown_frontmatter_fields_are_preserved(
    tmp_constitution: Path,
) -> None:
    """Fields not defined in the schema remain verbatim after migration."""

    source = """---
id: app-acme
name: Acme
owner: alice@example.com
custom_metadata:
  tier: gold
---

# Body
"""
    tmp_constitution.write_text(source, encoding="utf-8")

    result = migrate_constitution(tmp_constitution)

    assert result.action is MigrationAction.PATCHED

    post = tmp_constitution.read_text(encoding="utf-8")
    assert "owner: alice@example.com" in post
    assert "tier: gold" in post


def test_patched_file_preserves_body_hash(tmp_constitution: Path) -> None:
    body = """

# Constitution

## Purpose & Goals

### Project Purpose

Ship widgets.
"""
    source = "---\nid: app-acme-widgets\nname: Acme\n---\n" + body[1:]  # drop leading \n from body
    tmp_constitution.write_text(source, encoding="utf-8")

    result = migrate_constitution(tmp_constitution)

    assert result.action is MigrationAction.PATCHED
    # Body bytes after the migrator's rewrite must equal the original body bytes.
    post_body = _extract_body(tmp_constitution.read_text(encoding="utf-8"))
    assert result.preserved_body_hash == _body_hash(post_body)


def test_partial_frontmatter_is_idempotent_when_rerun(
    tmp_constitution: Path,
) -> None:
    """After PATCHED, the second run sees placeholder values as 'present'
    and reports NO_OP."""

    source = "---\nid: app-acme-widgets\nname: Acme\n---\n\n# Body\n"
    tmp_constitution.write_text(source, encoding="utf-8")

    first = migrate_constitution(tmp_constitution)
    assert first.action is MigrationAction.PATCHED
    after_first = tmp_constitution.read_bytes()

    second = migrate_constitution(tmp_constitution)
    assert second.action is MigrationAction.NO_OP
    assert tmp_constitution.read_bytes() == after_first
