# Contract: `ConstitutionMigrator`

**Module**: `src/doit_cli/services/constitution_migrator.py`
**Public API version**: 1 (introduced in doit 0.3.0)

This is not an HTTP API. The doit CLI is a Python package; the contract
expressed here is the **Python service API** the migration exposes to the
rest of the codebase and the semantic contract both sides (CLI and skill)
must honour.

## 1. Constants

```python
from typing import Final, Mapping, Any

REQUIRED_FIELDS: Final[tuple[str, ...]] = (
    "id", "name", "kind", "phase", "icon", "tagline", "dependencies",
)

PLACEHOLDER_REGISTRY: Final[Mapping[str, Any]] = {
    "id":           "[PROJECT_ID]",
    "name":         "[PROJECT_NAME]",
    "kind":         "[PROJECT_KIND]",
    "phase":        "[PROJECT_PHASE]",
    "icon":         "[PROJECT_ICON]",
    "tagline":      "[PROJECT_TAGLINE]",
    "dependencies": ["[PROJECT_DEPENDENCIES]"],
}
```

**Invariants**:

- `REQUIRED_FIELDS` order matches `frontmatter.schema.json`'s `required`
  array, index-by-index.
- Every key in `PLACEHOLDER_REGISTRY` is in `REQUIRED_FIELDS` and vice
  versa (contract test enforces bijection).
- Values in `PLACEHOLDER_REGISTRY` are exact-match sentinels. Callers use
  `==` (not regex, not `in`) to detect placeholders.

## 2. Result types

```python
from dataclasses import dataclass
from enum import Enum
from pathlib import Path

class MigrationAction(str, Enum):
    NO_OP = "no_op"
    PREPENDED = "prepended"
    PATCHED = "patched"
    ERROR = "error"


@dataclass(frozen=True)
class MigrationResult:
    path: Path
    action: MigrationAction
    added_fields: tuple[str, ...]
    preserved_body_hash: bytes | None
    error: "DoitError | None"
```

**Invariants**:

- When `action == MigrationAction.ERROR`, `error` is non-None and
  `preserved_body_hash` is None.
- When `action != ERROR`, `error` is None and `preserved_body_hash` is a
  32-byte SHA-256 digest.
- `added_fields` is non-empty **only** when
  `action ∈ {PREPENDED, PATCHED}`.

## 3. Public function

```python
def migrate_constitution(path: Path) -> MigrationResult:
    """
    Migrate .doit/memory/constitution.md in place to conform to the 0.2.0+
    memory contract.

    Behaviour:
      - If `path` does not exist → MigrationResult(action=NO_OP, added_fields=())
      - If file has no YAML frontmatter → prepend placeholder skeleton,
        preserve body byte-for-byte → action=PREPENDED.
      - If file has well-formed frontmatter missing required fields →
        patch in missing fields with placeholder values, preserve body
        and existing field values byte-for-byte → action=PATCHED.
      - If file has well-formed frontmatter with all required fields →
        no write → action=NO_OP.
      - If file has frontmatter block but YAML is malformed → no write →
        action=ERROR with a DoitError subclass describing the YAML issue.

    Never:
      - Reorders existing frontmatter keys.
      - Strips unknown frontmatter keys.
      - Rewrites body content.
      - Prompts the user.
    """
```

## 4. Error types

```python
from doit_cli.errors import DoitError

class ConstitutionMigrationError(DoitError):
    """Base class for migration errors. Subclasses set exit_code."""
    exit_code: int = ExitCode.FAILURE

class MalformedFrontmatterError(ConstitutionMigrationError):
    """Raised when an existing --- block contains invalid YAML.
    Message includes line and column from yaml.YAMLError.problem_mark."""
    exit_code: int = ExitCode.VALIDATION_ERROR
```

Behavioural contract:

- `migrate_constitution` **never raises** — errors are returned in
  `MigrationResult.error`. The caller (init flow) decides whether to
  `raise typer.Exit(...)`.
