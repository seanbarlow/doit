"""Cross-reference service for spec-task traceability."""

from pathlib import Path
from typing import Optional

from ..models.crossref_models import (
    CoverageReport,
    Requirement,
    RequirementCoverage,
    Task,
)
from .coverage_calculator import CoverageCalculator
from .requirement_parser import RequirementParser
from .task_parser import TaskParser


class CrossReferenceService:
    """Service for managing cross-references between specs and tasks.

    This service provides a unified API for:
    - Getting coverage reports
    - Finding tasks for requirements
    - Finding requirements for tasks
    - Locating requirement definitions
    """

    def __init__(
        self,
        project_root: Optional[Path] = None,
        specs_dir: str = "specs",
    ) -> None:
        """Initialize the service.

        Args:
            project_root: Root directory of the project. Defaults to cwd.
            specs_dir: Name of the specs directory.
        """
        self.project_root = Path(project_root) if project_root else Path.cwd()
        self.specs_dir = specs_dir
        self.requirement_parser = RequirementParser()
        self.task_parser = TaskParser()
        self.coverage_calculator = CoverageCalculator(
            self.requirement_parser,
            self.task_parser,
        )

    def get_coverage(
        self,
        spec_name: Optional[str] = None,
        spec_path: Optional[Path] = None,
    ) -> CoverageReport:
        """Get coverage report for a specification.

        Args:
            spec_name: Name of spec directory (e.g., "033-my-feature").
            spec_path: Direct path to spec.md. Overrides spec_name.

        Returns:
            CoverageReport for the specification.

        Raises:
            FileNotFoundError: If spec doesn't exist.
            ValueError: If neither spec_name nor spec_path provided.
        """
        if spec_path:
            return self.coverage_calculator.calculate(spec_path)

        if spec_name:
            feature_dir = self.project_root / self.specs_dir / spec_name
            return self.coverage_calculator.calculate_for_feature(feature_dir)

        raise ValueError("Either spec_name or spec_path must be provided")

    def get_tasks_for_requirement(
        self,
        requirement_id: str,
        spec_name: Optional[str] = None,
        tasks_path: Optional[Path] = None,
    ) -> list[Task]:
        """Get all tasks that implement a specific requirement.

        Args:
            requirement_id: The FR-XXX ID to search for.
            spec_name: Name of spec directory.
            tasks_path: Direct path to tasks.md.

        Returns:
            List of tasks that reference the requirement.

        Raises:
            ValueError: If neither spec_name nor tasks_path provided.
        """
        if tasks_path:
            return self.task_parser.get_tasks_for_requirement(
                requirement_id, tasks_path
            )

        if spec_name:
            feature_dir = self.project_root / self.specs_dir / spec_name
            tasks_file = feature_dir / "tasks.md"
            if not tasks_file.exists():
                return []
            return self.task_parser.get_tasks_for_requirement(
                requirement_id, tasks_file
            )

        raise ValueError("Either spec_name or tasks_path must be provided")

    def locate_requirement(
        self,
        requirement_id: str,
        spec_name: Optional[str] = None,
        spec_path: Optional[Path] = None,
    ) -> Optional[Requirement]:
        """Find a requirement definition in a spec.

        Args:
            requirement_id: The FR-XXX ID to find.
            spec_name: Name of spec directory.
            spec_path: Direct path to spec.md.

        Returns:
            Requirement if found, None otherwise.

        Raises:
            ValueError: If neither spec_name nor spec_path provided.
        """
        if spec_path:
            return self.requirement_parser.get_requirement(requirement_id, spec_path)

        if spec_name:
            feature_dir = self.project_root / self.specs_dir / spec_name
            spec_file = feature_dir / "spec.md"
            if not spec_file.exists():
                return None
            return self.requirement_parser.get_requirement(requirement_id, spec_file)

        raise ValueError("Either spec_name or spec_path must be provided")

    def get_requirement_coverage(
        self,
        requirement_id: str,
        spec_name: Optional[str] = None,
        spec_path: Optional[Path] = None,
    ) -> Optional[RequirementCoverage]:
        """Get coverage details for a specific requirement.

        Args:
            requirement_id: The FR-XXX ID to check.
            spec_name: Name of spec directory.
            spec_path: Direct path to spec.md.

        Returns:
            RequirementCoverage if requirement exists, None otherwise.
        """
        report = self.get_coverage(spec_name=spec_name, spec_path=spec_path)
        return report.get_requirement_coverage(requirement_id)

    def validate_references(
        self,
        spec_name: Optional[str] = None,
        spec_path: Optional[Path] = None,
    ) -> tuple[list[str], list[tuple[Task, str]]]:
        """Validate cross-references and find issues.

        Args:
            spec_name: Name of spec directory.
            spec_path: Direct path to spec.md.

        Returns:
            Tuple of (uncovered_requirement_ids, orphaned_references).
            orphaned_references is list of (task, invalid_requirement_id) tuples.
        """
        report = self.get_coverage(spec_name=spec_name, spec_path=spec_path)

        # Find uncovered requirements
        uncovered = [r.id for r in report.get_uncovered_requirements()]

        return uncovered, report.orphaned_references

    def get_all_requirements(
        self,
        spec_name: Optional[str] = None,
        spec_path: Optional[Path] = None,
    ) -> list[Requirement]:
        """Get all requirements from a spec.

        Args:
            spec_name: Name of spec directory.
            spec_path: Direct path to spec.md.

        Returns:
            List of all requirements in the spec.

        Raises:
            ValueError: If neither spec_name nor spec_path provided.
        """
        if spec_path:
            return self.requirement_parser.parse(spec_path)

        if spec_name:
            feature_dir = self.project_root / self.specs_dir / spec_name
            spec_file = feature_dir / "spec.md"
            return self.requirement_parser.parse(spec_file)

        raise ValueError("Either spec_name or spec_path must be provided")

    def get_all_tasks(
        self,
        spec_name: Optional[str] = None,
        tasks_path: Optional[Path] = None,
    ) -> list[Task]:
        """Get all tasks from a tasks file.

        Args:
            spec_name: Name of spec directory.
            tasks_path: Direct path to tasks.md.

        Returns:
            List of all tasks. Empty list if tasks.md doesn't exist.

        Raises:
            ValueError: If neither spec_name nor tasks_path provided.
        """
        if tasks_path:
            if not tasks_path.exists():
                return []
            return self.task_parser.parse(tasks_path)

        if spec_name:
            feature_dir = self.project_root / self.specs_dir / spec_name
            tasks_file = feature_dir / "tasks.md"
            if not tasks_file.exists():
                return []
            return self.task_parser.parse(tasks_file)

        raise ValueError("Either spec_name or tasks_path must be provided")
