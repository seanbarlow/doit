"""Tests for CoverageCalculator service."""

import pytest
from pathlib import Path

from doit_cli.services.coverage_calculator import CoverageCalculator
from doit_cli.models.crossref_models import CoverageStatus


class TestCoverageCalculator:
    """Tests for CoverageCalculator."""

    def test_calculate_full_coverage(self, tmp_path: Path) -> None:
        """Test calculating coverage when all requirements have tasks."""
        spec_content = """# Spec
- **FR-001**: First requirement
- **FR-002**: Second requirement
"""
        tasks_content = """# Tasks
- [ ] Task A [FR-001]
- [ ] Task B [FR-002]
"""
        spec_file = tmp_path / "spec.md"
        tasks_file = tmp_path / "tasks.md"
        spec_file.write_text(spec_content)
        tasks_file.write_text(tasks_content)

        calculator = CoverageCalculator()
        report = calculator.calculate(spec_file, tasks_file)

        assert report.total_count == 2
        assert report.covered_count == 2
        assert report.coverage_percent == 100.0
        assert report.is_fully_covered

    def test_calculate_partial_coverage(self, tmp_path: Path) -> None:
        """Test calculating coverage when some requirements are uncovered."""
        spec_content = """# Spec
- **FR-001**: First requirement
- **FR-002**: Second requirement
- **FR-003**: Third requirement
"""
        tasks_content = """# Tasks
- [ ] Task A [FR-001]
"""
        spec_file = tmp_path / "spec.md"
        tasks_file = tmp_path / "tasks.md"
        spec_file.write_text(spec_content)
        tasks_file.write_text(tasks_content)

        calculator = CoverageCalculator()
        report = calculator.calculate(spec_file, tasks_file)

        assert report.total_count == 3
        assert report.covered_count == 1
        assert report.uncovered_count == 2
        assert 33 < report.coverage_percent < 34  # ~33.3%
        assert not report.is_fully_covered

    def test_calculate_no_tasks_file(self, tmp_path: Path) -> None:
        """Test calculating coverage when tasks.md doesn't exist."""
        spec_content = """# Spec
- **FR-001**: First requirement
"""
        spec_file = tmp_path / "spec.md"
        spec_file.write_text(spec_content)

        calculator = CoverageCalculator()
        report = calculator.calculate(spec_file)

        assert report.total_count == 1
        assert report.covered_count == 0
        assert report.coverage_percent == 0.0

    def test_calculate_empty_spec(self, tmp_path: Path) -> None:
        """Test calculating coverage for spec with no requirements."""
        spec_file = tmp_path / "spec.md"
        tasks_file = tmp_path / "tasks.md"
        spec_file.write_text("# Empty Spec")
        tasks_file.write_text("- [ ] Task")

        calculator = CoverageCalculator()
        report = calculator.calculate(spec_file, tasks_file)

        assert report.total_count == 0
        assert report.coverage_percent == 100.0  # No requirements = 100%

    def test_calculate_orphaned_references(self, tmp_path: Path) -> None:
        """Test detecting orphaned task references."""
        spec_content = """# Spec
- **FR-001**: First requirement
"""
        tasks_content = """# Tasks
- [ ] Task A [FR-001]
- [ ] Task B [FR-999]
"""
        spec_file = tmp_path / "spec.md"
        tasks_file = tmp_path / "tasks.md"
        spec_file.write_text(spec_content)
        tasks_file.write_text(tasks_content)

        calculator = CoverageCalculator()
        report = calculator.calculate(spec_file, tasks_file)

        assert len(report.orphaned_references) == 1
        task, ref_id = report.orphaned_references[0]
        assert ref_id == "FR-999"

    def test_calculate_multiple_tasks_per_requirement(self, tmp_path: Path) -> None:
        """Test when multiple tasks implement the same requirement."""
        spec_content = """# Spec
- **FR-001**: Requirement
"""
        tasks_content = """# Tasks
- [ ] Task A [FR-001]
- [ ] Task B [FR-001]
- [x] Task C [FR-001]
"""
        spec_file = tmp_path / "spec.md"
        tasks_file = tmp_path / "tasks.md"
        spec_file.write_text(spec_content)
        tasks_file.write_text(tasks_content)

        calculator = CoverageCalculator()
        report = calculator.calculate(spec_file, tasks_file)

        assert report.total_count == 1
        assert report.covered_count == 1
        rc = report.requirements[0]
        assert rc.task_count == 3
        assert rc.completed_count == 1

    def test_calculate_coverage_status(self, tmp_path: Path) -> None:
        """Test coverage status determination."""
        spec_content = """# Spec
- **FR-001**: Covered
- **FR-002**: Partial
- **FR-003**: Uncovered
"""
        tasks_content = """# Tasks
- [x] Task A [FR-001]
- [ ] Task B [FR-002]
"""
        spec_file = tmp_path / "spec.md"
        tasks_file = tmp_path / "tasks.md"
        spec_file.write_text(spec_content)
        tasks_file.write_text(tasks_content)

        calculator = CoverageCalculator()
        report = calculator.calculate(spec_file, tasks_file)

        # FR-001 has completed task -> COVERED
        rc1 = report.get_requirement_coverage("FR-001")
        assert rc1.status == CoverageStatus.COVERED

        # FR-002 has incomplete task -> PARTIAL
        rc2 = report.get_requirement_coverage("FR-002")
        assert rc2.status == CoverageStatus.PARTIAL

        # FR-003 has no tasks -> UNCOVERED
        rc3 = report.get_requirement_coverage("FR-003")
        assert rc3.status == CoverageStatus.UNCOVERED

    def test_calculate_get_uncovered_requirements(self, tmp_path: Path) -> None:
        """Test getting list of uncovered requirements."""
        spec_content = """# Spec
- **FR-001**: Covered
- **FR-002**: Uncovered
- **FR-003**: Uncovered
"""
        tasks_content = """# Tasks
- [ ] Task A [FR-001]
"""
        spec_file = tmp_path / "spec.md"
        tasks_file = tmp_path / "tasks.md"
        spec_file.write_text(spec_content)
        tasks_file.write_text(tasks_content)

        calculator = CoverageCalculator()
        report = calculator.calculate(spec_file, tasks_file)

        uncovered = report.get_uncovered_requirements()
        assert len(uncovered) == 2
        assert {r.id for r in uncovered} == {"FR-002", "FR-003"}

    def test_calculate_for_feature(self, tmp_path: Path) -> None:
        """Test calculating coverage for a feature directory."""
        feature_dir = tmp_path / "033-test-feature"
        feature_dir.mkdir()

        spec_content = """- **FR-001**: Requirement"""
        tasks_content = """- [ ] Task [FR-001]"""

        (feature_dir / "spec.md").write_text(spec_content)
        (feature_dir / "tasks.md").write_text(tasks_content)

        calculator = CoverageCalculator()
        report = calculator.calculate_for_feature(feature_dir)

        assert report.total_count == 1
        assert report.covered_count == 1

    def test_calculate_spec_not_found(self, tmp_path: Path) -> None:
        """Test error when spec.md doesn't exist."""
        calculator = CoverageCalculator()

        with pytest.raises(FileNotFoundError):
            calculator.calculate(tmp_path / "nonexistent.md")
