"""Tests for CrossReferenceService."""

import pytest
from pathlib import Path

from doit_cli.services.crossref_service import CrossReferenceService


class TestCrossReferenceService:
    """Tests for CrossReferenceService."""

    @pytest.fixture
    def feature_dir(self, tmp_path: Path) -> Path:
        """Create a feature directory structure for testing."""
        specs_dir = tmp_path / "specs"
        feature = specs_dir / "033-test-feature"
        feature.mkdir(parents=True)

        spec_content = """# Test Feature

## Requirements

- **FR-001**: First requirement
- **FR-002**: Second requirement
- **FR-003**: Third requirement
"""
        tasks_content = """# Tasks

- [ ] Task A [FR-001]
- [x] Task B [FR-001, FR-002]
- [ ] Task C [FR-002]
"""
        (feature / "spec.md").write_text(spec_content)
        (feature / "tasks.md").write_text(tasks_content)

        return tmp_path

    def test_get_coverage_by_spec_name(self, feature_dir: Path) -> None:
        """Test getting coverage by spec name."""
        service = CrossReferenceService(project_root=feature_dir)
        report = service.get_coverage(spec_name="033-test-feature")

        assert report.total_count == 3
        assert report.covered_count == 2  # FR-001, FR-002
        assert report.uncovered_count == 1  # FR-003

    def test_get_coverage_by_spec_path(self, feature_dir: Path) -> None:
        """Test getting coverage by spec path."""
        spec_path = feature_dir / "specs" / "033-test-feature" / "spec.md"
        service = CrossReferenceService(project_root=feature_dir)
        report = service.get_coverage(spec_path=spec_path)

        assert report.total_count == 3

    def test_get_coverage_no_args_raises(self, feature_dir: Path) -> None:
        """Test that ValueError is raised when no spec specified."""
        service = CrossReferenceService(project_root=feature_dir)

        with pytest.raises(ValueError, match="Either spec_name or spec_path"):
            service.get_coverage()

    def test_get_tasks_for_requirement(self, feature_dir: Path) -> None:
        """Test getting tasks that implement a requirement."""
        service = CrossReferenceService(project_root=feature_dir)
        tasks = service.get_tasks_for_requirement("FR-001", spec_name="033-test-feature")

        assert len(tasks) == 2
        assert all("FR-001" in t.requirement_ids for t in tasks)

    def test_get_tasks_for_requirement_not_found(self, feature_dir: Path) -> None:
        """Test getting tasks for requirement with no implementations."""
        service = CrossReferenceService(project_root=feature_dir)
        tasks = service.get_tasks_for_requirement("FR-003", spec_name="033-test-feature")

        assert len(tasks) == 0

    def test_locate_requirement(self, feature_dir: Path) -> None:
        """Test finding a requirement definition."""
        service = CrossReferenceService(project_root=feature_dir)
        req = service.locate_requirement("FR-002", spec_name="033-test-feature")

        assert req is not None
        assert req.id == "FR-002"
        assert "Second" in req.description

    def test_locate_requirement_not_found(self, feature_dir: Path) -> None:
        """Test finding a non-existent requirement."""
        service = CrossReferenceService(project_root=feature_dir)
        req = service.locate_requirement("FR-999", spec_name="033-test-feature")

        assert req is None

    def test_get_requirement_coverage(self, feature_dir: Path) -> None:
        """Test getting coverage for a specific requirement."""
        service = CrossReferenceService(project_root=feature_dir)
        rc = service.get_requirement_coverage("FR-001", spec_name="033-test-feature")

        assert rc is not None
        assert rc.task_count == 2
        assert rc.is_covered

    def test_validate_references(self, feature_dir: Path) -> None:
        """Test validating cross-references."""
        # Add a task with orphaned reference
        tasks_file = feature_dir / "specs" / "033-test-feature" / "tasks.md"
        content = tasks_file.read_text()
        content += "\n- [ ] Bad task [FR-999]"
        tasks_file.write_text(content)

        service = CrossReferenceService(project_root=feature_dir)
        uncovered, orphaned = service.validate_references(spec_name="033-test-feature")

        assert "FR-003" in uncovered  # Has no tasks
        assert len(orphaned) == 1  # FR-999 doesn't exist
        assert orphaned[0][1] == "FR-999"

    def test_get_all_requirements(self, feature_dir: Path) -> None:
        """Test getting all requirements from spec."""
        service = CrossReferenceService(project_root=feature_dir)
        requirements = service.get_all_requirements(spec_name="033-test-feature")

        assert len(requirements) == 3
        assert [r.id for r in requirements] == ["FR-001", "FR-002", "FR-003"]

    def test_get_all_tasks(self, feature_dir: Path) -> None:
        """Test getting all tasks from tasks file."""
        service = CrossReferenceService(project_root=feature_dir)
        tasks = service.get_all_tasks(spec_name="033-test-feature")

        assert len(tasks) == 3
        assert sum(1 for t in tasks if t.completed) == 1

    def test_get_all_tasks_no_tasks_file(self, feature_dir: Path) -> None:
        """Test getting tasks when tasks.md doesn't exist."""
        # Create spec without tasks
        new_feature = feature_dir / "specs" / "034-no-tasks"
        new_feature.mkdir()
        (new_feature / "spec.md").write_text("- **FR-001**: Requirement")

        service = CrossReferenceService(project_root=feature_dir)
        tasks = service.get_all_tasks(spec_name="034-no-tasks")

        assert tasks == []

    def test_custom_specs_dir(self, tmp_path: Path) -> None:
        """Test using custom specs directory name."""
        custom_dir = tmp_path / "specifications"
        feature = custom_dir / "test"
        feature.mkdir(parents=True)
        (feature / "spec.md").write_text("- **FR-001**: Requirement")
        (feature / "tasks.md").write_text("- [ ] Task [FR-001]")

        service = CrossReferenceService(project_root=tmp_path, specs_dir="specifications")
        report = service.get_coverage(spec_name="test")

        assert report.total_count == 1
