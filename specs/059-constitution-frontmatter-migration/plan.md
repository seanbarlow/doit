# Implementation Plan: Constitution Frontmatter Migration

**Branch**: `059-constitution-frontmatter-migration` | **Date**: 2026-04-20 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/059-constitution-frontmatter-migration/spec.md`

## Summary

`doit update` today copies bundled memory templates but does not migrate
shape drift in user-authored `.doit/memory/constitution.md`. Projects
initialized on 0.1.x have no YAML frontmatter and now fail the 0.2.0+
memory contract with an error. This feature introduces a
`ConstitutionMigrator` service invoked at the end of `run_init(update=True)`
that prepends or patches in a frontmatter skeleton with placeholder tokens,
preserving the body byte-for-byte. The validator is taught to classify
placeholder values as warnings (not errors) so a migrated file passes
verify-memory immediately. Downstream, the `/doit.constitution` skill gains
an enrichment branch that reads the body and replaces placeholders with
inferred real values — using the AI assistant already in the loop rather
than requiring the CLI to call an LLM.

Technical approach from research: reuse PyYAML (already a dep), introduce a
small `atomic_write` utility, and integrate the migrator via one new call
site in `init_command.py`. The migrator never raises — it returns a
`MigrationResult` so callers decide error propagation.

## Technical Context

**Language/Version**: Python 3.11+ (per constitution; consistent with rest of repo)
**Primary Dependencies**: Typer (CLI), Rich (logging), PyYAML (already declared `pyyaml>=6.0` in `pyproject.toml:31`)
**Storage**: File-based — markdown in `.doit/memory/constitution.md`
**Testing**: pytest with `typer.testing.CliRunner`, `tempfile.TemporaryDirectory()` fixtures
**Target Platform**: macOS, Linux, Windows (all doit-supported platforms)
**Project Type**: single — CLI tool (`src/doit_cli/`); no web, mobile, or multi-service split
**Performance Goals**: Migration completes in <500ms for files ≤50 KB (SC-004)
**Constraints**: Non-interactive (no prompts in CLI); byte-for-byte body preservation; atomic write (no partial state on error)
**Scale/Scope**: One file per project (`.doit/memory/constitution.md`); run once per `doit update` invocation

All fields filled without `NEEDS CLARIFICATION`.

## Architecture Overview

<!-- BEGIN:AUTO-GENERATED section="architecture" -->
```mermaid
flowchart TD
    subgraph "Presentation"
        UPDATE[doit update CLI]
        SKILL[/doit.constitution skill]
    end
    subgraph "Application"
        INIT[run_init update=True]
        MIGRATOR[ConstitutionMigrator service]
        VALIDATOR[memory_validator]
    end
    subgraph "Data"
        FS[(.doit/memory/constitution.md)]
        SCHEMA[(frontmatter.schema.json)]
    end
    UPDATE --> INIT --> MIGRATOR
    MIGRATOR --> FS
    MIGRATOR -. uses .-> SCHEMA
    SKILL --> FS
    SKILL -. uses .-> VALIDATOR
    VALIDATOR --> FS
    VALIDATOR -. uses .-> SCHEMA
