"""Unit tests for spec file parser."""

import pytest
import tempfile
import shutil
from pathlib import Path
from doit_cli.utils.spec_parser import (
    SpecFrontmatter,
    parse_spec_file,
    update_spec_frontmatter,
    add_epic_reference,
    remove_epic_reference,
    get_epic_reference,
    write_spec_file
)


@pytest.fixture
def temp_spec_dir():
    """Create temporary directory for test spec files."""
    temp_dir = tempfile.mkdtemp()
    yield Path(temp_dir)
    shutil.rmtree(temp_dir)


@pytest.fixture
def sample_spec_content():
    """Sample spec file content with frontmatter."""
    return """---
Feature: "Test Feature"
Branch: "[001-test]"
Created: "2026-01-22"
Status: "Draft"
---

# Feature Specification: Test Feature

This is the body content.
"""


@pytest.fixture
def sample_spec_with_epic():
    """Sample spec file content with epic reference."""
    return """---
Feature: "Test Feature"
Branch: "[001-test]"
Created: "2026-01-22"
Status: "Draft"
Epic: "[#123](https://github.com/owner/repo/issues/123)"
Epic URL: "https://github.com/owner/repo/issues/123"
Priority: "P1"
---

# Feature Specification: Test Feature

This is the body content with epic link.
"""


class TestSpecFrontmatter:
    """Tests for SpecFrontmatter class."""

    def test_init_basic_fields(self):
        """Test initialization with basic fields."""
        data = {
            "Feature": "Test",
            "Branch": "[001-test]",
            "Created": "2026-01-22",
            "Status": "Draft"
        }
        fm = SpecFrontmatter(data)
        assert fm.feature_name == "Test"
        assert fm.branch_name == "[001-test]"
        assert fm.created_date == "2026-01-22"
        assert fm.status == "Draft"

    def test_extract_epic_number_from_markdown_link(self):
        """Test extracting epic number from markdown link format."""
        data = {"Epic": "[#123](https://github.com/owner/repo/issues/123)"}
        fm = SpecFrontmatter(data)
        assert fm.epic_number == 123

    def test_extract_epic_number_from_plain_number(self):
        """Test extracting epic number from plain number."""
        data = {"Epic": "#456"}
        fm = SpecFrontmatter(data)
        assert fm.epic_number == 456

        data2 = {"Epic": "789"}
        fm2 = SpecFrontmatter(data2)
        assert fm2.epic_number == 789

    def test_extract_epic_number_invalid(self):
        """Test handling of invalid epic number."""
        data = {"Epic": "not-a-number"}
        fm = SpecFrontmatter(data)
        assert fm.epic_number is None

    def test_to_yaml_dict_basic(self):
        """Test converting to YAML dictionary."""
        data = {
            "Feature": "Test",
            "Branch": "[001-test]",
            "Created": "2026-01-22",
            "Status": "Draft"
        }
        fm = SpecFrontmatter(data)
        yaml_dict = fm.to_yaml_dict()
        assert yaml_dict["Feature"] == "Test"
        assert yaml_dict["Status"] == "Draft"

    def test_to_yaml_dict_with_epic(self):
        """Test converting to YAML dictionary with epic."""
        data = {"Feature": "Test"}
        fm = SpecFrontmatter(data)
        fm.epic_number = 123
        fm.epic_url = "https://github.com/owner/repo/issues/123"
        fm.priority = "P1"

        yaml_dict = fm.to_yaml_dict()
        assert yaml_dict["Epic"] == "[#123](https://github.com/owner/repo/issues/123)"
        assert yaml_dict["Epic URL"] == "https://github.com/owner/repo/issues/123"
        assert yaml_dict["Priority"] == "P1"

    def test_to_yaml_dict_removes_epic_when_cleared(self):
        """Test that epic fields are removed when cleared."""
        data = {
            "Feature": "Test",
            "Epic": "[#123](url)",
            "Epic URL": "url"
        }
        fm = SpecFrontmatter(data)
        fm.epic_number = None
        fm.epic_url = None

        yaml_dict = fm.to_yaml_dict()
        assert "Epic" not in yaml_dict
        assert "Epic URL" not in yaml_dict


