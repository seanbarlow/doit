# Research: Interactive Guided Workflows

**Date**: 2026-01-15
**Feature**: 030-guided-workflows

## Decision Summary

| Topic | Decision | Rationale |
|-------|----------|-----------|
| Interactive Prompts | Use Rich + readchar (existing pattern) | Already proven in doit init command |
| TTY Detection | `sys.stdin.isatty()` | Standard Python, cross-platform |
| Progress Display | Extend existing StepTracker | Consistent UX, code reuse |
| State Persistence | JSON files in `.doit/state/` | Simple, human-readable, git-friendly |
| Navigation | 'back'/'skip' keywords + arrow keys | Matches existing select_with_arrows pattern |

---

## Research Topics

### 1. Interactive Terminal Detection

**Decision**: Use `sys.stdin.isatty()` for TTY detection

**Rationale**: Already implemented in doit codebase at [src/doit_cli/__init__.py:1081](src/doit_cli/__init__.py#L1081)

**Pattern**:
```python
if sys.stdin.isatty():
    # Interactive mode - show prompts
    selected = select_with_arrows(options, prompt)
else:
    # Non-interactive mode - use defaults
    selected = default_value
```

**Alternatives Considered**:
- `os.isatty(sys.stdin.fileno())` - Equivalent but more verbose
- `curses.initscr()` - Overkill for simple detection
- Environment variable check only - Less reliable

---

### 2. Step-by-Step Prompts with Navigation

**Decision**: Extend `select_with_arrows()` pattern for multi-step workflows

**Rationale**: Proven pattern in doit init, supports arrow keys and escape handling

**Key Features from Existing Code**:
- Arrow key navigation (UP/DOWN)
- Enter to confirm, Escape to cancel
- Ctrl+C raises KeyboardInterrupt (can trap for state save)
- Rich Live display for flicker-free updates

**Navigation Extensions Needed**:
- 'back' keyword to return to previous step
- 'skip' keyword or Enter with empty input for optional steps
- Step history tracking for back navigation

**Pattern for Back Navigation**:
```python
class WorkflowNavigator:
    def __init__(self, steps: list[WorkflowStep]):
        self.steps = steps
        self.current_index = 0
        self.responses = {}  # step_id -> value

    def go_back(self):
        if self.current_index > 0:
            self.current_index -= 1
            return True
        return False

    def skip_current(self):
        if self.steps[self.current_index].required:
            return False
        self.current_index += 1
        return True
```

---

### 3. Progress Visualization

**Decision**: Extend existing `StepTracker` class with step numbering

**Rationale**: StepTracker already provides hierarchical tracking with status symbols

**Existing StepTracker Features**:
- Status states: pending, running, done, error, skipped
- Visual symbols: ● (done), ○ (pending), with color coding
- Live refresh callback integration
- Tree rendering for hierarchy

**Extensions Needed**:
- "Step X of Y" counter display
- Optional step marking (different visual treatment)
- Completion percentage calculation

**Pattern**:
```python
class WorkflowProgress(StepTracker):
    def get_progress_text(self) -> str:
        completed = len([s for s in self.steps if s["status"] == "done"])
        required = len([s for s in self.steps if not s.get("optional")])
        return f"Step {self.current_index + 1} of {len(self.steps)} ({completed}/{required} required complete)"
```

---

### 4. Workflow State Persistence

**Decision**: JSON files in `.doit/state/` directory

**Rationale**:
- Consistent with file-based storage pattern in constitution
- Human-readable for debugging
- Git-friendly (can be ignored or tracked per project preference)
- Simple serialization/deserialization

**State File Structure**:
```json
{
  "workflow_id": "init-2026-01-15-143022",
  "command_name": "init",
  "current_step": 2,
  "started_at": "2026-01-15T14:30:22Z",
  "updated_at": "2026-01-15T14:31:45Z",
  "responses": {
    "step_1": "value1",
    "step_2": "value2"
  },
  "completed_steps": ["step_1", "step_2"],
  "skipped_steps": []
}
```

**File Naming**: `.doit/state/{command}_{timestamp}.json`

**Cleanup Strategy**:
- Auto-delete on successful completion
- Keep failed/interrupted states for 7 days
- Offer cleanup on next run if stale

**Alternatives Considered**:
- SQLite database - Overkill for simple key-value state
- YAML files - Less suitable for programmatic updates
- In-memory only - Loses state on interrupt

---

### 5. Ctrl+C Handling for State Saving

**Decision**: Trap KeyboardInterrupt, save state, then re-raise or exit cleanly

**Rationale**: Existing pattern in codebase handles Ctrl+C gracefully

**Pattern**:
```python
try:
    with Live(tracker.render(), console=console, transient=True) as live:
        tracker.attach_refresh(lambda: live.update(tracker.render()))

        for step in workflow.steps:
            result = prompt_for_step(step)
            state_manager.save(workflow_id, step.id, result)

except KeyboardInterrupt:
    console.print("\n[yellow]Workflow interrupted. Progress saved.[/yellow]")
    state_manager.mark_interrupted(workflow_id)
    raise typer.Exit(1)
```

---

### 6. Non-Interactive Mode

**Decision**: Support via flag, environment variable, and auto-detection

**Rationale**: Matches FR-010, FR-011, FR-012 requirements

**Detection Order**:
1. `--non-interactive` flag (highest priority)
2. `DOIT_NON_INTERACTIVE=true` environment variable
3. `not sys.stdin.isatty()` (piped input or non-TTY)

**Behavior in Non-Interactive Mode**:
- Use default values for all optional inputs
- Fail with clear error if required input missing
- No progress display animations
- Machine-readable output (JSON or simple text)

---

### 7. Input Validation Patterns

**Decision**: Validator classes with immediate feedback

**Rationale**: Clean separation, testable, reusable across steps

**Existing Validation Pattern** (from validation_models.py):
```python
@dataclass
class ValidationResult:
    passed: bool
    error_message: str | None = None
    suggestion: str | None = None
```

**Step Validation Pattern**:
```python
class StepValidator:
    def validate(self, value: str, context: dict) -> ValidationResult:
        """Validate input value with access to previous step responses."""
        pass

class PathExistsValidator(StepValidator):
    def validate(self, value: str, context: dict) -> ValidationResult:
        path = Path(value)
        if not path.exists():
            return ValidationResult(
                passed=False,
                error_message=f"Path does not exist: {value}",
                suggestion="Create the file or specify a different path"
            )
        return ValidationResult(passed=True)
```

---

## Dependencies

No new dependencies required. All functionality can be built with existing stack:

| Library | Version | Purpose |
|---------|---------|---------|
| typer | >=0.9.0 | CLI framework |
| rich | >=13.0.0 | Terminal formatting, Live display |
| readchar | (current) | Cross-platform key input |

---

## Risks and Mitigations

| Risk | Mitigation |
|------|------------|
| Terminal resize during workflow | Rich handles resize events automatically |
| State file corruption | Use atomic writes (write to temp, rename) |
| Large state files | Limit step history, periodic cleanup |
| Cross-platform key differences | readchar abstracts platform differences |

---

## References

- Existing implementation: [src/doit_cli/__init__.py](src/doit_cli/__init__.py) (StepTracker, select_with_arrows)
- Rich documentation: https://rich.readthedocs.io/
- readchar documentation: https://pypi.org/project/readchar/
