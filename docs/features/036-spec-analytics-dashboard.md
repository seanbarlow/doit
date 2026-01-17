# Spec Analytics and Metrics Dashboard

**Completed**: 2026-01-16
**Branch**: 036-spec-analytics-dashboard
**PR**: (pending)

## Overview

The Spec Analytics and Metrics Dashboard provides project leads and developers with visibility into specification completion metrics, cycle time analysis, and velocity trends. It enables data-driven decisions about project health and team performance through a dedicated `doit analytics` CLI command group.

## Requirements Implemented

| ID | Description | Status |
|----|-------------|--------|
| FR-001 | Parse all spec.md files to extract status and metadata | Done |
| FR-002 | Calculate overall completion percentage | Done |
| FR-003 | Display count of specs by status (Draft, In Progress, Complete, etc.) | Done |
| FR-004 | Extract creation date from spec metadata or git history | Done |
| FR-005 | Extract completion date from spec metadata or git history | Done |
| FR-006 | Calculate cycle time (days between creation and completion) | Done |
| FR-007 | Provide cycle time statistics (average, median, min, max, std dev) | Done |
| FR-008 | Support time period filtering (--days, --since) | Done |
| FR-009 | Aggregate completions by ISO week for velocity calculation | Done |
| FR-010 | Display velocity in table format with bar visualization | Done |
| FR-011 | Support individual spec lookup by name or number | Done |
| FR-012 | Display elapsed time for in-progress specs | Done |
| FR-013 | Export reports to Markdown format | Done |
| FR-014 | Export reports to JSON format | Done |
| FR-015 | Handle missing metadata gracefully with fallback strategies | Done |
| FR-016 | Provide helpful error messages with suggestions for typos | Done |
| FR-017 | Integrate as subcommand under main CLI | Done |

## Technical Details

### Architecture

- **AnalyticsModels** (`src/doit_cli/models/analytics_models.py`): Dataclasses for SpecMetadata, CycleTimeRecord, CycleTimeStats, VelocityDataPoint, AnalyticsReport
- **DateInferrer** (`src/doit_cli/services/date_inferrer.py`): Multi-tier date extraction (metadata → git → filesystem)
- **AnalyticsService** (`src/doit_cli/services/analytics_service.py`): Core service for scanning specs and generating reports
- **CycleTimeCalculator** (`src/doit_cli/services/cycle_time_calculator.py`): Statistical analysis of completion cycle times
- **VelocityTracker** (`src/doit_cli/services/velocity_tracker.py`): Weekly velocity aggregation and trend analysis
- **ReportExporter** (`src/doit_cli/services/report_exporter.py`): Markdown and JSON export functionality
- **CLI Command** (`src/doit_cli/cli/analytics_command.py`): Typer-based `doit analytics` command group

### Key Decisions

1. **Date Inference Strategy**: Multi-tier fallback (metadata → git history → filesystem) ensures dates are always available
2. **ISO Week Aggregation**: Velocity uses ISO week keys (YYYY-WNN) for consistent cross-year reporting
3. **Rich Table Output**: Human-readable tables with optional bar visualization for velocity trends
4. **Statistics Module**: Uses Python's statistics library for cycle time calculations (mean, median, stdev)
5. **Consistent JSON Wrapper**: All JSON outputs use `{success, data}` pattern for CLI consistency

## Files Changed

### New Files

- `src/doit_cli/models/analytics_models.py`
- `src/doit_cli/services/date_inferrer.py`
- `src/doit_cli/services/analytics_service.py`
- `src/doit_cli/services/cycle_time_calculator.py`
- `src/doit_cli/services/velocity_tracker.py`
- `src/doit_cli/services/report_exporter.py`
- `src/doit_cli/cli/analytics_command.py`
- `tests/integration/test_analytics_command.py`

### Modified Files

- `src/doit_cli/main.py` - Registered analytics_app subcommand

## Testing

- **Integration Tests**: 21 tests covering all CLI commands and edge cases
- **Total Project Tests**: 948 tests passing

## CLI Commands

| Command | Description |
|---------|-------------|
| `doit analytics show` | Display completion metrics with status breakdown |
| `doit analytics show --json` | Output completion metrics in JSON format |
| `doit analytics cycles` | Show cycle time statistics for completed specs |
| `doit analytics cycles --days 30` | Filter to specs completed in last 30 days |
| `doit analytics cycles --since 2026-01-01` | Filter to specs completed since date |
| `doit analytics velocity` | Display weekly velocity trend with bar chart |
| `doit analytics velocity --weeks 12` | Show velocity for last 12 weeks |
| `doit analytics velocity --format csv` | Output velocity data in CSV format |
| `doit analytics spec <name>` | Show detailed metrics for a specific spec |
| `doit analytics export` | Export full analytics report to Markdown |
| `doit analytics export --format json` | Export full analytics report to JSON |
| `doit analytics export --output path` | Export to specified file path |

## Related Issues

- Epic: #473 (closed)
- Task issues: #479-#503 (all closed)

## Notes

- Velocity bar visualization scales to terminal width for optimal display
- Date inference prioritizes explicit metadata for accuracy
- Export files default to `.doit/reports/analytics-YYYY-MM-DD.{md|json}`
