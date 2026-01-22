"""Unit tests for CleanupService."""

import pytest
from pathlib import Path

from doit_cli.models.cleanup_models import AnalysisResult, CleanupResult
from doit_cli.services.cleanup_service import CleanupService, TECH_SECTIONS


@pytest.fixture
def project_dir(tmp_path):
    """Create a temporary project directory with .doit/memory."""
    memory_dir = tmp_path / ".doit" / "memory"
    memory_dir.mkdir(parents=True)
    return tmp_path


@pytest.fixture
def service(project_dir):
    """Create a CleanupService instance."""
    return CleanupService(project_dir)


@pytest.fixture
def combined_constitution():
    """Constitution with tech sections (pre-split format)."""
    return """# My Project Constitution

## Purpose & Goals

### Project Purpose

A CLI tool for managing specifications.

### Success Criteria

- Reduce specification time by 50%
- Enable consistent task breakdown

## Core Principles

### I. Test-First

All code must have tests before implementation.

### II. Simplicity

Start simple, avoid over-engineering.

## Tech Stack

### Languages

Python 3.11+

### Frameworks

Typer (CLI), pytest (testing)

### Libraries

Rich (terminal output), Pydantic (validation)

## Infrastructure

### Hosting

Self-hosted

### Cloud Provider

None (local CLI tool)

### Database

None (file-based storage)

## Deployment

### CI/CD Pipeline

GitHub Actions

### Deployment Strategy

Manual release to PyPI

### Environments

Development (local)

## Quality Standards

All code MUST include tests.

## Governance

Constitution supersedes all other practices.

**Version**: 1.0.0 | **Ratified**: 2025-01-01 | **Last Amended**: 2025-01-15
"""


@pytest.fixture
def clean_constitution():
    """Constitution without tech sections (post-split format)."""
    return """# My Project Constitution

> **See also**: [Tech Stack](tech-stack.md) for languages, frameworks, and deployment details.

## Purpose & Goals

### Project Purpose

A CLI tool for managing specifications.

## Core Principles

### I. Test-First

All code must have tests before implementation.

## Quality Standards

All code MUST include tests.

## Governance

Constitution supersedes all other practices.

**Version**: 1.0.0 | **Ratified**: 2025-01-01 | **Last Amended**: 2025-01-15
"""


class TestCleanupServiceAnalyze:
    """Tests for CleanupService.analyze() method."""

    def test_analyze_identifies_tech_sections(self, service, project_dir, combined_constitution):
        """Test that analyze correctly identifies tech-stack sections."""
        constitution_path = project_dir / ".doit" / "memory" / "constitution.md"
        constitution_path.write_text(combined_constitution)

        result = service.analyze()

        assert result.has_tech_content
        assert "Tech Stack" in result.tech_sections
        assert "Infrastructure" in result.tech_sections
        assert "Deployment" in result.tech_sections

    def test_analyze_identifies_preserved_sections(self, service, project_dir, combined_constitution):
        """Test that analyze correctly identifies non-tech sections."""
        constitution_path = project_dir / ".doit" / "memory" / "constitution.md"
        constitution_path.write_text(combined_constitution)

        result = service.analyze()

        assert "Purpose & Goals" in result.preserved_sections
        assert "Core Principles" in result.preserved_sections
        assert "Quality Standards" in result.preserved_sections
        assert "Governance" in result.preserved_sections

    def test_analyze_no_tech_sections(self, service, project_dir, clean_constitution):
        """Test analyze with constitution that has no tech sections."""
        constitution_path = project_dir / ".doit" / "memory" / "constitution.md"
        constitution_path.write_text(clean_constitution)

        result = service.analyze()

        assert not result.has_tech_content
        assert len(result.tech_sections) == 0

    def test_analyze_missing_constitution(self, service):
        """Test analyze when constitution doesn't exist."""
        result = service.analyze()

        assert not result.has_tech_content
        assert len(result.tech_sections) == 0
        assert len(result.preserved_sections) == 0


class TestCleanupServiceBackup:
    """Tests for CleanupService.create_backup() method."""

    def test_create_backup_creates_file(self, service, project_dir, combined_constitution):
        """Test that create_backup creates a backup file."""
        constitution_path = project_dir / ".doit" / "memory" / "constitution.md"
        constitution_path.write_text(combined_constitution)

        backup_path = service.create_backup()

        assert backup_path is not None
        assert backup_path.exists()
        assert ".bak" in backup_path.suffix
        assert backup_path.read_text() == combined_constitution

    def test_create_backup_missing_file(self, service):
        """Test create_backup when constitution doesn't exist."""
        backup_path = service.create_backup()

        assert backup_path is None