class TestParseSpecFile:
    """Tests for parse_spec_file function."""

    def test_parse_valid_spec(self, temp_spec_dir, sample_spec_content):
        """Test parsing a valid spec file."""
        spec_path = temp_spec_dir / "spec.md"
        spec_path.write_text(sample_spec_content)

        frontmatter, body = parse_spec_file(spec_path)
        assert frontmatter.feature_name == "Test Feature"
        assert frontmatter.branch_name == "[001-test]"
        assert "This is the body content" in body

    def test_parse_spec_with_epic(self, temp_spec_dir, sample_spec_with_epic):
        """Test parsing spec with epic reference."""
        spec_path = temp_spec_dir / "spec.md"
        spec_path.write_text(sample_spec_with_epic)

        frontmatter, body = parse_spec_file(spec_path)
        assert frontmatter.epic_number == 123
        assert frontmatter.epic_url == "https://github.com/owner/repo/issues/123"
        assert frontmatter.priority == "P1"

    def test_parse_missing_file(self, temp_spec_dir):
        """Test parsing non-existent file raises FileNotFoundError."""
        spec_path = temp_spec_dir / "missing.md"
        with pytest.raises(FileNotFoundError):
            parse_spec_file(spec_path)

    def test_parse_missing_frontmatter(self, temp_spec_dir):
        """Test parsing file without frontmatter raises ValueError."""
        spec_path = temp_spec_dir / "spec.md"
        spec_path.write_text("# Title\n\nContent without frontmatter")

        with pytest.raises(ValueError, match="missing frontmatter"):
            parse_spec_file(spec_path)

    def test_parse_malformed_yaml(self, temp_spec_dir):
        """Test parsing file with malformed YAML raises ValueError."""
        spec_path = temp_spec_dir / "spec.md"
        content = """---
Feature: [unclosed bracket
Branch: test
---

Content
"""
        spec_path.write_text(content)

        with pytest.raises(ValueError, match="Malformed frontmatter"):
            parse_spec_file(spec_path)


class TestUpdateSpecFrontmatter:
    """Tests for update_spec_frontmatter function."""

    def test_update_single_field(self, temp_spec_dir, sample_spec_content):
        """Test updating a single field."""
        spec_path = temp_spec_dir / "spec.md"
        spec_path.write_text(sample_spec_content)

        update_spec_frontmatter(spec_path, {"Status": "In Progress"})

        frontmatter, _ = parse_spec_file(spec_path)
        assert frontmatter.status == "In Progress"

    def test_update_multiple_fields(self, temp_spec_dir, sample_spec_content):
        """Test updating multiple fields."""
        spec_path = temp_spec_dir / "spec.md"
        spec_path.write_text(sample_spec_content)

        updates = {
            "Status": "Complete",
            "Priority": "P1"
        }
        update_spec_frontmatter(spec_path, updates)

        frontmatter, _ = parse_spec_file(spec_path)
        assert frontmatter.status == "Complete"
        assert frontmatter.priority == "P1"

    def test_update_preserves_body(self, temp_spec_dir, sample_spec_content):
        """Test that update preserves body content."""
        spec_path = temp_spec_dir / "spec.md"
        spec_path.write_text(sample_spec_content)

        update_spec_frontmatter(spec_path, {"Status": "Complete"})

        _, body = parse_spec_file(spec_path)
        assert "This is the body content" in body

    def test_atomic_update(self, temp_spec_dir, sample_spec_content):
        """Test that update is atomic (uses temp file + rename)."""
        spec_path = temp_spec_dir / "spec.md"
        spec_path.write_text(sample_spec_content)

        # Verify no .tmp files remain after update
        update_spec_frontmatter(spec_path, {"Status": "Complete"})

        tmp_files = list(temp_spec_dir.glob("*.tmp"))
        assert len(tmp_files) == 0


