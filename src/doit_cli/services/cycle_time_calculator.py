"""Cycle time calculator service for spec analytics.

Provides statistical analysis of spec completion cycle times.
"""

from datetime import date, timedelta
from typing import Optional

from ..models.analytics_models import (
    CycleTimeRecord,
    CycleTimeStats,
    SpecMetadata,
)


class CycleTimeCalculator:
    """Calculator for cycle time statistics.

    Processes SpecMetadata to extract cycle time records and
    calculate statistical summaries.
    """

    def __init__(self, specs: list[SpecMetadata]):
        """Initialize calculator with spec metadata.

        Args:
            specs: List of SpecMetadata objects to analyze
        """
        self.specs = specs
        self._records: Optional[list[CycleTimeRecord]] = None

    @property
    def records(self) -> list[CycleTimeRecord]:
        """Get all cycle time records from completed specs.

        Returns:
            List of CycleTimeRecord for specs with both dates
        """
        if self._records is None:
            self._records = []
            for spec in self.specs:
                record = CycleTimeRecord.from_metadata(spec)
                if record:
                    self._records.append(record)
        return self._records

    def calculate_stats(
        self,
        days: Optional[int] = None,
        since: Optional[date] = None,
    ) -> Optional[CycleTimeStats]:
        """Calculate cycle time statistics.

        Args:
            days: Filter to specs completed in last N days
            since: Filter to specs completed since this date

        Returns:
            CycleTimeStats or None if no matching records
        """
        filtered = self.filter_records(days=days, since=since)
        return CycleTimeStats.calculate(filtered)

    def filter_records(
        self,
        days: Optional[int] = None,
        since: Optional[date] = None,
    ) -> list[CycleTimeRecord]:
        """Filter cycle time records by time period.

        Args:
            days: Filter to specs completed in last N days
            since: Filter to specs completed since this date (overrides days)

        Returns:
            Filtered list of CycleTimeRecord objects
        """
        records = self.records

        if since is not None:
            records = [r for r in records if r.end_date >= since]
        elif days is not None:
            cutoff = date.today() - timedelta(days=days)
            records = [r for r in records if r.end_date >= cutoff]

        # Sort by end date (most recent first)
        return sorted(records, key=lambda r: r.end_date, reverse=True)

    def get_recent_completions(self, limit: int = 10) -> list[CycleTimeRecord]:
        """Get most recently completed specs.

        Args:
            limit: Maximum number of records to return

        Returns:
            List of CycleTimeRecord sorted by completion date
        """
        sorted_records = sorted(
            self.records,
            key=lambda r: r.end_date,
            reverse=True,
        )
        return sorted_records[:limit]

    def get_slowest_completions(self, limit: int = 5) -> list[CycleTimeRecord]:
        """Get specs with longest cycle times.

        Args:
            limit: Maximum number of records to return

        Returns:
            List of CycleTimeRecord sorted by cycle time descending
        """
        sorted_records = sorted(
            self.records,
            key=lambda r: r.days_to_complete,
            reverse=True,
        )
        return sorted_records[:limit]

    def get_fastest_completions(self, limit: int = 5) -> list[CycleTimeRecord]:
        """Get specs with shortest cycle times.

        Args:
            limit: Maximum number of records to return

        Returns:
            List of CycleTimeRecord sorted by cycle time ascending
        """
        sorted_records = sorted(
            self.records,
            key=lambda r: r.days_to_complete,
        )
        return sorted_records[:limit]
