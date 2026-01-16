# Quickstart: Bug-Fix Workflow Command

**Feature**: 034-fixit-workflow
**Date**: 2026-01-16

## Overview

The `doit fixit` command provides a structured workflow for fixing bugs from GitHub issues. This guide walks through implementing the feature from scratch.

---

## Prerequisites

- Python 3.11+ installed
- GitHub CLI (`gh`) installed and authenticated
- Existing doit-cli codebase checked out
- Feature branch `034-fixit-workflow` created

---

## Implementation Steps

### Step 1: Create Models (30 min)

Create `src/doit_cli/models/fixit_models.py`:

```python
"""Data models for bug-fix workflow."""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional

class FixPhase(Enum):
    INITIALIZED = "initialized"
    INVESTIGATING = "investigating"
    PLANNING = "planning"
    REVIEWING = "reviewing"
    APPROVED = "approved"
    IMPLEMENTING = "implementing"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class FindingType(Enum):
    HYPOTHESIS = "hypothesis"
    CONFIRMED_CAUSE = "confirmed_cause"
    AFFECTED_FILE = "affected_file"
    REPRODUCTION_STEP = "reproduction_step"
    RELATED_COMMIT = "related_commit"

@dataclass
class GitHubIssue:
    number: int
    title: str
    body: str = ""
    state: str = "open"
    labels: list[str] = field(default_factory=list)

@dataclass
class InvestigationFinding:
    id: str
    type: FindingType
    description: str
    evidence: str = ""
    file_path: Optional[str] = None
    line_number: Optional[int] = None

@dataclass
class FixWorkflow:
    id: str
    issue_id: int
    branch_name: str
    phase: FixPhase = FixPhase.INITIALIZED
    started_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
```

### Step 2: Create GitHub Service (45 min)

Create `src/doit_cli/services/github_service.py`:

```python
"""Service for GitHub issue operations via gh CLI."""

import json
import subprocess
from typing import Optional

from ..models.fixit_models import GitHubIssue

class GitHubService:
    """Manages GitHub issue operations."""

    def get_issue(self, issue_id: int) -> Optional[GitHubIssue]:
        """Fetch a GitHub issue by ID."""
        result = subprocess.run(
            ["gh", "issue", "view", str(issue_id), "--json",
             "number,title,body,state,labels"],
            capture_output=True, text=True
        )
        if result.returncode != 0:
            return None
        data = json.loads(result.stdout)
        return GitHubIssue(
            number=data["number"],
            title=data["title"],
            body=data.get("body", ""),
            state=data["state"],
            labels=[l["name"] for l in data.get("labels", [])]
        )

    def list_bugs(self, label: str = "bug") -> list[GitHubIssue]:
        """List open issues with bug label."""
        result = subprocess.run(
            ["gh", "issue", "list", "--label", label, "--state", "open",
             "--json", "number,title,body,state,labels"],
            capture_output=True, text=True
        )
        if result.returncode != 0:
            return []
        return [
            GitHubIssue(
                number=d["number"],
                title=d["title"],
                body=d.get("body", ""),
                state=d["state"],
                labels=[l["name"] for l in d.get("labels", [])]
            )
            for d in json.loads(result.stdout)
        ]

    def close_issue(self, issue_id: int, comment: str = "") -> bool:
        """Close a GitHub issue."""
        cmd = ["gh", "issue", "close", str(issue_id)]
        if comment:
            cmd.extend(["--comment", comment])
        result = subprocess.run(cmd, capture_output=True)
        return result.returncode == 0
```

### Step 3: Create Fixit Service (60 min)

Create `src/doit_cli/services/fixit_service.py`:

```python
"""Service for orchestrating bug-fix workflow."""

import re
from pathlib import Path
from typing import Optional

from ..models.fixit_models import FixWorkflow, FixPhase, GitHubIssue
from .github_service import GitHubService
from .state_manager import StateManager

class FixitService:
    """Orchestrates the bug-fix workflow."""

    def __init__(
        self,
        github_service: Optional[GitHubService] = None,
        state_manager: Optional[StateManager] = None,
    ):
        self.github = github_service or GitHubService()
        self.state = state_manager or StateManager()

    def start_workflow(self, issue_id: int) -> FixWorkflow:
        """Start a new fix workflow for an issue."""
        issue = self.github.get_issue(issue_id)
        if not issue:
            raise ValueError(f"Issue #{issue_id} not found")

        branch_name = self._create_branch_name(issue)
        workflow = FixWorkflow(
            id=f"fixit-{issue_id}",
            issue_id=issue_id,
            branch_name=branch_name,
            phase=FixPhase.INITIALIZED,
        )
        self._save_state(workflow, issue)
        return workflow

    def _create_branch_name(self, issue: GitHubIssue) -> str:
        """Generate branch name from issue."""
        slug = re.sub(r'[^a-z0-9]+', '-', issue.title.lower())
        slug = slug.strip('-')[:50]
        return f"fix/{issue.number}-{slug}"

    def _save_state(self, workflow: FixWorkflow, issue: GitHubIssue):
        """Persist workflow state."""
        # Implementation using StateManager
        pass
```

### Step 4: Create CLI Command (45 min)

Create `src/doit_cli/cli/fixit_command.py`:

```python
"""CLI command for bug-fix workflow."""

from typing import Optional
import typer
from rich.console import Console

from ..services.fixit_service import FixitService
from ..services.github_service import GitHubService

app = typer.Typer(help="Bug-fix workflow commands")
console = Console()

@app.callback(invoke_without_command=True)
def fixit(
    ctx: typer.Context,
    issue_id: Optional[int] = typer.Argument(None, help="GitHub issue number"),
    resume: bool = typer.Option(False, "--resume", "-r", help="Resume workflow"),
    manual: bool = typer.Option(False, "--manual", "-m", help="Manual entry mode"),
):
    """Start or resume a bug-fix workflow."""
    if ctx.invoked_subcommand is not None:
        return

    service = FixitService()

    if issue_id:
        # Start workflow for specific issue
        workflow = service.start_workflow(issue_id)
        console.print(f"[green]Started fix workflow for #{issue_id}[/]")
    else:
        # Show bug list for selection
        bugs = service.github.list_bugs()
        # Interactive selection...

@app.command()
def list(
    label: str = typer.Option("bug", "--label", "-l"),
    format: str = typer.Option("table", "--format", "-f"),
):
    """List open bug issues."""
    github = GitHubService()
    bugs = github.list_bugs(label)
    # Display bugs...

@app.command()
def status(issue_id: Optional[int] = typer.Argument(None)):
    """Show fix workflow status."""
    # Implementation...
```

### Step 5: Register Command (5 min)

Update `src/doit_cli/main.py`:

```python
from .cli.fixit_command import app as fixit_app

# Add to existing app
app.add_typer(fixit_app, name="fixit")
```

### Step 6: Write Tests (60 min)

Create test files following the test patterns in the codebase:

- `tests/unit/test_fixit_models.py` - Model validation
- `tests/unit/test_github_service.py` - Mock subprocess calls
- `tests/unit/test_fixit_service.py` - Service logic
- `tests/integration/test_fixit_workflow.py` - End-to-end

---

## Verification Checklist

After implementation, verify:

- [x] `doit fixit start 123` starts workflow for issue #123
- [x] `doit fixit start` lists open bugs for selection
- [x] `doit fixit start 123 --resume` continues interrupted workflow
- [x] `doit fixit list` displays bug issues
- [x] `doit fixit status` shows workflow progress
- [x] State persists in `.doit/state/fixit-{id}.json`
- [x] All tests pass: `pytest tests/ -v` (806 tests passing)

---

## Key Integration Points

| Component | Purpose |
|-----------|---------|
| `StateManager` | Persist workflow state for resume |
| `WorkflowEngine` | Guided step execution |
| `status_command` | Show fix progress in dashboard |
| `reviewit` | Review fix plans |
| `taskit` | Generate implementation tasks |
| `checkin` | Close GitHub issue on completion |

---

## Estimated Timeline

| Phase | Task | Time |
|-------|------|------|
| 1 | Models | 30 min |
| 2 | GitHub Service | 45 min |
| 3 | Fixit Service | 60 min |
| 4 | CLI Commands | 45 min |
| 5 | Registration | 5 min |
| 6 | Unit Tests | 60 min |
| 7 | Integration Tests | 45 min |
| **Total** | | **~5 hours** |
