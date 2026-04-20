"""Integration tests for `doit verify-memory` and `doit memory schema`."""

from __future__ import annotations

import json
import textwrap
from pathlib import Path

from typer.testing import CliRunner


runner = CliRunner()


def _make_project(
    tmp_path: Path,
    *,
    constitution: str,
    tech_stack: str | None = None,
    roadmap: str | None = None,
) -> Path:
    root = tmp_path / "proj"
    memory = root / ".doit" / "memory"
    memory.mkdir(parents=True)
    (memory / "constitution.md").write_text(textwrap.dedent(constitution))
    if tech_stack is not None:
        (memory / "tech-stack.md").write_text(textwrap.dedent(tech_stack))
    if roadmap is not None:
        (memory / "roadmap.md").write_text(textwrap.dedent(roadmap))
    return root


GOOD_CONSTITUTION = """\
---
id: app-foo
name: Foo
kind: application
phase: 2
icon: FO
tagline: An example component.
competitor: null
dependencies: []
consumers: null
---

# Foo Constitution

## Purpose & Goals

### Project Purpose

A clear purpose.
"""

GOOD_TECH_STACK = """\
# Foo Tech Stack

## Tech Stack

### Languages
- Python
"""

GOOD_ROADMAP = """\
# Project Roadmap

## Active Requirements

### P1 - Critical
- [ ] Do the thing
  - **Rationale**: Because.
"""


class TestVerifyMemory:
    """Integration tests for `doit verify-memory`."""

    def test_happy_path_exits_zero(self, tmp_path):
        from doit_cli.main import app

        root = _make_project(
            tmp_path,
            constitution=GOOD_CONSTITUTION,
            tech_stack=GOOD_TECH_STACK,
            roadmap=GOOD_ROADMAP,
        )
        result = runner.invoke(app, ["verify-memory", str(root)])
        assert result.exit_code == 0, result.output

    def test_missing_frontmatter_exits_non_zero(self, tmp_path):
        from doit_cli.main import app

        broken = GOOD_CONSTITUTION.split("---\n", 2)[2]  # drop the frontmatter
        root = _make_project(tmp_path, constitution=broken)
        result = runner.invoke(app, ["verify-memory", str(root), "--json"])
        assert result.exit_code != 0
        payload = json.loads(result.output)
        assert payload["error_count"] >= 1
        assert any(
            "no YAML frontmatter" in issue["message"] for issue in payload["issues"]
        )

    def test_json_output_is_valid_json(self, tmp_path):
        from doit_cli.main import app

        root = _make_project(
            tmp_path,
            constitution=GOOD_CONSTITUTION,
            tech_stack=GOOD_TECH_STACK,
            roadmap=GOOD_ROADMAP,
        )
        result = runner.invoke(app, ["verify-memory", str(root), "--json"])
        payload = json.loads(result.output)
        assert payload["error_count"] == 0
        assert "issues" in payload
        assert "placeholder_files" in payload

    def test_missing_memory_dir_exits_non_zero(self, tmp_path):
        from doit_cli.main import app

        bare = tmp_path / "bare"
        bare.mkdir()
        result = runner.invoke(app, ["verify-memory", str(bare)])
        assert result.exit_code != 0


class TestMemorySchema:
    """Integration tests for `doit memory schema`."""

    def test_schema_prints_canonical_json(self):
        from doit_cli.main import app

        result = runner.invoke(app, ["memory", "schema", "--raw"])
        assert result.exit_code == 0
        payload = json.loads(result.output)
        assert payload["$schema"].startswith("https://json-schema.org/")
        required = payload["required"]
        assert {"id", "name", "kind", "phase", "icon", "tagline", "dependencies"} <= set(required)

    def test_schema_formatted_mode_still_valid_json(self):
        from doit_cli.main import app

        result = runner.invoke(app, ["memory", "schema"])
        assert result.exit_code == 0
        # Rich's print_json pretty-prints but the output is still parseable.
        # Strip ANSI colour codes just in case.
        import re

        cleaned = re.sub(r"\x1b\[[0-9;]*m", "", result.output)
        payload = json.loads(cleaned)
        assert payload["title"] == "doit constitution.md frontmatter"
