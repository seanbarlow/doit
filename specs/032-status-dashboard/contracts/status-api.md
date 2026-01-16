# Contract: Status Command API

**Feature**: 032-status-dashboard
**Date**: 2026-01-16

---

## CLI Interface Contract

### Command Signature

```text
doit status [OPTIONS]
```

### Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `--status` | `str` | None | Filter by spec status (draft, in-progress, complete, approved) |
| `--blocking` | `flag` | False | Show only specs that are blocking commits |
| `--verbose` / `-v` | `flag` | False | Show detailed validation errors |
| `--recent` | `int` | None | Show specs modified in last N days |
| `--format` | `str` | "rich" | Output format: rich, json, markdown |
| `--output` / `-o` | `Path` | None | Write report to file instead of stdout |

### Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success, no blocking specs |
| 1 | Success, but blocking specs exist |
| 2 | Error (not a doit project, invalid options) |

---

## Service Interface Contracts

### SpecScanner

```python
class SpecScanner:
    """Scans specs directory and parses spec metadata."""

    def __init__(self, project_root: Path) -> None:
        """Initialize scanner with project root directory."""
        ...

    def scan(self) -> list[SpecStatus]:
        """
        Scan specs/ directory and return all spec statuses.

        Returns:
            List of SpecStatus objects, one per spec directory.

        Raises:
            NotADoitProjectError: If project_root lacks .doit/ directory.
        """
        ...

    def scan_single(self, spec_name: str) -> SpecStatus:
        """
        Parse status for a single spec by name.

        Args:
            spec_name: Directory name of the spec (e.g., "032-status-dashboard")

        Returns:
            SpecStatus for the specified spec.

        Raises:
            SpecNotFoundError: If spec directory doesn't exist.
        """
        ...
```

### StatusReporter

```python
class StatusReporter:
    """Aggregates spec statuses into reports with statistics."""

    def __init__(
        self,
        scanner: SpecScanner,
        validator: SpecValidator
    ) -> None:
        """Initialize reporter with scanner and validator."""
        ...

    def generate_report(
        self,
        status_filter: SpecState | None = None,
        blocking_only: bool = False,
        recent_days: int | None = None
    ) -> StatusReport:
        """
        Generate a status report with optional filtering.

        Args:
            status_filter: Only include specs with this status.
            blocking_only: Only include specs blocking commits.
            recent_days: Only include specs modified in last N days.

        Returns:
            StatusReport with filtered specs and computed statistics.
        """
        ...
```

### Formatter Interface

```python
from abc import ABC, abstractmethod

class StatusFormatter(ABC):
    """Abstract base class for status output formatters."""

    @abstractmethod
    def format(self, report: StatusReport, verbose: bool = False) -> str:
        """
        Format the status report for output.

        Args:
            report: The StatusReport to format.
            verbose: Include detailed validation errors.

        Returns:
            Formatted string representation.
        """
        ...

class RichFormatter(StatusFormatter):
    """Formats status as rich terminal output with colors."""
    ...

class JsonFormatter(StatusFormatter):
    """Formats status as JSON for machine consumption."""
    ...

class MarkdownFormatter(StatusFormatter):
    """Formats status as markdown table for documentation."""
    ...
```

---

## Output Format Contracts

### Rich Terminal Output (Default)

```text
╭─ Spec Status Dashboard ─────────────────────────────────────╮
│                                                             │
│  📊 Project: doit                                           │
│  📅 Generated: 2026-01-16 14:30:00                         │
│                                                             │
╰─────────────────────────────────────────────────────────────╯

┏━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━┳━━━━━━━━━━━━┳━━━━━━━━━━━┓
┃ Spec                  ┃ Status      ┃ Validation ┃ Modified  ┃
┡━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━╇━━━━━━━━━━━━╇━━━━━━━━━━━┩
│ 032-status-dashboard  │ 📝 Draft    │ ✅ Pass    │ Today     │
│ 031-init-workflow     │ ✅ Complete │ ✅ Pass    │ Yesterday │
│ 030-guided-workflows  │ ✅ Complete │ ✅ Pass    │ 2 days    │
└───────────────────────┴─────────────┴────────────┴───────────┘

╭─ Summary ───────────────────────────────────────────────────╮
│  Draft: 1  │  In Progress: 0  │  Complete: 2  │  Approved: 0│
│  Completion: 66%  │  ✅ Ready to commit                     │
╰─────────────────────────────────────────────────────────────╯
```

### JSON Output (`--format json`)

```json
{
  "generated_at": "2026-01-16T14:30:00Z",
  "project_root": "/path/to/project",
  "summary": {
    "total": 3,
    "by_status": {
      "draft": 1,
      "in_progress": 0,
      "complete": 2,
      "approved": 0
    },
    "blocking": 0,
    "validation_pass": 3,
    "validation_fail": 0,
    "completion_percentage": 66.67,
    "ready_to_commit": true
  },
  "specs": [
    {
      "name": "032-status-dashboard",
      "path": "specs/032-status-dashboard/spec.md",
      "status": "draft",
      "last_modified": "2026-01-16T10:00:00Z",
      "validation": {
        "passed": true,
        "score": 95,
        "errors": []
      },
      "is_blocking": false,
      "error": null
    }
  ]
}
```

### Markdown Output (`--format markdown`)

```markdown
# Spec Status Report

**Generated**: 2026-01-16 14:30:00
**Project**: doit

## Specifications

| Spec | Status | Validation | Last Modified |
|------|--------|------------|---------------|
| 032-status-dashboard | Draft | ✅ Pass | 2026-01-16 |
| 031-init-workflow | Complete | ✅ Pass | 2026-01-15 |
| 030-guided-workflows | Complete | ✅ Pass | 2026-01-14 |

## Summary

- **Total Specs**: 3
- **Draft**: 1
- **In Progress**: 0
- **Complete**: 2
- **Approved**: 0
- **Completion**: 66%
- **Status**: ✅ Ready to commit
```

---

## Error Messages Contract

| Scenario | Message |
|----------|---------|
| Not a doit project | "Error: Not a doit project. Run 'doit init' first." |
| No specs found | "No specifications found. Run 'doit specit' to create one." |
| Invalid status filter | "Error: Invalid status '[value]'. Valid: draft, in-progress, complete, approved" |
| File parse error | "Warning: Unable to parse specs/[name]/spec.md: [error]" |
| Invalid format | "Error: Invalid format '[value]'. Valid: rich, json, markdown" |

---

## Integration Points

### With SpecValidator (Feature 029)

```python
# Reuse existing validator
from doit_cli.services.spec_validator import SpecValidator, ValidationResult

validator = SpecValidator()
result: ValidationResult = validator.validate(spec_path)
```

### With Git (for blocking detection)

```python
# Check if spec is staged for commit
def is_git_staged(spec_path: Path) -> bool:
    """Check if spec file is in git staging area."""
    result = subprocess.run(
        ["git", "diff", "--cached", "--name-only"],
        capture_output=True, text=True
    )
    return str(spec_path) in result.stdout
```
