# Research: Bug-Fix Workflow Command

**Date**: 2026-01-16
**Feature**: 034-fixit-workflow

## Research Summary

This document captures technical decisions and research findings for the fixit command implementation.

---

## 1. GitHub Issue Integration

### Decision: Use `gh` CLI subprocess calls

**Rationale**:
- GitHub CLI (`gh`) is already a common dependency for developers
- Handles authentication automatically (OAuth, tokens, SSH)
- Well-documented JSON output format for parsing
- Avoids managing GitHub API tokens directly in doit

**Alternatives Considered**:
- **PyGithub library**: Requires separate token management, adds dependency
- **Direct REST API with httpx**: More control but requires auth handling
- **GraphQL API**: Overkill for simple issue operations

**Implementation Pattern**:
```python
import subprocess
import json

def get_issue(issue_id: int) -> dict | None:
    """Fetch GitHub issue by ID using gh CLI."""
    result = subprocess.run(
        ["gh", "issue", "view", str(issue_id), "--json",
         "number,title,body,state,labels,comments"],
        capture_output=True, text=True
    )
    if result.returncode != 0:
        return None
    return json.loads(result.stdout)

def list_bugs() -> list[dict]:
    """List open issues labeled 'bug'."""
    result = subprocess.run(
        ["gh", "issue", "list", "--label", "bug", "--state", "open",
         "--json", "number,title,labels,createdAt"],
        capture_output=True, text=True
    )
    if result.returncode != 0:
        return []
    return json.loads(result.stdout)
```

---

## 2. Workflow State Persistence

### Decision: Extend existing StateManager

**Rationale**:
- `StateManager` in `services/state_manager.py` already handles workflow state
- Stores state as JSON in `.doit/state/` directory
- Supports save, load, delete, and cleanup operations
- Consistent with existing init command workflow

**Extension Points**:
- Add `FixWorkflowState` model with fix-specific fields
- Store fix workflow state with key format: `fixit-{issue_id}`
- Include phase, investigation findings, and fix plan status

**State File Structure**:
```json
{
  "workflow_id": "fixit-123",
  "command_name": "fixit",
  "issue_id": 123,
  "branch_name": "fix/123-brief-description",
  "phase": "investigation",
  "investigation_findings": [],
  "fix_plan_status": "pending",
  "started_at": "2026-01-16T10:00:00Z",
  "updated_at": "2026-01-16T10:30:00Z"
}
```

---

## 3. Fix Branch Naming

### Decision: `fix/{issue-id}-{slugified-title}`

**Rationale**:
- Follows common git branch naming conventions
- Issue ID provides traceability
- Slugified title adds human-readable context
- Consistent with feature branch pattern (e.g., `034-fixit-workflow`)

**Implementation**:
```python
import re

def create_branch_name(issue_id: int, title: str) -> str:
    """Generate fix branch name from issue."""
    slug = re.sub(r'[^a-z0-9]+', '-', title.lower())
    slug = slug.strip('-')[:50]  # Limit length
    return f"fix/{issue_id}-{slug}"
```

---

## 4. AI-Assisted Investigation

### Decision: Generate investigation prompts, not execute AI directly

**Rationale**:
- doit is a CLI tool that works *with* AI assistants, not replaces them
- Generate structured prompts for Claude/Copilot to execute
- Keep investigation findings in markdown for human review
- Avoids API costs and complexity within the CLI

**Investigation Flow**:
1. Create `investigation-plan.md` with structured prompts
2. AI assistant executes prompts and records findings
3. User reviews and confirms findings
4. System generates `fix-plan.md` from confirmed findings

**Investigation Plan Template**:
```markdown
# Investigation Plan: Issue #{issue_id}

## Issue Summary
{issue_title}
{issue_description}

## Investigation Checkpoints

### 1. Reproduce the Bug
- [ ] Set up test environment
- [ ] Follow reproduction steps from issue
- [ ] Document actual vs expected behavior

### 2. Identify Related Code
Ask the AI to:
- Search for code related to: {keywords from issue}
- Find recent commits touching these files
- Identify test files for affected code

### 3. Root Cause Analysis
For each hypothesis:
- [ ] Hypothesis: {description}
- [ ] Evidence: {what supports this}
- [ ] Disproved because: {if applicable}

### 4. Confirmed Root Cause
{Document the confirmed root cause here}
```

---

## 5. Integration with Existing Commands

### Decision: Reuse reviewit/taskit via command composition

**Rationale**:
- Maintains consistency with existing workflow
- No duplication of review/task logic
- Users already familiar with these commands

**Integration Points**:

| Phase | Existing Command | How |
|-------|------------------|-----|
| Fix Plan Review | `/doit.reviewit` | Pass `fix-plan.md` as artifact to review |
| Task Generation | `/doit.taskit` | Generate tasks from approved fix plan |
| Completion | `/doit.checkin` | Hook to close GitHub issue on merge |

**Checkin Hook**:
```python
def on_checkin_complete(branch_name: str):
    """Close GitHub issue when fix is checked in."""
    if branch_name.startswith("fix/"):
        issue_id = extract_issue_id(branch_name)
        close_issue(issue_id, branch_name)
```

---

## 6. Offline/Degraded Mode

### Decision: Graceful degradation with manual entry

**Rationale**:
- Network issues shouldn't block development
- Manual fallback provides usable experience
- Clear messaging about limited functionality

**Implementation**:
```python
def start_fix_workflow(issue_id: int | None = None):
    """Start fix workflow, with offline fallback."""
    if issue_id:
        issue = fetch_issue(issue_id)
        if issue is None:
            if is_offline():
                console.print("[yellow]Offline mode: Enter issue details manually[/]")
                issue = prompt_manual_issue_entry(issue_id)
            else:
                raise IssueNotFoundError(issue_id)
```

---

## 7. Fix Plan Document Structure

### Decision: Structured markdown matching spec.md pattern

**Rationale**:
- Consistent with other doit artifacts
- Reviewable by humans and AI
- Supports reviewit command integration

**fix-plan.md Template**:
```markdown
# Fix Plan: Issue #{issue_id}

**Issue**: {title}
**Branch**: {branch_name}
**Status**: {pending|approved|rejected}

## Root Cause

{Confirmed root cause from investigation}

## Proposed Fix

### Changes Required

| File | Change Description |
|------|-------------------|
| {file} | {description} |

### Implementation Approach

{Step-by-step approach}

## Risk Assessment

**Risk Level**: {low|medium|high}
**Affected Areas**: {list of affected functionality}
**Regression Risk**: {assessment}

## Testing Strategy

- [ ] Unit tests for fix
- [ ] Regression test for original bug
- [ ] Integration tests if needed

## Approval

- [ ] Code review approved
- [ ] Risk assessment accepted
```

---

## Summary

| Area | Decision | Key Technology |
|------|----------|----------------|
| GitHub Integration | `gh` CLI subprocess | subprocess, json |
| State Persistence | Extend StateManager | Existing service |
| Branch Naming | `fix/{id}-{slug}` | regex slugify |
| AI Investigation | Generate prompts | Markdown templates |
| Command Integration | Reuse via composition | Command hooks |
| Offline Mode | Graceful degradation | Manual entry fallback |
| Fix Plan | Structured markdown | Consistent with spec.md |
