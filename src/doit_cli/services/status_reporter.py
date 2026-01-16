"""StatusReporter service for aggregating and filtering spec statuses."""

from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

from ..models.status_models import SpecState, SpecStatus, StatusReport
from .spec_scanner import SpecScanner


class StatusReporter:
    """Aggregates spec statuses into reports with statistics and filtering.

    This service combines SpecScanner results with optional filtering
    to generate StatusReport objects with computed statistics.
    """

    def __init__(
        self,
        project_root: Optional[Path] = None,
        validate: bool = True,
    ) -> None:
        """Initialize reporter with project root.

        Args:
            project_root: Root directory of the doit project.
                         Defaults to current working directory.
            validate: Whether to run validation on specs.
        """
        self.scanner = SpecScanner(project_root, validate=validate)
        self.project_root = self.scanner.project_root

    def generate_report(
        self,
        status_filter: Optional[SpecState] = None,
        blocking_only: bool = False,
        recent_days: Optional[int] = None,
    ) -> StatusReport:
        """Generate a status report with optional filtering.

        Args:
            status_filter: Only include specs with this status.
            blocking_only: Only include specs blocking commits.
            recent_days: Only include specs modified in last N days.

        Returns:
            StatusReport with filtered specs and computed statistics.
        """
        # Scan all specs
        specs = self.scanner.scan(include_validation=True)

        # Apply filters
        specs = self._apply_filters(
            specs,
            status_filter=status_filter,
            blocking_only=blocking_only,
            recent_days=recent_days,
        )

        return StatusReport(
            specs=specs,
            generated_at=datetime.now(),
            project_root=self.project_root,
        )

    def _apply_filters(
        self,
        specs: list[SpecStatus],
        status_filter: Optional[SpecState] = None,
        blocking_only: bool = False,
        recent_days: Optional[int] = None,
    ) -> list[SpecStatus]:
        """Apply filters to spec list.

        Args:
            specs: List of SpecStatus to filter.
            status_filter: Only include specs with this status.
            blocking_only: Only include blocking specs.
            recent_days: Only include specs modified in last N days.

        Returns:
            Filtered list of SpecStatus objects.
        """
        filtered = specs

        # Filter by status
        if status_filter is not None:
            filtered = [s for s in filtered if s.status == status_filter]

        # Filter by blocking
        if blocking_only:
            filtered = [s for s in filtered if s.is_blocking]

        # Filter by recent modification
        if recent_days is not None:
            cutoff = datetime.now() - timedelta(days=recent_days)
            filtered = [s for s in filtered if s.last_modified >= cutoff]

        return filtered

    def filter_by_status(
        self,
        specs: list[SpecStatus],
        status: SpecState,
    ) -> list[SpecStatus]:
        """Filter specs by status.

        Args:
            specs: List of SpecStatus to filter.
            status: Status to filter by.

        Returns:
            Specs with matching status.
        """
        return [s for s in specs if s.status == status]

    def filter_blocking(self, specs: list[SpecStatus]) -> list[SpecStatus]:
        """Filter to only blocking specs.

        Args:
            specs: List of SpecStatus to filter.

        Returns:
            Only specs that are blocking.
        """
        return [s for s in specs if s.is_blocking]

    def filter_recent(
        self,
        specs: list[SpecStatus],
        days: int,
    ) -> list[SpecStatus]:
        """Filter to specs modified within N days.

        Args:
            specs: List of SpecStatus to filter.
            days: Number of days to look back.

        Returns:
            Specs modified within the time period.
        """
        cutoff = datetime.now() - timedelta(days=days)
        return [s for s in specs if s.last_modified >= cutoff]