class TestCleanupServiceCleanup:
    """Tests for CleanupService.cleanup() method."""

    def test_cleanup_creates_tech_stack(self, service, project_dir, combined_constitution):
        """Test that cleanup creates tech-stack.md."""
        constitution_path = project_dir / ".doit" / "memory" / "constitution.md"
        constitution_path.write_text(combined_constitution)

        result = service.cleanup()

        assert result.success
        assert result.tech_stack_created
        tech_stack_path = project_dir / ".doit" / "memory" / "tech-stack.md"
        assert tech_stack_path.exists()

    def test_cleanup_removes_tech_from_constitution(self, service, project_dir, combined_constitution):
        """Test that cleanup removes tech sections from constitution."""
        constitution_path = project_dir / ".doit" / "memory" / "constitution.md"
        constitution_path.write_text(combined_constitution)

        result = service.cleanup()

        updated_constitution = constitution_path.read_text()
        assert "## Tech Stack" not in updated_constitution
        assert "## Infrastructure" not in updated_constitution
        assert "## Deployment" not in updated_constitution
        # Preserved sections should remain
        assert "## Purpose & Goals" in updated_constitution
        assert "## Core Principles" in updated_constitution

    def test_cleanup_adds_cross_references(self, service, project_dir, combined_constitution):
        """Test that cleanup adds cross-references to both files."""
        constitution_path = project_dir / ".doit" / "memory" / "constitution.md"
        constitution_path.write_text(combined_constitution)

        service.cleanup()

        # Check constitution has cross-reference
        constitution_content = constitution_path.read_text()
        assert "tech-stack.md" in constitution_content
        assert "See also" in constitution_content

        # Check tech-stack has cross-reference
        tech_stack_path = project_dir / ".doit" / "memory" / "tech-stack.md"
        tech_stack_content = tech_stack_path.read_text()
        assert "constitution.md" in tech_stack_content
        assert "See also" in tech_stack_content

    def test_cleanup_creates_backup(self, service, project_dir, combined_constitution):
        """Test that cleanup creates a backup before modifying."""
        constitution_path = project_dir / ".doit" / "memory" / "constitution.md"
        constitution_path.write_text(combined_constitution)

        result = service.cleanup()

        assert result.backup_path is not None
        assert result.backup_path.exists()

    def test_cleanup_dry_run_no_changes(self, service, project_dir, combined_constitution):
        """Test that dry_run=True doesn't make changes."""
        constitution_path = project_dir / ".doit" / "memory" / "constitution.md"
        constitution_path.write_text(combined_constitution)

        result = service.cleanup(dry_run=True)

        assert result.extracted_sections  # Should identify sections
        assert not result.tech_stack_created  # But not create file
        tech_stack_path = project_dir / ".doit" / "memory" / "tech-stack.md"
        assert not tech_stack_path.exists()

    def test_cleanup_no_tech_sections(self, service, project_dir, clean_constitution):
        """Test cleanup when no tech sections to extract."""
        constitution_path = project_dir / ".doit" / "memory" / "constitution.md"
        constitution_path.write_text(clean_constitution)

        result = service.cleanup()

        assert result.success
        assert not result.tech_stack_created
        assert len(result.extracted_sections) == 0

    def test_cleanup_existing_tech_stack_without_merge(self, service, project_dir, combined_constitution):
        """Test cleanup fails when tech-stack.md exists and merge=False."""
        constitution_path = project_dir / ".doit" / "memory" / "constitution.md"
        constitution_path.write_text(combined_constitution)
        tech_stack_path = project_dir / ".doit" / "memory" / "tech-stack.md"
        tech_stack_path.write_text("# Existing Tech Stack\n")

        result = service.cleanup(merge_existing=False)

        assert not result.success
        assert "already exists" in result.error_message

    def test_cleanup_existing_tech_stack_with_merge(self, service, project_dir, combined_constitution):
        """Test cleanup succeeds when tech-stack.md exists and merge=True."""
        constitution_path = project_dir / ".doit" / "memory" / "constitution.md"
        constitution_path.write_text(combined_constitution)
        tech_stack_path = project_dir / ".doit" / "memory" / "tech-stack.md"
        tech_stack_path.write_text("# Existing Tech Stack\n\n## Custom Section\n\nCustom content\n")

        result = service.cleanup(merge_existing=True)

        assert result.success
        assert result.tech_stack_merged

    def test_cleanup_missing_constitution(self, service):
        """Test cleanup when constitution doesn't exist."""
        result = service.cleanup()

        assert not result.success
        assert "not found" in result.error_message


class TestCleanupServiceHelpers:
    """Tests for CleanupService helper methods."""

    def test_is_tech_section_exact_match(self, service, project_dir):
        """Test that exact header matches are detected."""
        # Create empty constitution so service initializes
        constitution_path = project_dir / ".doit" / "memory" / "constitution.md"
        constitution_path.write_text("# Test")

        for section_name in TECH_SECTIONS:
            assert service._is_tech_section(section_name, "") is True

    def test_is_tech_section_partial_match(self, service, project_dir):
        """Test that partial header matches work."""
        constitution_path = project_dir / ".doit" / "memory" / "constitution.md"
        constitution_path.write_text("# Test")

        # Headers containing the exact tech section names
        assert service._is_tech_section("Tech Stack Overview", "") is True
        assert service._is_tech_section("Infrastructure Setup", "") is True
        assert service._is_tech_section("Deployment Guide", "") is True
        # Headers that don't contain tech section names should not match
        assert service._is_tech_section("Technology Stack", "") is False  # "Tech Stack" not in "Technology Stack"
        assert service._is_tech_section("Infra", "") is False

    def test_is_tech_section_keyword_fallback(self, service, project_dir):
        """Test keyword-based detection as fallback."""
        constitution_path = project_dir / ".doit" / "memory" / "constitution.md"
        constitution_path.write_text("# Test")

        # Custom header with enough tech keywords
        content = "Using Python 3.11 language with FastAPI framework and PostgreSQL database"
        assert service._is_tech_section("Custom Section", content) is True

        # Not enough keywords
        content = "This is a governance section about rules"
        assert service._is_tech_section("Custom Section", content) is False

    def test_extract_project_name(self, service, project_dir):
        """Test project name extraction from header."""
        constitution_path = project_dir / ".doit" / "memory" / "constitution.md"
        constitution_path.write_text("# Test")

        # Standard format
        header = "# My Project Constitution\n\nSome intro text"
        assert service._extract_project_name(header) == "My Project"

        # Just H1 header
        header = "# Cool Tool\n"
        assert service._extract_project_name(header) == "Cool Tool"

        # No valid header
        header = "Some text without header"
        assert service._extract_project_name(header) == "[PROJECT_NAME]"
