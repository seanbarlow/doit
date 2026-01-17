# Research: Spec Analytics and Metrics Dashboard

**Feature**: 036-spec-analytics-dashboard
**Date**: 2026-01-16
**Status**: Complete

## Overview

This document captures research findings for implementing spec analytics and metrics functionality. The feature builds on existing infrastructure from feature 032 (status dashboard), so the primary research focused on date extraction strategies and statistical calculation approaches.

---

## Research Topics

### R1: Date Extraction from Spec Files

**Question**: How do we reliably extract creation and completion dates for specs?

**Decision**: Multi-tier fallback strategy

**Rationale**: Spec files may have varying levels of metadata completeness. A fallback chain ensures we can always provide some date information.

**Alternatives Considered**:

| Approach | Pros | Cons | Verdict |
|----------|------|------|---------|
| Spec metadata only | Simple, fast | Incomplete for older specs | Insufficient |
| Git history only | Always available | Slower, requires git | Good fallback |
| File timestamps only | Always available | Unreliable after git clone | Last resort |
| Combined approach | Best accuracy | More complex | **Selected** |

**Implementation**:

```python
# Priority order for creation date:
1. Parse **Created**: YYYY-MM-DD from spec.md frontmatter
2. git log --follow --diff-filter=A -- specs/{name}/spec.md (first commit)
3. file.stat().st_ctime (file creation time)

# Priority order for completion date:
1. Search git log for commit changing "**Status**: Complete"
2. git log -1 --format=%aI -- specs/{name}/spec.md (last modified in git)
3. file.stat().st_mtime (file modification time)
```

---

### R2: Cycle Time Statistical Calculations

**Question**: Which statistical measures are most useful for cycle time analysis?

**Decision**: Provide average, median, min, max, and standard deviation

**Rationale**: Different metrics serve different purposes:

- **Average (mean)**: Overall trend indicator
- **Median**: Central tendency resistant to outliers
- **Min/Max**: Range bounds for planning
- **Std Dev**: Variability indicator for predictability

**Alternatives Considered**:

| Approach | Pros | Cons | Verdict |
|----------|------|------|---------|
| Average only | Simple | Skewed by outliers | Insufficient |
| Median only | Robust | Loses range info | Insufficient |
| Percentiles (p50, p90, p95) | Detailed distribution | Overly complex for CLI | Deferred |
| Mean + Median + Range | Balanced | Covers common needs | **Selected** |

**Implementation**:

```python
from statistics import mean, median, stdev

def calculate_cycle_stats(cycle_times: list[int]) -> dict:
    return {
        "average": mean(cycle_times),
        "median": median(cycle_times),
        "min": min(cycle_times),
        "max": max(cycle_times),
        "std_dev": stdev(cycle_times) if len(cycle_times) > 1 else 0,
    }
```

---

### R3: Velocity Aggregation Period

**Question**: What time period should be used for velocity trend aggregation?

**Decision**: ISO week (Monday-Sunday), with option to view by month

**Rationale**: Weekly aggregation provides actionable granularity while smoothing daily variations. ISO weeks provide consistent week boundaries.

**Alternatives Considered**:

| Period | Pros | Cons | Verdict |
|--------|------|------|---------|
| Daily | High granularity | Too noisy for small teams | Rejected |
| Weekly | Good balance | Requires 2+ weeks data | **Selected** |
| Monthly | Smooth trends | Too coarse for active projects | Optional |
| Sprint-based | Aligns with agile | Requires sprint config | Deferred |

**Implementation**:

```python
from datetime import datetime
from collections import defaultdict

def aggregate_by_week(completion_dates: list[datetime]) -> dict[str, int]:
    """Aggregate completions by ISO week."""
    weeks = defaultdict(int)
    for dt in completion_dates:
        year, week, _ = dt.isocalendar()
        week_key = f"{year}-W{week:02d}"
        weeks[week_key] += 1
    return dict(sorted(weeks.items()))
```

---

### R4: Export Format Design

**Question**: What export formats should be supported and what should they contain?

**Decision**: Markdown and JSON, with full analytics data

**Rationale**: Markdown for human-readable reports (GitHub, documentation). JSON for machine processing and external tool integration.

**Alternatives Considered**:

| Format | Pros | Cons | Verdict |
|--------|------|------|---------|
| Markdown only | Simple, readable | Not machine-parseable | Insufficient |
| JSON only | Machine-friendly | Not human-readable | Insufficient |
| CSV | Spreadsheet-friendly | Loses structure | Deferred |
| HTML | Rich formatting | Requires rendering | Deferred |
| Both MD + JSON | Best coverage | Two formats to maintain | **Selected** |

**Export Content**:

```markdown
# Analytics Report - {project_name}

Generated: {timestamp}

## Summary
- Total Specs: {count}
- Completion Rate: {percentage}%
- Average Cycle Time: {days} days

## Cycle Time Statistics
| Metric | Value |
|--------|-------|
| Average | {avg} days |
| Median | {median} days |
| Min | {min} days |
| Max | {max} days |

## Velocity Trends
| Week | Completed |
|------|-----------|
| 2026-W02 | 3 |
| 2026-W03 | 2 |
```

---

### R5: Existing Infrastructure Reuse

**Question**: What existing code can be reused from feature 032?

**Decision**: Reuse SpecScanner, SpecStatus, StatusReport; extend with new models

**Findings**:

| Component | Location | Reuse Strategy |
|-----------|----------|----------------|
| SpecScanner | services/spec_scanner.py | Direct import, use scan() method |
| SpecStatus | models/status_models.py | Extend with date fields via composition |
| StatusReport | models/status_models.py | Use for base statistics |
| SpecState | models/status_models.py | Direct import for status checks |

**Integration Pattern**:

```python
class AnalyticsService:
    def __init__(self, project_root: Path):
        self.scanner = SpecScanner(project_root, validate=False)
        self.date_inferrer = DateInferrer(project_root)

    def generate_report(self) -> AnalyticsReport:
        # Reuse existing scanning
        specs = self.scanner.scan(include_validation=False)

        # Enrich with date information
        enriched = [self._enrich_with_dates(s) for s in specs]

        # Calculate analytics
        return self._build_report(enriched)
```

---

## Resolved Clarifications

All technical questions from the spec have been resolved:

| Topic | Resolution |
|-------|------------|
| Date extraction | Multi-tier fallback (metadata → git → filesystem) |
| Statistical measures | Mean, median, min, max, std dev |
| Velocity period | ISO weeks, optional monthly |
| Export formats | Markdown + JSON |
| Code reuse | Compose with existing SpecScanner |

---

## References

- Python statistics module: https://docs.python.org/3/library/statistics.html
- ISO week date: https://en.wikipedia.org/wiki/ISO_week_date
- Git log formats: https://git-scm.com/docs/git-log
- Existing SpecScanner: src/doit_cli/services/spec_scanner.py
