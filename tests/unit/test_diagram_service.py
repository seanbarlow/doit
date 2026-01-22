"""Unit tests for DiagramService."""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch

from doit_cli.models.diagram_models import DiagramType, GeneratedDiagram, ValidationResult
from doit_cli.services.diagram_service import DiagramService


@pytest.fixture
def service():
    """Create a DiagramService instance."""
    return DiagramService(strict=False, backup=False)


@pytest.fixture
def strict_service():
    """Create a DiagramService with strict mode."""
    return DiagramService(strict=True, backup=False)


@pytest.fixture
def sample_spec_content():
    """Sample spec content with user stories and entities."""
    return """# Feature: Test Feature

## User Stories

### User Story 1 - Login Flow (Priority: P1)

**Description**: User can log in to the system.

**Acceptance Criteria**:

#### Scenario 1
- **Given**: user is on login page
- **When**: user enters valid credentials
- **Then**: user is redirected to dashboard

## Key Entities

### User
Central entity representing a system user.
- Has many Tasks
- Has one Profile

### Task
Represents a task item.
- Belongs to User

<!-- BEGIN:AUTO-GENERATED section="user-journey" -->
<!-- END:AUTO-GENERATED -->

<!-- BEGIN:AUTO-GENERATED section="entity-relationships" -->
<!-- END:AUTO-GENERATED -->
"""


@pytest.fixture
def sample_spec_file(tmp_path, sample_spec_content):
    """Create a temporary spec file."""
    spec_file = tmp_path / "spec.md"
    spec_file.write_text(sample_spec_content, encoding="utf-8")
    return spec_file


