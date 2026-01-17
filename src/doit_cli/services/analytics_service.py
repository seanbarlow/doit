"""Analytics service for spec metrics and reporting.

This service orchestrates the generation of analytics reports by:
1. Using SpecScanner to discover specs
2. Using DateInferrer to enrich specs with dates
3. Building AnalyticsReport with aggregated metrics
"""

from datetime import date
from pathlib import Path
from typing import Optional

from ..models.analytics_models import (
    AnalyticsReport,
    CycleTimeRecord,
    CycleTimeStats,
    SpecMetadata,
    VelocityDataPoint,
)
from ..models.status_models import SpecState
from .date_inferrer import DateInferrer
from .spec_scanner import NotADoitProjectError, SpecNotFoundError, SpecScanner


class AnalyticsService:
    """Service for generating spec analytics and metrics.

    Composes SpecScanner and DateInferrer to produce enriched
    SpecMetadata and aggregated analytics reports.
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize the analytics service.

        Args:
            project_root: Root directory of the project. Defaults to cwd.

        Raises:
            NotADoitProjectError: If not a valid doit project
        """
        self.project_root = project_root or Path.cwd()
        self.scanner = SpecScanner(self.project_root, validate=False)
        self.date_inferrer = DateInferrer(self.project_root)

    def get_all_specs(self) -> list[SpecMetadata]:
        """Get all specs with enriched metadata.

        Returns:
            List of SpecMetadata objects with date information
        """
        spec_statuses = self.scanner.scan(include_validation=False)

        return [self._enrich_with_dates(status) for status in spec_statuses]

    def get_spec_details(self, spec_name: str) -> SpecMetadata:
        """Get detailed metadata for a single spec.

        Args:
            spec_name: Name of the spec directory (e.g., "036-analytics")

        Returns:
            SpecMetadata with enriched date information

        Raises:
            SpecNotFoundError: If spec doesn't exist
        """
        spec_status = self.scanner.scan_single(spec_name)
        return self._enrich_with_dates(spec_status)

    def get_completion_summary(self) -> dict:
        """Get completion metrics summary.

        Returns:
            Dictionary with total_specs, by_status counts, and completion_pct
        """
        specs = self.get_all_specs()

        total = len(specs)
        by_status: dict[str, int] = {}

        for spec in specs:
            status_name = spec.status.display_name
            by_status[status_name] = by_status.get(status_name, 0) + 1

        completed = sum(
            1 for s in specs if s.status in (SpecState.COMPLETE, SpecState.APPROVED)
        )
        completion_pct = (completed / total * 100) if total > 0 else 0.0

        return {
            "total_specs": total,
            "by_status": by_status,
            "completion_pct": round(completion_pct, 1),
            "draft_count": by_status.get("Draft", 0),
            "in_progress_count": by_status.get("In Progress", 0),
            "complete_count": by_status.get("Complete", 0),
            "approved_count": by_status.get("Approved", 0),
        }

    def get_cycle_time_stats(
        self,
        days: Optional[int] = None,
        since: Optional[date] = None,
    ) -> tuple[Optional[CycleTimeStats], list[CycleTimeRecord]]:
        """Get cycle time statistics for completed specs.

        Args:
            days: Filter to specs completed in the last N days
            since: Filter to specs completed since this date

        Returns:
            Tuple of (CycleTimeStats or None, list of CycleTimeRecords)
        """
        specs = self.get_all_specs()

        # Filter to completed specs with dates
        records: list[CycleTimeRecord] = []
        for spec in specs:
            record = CycleTimeRecord.from_metadata(spec)
            if record:
                # Apply time filter
                if days is not None:
                    cutoff = date.today().replace(day=date.today().day)
                    from datetime import timedelta

                    cutoff = date.today() - timedelta(days=days)
                    if record.end_date < cutoff:
                        continue
                elif since is not None:
                    if record.end_date < since:
                        continue

                records.append(record)

        # Sort by end date (most recent first)
        records.sort(key=lambda r: r.end_date, reverse=True)

        stats = CycleTimeStats.calculate(records)
        return stats, records

    def get_velocity_data(self, weeks: int = 8) -> list[VelocityDataPoint]:
        """Get weekly velocity data.

        Args:
            weeks: Number of weeks to include (default 8)

        Returns:
            List of VelocityDataPoint sorted by week (most recent first)
        """
        specs = self.get_all_specs()

        # Build velocity points from completed specs
        weekly: dict[str, VelocityDataPoint] = {}

        for spec in specs:
            if spec.completed_at:
                point = VelocityDataPoint.from_completion(spec.completed_at, spec.name)
                if point.week_key in weekly:
                    weekly[point.week_key] = weekly[point.week_key].merge(point)
                else:
                    weekly[point.week_key] = point

        # Sort by week (descending) and limit
        sorted_points = sorted(weekly.values(), key=lambda v: v.week_key, reverse=True)
        return sorted_points[:weeks]

    def generate_report(self) -> AnalyticsReport:
        """Generate a complete analytics report.

        Returns:
            AnalyticsReport with all metrics calculated
        """
        specs = self.get_all_specs()
        return AnalyticsReport.generate(specs, self.project_root)

    def _enrich_with_dates(self, spec_status) -> SpecMetadata:
        """Enrich a SpecStatus with inferred dates.

        Args:
            spec_status: SpecStatus from scanner

        Returns:
            SpecMetadata with date information
        """
        created_at = self.date_inferrer.infer_created_date(spec_status.path)
        completed_at = self.date_inferrer.infer_completed_date(spec_status.path)

        return SpecMetadata.from_spec_status(
            spec_status,
            created_at=created_at,
            completed_at=completed_at,
        )

    def find_spec(self, partial_name: str) -> list[str]:
        """Find specs matching a partial name.

        Args:
            partial_name: Partial spec name to search for

        Returns:
            List of matching spec names
        """
        specs = self.scanner.scan(include_validation=False)
        matches = [
            s.name
            for s in specs
            if partial_name.lower() in s.name.lower()
        ]
        return matches

    def list_all_spec_names(self) -> list[str]:
        """List all available spec names.

        Returns:
            List of spec directory names
        """
        specs = self.scanner.scan(include_validation=False)
        return [s.name for s in specs]
