"""Velocity tracker service for spec analytics.

Provides weekly velocity aggregation and trend analysis.
"""

from datetime import date, timedelta
from typing import Optional

from ..models.analytics_models import SpecMetadata, VelocityDataPoint


class VelocityTracker:
    """Tracker for spec completion velocity.

    Aggregates spec completions by ISO week to enable
    trend analysis and velocity metrics.
    """

    def __init__(self, specs: list[SpecMetadata]):
        """Initialize tracker with spec metadata.

        Args:
            specs: List of SpecMetadata objects to analyze
        """
        self.specs = specs
        self._weekly_data: Optional[dict[str, VelocityDataPoint]] = None

    @property
    def weekly_data(self) -> dict[str, VelocityDataPoint]:
        """Get weekly aggregated velocity data.

        Returns:
            Dictionary mapping week keys to VelocityDataPoint objects
        """
        if self._weekly_data is None:
            self._weekly_data = self._aggregate_by_week()
        return self._weekly_data

    def _aggregate_by_week(self) -> dict[str, VelocityDataPoint]:
        """Aggregate completions by ISO week.

        Returns:
            Dictionary of week_key -> VelocityDataPoint
        """
        weekly: dict[str, VelocityDataPoint] = {}

        for spec in self.specs:
            if spec.completed_at:
                point = VelocityDataPoint.from_completion(
                    spec.completed_at, spec.name
                )
                if point.week_key in weekly:
                    weekly[point.week_key] = weekly[point.week_key].merge(point)
                else:
                    weekly[point.week_key] = point

        return weekly

    def aggregate_by_week(self, weeks: int = 8) -> list[VelocityDataPoint]:
        """Get velocity data for the specified number of weeks.

        Args:
            weeks: Number of weeks to include (default 8)

        Returns:
            List of VelocityDataPoint sorted by week (most recent first)
        """
        # Get all weekly data
        all_weeks = list(self.weekly_data.values())

        # Sort by week key (descending)
        sorted_weeks = sorted(all_weeks, key=lambda v: v.week_key, reverse=True)

        # Limit to requested number of weeks
        return sorted_weeks[:weeks]

    def get_velocity_trend(
        self,
        weeks: int = 8,
        fill_missing: bool = True,
    ) -> list[VelocityDataPoint]:
        """Get velocity trend with optional gap filling.

        Args:
            weeks: Number of weeks to analyze
            fill_missing: If True, include weeks with zero completions

        Returns:
            List of VelocityDataPoint covering the time range
        """
        if not fill_missing:
            return self.aggregate_by_week(weeks)

        # Generate all weeks in range
        today = date.today()
        current_week_start = today - timedelta(days=today.weekday())

        result: list[VelocityDataPoint] = []

        for i in range(weeks):
            week_date = current_week_start - timedelta(weeks=i)
            year, week, _ = week_date.isocalendar()
            week_key = f"{year}-W{week:02d}"

            if week_key in self.weekly_data:
                result.append(self.weekly_data[week_key])
            else:
                # Create empty data point for missing week
                result.append(
                    VelocityDataPoint(
                        week_key=week_key,
                        week_start=week_date,
                        specs_completed=0,
                        spec_names=[],
                    )
                )

        return result

    def calculate_average_velocity(self, weeks: int = 8) -> float:
        """Calculate average specs completed per week.

        Args:
            weeks: Number of weeks to average over

        Returns:
            Average completions per week
        """
        data = self.aggregate_by_week(weeks)
        if not data:
            return 0.0

        total = sum(v.specs_completed for v in data)
        return total / len(data)

    def get_peak_week(self) -> Optional[VelocityDataPoint]:
        """Get the week with most completions.

        Returns:
            VelocityDataPoint for peak week, or None if no data
        """
        if not self.weekly_data:
            return None

        return max(
            self.weekly_data.values(),
            key=lambda v: v.specs_completed,
        )

    def has_sufficient_data(self, min_weeks: int = 2) -> bool:
        """Check if there's enough data for trend analysis.

        Args:
            min_weeks: Minimum weeks required

        Returns:
            True if sufficient data exists
        """
        return len(self.weekly_data) >= min_weeks

    def to_csv(self, weeks: int = 8) -> str:
        """Export velocity data as CSV string.

        Args:
            weeks: Number of weeks to include

        Returns:
            CSV formatted string with header
        """
        lines = ["week,completed"]
        for v in self.aggregate_by_week(weeks):
            lines.append(f"{v.week_key},{v.specs_completed}")
        return "\n".join(lines)