```
<!-- END:AUTO-GENERATED -->

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

Evaluated against `.doit/memory/constitution.md` (v1.0.0) principles:

| Principle | Status | Note |
|:----------|:-------|:-----|
| I. Specification-First | ✓ Pass | Spec (spec.md) was written and validated before this plan. |
| II. Persistent Memory | ✓ Pass | Feature *strengthens* this principle by making the memory-file contract enforceable on legacy projects. |
| III. Auto-Generated Diagrams | ✓ Pass | Plan's ER diagram (data-model.md) and architecture diagram (above) are mermaid, generated in the template markers. |
| IV. Opinionated Workflow | ✓ Pass | Feature integrates into the existing `update` command; no new top-level commands or workflow deviations. |
| V. AI-Native Design | ✓ Pass | Enrichment uses the existing `/doit.constitution` skill surface; CLI remains non-interactive. |
| Quality Standards (tests) | ✓ Pass | Plan mandates contract + integration tests alongside implementation (see task scope below). |
| Tech Stack alignment | ✓ Pass | PyYAML already declared; no new dependencies. |

**Result**: all gates pass, no complexity-tracking entries needed. Re-check
after Phase 1 design: **still passing** (design introduces one new service
module, one new utility module, one new test file each — all within existing
architectural patterns).

## Project Structure

### Documentation (this feature)

```text
specs/059-constitution-frontmatter-migration/
├── spec.md              # Feature specification (/doit.specit)
├── plan.md              # This file (/doit.planit)
├── research.md          # Phase 0 — decisions & alternatives
├── data-model.md        # Phase 1 — entities + ER diagram
├── contracts/
│   └── migrator.md      # Phase 1 — ConstitutionMigrator Python API contract
├── quickstart.md        # Phase 1 — manual smoke-test scenarios
└── checklists/
    └── requirements.md  # Spec quality checklist
```

### Source Code (repository root)

New files:

```text
src/doit_cli/
├── services/
│   └── constitution_migrator.py      # NEW — migration service, PLACEHOLDER_REGISTRY, MigrationResult
└── utils/
    └── atomic_write.py               # NEW — write_text_atomic() helper

tests/
├── contract/
│   └── test_constitution_frontmatter_contract.py   # NEW — registry shape, schema bijection
└── integration/
    └── test_constitution_frontmatter_migration.py  # NEW — end-to-end migration scenarios
```

Modified files:

```text
src/doit_cli/
├── cli/
│   └── init_command.py                             # MOD — add migrator hook after copy_memory_templates
├── models/
│   └── memory_contract.py                          # MOD — placeholder-aware validation (WARNING severity)
├── services/
│   └── memory_validator.py                         # MOD — import PLACEHOLDER_REGISTRY; no duplication
└── templates/
    └── skills/
        └── doit.constitution/
            └── SKILL.md                            # MOD — add Step 2b enrichment branch
```

**Structure Decision**: single-project layout per constitution Tech Stack
section. All new code lives under `src/doit_cli/` in the same module
hierarchy already in use. Tests match the existing `unit/integration/
contract/e2e` split.

## Complexity Tracking

> No constitution violations — this section intentionally blank.

The feature introduces:

- 2 new modules (migrator service, atomic-write utility) — both
  single-responsibility and narrowly scoped.
- 1 new shared constant (`PLACEHOLDER_REGISTRY`) imported by validator to
  avoid duplication.
- 0 new dependencies, 0 new CLI commands, 0 new top-level abstractions.

## Phase 0 outputs

See [research.md](research.md). All eight decisions documented with
rationale and rejected alternatives. Zero open clarifications.

## Phase 1 outputs

- [data-model.md](data-model.md) — entities (`ConstitutionFile`,
  `FrontmatterBlock`, `FrontmatterField`, `PlaceholderToken`,
  `MigrationResult`), ER diagram, state-transition diagram, derived
  invariants.
- [contracts/migrator.md](contracts/migrator.md) — Python API contract
  for `ConstitutionMigrator`, including `PLACEHOLDER_REGISTRY`,
  `MigrationAction` enum, `MigrationResult` dataclass, error types,
  integration hook, validator integration, atomic-write helper signature,
  and the skill-side natural-language contract.
- [quickstart.md](quickstart.md) — five end-to-end scenarios covering
  every FR and SC, executable manually or as the basis for integration
  tests.

Agent context file update: run
`.doit/scripts/bash/update-agent-context.sh claude` as part of this plan's
completion (see "Next Steps").

## Ready for `/doit.taskit`

Plan is complete. All gates pass. Phase 1 artifacts generated and
cross-referenced. The next command (`/doit.taskit`) can break this plan
into a dependency-ordered task list.
