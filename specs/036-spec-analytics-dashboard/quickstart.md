# Quickstart: Spec Analytics and Metrics Dashboard

**Feature**: 036-spec-analytics-dashboard
**Date**: 2026-01-16

## Prerequisites

- doit CLI installed (`pip install doit-toolkit-cli`)
- Project initialized with `doit init`
- At least one spec in `specs/` directory

## Quick Commands

### View Completion Metrics

```bash
# Show overall project analytics
doit analytics

# Same as above (explicit)
doit analytics show

# Output as JSON
doit analytics --json
```

### View Cycle Time Statistics

```bash
# Cycle times for last 30 days (default)
doit analytics cycles

# Cycle times for last 14 days
doit analytics cycles --days 14

# Cycle times since specific date
doit analytics cycles --since 2026-01-01
```

### View Velocity Trends

```bash
# Weekly velocity for last 8 weeks
doit analytics velocity

# Weekly velocity for last 12 weeks
doit analytics velocity --weeks 12

# Export velocity as CSV
doit analytics velocity --format csv
```

### View Individual Spec Metrics

```bash
# Details for a specific spec
doit analytics spec 035-auto-mermaid-diagrams

# Output as JSON
doit analytics spec 035-auto-mermaid-diagrams --json
```

### Export Analytics Report

```bash
# Export as Markdown (default)
doit analytics export

# Export as JSON
doit analytics export --format json

# Export to specific location
doit analytics export --output ./reports/analytics.md
```

## Implementation Steps

### Step 1: Create Models

Create `src/doit_cli/models/analytics_models.py` with:

- `SpecMetadata` - Extended spec info with dates
- `CycleTimeRecord` - Individual cycle time data
- `CycleTimeStats` - Statistical summary
- `VelocityDataPoint` - Weekly velocity data
- `AnalyticsReport` - Complete report

### Step 2: Create Services

Create services in `src/doit_cli/services/`:

1. **date_inferrer.py** - Extract dates from specs/git
2. **cycle_time_calculator.py** - Calculate statistics
3. **velocity_tracker.py** - Aggregate by week
4. **report_exporter.py** - Export to MD/JSON
5. **analytics_service.py** - Orchestrate all services

### Step 3: Create CLI Command

Create `src/doit_cli/cli/analytics_command.py`:

```python
import typer
from rich.console import Console

app = typer.Typer(help="Spec analytics and metrics")
console = Console()

@app.command()
def show(json_output: bool = typer.Option(False, "--json")):
    """Display completion metrics summary."""
    # Implementation here

@app.command()
def cycles(
    days: int = typer.Option(30, "--days"),
    since: str = typer.Option(None, "--since"),
    json_output: bool = typer.Option(False, "--json"),
):
    """Display cycle time statistics."""
    # Implementation here

# ... more commands
```

### Step 4: Register Command

Add to `src/doit_cli/main.py`:

```python
from .cli.analytics_command import app as analytics_app

app.add_typer(analytics_app, name="analytics")
```

### Step 5: Write Tests

Create tests in `tests/`:

- `tests/unit/test_analytics_models.py`
- `tests/unit/test_date_inferrer.py`
- `tests/unit/test_cycle_time_calculator.py`
- `tests/unit/test_velocity_tracker.py`
- `tests/unit/test_report_exporter.py`
- `tests/integration/test_analytics_command.py`

## Example Workflow

```bash
# 1. Check current analytics
doit analytics

# 2. Analyze recent cycle times
doit analytics cycles --days 7

# 3. Check velocity trends
doit analytics velocity

# 4. Investigate a specific spec
doit analytics spec 036-spec-analytics-dashboard

# 5. Export for stakeholder report
doit analytics export --format markdown --output ./reports/weekly-analytics.md
```

## Testing Checklist

- [ ] `doit analytics` shows completion metrics
- [ ] `doit analytics cycles` shows cycle time stats
- [ ] `doit analytics velocity` shows weekly trends
- [ ] `doit analytics spec NAME` shows spec details
- [ ] `doit analytics export` creates report file
- [ ] All commands work with `--json` flag
- [ ] Error handling for missing specs/data
- [ ] Performance < 2s for 100 specs
