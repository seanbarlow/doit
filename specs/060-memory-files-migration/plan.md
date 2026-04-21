# Implementation Plan: Memory Files Migration (roadmap.md, tech-stack.md)

**Branch**: `060-memory-files-migration` | **Date**: 2026-04-21 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/060-memory-files-migration/spec.md`

## Summary

Extend spec 059's migrator + enricher pattern from `.doit/memory/constitution.md`
to the two other memory files the validator enforces shape on:
`roadmap.md` (needs `## Active Requirements` + `### P1..P4`) and
`tech-stack.md` (needs `## Tech Stack` + `### Languages/Frameworks/Libraries`).

Unlike the constitution work, these files have no YAML frontmatter —
the migration target is markdown-section shape. Two new migrators
(`RoadmapMigrator`, `TechStackMigrator`) insert missing sections with
placeholder stubs, preserving body bytes via the
`write_text_atomic` helper already shipped by spec 059. Two new
enrichers (`RoadmapEnricher`, `TechStackEnricher`) populate those
placeholders deterministically by parsing `.doit/memory/constitution.md`
(tech-stack content, Project Purpose sentence) and
`.doit/memory/completed_roadmap.md` (shipped items). New CLIs live
under the existing `doit memory` Typer group:
`doit memory enrich roadmap`, `doit memory enrich tech-stack`, and an
umbrella `doit memory migrate`. No new dependencies, no new
infrastructure, no LLM calls from the CLI.

Roadmap priority-item generation is **explicitly excluded** — that's
product judgment that belongs to the `/doit.roadmapit` skill.

## Technical Context

**Language/Version**: Python 3.11+ (constitution baseline)
**Primary Dependencies**: Typer (CLI), Rich (logging), PyYAML (already declared); no new deps
**Storage**: File-based — markdown in `.doit/memory/{roadmap,tech-stack}.md`
**Testing**: pytest with `typer.testing.CliRunner`, `tmp_path` fixtures; matches the style established by spec 059
**Target Platform**: macOS, Linux, Windows (all doit-supported platforms)
**Project Type**: single — CLI tool (`src/doit_cli/`)
**Performance Goals**: migration + enrichment <500 ms per file for files up to 50 KB (SC-004)
**Constraints**: non-interactive, atomic writes (crash-safe), byte-for-byte body preservation outside modified sections
**Scale/Scope**: two files per project; run once per `doit update` invocation plus on-demand via CLI

All fields filled without `NEEDS CLARIFICATION`.

## Architecture Overview

<!-- BEGIN:AUTO-GENERATED section="architecture" -->
```mermaid
flowchart TD
    subgraph "Presentation"
        UPDATE[doit update CLI]
        MEMORYCLI[doit memory enrich / migrate]
        SKILL[/doit.roadmapit skill]
    end
    subgraph "Application"
        INIT[run_init]
        ROADMAP_MIG[RoadmapMigrator]
        TECHSTACK_MIG[TechStackMigrator]
        ROADMAP_ENR[RoadmapEnricher]
        TECHSTACK_ENR[TechStackEnricher]
        VALIDATOR[memory_validator]
        SHAPE[_memory_shape helper]
    end
    subgraph "Data"
        ROADMAP[(.doit/memory/roadmap.md)]
        TECHSTACK[(.doit/memory/tech-stack.md)]
        CONSTIT[(.doit/memory/constitution.md)]
        COMPLETED[(.doit/memory/completed_roadmap.md)]
    end
    UPDATE --> INIT --> ROADMAP_MIG
    INIT --> TECHSTACK_MIG
    MEMORYCLI --> ROADMAP_ENR
    MEMORYCLI --> TECHSTACK_ENR
    ROADMAP_MIG --> SHAPE
    TECHSTACK_MIG --> SHAPE
    ROADMAP_MIG --> ROADMAP
    TECHSTACK_MIG --> TECHSTACK
    ROADMAP_ENR --> ROADMAP
    ROADMAP_ENR -. reads .-> CONSTIT
    ROADMAP_ENR -. reads .-> COMPLETED
    TECHSTACK_ENR --> TECHSTACK
    TECHSTACK_ENR -. reads .-> CONSTIT
    SKILL --> MEMORYCLI
    VALIDATOR --> ROADMAP
    VALIDATOR --> TECHSTACK
```
<!-- END:AUTO-GENERATED -->

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

Evaluated against `.doit/memory/constitution.md` (v1.0.0) principles:

| Principle | Status | Note |
|:----------|:-------|:-----|
| I. Specification-First | ✓ Pass | Spec and checklist validated before this plan. |
| II. Persistent Memory | ✓ Pass | Feature *strengthens* the persistent-memory contract by extending enforced shape to two more files. |
| III. Auto-Generated Diagrams | ✓ Pass | ER diagram (data-model.md) + architecture diagram + state diagrams are mermaid. |
| IV. Opinionated Workflow | ✓ Pass | Integrates into existing `doit update` and `doit memory` subgroup; no new top-level commands; no workflow deviations. |
| V. AI-Native Design | ✓ Pass | Skills invoke new CLIs for deterministic work; LLM reserved for content that truly needs it. |
| Quality Standards | ✓ Pass | Plan mandates contract, unit, and integration tests per existing conventions. |
| Tech Stack alignment | ✓ Pass | No new dependencies. |

**Result**: all gates pass. Re-check after Phase 1 design: **still passing** —
the design introduces four new service modules and one small internal
helper, all within the existing pattern.

## Project Structure

### Documentation (this feature)

```text
specs/060-memory-files-migration/
├── spec.md
├── plan.md              # This file
├── research.md          # 8 design decisions
├── data-model.md        # Entities + state diagrams + invariants
├── contracts/
│   └── migrators.md     # Public API contracts for 4 services + CLI
├── quickstart.md        # 5 end-to-end scenarios
└── checklists/
    └── requirements.md  # Spec quality checklist
```

### Source Code (repository root)

New files:

```text
src/doit_cli/
└── services/
    ├── _memory_shape.py           # NEW — shared insert_section_if_missing helper
    ├── roadmap_migrator.py        # NEW — migrate_roadmap()
    ├── tech_stack_migrator.py     # NEW — migrate_tech_stack()
    ├── roadmap_enricher.py        # NEW — enrich_roadmap()
    └── tech_stack_enricher.py     # NEW — enrich_tech_stack()

tests/
├── contract/
│   └── test_memory_files_migration_contract.py   # NEW — validator ↔ migrator bijection
├── integration/
│   ├── test_roadmap_migration.py                 # NEW — US1 + US3 integration
│   └── test_tech_stack_migration.py              # NEW — US1 + US2 integration
└── unit/
    └── services/
        └── test_memory_shape.py                  # NEW — helper unit tests
```

Modified files:

```text
src/doit_cli/
└── cli/
    ├── init_command.py            # MOD — add roadmap + tech-stack migrator calls after spec 059's constitution block
    └── memory_command.py          # MOD — register `enrich roadmap`, `enrich tech-stack`, `migrate` subcommands

src/doit_cli/templates/
├── commands/
│   └── doit.roadmapit.md          # MOD — add Step 2b enrichment workflow pointing at new CLI
└── skills/
    └── doit.roadmapit/SKILL.md    # MOD — mirror of above
```

**Structure Decision**: single-project layout. All new code lives under
`src/doit_cli/services/` (one service per responsibility, matching
spec 059's pattern). No cross-cutting refactors.

## Complexity Tracking

> No constitution violations — intentionally blank.

The feature adds:

- 5 new modules (4 services + 1 internal helper) — each single-responsibility,
  ~100–180 lines.
- 4 new test files.
- 0 new dependencies, 0 new top-level CLI commands, 0 new validator rules.

Reuses from spec 059:

- `write_text_atomic`
- `MigrationAction` / `MigrationResult`
- `EnrichmentAction` / `EnrichmentResult`
- `PLACEHOLDER_TOKENS` body-token registry (via `memory_validator`)

## Phase 0 outputs

See [research.md](research.md). 8 decisions documented with rationale
and rejected alternatives. Zero open clarifications.

## Phase 1 outputs

- [data-model.md](data-model.md) — entities (`MemoryFile`,
  `RequiredSection`, `RequiredSubsection`, `MigrationResult`,
  `EnrichmentResult`, `EnrichmentSource`), ER diagram, two
  state-transition diagrams, derived invariants.
- [contracts/migrators.md](contracts/migrators.md) — Python API
  contracts for 4 services + shared helper + CLI surface + init-hook
  integration code + validator and skill integration notes + backwards-
  compatibility guarantees.
- [quickstart.md](quickstart.md) — 5 end-to-end scenarios covering
  every FR and SC.

Agent context file update: run
`.doit/scripts/bash/update-agent-context.sh claude` as the final step
(see "Next Steps").

## Ready for `/doit.taskit`

Plan is complete. All gates pass. Phase 1 artifacts generated and
cross-referenced. The next command (`/doit.taskit`) can break this plan
into a dependency-ordered task list.