- Library callers (tests, future services) can inspect `.error` and act
  programmatically.

## 5. Integration hook

```python
# src/doit_cli/cli/init_command.py, inside run_init() when update=True
from doit_cli.services.constitution_migrator import migrate_constitution

# ... after copy_memory_templates(...)
migration = migrate_constitution(project.path / ".doit/memory/constitution.md")
if migration.action == MigrationAction.ERROR:
    raise migration.error  # becomes typer.Exit with VALIDATION_ERROR
# NO_OP / PREPENDED / PATCHED → log and continue.
```

Log levels (using the existing Rich console):

| Action | Message |
|:-------|:--------|
| `NO_OP` | nothing (silent) |
| `PREPENDED` | `[yellow]Added YAML frontmatter to .doit/memory/constitution.md — run /doit.constitution to fill in placeholders.[/yellow]` |
| `PATCHED` | `[yellow]Added {N} missing frontmatter field(s) to .doit/memory/constitution.md: {field_list}[/yellow]` |
| `ERROR` | `[red]Could not migrate constitution.md: {error.message}[/red]` (exit after) |

## 6. Validator integration

`src/doit_cli/models/memory_contract.py:ConstitutionFrontmatter.validate()`
imports `PLACEHOLDER_REGISTRY` from
`src/doit_cli/services/constitution_migrator.py`. When a field value
exact-matches its placeholder, emit:

```python
MemoryContractIssue(
    file="constitution.md",
    severity=MemoryIssueSeverity.WARNING,
    field_name=key,
    message=f"Field '{key}' contains placeholder value — run /doit.constitution to enrich.",
)
```

Invariant: **placeholder-present WARNINGs never co-exist with "missing
field" ERRORs for the same key** — a placeholder is by definition
present. Callers can treat warnings as a distinct state.

## 7. Atomic-write helper

```python
# src/doit_cli/utils/atomic_write.py (new)
def write_text_atomic(path: Path, content: str, *, encoding: str = "utf-8") -> None:
    """
    Write `content` to `path` atomically:
      1. Create a sibling temp file in the same directory.
      2. Write and fsync.
      3. os.replace() to the final path.

    Raises OSError on any failure; caller wraps in DoitError.
    """
```

Invariants:

- The original file bytes are unchanged if any step raises.
- The new file's mtime is the rename timestamp, not the temp-write
  timestamp.

## 8. Skill contract (`/doit.constitution` Step 2b)

The skill is authored in `SKILL.md`; it's natural-language instruction,
not code. The contract it must satisfy:

1. **Trigger**: `PLACEHOLDER_REGISTRY` has at least one token that
   exactly matches a value in the parsed frontmatter of
   `.doit/memory/constitution.md`.
2. **Inputs**: file contents, `doit context show` output (project
   directory basename, roadmap, tech-stack).
3. **Output**: rewritten `.doit/memory/constitution.md` in which each
   placeholder value is replaced by a concrete inferred value **OR**
   left as the placeholder when inference is low-confidence. The body
   (every byte after the closing frontmatter `---`) is byte-identical to
   the input.
4. **Verification**: after the rewrite, the skill runs
   `doit verify-memory . --json` and MUST see zero placeholder warnings
   for the enriched fields. Any remaining placeholder fields MUST be
   reported to the user in the skill's final summary.
5. **Fallback**: if the skill cannot confidently infer a value for a
   specific field, it MUST preserve that field's placeholder and
   explicitly list it in the skill's output under a "Needs human input"
   section.

## 9. Backwards compatibility

- Existing constitutions with complete frontmatter are untouched
  (`NO_OP`).
- Existing constitutions with extra/unknown frontmatter keys are
  preserved verbatim.
- No new CLI flags. No new CLI subcommands. The migration runs
  silently-on-success inside `doit update` / `doit init --update`.
