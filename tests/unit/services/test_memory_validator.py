"""Unit tests for the memory-file validator service."""

from __future__ import annotations

import textwrap
from pathlib import Path

from doit_cli.models.memory_contract import MemoryIssueSeverity
from doit_cli.services.memory_validator import validate_project

# ---------------------------------------------------------------------------
# Helpers


def make_project(
    tmp_path: Path,
    *,
    constitution: str | None,
    tech_stack: str | None = None,
    roadmap: str | None = None,
) -> Path:
    """Create a skeletal project at ``tmp_path`` with the three memory files."""

    root = tmp_path / "project"
    memory = root / ".doit" / "memory"
    memory.mkdir(parents=True)
    if constitution is not None:
        (memory / "constitution.md").write_text(textwrap.dedent(constitution))
    if tech_stack is not None:
        (memory / "tech-stack.md").write_text(textwrap.dedent(tech_stack))
    if roadmap is not None:
        (memory / "roadmap.md").write_text(textwrap.dedent(roadmap))
    return root


GOOD_CONSTITUTION = """\
---
id: app-example
name: Example App
kind: application
phase: 2
icon: EX
tagline: >-
  An example app used only for unit tests.
competitor: null
dependencies:
  - platform-identity-service
consumers: null
---

# Example App Constitution

## Purpose & Goals

### Project Purpose

The purpose of this project.

### Success Criteria

- Ship on time
"""

GOOD_TECH_STACK = """\
# Example Tech Stack

## Tech Stack

### Languages
- TypeScript

### Frameworks
- Express

## Infrastructure
- AKS
"""

GOOD_ROADMAP = """\
# Project Roadmap

## Vision

A clear vision.

## Active Requirements

### P1 - Critical

- [ ] First feature `[001-first]`
  - **Rationale**: Because.

## Open Questions

| Priority | Question | Owner |
| -------- | -------- | ----- |
| High     | Should we?           | Product |
"""


# ---------------------------------------------------------------------------
# Tests


class TestValidateProject:
    """Tests for :func:`validate_project`."""

    def test_missing_memory_dir_reports_error(self, tmp_path):
        root = tmp_path / "project"
        root.mkdir()
        report = validate_project(root)
        assert report.has_errors()
        assert any("does not exist" in i.message for i in report.issues)

    def test_happy_path_produces_no_errors(self, tmp_path):
        root = make_project(
            tmp_path,
            constitution=GOOD_CONSTITUTION,
            tech_stack=GOOD_TECH_STACK,
            roadmap=GOOD_ROADMAP,
        )
        report = validate_project(root)
        # Warnings may exist (e.g. about optional sections) but there must be no errors.
        assert not report.has_errors(), [i.message for i in report.issues]
        assert report.placeholder_files == []

    def test_missing_frontmatter_is_an_error(self, tmp_path):
        source = GOOD_CONSTITUTION.split("---\n\n", 1)[1]  # drop frontmatter
        root = make_project(tmp_path, constitution=source)
        report = validate_project(root)
        assert report.has_errors()
        assert any("no YAML frontmatter" in i.message for i in report.issues)

    def test_bad_frontmatter_field_surfaces_error(self, tmp_path):
        bad = GOOD_CONSTITUTION.replace("kind: application", "kind: widget")
        root = make_project(tmp_path, constitution=bad)
        report = validate_project(root)
        assert any(i.field_name == "kind" for i in report.issues)

    def test_placeholder_body_is_a_warning_not_an_error(self, tmp_path):
        placeholder = textwrap.dedent(
            """\
            # [PROJECT_NAME] Constitution

            ## Purpose & Goals

            ### Project Purpose

            [PROJECT_PURPOSE]

            ### Success Criteria

            [SUCCESS_CRITERIA]

            ## Core Principles

            ### [PRINCIPLE_1_NAME]

            [PRINCIPLE_1_DESCRIPTION]
            """
        )
        root = make_project(tmp_path, constitution=placeholder)
        report = validate_project(root)
        # Placeholder bodies produce a warning, not an error (beyond the
        # missing-frontmatter error which is unrelated).
        warnings = [
            i
            for i in report.issues
            if i.severity is MemoryIssueSeverity.WARNING
            and "placeholder" in i.message
        ]
        assert warnings
        assert ".doit/memory/constitution.md" in report.placeholder_files

    def test_incidental_token_does_not_trip_placeholder_detection(self, tmp_path):
        """Files that reference a single placeholder token in a 'rename' comment
        (as several velocity-platform constitutions do) must NOT flag."""

        text = GOOD_CONSTITUTION.replace(
            "The purpose of this project.",
            "The purpose of this project.\n\n"
            "<!-- [PRINCIPLE_1_NAME] → I. My Principle -->",
        )
        root = make_project(tmp_path, constitution=text)
        report = validate_project(root)
        assert ".doit/memory/constitution.md" not in report.placeholder_files

    def test_tech_stack_without_subheadings_warns(self, tmp_path):
        no_sub = textwrap.dedent(
            """\
            ## Tech Stack

            See the constitution.
            """
        )
        root = make_project(
            tmp_path, constitution=GOOD_CONSTITUTION, tech_stack=no_sub
        )
        report = validate_project(root)
        assert any("no `### <Group>` subsections" in i.message for i in report.issues)

    def test_missing_active_requirements_is_an_error(self, tmp_path):
        no_active = "# Project Roadmap\n\n## Vision\nA vision.\n"
        root = make_project(
            tmp_path,
            constitution=GOOD_CONSTITUTION,
            tech_stack=GOOD_TECH_STACK,
            roadmap=no_active,
        )
        report = validate_project(root)
        assert any("Active Requirements" in i.message for i in report.issues)
        assert report.has_errors()

    def test_open_questions_wrong_column_order_warns(self, tmp_path):
        wrong = GOOD_ROADMAP.replace(
            "| Priority | Question | Owner |\n| -------- | -------- | ----- |",
            "| Question | Priority | Owner |\n| -------- | -------- | ----- |",
        )
        root = make_project(
            tmp_path,
            constitution=GOOD_CONSTITUTION,
            tech_stack=GOOD_TECH_STACK,
            roadmap=wrong,
        )
        report = validate_project(root)
        assert any("must be `Priority | Question | Owner`" in i.message for i in report.issues)

    def test_open_questions_bad_priority_warns(self, tmp_path):
        bad = GOOD_ROADMAP.replace(
            "| High     | Should we?           | Product |",
            "| Urgent   | Should we?           | Product |",
        )
        root = make_project(
            tmp_path,
            constitution=GOOD_CONSTITUTION,
            tech_stack=GOOD_TECH_STACK,
            roadmap=bad,
        )
        report = validate_project(root)
        assert any("Urgent" in i.message for i in report.issues)

    def test_open_questions_section_is_optional(self, tmp_path):
        without = GOOD_ROADMAP.split("## Open Questions", 1)[0].rstrip() + "\n"
        root = make_project(
            tmp_path,
            constitution=GOOD_CONSTITUTION,
            tech_stack=GOOD_TECH_STACK,
            roadmap=without,
        )
        report = validate_project(root)
        assert not report.has_errors()

    def test_to_dict_is_json_friendly(self, tmp_path):
        root = make_project(
            tmp_path,
            constitution=GOOD_CONSTITUTION,
            tech_stack=GOOD_TECH_STACK,
            roadmap=GOOD_ROADMAP,
        )
        d = validate_project(root).to_dict()
        assert {"issues", "placeholder_files", "error_count", "warning_count"} <= d.keys()
        assert isinstance(d["issues"], list)
