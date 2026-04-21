# Personas.md Migration

**Completed**: 2026-04-21
**Branch**: `062-personas-migration`
**Type**: Infrastructure — closes the memory-file-migration pattern

## Overview

Extends the migrator + enricher + validator pattern from specs 059 (constitution frontmatter) and 060 (roadmap + tech-stack shape) to the fourth and final `.doit/memory/*.md` file: `personas.md`. With this feature, all four memory files share:

- A **shape migrator** that inserts placeholder stubs for missing required sections while preserving existing prose byte-for-byte.
- A **deterministic enricher** CLI.
- A **validator rule** in `memory_validator.verify_memory_contract`.
- A row in the **`doit memory migrate` umbrella**.

Personas differ from the other three files in two deliberate ways:

1. **Opt-in**: `.doit/memory/personas.md` is NOT auto-created. Absence is a valid state. Constitution/roadmap/tech-stack are required; personas are a methodology choice (projects that don't use persona-driven workflows continue to work without emitting errors).
2. **Linter-only enricher**: the enricher detects `{placeholder}` tokens and reports `PARTIAL`, but **never modifies the file**. Persona content (names, roles, goals) is intrinsically project-specific — an enricher has no upstream source to infer it. Users populate via `/doit.roadmapit` or `/doit.researchit` (interactive Q&A).

## Requirements Implemented

| ID | Description | Status |
|----|-------------|--------|
| FR-001 | `migrate_personas(path) -> MigrationResult`, reusing constitution types | Done |
| FR-002 | File absent → NO_OP, no file created | Done |
| FR-003 | Both H2s present → NO_OP, byte-identical | Done |
| FR-004 | Missing H2(s) → PATCHED with inserted stub(s) | Done |
| FR-005 | Prose outside stubs preserved byte-for-byte | Done |
| FR-006 | Inserted stubs carry ≥ 3 `[TOKEN]` placeholders | Done |
| FR-007 | `enrich_personas(path) -> EnrichmentResult`, reusing constitution types | Done |
| FR-008 | Enricher detects `{…}` tokens, reports in `unresolved_fields` | Done |
| FR-009 | Linter-only: PARTIAL on placeholders, never fills content | Done |
| FR-010 | Missing file → enricher NO_OP, exit 0 | Done |
| FR-011 | `doit memory enrich personas` subcommand, exit codes 0/1/2 | Done |
| FR-012 | Umbrella `doit memory migrate` emits 4 deterministic rows | Done |
| FR-013 | `_validate_personas` enforces H2s + `P-\d{3}` ID regex | Done |
| FR-014 | Validator emits zero issues when file absent | Done |
| FR-015 | Contract test locks `REQUIRED_PERSONAS_H2` ↔ validator | Done |
| FR-016 | Contract test locks ID bijection | Done |
| FR-017 | Specs 059/060/061 tests pass unchanged | Done |

## Technical Details

### Required shape

```text
## Persona Summary           (table of personas keyed by P-NNN ID)
## Detailed Profiles         (### Persona: P-NNN blocks)
```

No H3 subsections required — persona entries are project-specific content authored via `/doit.roadmapit` or `/doit.researchit`. The two H2s are the minimum the context loader (spec 056) and the `/doit.specit` persona matcher (spec 057) rely on. Other template sections (`## Relationship Map`, `## Traceability`) remain optional.

### Migrator structure — reuses the shared helper without extending it

```python
REQUIRED_PERSONAS_H2: Final = ("Persona Summary", "Detailed Profiles")

def migrate_personas(path: Path) -> MigrationResult:
    # Opt-in: absent file is a valid NO_OP.
    if not path.exists():
        return MigrationResult(path=path, action=MigrationAction.NO_OP)
    # Two required H2s, no required H3s → call the shared helper twice.
    working = original
    for h2_title in REQUIRED_PERSONAS_H2:
        working, added_this = insert_section_if_missing(
            working, h2_title=h2_title, h3_titles=(),
            stub_body=_personas_stub_body,
        )
        added.extend(added_this)
    ...
```

Spec 061's shared `matchers` parameter is **not used** here — exact-match is correct because persona H2 titles are not decoration-prone.

### Persona ID regex

```python
_PERSONA_ID_RE = re.compile(r"^Persona: P-\d{3}$")
```

Scoped to `## Detailed Profiles`. Case-sensitive, anchored; rejects `P-1`, `P-01`, `P-1000`, `p-001`, `Persona-001`, etc. Three-digit zero-padded matches the established convention in [`personas-output-template.md`](../../src/doit_cli/templates/personas-output-template.md) and the `/doit.specit` persona matcher.

### Never returns `PREPENDED` or `ENRICHED`

- **`PREPENDED`** (migrator): conflicts with opt-in — it would require creating the file first. Impossible state.
- **`ENRICHED`** (enricher): linter-only design — the enricher never modifies the file. Impossible state.

Both are documented in the module docstrings and locked by tests.

## Files Changed

- [src/doit_cli/services/personas_migrator.py](../../src/doit_cli/services/personas_migrator.py) — NEW
- [src/doit_cli/services/personas_enricher.py](../../src/doit_cli/services/personas_enricher.py) — NEW
- [src/doit_cli/services/memory_validator.py](../../src/doit_cli/services/memory_validator.py) — +`_validate_personas`, `_PERSONA_ID_RE`; reuses `REQUIRED_PERSONAS_H2` from migrator (single source of truth)
- [src/doit_cli/cli/memory_command.py](../../src/doit_cli/cli/memory_command.py) — +`doit memory enrich personas` subcommand, +personas row in umbrella migrate, +personas-specific `/doit.roadmapit` / `/doit.researchit` hint in non-JSON PARTIAL output
- [tests/unit/services/test_personas_migrator.py](../../tests/unit/services/test_personas_migrator.py) — NEW
- [tests/unit/services/test_personas_enricher.py](../../tests/unit/services/test_personas_enricher.py) — NEW
- [tests/integration/test_personas_migration.py](../../tests/integration/test_personas_migration.py) — NEW
- [tests/contract/test_personas_validator_migrator_alignment.py](../../tests/contract/test_personas_validator_migrator_alignment.py) — NEW
- [tests/contract/test_memory_files_migration_contract.py](../../tests/contract/test_memory_files_migration_contract.py) — +2 tests (H2 alignment + type reuse)
- [CHANGELOG.md](../../CHANGELOG.md) — `[Unreleased]` Added + Changed entries

## Testing

### Automated

- **47 feature tests** pass: 9 unit (constants + enricher behaviour) + 10 integration (migrator + CLI) + 28 contract (ID bijection + umbrella ordering + required-H2 alignment + SC-11 WARNING branch).
- **Full suite**: 2,296 passed / 182 skipped / 0 failed.
- **Coverage (new files)**: 81% (`personas_enricher.py` 92%, `personas_migrator.py` 75%). Missed lines are error-path branches; matches tech_stack_migrator's 86% / roadmap_migrator's 88% profile from specs 060/061.
- **Ruff**: clean on all spec-062 new files.
- **Mypy**: clean (full tree).

### Dogfood

`doit memory migrate .` on the doit repo's own memory directory now reports 4 rows; personas.md row = `no_op` (this project doesn't use personas). `doit verify-memory .` → `0 error(s), 0 warning(s)`. Working tree remains clean.

### Manual tests

None — every `quickstart.md` scenario (1–15) is automated, including SC-11 (shape-valid-but-content-empty WARNING) added during the reviewit pass.

## Related

- **Precursors**: #059 (constitution frontmatter), #060 (roadmap + tech-stack shape), #061 (roadmap H3 prefix-match fix). Spec 062 completes the four-spec closure.
- **Persona infrastructure**: depends on the persona template introduced by #053 and the context-loader wiring from #056; consumed by the persona matcher in #057.
- **Follow-ups (out of scope)**: two pre-existing ruff warnings in unrelated files (B904 in `memory_command.py:317`, SIM110 in `memory_validator.py:414`) remain tracked for a separate cleanup spec.
