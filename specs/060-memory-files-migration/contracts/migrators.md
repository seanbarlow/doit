# Contract: Roadmap + Tech-Stack Migrators & Enrichers

**Modules**:

- `src/doit_cli/services/roadmap_migrator.py` (new)
- `src/doit_cli/services/tech_stack_migrator.py` (new)
- `src/doit_cli/services/roadmap_enricher.py` (new)
- `src/doit_cli/services/tech_stack_enricher.py` (new)
- `src/doit_cli/services/_memory_shape.py` (new, internal)

**Public API version**: 1 (introduced in doit 0.4.0)

This contract **reuses** spec 059's `MigrationAction`, `MigrationResult`,
`EnrichmentAction`, `EnrichmentResult`, and
`write_text_atomic`. No new result types. Cross-refer
[specs/059-constitution-frontmatter-migration/contracts/migrator.md](../../059-constitution-frontmatter-migration/contracts/migrator.md).

## 1. Constants

```python
from typing import Final

# roadmap_migrator.py
REQUIRED_ROADMAP_H2: Final[tuple[str, ...]] = ("Active Requirements",)
REQUIRED_ROADMAP_H3_UNDER_ACTIVE_REQS: Final[tuple[str, ...]] = (
    "P1", "P2", "P3", "P4",
)

# tech_stack_migrator.py
REQUIRED_TECHSTACK_H2: Final[tuple[str, ...]] = ("Tech Stack",)
REQUIRED_TECHSTACK_H3_UNDER_TECH_STACK: Final[tuple[str, ...]] = (
    "Languages", "Frameworks", "Libraries",
)
```

**Invariants**:

- Tuples preserve canonical schema order (used for insertion order).
- A contract test asserts these match the validator's rules in
  `memory_validator._validate_roadmap` / `_validate_tech_stack`.

## 2. Shared internal helper

```python
# src/doit_cli/services/_memory_shape.py
def insert_section_if_missing(
    source: str,
    h2_title: str,
    h3_titles: tuple[str, ...],
    *,
    stub_body: Callable[[str], str],
) -> tuple[str, list[str]]:
    """Return (new_source, added_titles).

    Scans ``source`` for an H2 matching ``h2_title``. If missing, appends
    the full H2 + H3 block built from ``stub_body(h3_title)``. If the
    H2 is present but some H3s are missing, inserts only the missing
    H3 subsections at the end of the existing H2 section, preserving
    the existing subsection order.

    Case-insensitive heading match (matches validator semantics).
    """
```

Internal (underscore-prefixed). Tests exercise it directly.

## 3. Public migrator APIs