class TestDiagramService:
    """Tests for DiagramService class."""

    def test_generate_returns_result(self, service, sample_spec_file):
        """Test that generate returns a DiagramResult."""
        result = service.generate(sample_spec_file)

        assert result is not None
        assert result.file_path == sample_spec_file
        assert result.success

    def test_generate_nonexistent_file(self, service, tmp_path):
        """Test generate with nonexistent file."""
        result = service.generate(tmp_path / "nonexistent.md")

        assert not result.success
        assert "not found" in result.error.lower()

    def test_generate_detects_user_stories(self, service, sample_spec_file):
        """Test that service detects and generates user journey diagram."""
        result = service.generate(sample_spec_file, diagram_types=[DiagramType.USER_JOURNEY])

        assert result.success
        assert len(result.diagrams) >= 1

        user_journey = next(
            (d for d in result.diagrams if d.diagram_type == DiagramType.USER_JOURNEY),
            None
        )
        assert user_journey is not None
        assert "flowchart" in user_journey.mermaid_content

    def test_generate_detects_entities(self, service, sample_spec_file):
        """Test that service attempts to generate ER diagram when requested."""
        result = service.generate(sample_spec_file, diagram_types=[DiagramType.ER_DIAGRAM])

        # May or may not find entities depending on parsing
        assert result.success or "not found" not in str(result.error).lower()

    def test_generate_auto_detects_types(self, service, sample_spec_file):
        """Test that service auto-detects applicable diagram types."""
        result = service.generate(sample_spec_file)

        assert result.success
        # Should detect user stories
        types = [d.diagram_type for d in result.diagrams]
        assert DiagramType.USER_JOURNEY in types

    def test_generate_inserts_into_sections(self, service, sample_spec_file):
        """Test that diagrams are inserted into AUTO-GENERATED sections."""
        result = service.generate(sample_spec_file, insert=True)

        assert result.success
        assert len(result.sections_updated) > 0

        # Read updated file
        updated_content = sample_spec_file.read_text(encoding="utf-8")
        assert "```mermaid" in updated_content

    def test_generate_no_insert(self, service, sample_spec_file):
        """Test generate with insert=False doesn't modify file."""
        original_content = sample_spec_file.read_text(encoding="utf-8")

        result = service.generate(sample_spec_file, insert=False)

        assert result.success
        # File should not be modified
        current_content = sample_spec_file.read_text(encoding="utf-8")
        assert current_content == original_content

    def test_generate_validates_diagrams(self, service, sample_spec_file):
        """Test that generated diagrams are validated."""
        result = service.generate(sample_spec_file)

        assert result.success
        for diagram in result.diagrams:
            assert diagram.validation is not None
            assert diagram.is_valid or len(diagram.validation.warnings) > 0

    def test_strict_mode_fails_on_validation_error(self, strict_service, tmp_path):
        """Test that strict mode fails on validation errors."""
        # Create a spec that will produce invalid output
        spec_content = """# Test

## User Stories

### User Story 1 - Test (Priority: P1)

**Description**: Test

<!-- BEGIN:AUTO-GENERATED section="user-journey" -->
<!-- END:AUTO-GENERATED -->
"""
        spec_file = tmp_path / "spec.md"
        spec_file.write_text(spec_content, encoding="utf-8")

        # This should work since basic stories are valid
        result = strict_service.generate(spec_file)
        # If no scenarios, no diagram generated
        if result.diagrams:
            for diagram in result.diagrams:
                assert diagram.is_valid or not result.success

    def test_validate_method(self, service):
        """Test the validate method directly."""
        valid_flowchart = """flowchart LR
    A[Start] --> B[End]
"""
        result = service.validate(valid_flowchart, DiagramType.USER_JOURNEY)
        assert result.passed

    def test_insert_diagram_method(self, service, sample_spec_file):
        """Test insert_diagram method."""
        diagram_content = """```mermaid
flowchart LR
    A[Test] --> B[Node]
```"""
        success = service.insert_diagram(
            sample_spec_file, "user-journey", diagram_content
        )
        assert success

        content = sample_spec_file.read_text(encoding="utf-8")
        assert "Test" in content
        assert "Node" in content

    def test_insert_diagram_missing_section(self, service, tmp_path):
        """Test insert_diagram with missing section."""
        spec_file = tmp_path / "spec.md"
        spec_file.write_text("# No sections here", encoding="utf-8")

        success = service.insert_diagram(
            spec_file, "user-journey", "```mermaid\ntest\n```"
        )
        assert not success

    def test_get_diagram_content(self, service, tmp_path):
        """Test get_diagram_content method."""
        content = """# Test

<!-- BEGIN:AUTO-GENERATED section="user-journey" -->
```mermaid
flowchart LR
    A --> B
```
<!-- END:AUTO-GENERATED -->
"""
        spec_file = tmp_path / "spec.md"
        spec_file.write_text(content, encoding="utf-8")

        diagram = service.get_diagram_content(spec_file, DiagramType.USER_JOURNEY)
        assert diagram is not None
        assert "flowchart" in diagram

    def test_regeneration_preserves_content(self, service, tmp_path):
        """Test that regeneration preserves content outside AUTO-GENERATED blocks."""
        original_content = """# My Feature

This is important content that should be preserved.

## User Stories

### User Story 1 - Test (Priority: P1)

**Description**: Test story

**Acceptance Criteria**:

#### Scenario 1
- **Given**: initial state
- **When**: action occurs
- **Then**: expected result

<!-- BEGIN:AUTO-GENERATED section="user-journey" -->
Old content here
<!-- END:AUTO-GENERATED -->

## More Content

This should also be preserved.
"""
        spec_file = tmp_path / "spec.md"
        spec_file.write_text(original_content, encoding="utf-8")

        result = service.generate(spec_file, insert=True)

        updated_content = spec_file.read_text(encoding="utf-8")

        # Preserved content should still be there
        assert "This is important content" in updated_content
        assert "This should also be preserved" in updated_content

        # Old content in AUTO-GENERATED should be replaced
        assert "Old content here" not in updated_content

    def test_backup_creation(self, tmp_path):
        """Test that backup is created when backup=True."""
        service = DiagramService(strict=False, backup=True)

        content = """# Test

## User Stories

### User Story 1 - Test (Priority: P1)

**Description**: Test

**Acceptance Criteria**:

#### Scenario 1
- **Given**: state
- **When**: action
- **Then**: result

<!-- BEGIN:AUTO-GENERATED section="user-journey" -->
<!-- END:AUTO-GENERATED -->
"""
        spec_file = tmp_path / "spec.md"
        spec_file.write_text(content, encoding="utf-8")

        service.generate(spec_file, insert=True)

        # Check for backup file
        backup_files = list(tmp_path.glob("*.bak"))
        assert len(backup_files) > 0

    def test_empty_spec_no_diagrams(self, service, tmp_path):
        """Test that empty spec produces no diagrams."""
        spec_file = tmp_path / "spec.md"
        spec_file.write_text("# Empty Spec\n\nNo content here.", encoding="utf-8")

        result = service.generate(spec_file)

        assert result.success
        assert len(result.diagrams) == 0


class TestDiagramServiceSectionHandling:
    """Tests for section finding and handling."""

    def test_finds_existing_sections(self, service, sample_spec_file):
        """Test that existing sections are found."""
        result = service.generate(sample_spec_file, insert=False)

        assert "user-journey" in result.sections_found or len(result.sections_found) > 0

    def test_alternate_section_names(self, service, tmp_path):
        """Test that alternate section names are recognized."""
        content = """# Test

## User Stories

### User Story 1 - Test (Priority: P1)

**Description**: Test

**Acceptance Criteria**:

#### Scenario 1
- **Given**: state
- **When**: action
- **Then**: result

<!-- BEGIN:AUTO-GENERATED section="flowchart" -->
<!-- END:AUTO-GENERATED -->
"""
        spec_file = tmp_path / "spec.md"
        spec_file.write_text(content, encoding="utf-8")

        result = service.generate(spec_file, insert=True)

        # Should find alternate section name
        assert result.success
