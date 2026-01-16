"""Calculator for requirement coverage metrics."""

from pathlib import Path
from typing import Optional

from ..models.crossref_models import (
    CoverageReport,
    Requirement,
    RequirementCoverage,
    Task,
)
from .requirement_parser import RequirementParser
from .task_parser import TaskParser


class CoverageCalculator:
    """Calculates coverage metrics for requirements.

    This service matches requirements from spec.md to tasks from tasks.md
    and computes coverage percentages and identifies gaps.
    """

    def __init__(
        self,
        requirement_parser: Optional[RequirementParser] = None,
        task_parser: Optional[TaskParser] = None,
    ) -> None:
        """Initialize calculator with optional parsers.

        Args:
            requirement_parser: Parser for spec.md. Created if not provided.
            task_parser: Parser for tasks.md. Created if not provided.
        """
        self.requirement_parser = requirement_parser or RequirementParser()
        self.task_parser = task_parser or TaskParser()

    def calculate(
        self,
        spec_path: Path,
        tasks_path: Optional[Path] = None,
    ) -> CoverageReport:
        """Calculate coverage for a specification.

        Args:
            spec_path: Path to spec.md file.
            tasks_path: Path to tasks.md file. Defaults to tasks.md in same directory.

        Returns:
            CoverageReport with all coverage metrics.

        Raises:
            FileNotFoundError: If spec.md doesn't exist.
        """
        spec_path = Path(spec_path)
        if not spec_path.exists():
            raise FileNotFoundError(f"Spec file not found: {spec_path}")

        # Default tasks path to same directory as spec
        if tasks_path is None:
            tasks_path = spec_path.parent / "tasks.md"

        # Parse requirements from spec
        requirements = self.requirement_parser.parse(spec_path)

        # Parse tasks (empty list if tasks.md doesn't exist)
        tasks: list[Task] = []
        if tasks_path.exists():
            tasks = self.task_parser.parse(tasks_path)

        # Build coverage data
        return self._build_coverage_report(
            spec_path=str(spec_path),
            requirements=requirements,
            tasks=tasks,
        )

    def _build_coverage_report(
        self,
        spec_path: str,
        requirements: list[Requirement],
        tasks: list[Task],
    ) -> CoverageReport:
        """Build a CoverageReport from parsed data.

        Args:
            spec_path: Path to spec.md file.
            requirements: List of requirements from spec.
            tasks: List of tasks from tasks.md.

        Returns:
            CoverageReport with requirement-task mappings.
        """
        # Build map of requirement ID -> requirement
        req_map: dict[str, Requirement] = {r.id: r for r in requirements}

        # Build requirement coverage entries
        coverage_list: list[RequirementCoverage] = []
        for req in requirements:
            # Find tasks that reference this requirement
            matching_tasks = [t for t in tasks if req.id in t.requirement_ids]
            coverage_list.append(
                RequirementCoverage(
                    requirement=req,
                    tasks=matching_tasks,
                )
            )

        # Find orphaned references (tasks referencing non-existent requirements)
        orphaned: list[tuple[Task, str]] = []
        for task in tasks:
            for ref in task.references:
                if ref.requirement_id not in req_map:
                    orphaned.append((task, ref.requirement_id))

        return CoverageReport(
            spec_path=spec_path,
            requirements=coverage_list,
            orphaned_references=orphaned,
        )

    def calculate_for_feature(
        self,
        feature_dir: Path,
    ) -> CoverageReport:
        """Calculate coverage for a feature directory.

        Convenience method that finds spec.md and tasks.md in the feature directory.

        Args:
            feature_dir: Path to feature directory (e.g., specs/033-my-feature/)

        Returns:
            CoverageReport for the feature.

        Raises:
            FileNotFoundError: If spec.md doesn't exist in feature directory.
        """
        feature_dir = Path(feature_dir)
        spec_path = feature_dir / "spec.md"
        tasks_path = feature_dir / "tasks.md"

        return self.calculate(spec_path, tasks_path)