```python
from pathlib import Path
from doit_cli.services.constitution_migrator import MigrationResult


def migrate_roadmap(path: Path) -> MigrationResult:
    """Ensure `.doit/memory/roadmap.md` has `## Active Requirements`
    + `### P1..P4` subsections. Body-preserving, atomic-write.

    - Missing file → NO_OP.
    - All required sections present → NO_OP.
    - H2 missing → PREPENDED (inserts H2 block at end of file).
    - H2 present, some H3s missing → PATCHED.
    - I/O error → ERROR with populated `MigrationResult.error`.
    """


def migrate_tech_stack(path: Path) -> MigrationResult:
    """Ensure `.doit/memory/tech-stack.md` has `## Tech Stack`
    + `### Languages / Frameworks / Libraries`. Same semantics as
    migrate_roadmap."""
```

Both never raise.

## 4. Public enricher APIs

```python
from pathlib import Path
from doit_cli.services.constitution_enricher import EnrichmentResult


def enrich_roadmap(
    path: Path, *, project_root: Path | None = None
) -> EnrichmentResult:
    """Replace placeholder Vision + seed completed-items hint.

    Reads:
      - `project_root / .doit/memory/constitution.md` for Project Purpose
      - `project_root / .doit/memory/completed_roadmap.md` for shipped items

    Behaviour:
      - File missing → NO_OP.
      - No placeholder subsections → NO_OP.
      - Vision seeded from Project Purpose → contributes to ENRICHED.
      - Completed items seeded → contributes to ENRICHED.
      - Any subsection left as placeholder after this run → listed in
        `unresolved_fields`; action becomes PARTIAL.
    """


def enrich_tech_stack(
    path: Path, *, project_root: Path | None = None
) -> EnrichmentResult:
    """Populate placeholder-stubbed Languages/Frameworks/Libraries/
    Infrastructure/Deployment subsections from constitution.md.

    Reads `project_root / .doit/memory/constitution.md` and extracts
    bullet content from `## Tech Stack / ## Infrastructure / ## Deployment`
    sections (including any `### <Group>` subsections under Tech Stack).

    - Verbatim extraction — no smartening.
    - Only overwrites subsections flagged is_placeholder.
    - Missing source → all target subsections become unresolved; action
      PARTIAL (or NO_OP if there were no placeholders to begin with).
    """
```

Both never raise.

## 5. Init hook integration

```python
# src/doit_cli/cli/init_command.py, inside run_init() after existing
# constitution migration block from spec 059:

from ..services.roadmap_migrator import migrate_roadmap
from ..services.tech_stack_migrator import migrate_tech_stack

for migrator_fn, filename in (
    (migrate_roadmap, "roadmap.md"),
    (migrate_tech_stack, "tech-stack.md"),
):
    result = migrator_fn(project.doit_folder / "memory" / filename)
    if result.action is MigrationAction.PREPENDED:
        console.print(
            f"[yellow]Added required sections to "
            f".doit/memory/{filename} — run /doit.roadmapit or "
            f"/doit.constitution to fill placeholders.[/yellow]"
        )
        result.updated_files.append(result.path)
    elif result.action is MigrationAction.PATCHED:
        console.print(
            f"[yellow]Added "
            f"{len(result.added_fields)} missing section(s) "
            f"to .doit/memory/{filename}: "
            f"{', '.join(result.added_fields)}[/yellow]"
        )
        result.updated_files.append(result.path)
    elif result.action is MigrationAction.ERROR and result.error is not None:
        console.print(
            f"[red]Could not migrate {filename}: {result.error}[/red]"
        )
        err_code = (
            ExitCode.VALIDATION_ERROR
            if isinstance(result.error, DoitValidationError)
            else ExitCode.FAILURE
        )
        raise typer.Exit(code=err_code)
```

Order: constitution (existing) → roadmap → tech-stack. Short-circuits
on first ERROR.

## 6. CLI subcommands

Added under the existing `memory_app` group
(`src/doit_cli/cli/memory_command.py`):

```text
doit memory enrich roadmap [PATH] [--json]
doit memory enrich tech-stack [PATH] [--json]
doit memory migrate [PATH] [--json]
```

Exit code contract (same as spec 059's `doit constitution enrich`):

- `0` — ENRICHED or NO_OP (everything resolved or nothing to do).
- `1` — PARTIAL (some fields unresolved).
- `2` — ERROR (file / validation error).

The `doit memory migrate` umbrella runs constitution + roadmap +
tech-stack migrators in order; exits with the first non-zero code
encountered. Output is a list of per-file `MigrationResult` objects in
JSON mode, or a Rich table in default mode.

## 7. Validator integration

**No changes** to `memory_validator.py`. The existing
`_validate_roadmap` / `_validate_tech_stack` rules already enforce the
same required-section set the new migrators emit. The existing
`_is_placeholder` body-token detection already classifies stubs as
placeholder with WARNING severity (via the adjacent "file contains
template placeholders" warning path).

The contract test at
`tests/contract/test_memory_files_migration_contract.py` asserts the
validator's required-section tuples match the migrator's
`REQUIRED_*` constants, index-by-index.

## 8. Skill integration

**`/doit.roadmapit` skill** gains a step analogous to spec 059's
Step 2b:

```markdown
**Placeholder-frontmatter enrichment (auto-triggered)**: `doit update`
inserts placeholder stubs into `.doit/memory/roadmap.md` when required
sections are missing. Do the mechanical pass first via the CLI, then
follow up:

    doit memory enrich roadmap --json

Exit codes: 0 (done / nothing to do), 1 (partial — see
`unresolved_fields`), 2 (file error).
```

**`/doit.constitution` skill** does NOT change — tech-stack content
lives in a separate skill-less file now, and the user-facing
enrichment command is `doit memory enrich tech-stack`. No new skill
is introduced; the `/doit.constitution cleanup` subcommand already
handles the "extract from constitution" side.

## 9. Backwards compatibility

- Existing `doit constitution enrich` CLI (spec 059) unchanged.
- `copy_memory_templates` behaviour unchanged — the migrators only
  act on files that already exist.
- Running spec 060's migrators on a project that predates spec 059 is
  safe: the constitution migrator runs first, then these two. If the
  user has an old-style constitution with embedded tech stack, the
  user gets:
  1. `constitution.md` frontmatter added (spec 059).
  2. `tech-stack.md` gets shape-migrated (spec 060 US1).
  3. `/doit.constitution cleanup` extracts tech stack to tech-stack.md
     (pre-existing).
  4. `doit memory enrich tech-stack` populates placeholders (spec 060 US2).
