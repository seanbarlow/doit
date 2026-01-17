# CLI Contract: doit analytics

**Feature**: 036-spec-analytics-dashboard
**Date**: 2026-01-16

## Command Structure

```text
doit analytics [COMMAND] [OPTIONS]
```

## Commands

### `doit analytics show` (default)

Display completion metrics summary for all specs.

**Usage**:

```bash
doit analytics show [OPTIONS]
doit analytics        # 'show' is default when no subcommand
```

**Options**:

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `--json` | flag | false | Output as JSON instead of table |

**Output (table)**:

```text
Spec Analytics - my-project

Summary
┏━━━━━━━━━━━━━━━━┳━━━━━━━┓
┃ Metric         ┃ Value ┃
┡━━━━━━━━━━━━━━━━╇━━━━━━━┩
│ Total Specs    │ 35    │
│ Completed      │ 28    │
│ In Progress    │ 5     │
│ Draft          │ 2     │
│ Completion %   │ 80.0% │
└────────────────┴───────┘

Status Breakdown
┏━━━━━━━━━━━━━━┳━━━━━━━┳━━━━━━━━━━━━━┓
┃ Status       ┃ Count ┃ Percentage  ┃
┡━━━━━━━━━━━━━━╇━━━━━━━╇━━━━━━━━━━━━━┩
│ ✅ Complete  │ 20    │ 57.1%       │
│ 🏆 Approved  │ 8     │ 22.9%       │
│ 🔄 Progress  │ 5     │ 14.3%       │
│ 📝 Draft     │ 2     │ 5.7%        │
└──────────────┴───────┴─────────────┘
```

**Exit Codes**:

| Code | Meaning |
|------|---------|
| 0 | Success |
| 1 | No specs found |
| 2 | Not a doit project |

---

### `doit analytics cycles`

Display cycle time statistics for completed specs.

**Usage**:

```bash
doit analytics cycles [OPTIONS]
```

**Options**:

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `--days N` | int | 30 | Filter to specs completed in last N days |
| `--since DATE` | date | - | Filter to specs completed since DATE (YYYY-MM-DD) |
| `--json` | flag | false | Output as JSON |

**Output (table)**:

```text
Cycle Time Analysis (last 30 days)

Statistics (N=12 completed specs)
┏━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━┓
┃ Metric          ┃ Value       ┃
┡━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━┩
│ Average         │ 5.2 days    │
│ Median          │ 4.0 days    │
│ Minimum         │ 1 day       │
│ Maximum         │ 14 days     │
│ Std Deviation   │ 3.1 days    │
└─────────────────┴─────────────┘

Recent Completions
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━┳━━━━━━━━━━━━━┓
┃ Spec                      ┃ Completed   ┃ Cycle Time  ┃
┡━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━╇━━━━━━━━━━━━━┩
│ 035-auto-mermaid-diagrams │ 2026-01-16  │ 3 days      │
│ 034-fixit-workflow        │ 2026-01-15  │ 2 days      │
│ 033-spec-task-crossrefs   │ 2026-01-14  │ 5 days      │
└───────────────────────────┴─────────────┴─────────────┘
```

**Exit Codes**:

| Code | Meaning |
|------|---------|
| 0 | Success |
| 1 | No completed specs in period |
| 2 | Not a doit project |

---

### `doit analytics velocity`

Display velocity trends over time.

**Usage**:

```bash
doit analytics velocity [OPTIONS]
```

**Options**:

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `--weeks N` | int | 8 | Number of weeks to display |
| `--format FMT` | str | table | Output format: table, json, csv |

**Output (table)**:

```text
Velocity Trends (last 8 weeks)

┏━━━━━━━━━━━┳━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Week      ┃ Completed ┃ Trend                               ┃
┡━━━━━━━━━━━╇━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ 2026-W03  │ 3         │ ███████████████                     │
│ 2026-W02  │ 4         │ ████████████████████                │
│ 2026-W01  │ 2         │ ██████████                          │
│ 2025-W52  │ 1         │ █████                               │
│ 2025-W51  │ 3         │ ███████████████                     │
│ 2025-W50  │ 2         │ ██████████                          │
│ 2025-W49  │ 0         │                                     │
│ 2025-W48  │ 1         │ █████                               │
└───────────┴───────────┴─────────────────────────────────────┘

Average: 2.0 specs/week
```

**Exit Codes**:

| Code | Meaning |
|------|---------|
| 0 | Success |
| 1 | Insufficient data (< 2 weeks) |
| 2 | Not a doit project |

---

### `doit analytics spec`

Display detailed metrics for a specific spec.

**Usage**:

```bash
doit analytics spec SPEC_NAME [OPTIONS]
```

**Arguments**:

| Argument | Required | Description |
|----------|----------|-------------|
| SPEC_NAME | Yes | Spec directory name (e.g., "036-spec-analytics") |

**Options**:

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `--json` | flag | false | Output as JSON |

**Output (table)**:

```text
Spec Details: 035-auto-mermaid-diagrams

┏━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Field            ┃ Value                                            ┃
┡━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ Status           │ ✅ Complete                                       │
│ Created          │ 2026-01-13                                        │
│ Completed        │ 2026-01-16                                        │
│ Cycle Time       │ 3 days                                            │
│ Current Phase    │ Review                                            │
│ Path             │ specs/035-auto-mermaid-diagrams/spec.md          │
└──────────────────┴──────────────────────────────────────────────────┘

Timeline
┏━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━┓
┃ Date       ┃ Event                ┃
┡━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━┩
│ 2026-01-13 │ Spec created (Draft) │
│ 2026-01-14 │ Started (In Progress)│
│ 2026-01-16 │ Completed            │
└────────────┴──────────────────────┘
```

**Exit Codes**:

| Code | Meaning |
|------|---------|
| 0 | Success |
| 1 | Spec not found |
| 2 | Not a doit project |

---

### `doit analytics export`

Export analytics report to file.

**Usage**:

```bash
doit analytics export [OPTIONS]
```

**Options**:

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `--format FMT` | str | markdown | Export format: markdown, json |
| `--output PATH` | path | auto | Output file path (default: .doit/reports/) |

**Output**:

```text
✓ Analytics report exported to .doit/reports/analytics-2026-01-16.md
```

**Exit Codes**:

| Code | Meaning |
|------|---------|
| 0 | Success |
| 1 | Export failed |
| 2 | Not a doit project |

---

## JSON Output Schema

When `--json` is specified, all commands output JSON in this format:

```json
{
  "success": true,
  "report_id": "20260116-143022",
  "generated_at": "2026-01-16T14:30:22Z",
  "data": {
    "total_specs": 35,
    "completion_pct": 80.0,
    "by_status": {
      "draft": 2,
      "in_progress": 5,
      "complete": 20,
      "approved": 8
    },
    "cycle_stats": {
      "average_days": 5.2,
      "median_days": 4.0,
      "min_days": 1,
      "max_days": 14,
      "std_dev_days": 3.1,
      "sample_count": 28
    },
    "velocity": [
      {"week": "2026-W03", "completed": 3},
      {"week": "2026-W02", "completed": 4}
    ]
  }
}
```

---

## Error Messages

| Scenario | Message |
|----------|---------|
| Not a doit project | `Error: Not a doit project. Run 'doit init' first.` |
| No specs found | `No specifications found in specs/ directory.` |
| Spec not found | `Error: Spec '{name}' not found. Available: {list}` |
| No completions | `No completed specs found in the specified period.` |
| Insufficient data | `Insufficient data for velocity trends. Need at least 2 weeks of history.` |
