"""Tests for RequirementParser service."""

import pytest
from pathlib import Path

from doit_cli.services.requirement_parser import RequirementParser


class TestRequirementParser:
    """Tests for RequirementParser."""

    def test_parse_single_requirement(self, tmp_path: Path) -> None:
        """Test parsing a spec with a single requirement."""
        spec_content = """# Feature Spec

## Requirements

- **FR-001**: System MUST support cross-reference syntax
"""
        spec_file = tmp_path / "spec.md"
        spec_file.write_text(spec_content)

        parser = RequirementParser()
        requirements = parser.parse(spec_file)

        assert len(requirements) == 1
        assert requirements[0].id == "FR-001"
        assert "cross-reference syntax" in requirements[0].description
        assert requirements[0].line_number == 5

    def test_parse_multiple_requirements(self, tmp_path: Path) -> None:
        """Test parsing a spec with multiple requirements."""
        spec_content = """# Feature Spec

## Requirements

- **FR-001**: First requirement description
- **FR-002**: Second requirement description
- **FR-003**: Third requirement description
"""
        spec_file = tmp_path / "spec.md"
        spec_file.write_text(spec_content)

        parser = RequirementParser()
        requirements = parser.parse(spec_file)

        assert len(requirements) == 3
        assert [r.id for r in requirements] == ["FR-001", "FR-002", "FR-003"]

    def test_parse_requirements_sorted_by_id(self, tmp_path: Path) -> None:
        """Test that requirements are sorted by ID."""
        spec_content = """# Feature Spec

- **FR-003**: Third
- **FR-001**: First
- **FR-002**: Second
"""
        spec_file = tmp_path / "spec.md"
        spec_file.write_text(spec_content)

        parser = RequirementParser()
        requirements = parser.parse(spec_file)

        assert [r.id for r in requirements] == ["FR-001", "FR-002", "FR-003"]

    def test_parse_with_indentation(self, tmp_path: Path) -> None:
        """Test parsing requirements with various indentation."""
        spec_content = """# Feature Spec

- **FR-001**: No indent
  - **FR-002**: Two space indent
    - **FR-003**: Four space indent
"""
        spec_file = tmp_path / "spec.md"
        spec_file.write_text(spec_content)

        parser = RequirementParser()
        requirements = parser.parse(spec_file)

        assert len(requirements) == 3

    def test_parse_ignores_non_requirement_lines(self, tmp_path: Path) -> None:
        """Test that non-requirement lines are ignored."""
        spec_content = """# Feature Spec

Some regular text.

- **FR-001**: Valid requirement
- Not a requirement
- **Bold text**: Not FR format
- FR-002: Missing asterisks
"""
        spec_file = tmp_path / "spec.md"
        spec_file.write_text(spec_content)

        parser = RequirementParser()
        requirements = parser.parse(spec_file)

        assert len(requirements) == 1
        assert requirements[0].id == "FR-001"

    def test_parse_captures_full_description(self, tmp_path: Path) -> None:
        """Test that full description is captured including special chars."""
        spec_content = """# Feature Spec

- **FR-001**: System MUST support `[FR-XXX]` syntax in task descriptions
"""
        spec_file = tmp_path / "spec.md"
        spec_file.write_text(spec_content)

        parser = RequirementParser()
        requirements = parser.parse(spec_file)

        assert "`[FR-XXX]`" in requirements[0].description

    def test_parse_empty_file(self, tmp_path: Path) -> None:
        """Test parsing an empty spec file."""
        spec_file = tmp_path / "spec.md"
        spec_file.write_text("")

        parser = RequirementParser()
        requirements = parser.parse(spec_file)

        assert len(requirements) == 0

    def test_parse_file_not_found(self, tmp_path: Path) -> None:
        """Test that FileNotFoundError is raised for missing file."""
        parser = RequirementParser()

        with pytest.raises(FileNotFoundError):
            parser.parse(tmp_path / "nonexistent.md")

    def test_parse_no_path_provided(self) -> None:
        """Test that ValueError is raised when no path provided."""
        parser = RequirementParser()

        with pytest.raises(ValueError, match="No spec path provided"):
            parser.parse()

    def test_get_requirement_by_id(self, tmp_path: Path) -> None:
        """Test getting a specific requirement by ID."""
        spec_content = """# Feature Spec

- **FR-001**: First requirement
- **FR-002**: Second requirement
"""
        spec_file = tmp_path / "spec.md"
        spec_file.write_text(spec_content)

        parser = RequirementParser()
        req = parser.get_requirement("FR-002", spec_file)

        assert req is not None
        assert req.id == "FR-002"
        assert "Second" in req.description

    def test_get_requirement_not_found(self, tmp_path: Path) -> None:
        """Test getting a non-existent requirement."""
        spec_content = """- **FR-001**: First requirement"""
        spec_file = tmp_path / "spec.md"
        spec_file.write_text(spec_content)

        parser = RequirementParser()
        req = parser.get_requirement("FR-999", spec_file)

        assert req is None

    def test_get_requirement_ids(self, tmp_path: Path) -> None:
        """Test getting list of all requirement IDs."""
        spec_content = """# Feature Spec

- **FR-001**: First
- **FR-002**: Second
- **FR-003**: Third
"""
        spec_file = tmp_path / "spec.md"
        spec_file.write_text(spec_content)

        parser = RequirementParser()
        ids = parser.get_requirement_ids(spec_file)

        assert ids == ["FR-001", "FR-002", "FR-003"]

    def test_constructor_with_path(self, tmp_path: Path) -> None:
        """Test using path from constructor."""
        spec_content = """- **FR-001**: Requirement"""
        spec_file = tmp_path / "spec.md"
        spec_file.write_text(spec_content)

        parser = RequirementParser(spec_file)
        requirements = parser.parse()

        assert len(requirements) == 1

    def test_parse_content_directly(self) -> None:
        """Test parsing content string directly."""
        content = """- **FR-001**: First requirement
- **FR-002**: Second requirement"""

        parser = RequirementParser()
        requirements = parser.parse_content(content, "/path/to/spec.md")

        assert len(requirements) == 2
        assert requirements[0].spec_path == "/path/to/spec.md"
