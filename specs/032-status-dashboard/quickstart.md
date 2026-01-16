# Quickstart: Spec Status Dashboard

**Feature**: 032-status-dashboard
**Date**: 2026-01-16

---

## Implementation Order

Follow this sequence for efficient implementation:

### Phase 1: Core Models (P1 - View All Specs)

1. **Create `status_models.py`**
   - Define `SpecState` enum
   - Define `SpecStatus` dataclass
   - Define `StatusReport` dataclass with computed properties

2. **Create `spec_scanner.py`**
   - Implement `scan()` to find all spec directories
   - Implement status parsing from `**Status**:` line
   - Handle parse errors gracefully

3. **Create `status_command.py`** (basic)
   - Wire up Typer command
   - Call scanner and print raw results

### Phase 2: Validation Integration (P1 - Identify Blockers)

4. **Enhance `spec_scanner.py`**
   - Integrate with `SpecValidator`
   - Compute `is_blocking` based on status + validation

5. **Create `status_reporter.py`**
   - Aggregate SpecStatus into StatusReport
   - Compute summary statistics

6. **Create `rich_formatter.py`**
   - Format status table with colors
   - Format summary panel
   - Handle "Ready to commit" indicator

### Phase 3: Filtering & Options (P2)

7. **Add CLI options**
   - `--status` filter
   - `--blocking` filter
   - `--verbose` flag
   - `--recent` filter

8. **Update reporter with filters**
   - Apply filters in `generate_report()`

### Phase 4: Export Formats (P3)

9. **Create `json_formatter.py`**
10. **Create `markdown_formatter.py`**
11. **Add `--format` and `--output` options**

---

## Key Implementation Details

### Status Parsing

```python
import re

STATUS_PATTERN = re.compile(r'\*\*Status\*\*:\s*(\w+(?:\s+\w+)?)')

def parse_status(content: str) -> SpecState:
    match = STATUS_PATTERN.search(content)
    if not match:
        return SpecState.ERROR

    status_text = match.group(1).lower().replace(" ", "_")
    try:
        return SpecState(status_text)
    except ValueError:
        return SpecState.ERROR
```

### Blocking Logic

```python
def compute_is_blocking(
    status: SpecState,
    validation: ValidationResult | None,
    is_staged: bool
) -> bool:
    if validation is None or validation.passed:
        return False

    if status == SpecState.IN_PROGRESS:
        return True  # Always blocking if in progress

    if status == SpecState.DRAFT and is_staged:
        return True  # Blocking if staged for commit

    return False
```

### Typer Command Setup

```python
import typer
from rich.console import Console

app = typer.Typer()
console = Console()

@app.command()
def status(
    status_filter: str = typer.Option(None, "--status", help="Filter by status"),
    blocking: bool = typer.Option(False, "--blocking", help="Show only blocking"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Show details"),
    recent: int = typer.Option(None, "--recent", help="Modified in last N days"),
    format: str = typer.Option("rich", "--format", help="Output format"),
    output: Path = typer.Option(None, "--output", "-o", help="Output file"),
):
    """Display status of all specifications in the project."""
    ...
```

---

## Testing Strategy

### Unit Tests

```text
tests/unit/
├── test_status_models.py      # SpecState, SpecStatus, StatusReport
├── test_spec_scanner.py       # Scanning and parsing
├── test_status_reporter.py    # Aggregation and filtering
└── test_formatters.py         # Output formatting
```

### Integration Tests

```text
tests/integration/
└── test_status_command.py     # End-to-end CLI tests
```

### Test Fixtures

Create fixtures in `tests/fixtures/specs/`:
- `valid-draft/spec.md` - Draft spec, passes validation
- `valid-complete/spec.md` - Complete spec, passes validation
- `invalid-spec/spec.md` - Fails validation (missing sections)
- `malformed/spec.md` - Cannot parse status line
- `no-status/spec.md` - Missing status field entirely

---

## File Checklist

```text
[ ] src/doit_cli/models/status_models.py
[ ] src/doit_cli/services/spec_scanner.py
[ ] src/doit_cli/services/status_reporter.py
[ ] src/doit_cli/formatters/__init__.py
[ ] src/doit_cli/formatters/base.py
[ ] src/doit_cli/formatters/rich_formatter.py
[ ] src/doit_cli/formatters/json_formatter.py
[ ] src/doit_cli/formatters/markdown_formatter.py
[ ] src/doit_cli/cli/status_command.py
[ ] tests/unit/test_status_models.py
[ ] tests/unit/test_spec_scanner.py
[ ] tests/unit/test_status_reporter.py
[ ] tests/unit/test_formatters.py
[ ] tests/integration/test_status_command.py
```

---

## Dependencies

Already in project:
- `typer` - CLI framework
- `rich` - Terminal formatting
- `pytest` - Testing

No new dependencies required.

---

## Success Validation

After implementation, verify:

1. `doit status` shows all specs in a table
2. `doit status --blocking` filters to blocking specs only
3. `doit status --verbose` shows validation error details
4. `doit status --format json` outputs valid JSON
5. Exit code 0 when no blockers, 1 when blockers exist