class TestAddEpicReference:
    """Tests for add_epic_reference function."""

    def test_add_epic_to_spec(self, temp_spec_dir, sample_spec_content):
        """Test adding epic reference to spec."""
        spec_path = temp_spec_dir / "spec.md"
        spec_path.write_text(sample_spec_content)

        add_epic_reference(
            spec_path,
            epic_number=123,
            epic_url="https://github.com/owner/repo/issues/123",
            priority="P1"
        )

        frontmatter, _ = parse_spec_file(spec_path)
        assert frontmatter.epic_number == 123
        assert frontmatter.epic_url == "https://github.com/owner/repo/issues/123"
        assert frontmatter.priority == "P1"

    def test_add_epic_invalid_number(self, temp_spec_dir, sample_spec_content):
        """Test adding epic with invalid number raises ValueError."""
        spec_path = temp_spec_dir / "spec.md"
        spec_path.write_text(sample_spec_content)

        with pytest.raises(ValueError, match="Invalid epic number"):
            add_epic_reference(spec_path, epic_number=-1, epic_url="url")

    def test_add_epic_invalid_url(self, temp_spec_dir, sample_spec_content):
        """Test adding epic with invalid URL raises ValueError."""
        spec_path = temp_spec_dir / "spec.md"
        spec_path.write_text(sample_spec_content)

        with pytest.raises(ValueError, match="Invalid epic URL"):
            add_epic_reference(spec_path, epic_number=123, epic_url="not-a-url")

    def test_add_epic_invalid_priority(self, temp_spec_dir, sample_spec_content):
        """Test adding epic with invalid priority raises ValueError."""
        spec_path = temp_spec_dir / "spec.md"
        spec_path.write_text(sample_spec_content)

        with pytest.raises(ValueError, match="Invalid priority"):
            add_epic_reference(
                spec_path,
                epic_number=123,
                epic_url="https://github.com/owner/repo/issues/123",
                priority="P5"
            )


class TestRemoveEpicReference:
    """Tests for remove_epic_reference function."""

    def test_remove_epic_from_spec(self, temp_spec_dir, sample_spec_with_epic):
        """Test removing epic reference from spec."""
        spec_path = temp_spec_dir / "spec.md"
        spec_path.write_text(sample_spec_with_epic)

        remove_epic_reference(spec_path)

        frontmatter, _ = parse_spec_file(spec_path)
        assert frontmatter.epic_number is None
        assert frontmatter.epic_url is None

    def test_remove_epic_preserves_other_fields(self, temp_spec_dir, sample_spec_with_epic):
        """Test that removing epic preserves other frontmatter fields."""
        spec_path = temp_spec_dir / "spec.md"
        spec_path.write_text(sample_spec_with_epic)

        remove_epic_reference(spec_path)

        frontmatter, _ = parse_spec_file(spec_path)
        assert frontmatter.feature_name == "Test Feature"
        assert frontmatter.status == "Draft"


class TestGetEpicReference:
    """Tests for get_epic_reference function."""

    def test_get_epic_when_present(self, temp_spec_dir, sample_spec_with_epic):
        """Test getting epic reference when present."""
        spec_path = temp_spec_dir / "spec.md"
        spec_path.write_text(sample_spec_with_epic)

        epic_ref = get_epic_reference(spec_path)
        assert epic_ref == (123, "https://github.com/owner/repo/issues/123")

    def test_get_epic_when_absent(self, temp_spec_dir, sample_spec_content):
        """Test getting epic reference when absent returns None."""
        spec_path = temp_spec_dir / "spec.md"
        spec_path.write_text(sample_spec_content)

        epic_ref = get_epic_reference(spec_path)
        assert epic_ref is None


class TestWriteSpecFile:
    """Tests for write_spec_file function."""

    def test_write_spec_creates_valid_file(self, temp_spec_dir):
        """Test writing spec file creates valid markdown."""
        spec_path = temp_spec_dir / "new_spec.md"

        data = {
            "Feature": "New Feature",
            "Branch": "[002-new]",
            "Created": "2026-01-22",
            "Status": "Draft"
        }
        frontmatter = SpecFrontmatter(data)
        body = "# New Feature\n\nContent here."

        write_spec_file(spec_path, frontmatter, body)

        # Verify file was created and is valid
        assert spec_path.exists()
        frontmatter_parsed, body_parsed = parse_spec_file(spec_path)
        assert frontmatter_parsed.feature_name == "New Feature"
        assert "Content here" in body_parsed

    def test_write_spec_overwrites_existing(self, temp_spec_dir, sample_spec_content):
        """Test writing spec file overwrites existing content."""
        spec_path = temp_spec_dir / "spec.md"
        spec_path.write_text(sample_spec_content)

        # Overwrite with new content
        data = {"Feature": "Updated", "Branch": "[003-updated]"}
        frontmatter = SpecFrontmatter(data)
        body = "Updated content."

        write_spec_file(spec_path, frontmatter, body)

        frontmatter_parsed, body_parsed = parse_spec_file(spec_path)
        assert frontmatter_parsed.feature_name == "Updated"
        assert "Updated content" in body_parsed
        assert "Test Feature" not in body_parsed
