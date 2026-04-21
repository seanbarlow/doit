# Memory Files Migration (roadmap.md, tech-stack.md)

**Completed**: 2026-04-21
**Branch**: `060-memory-files-migration`
**Spec**: [specs/060-memory-files-migration/spec.md](../../specs/060-memory-files-migration/spec.md)
**Plan**: [specs/060-memory-files-migration/plan.md](../../specs/060-memory-files-migration/plan.md)
**Depends on**: spec [059 — Constitution Frontmatter Migration](059-constitution-frontmatter-migration.md)

## Overview

Extends the migrator + enricher pattern from spec 059 to the two
remaining memory files the validator enforces shape on:
`.doit/memory/roadmap.md` and `.doit/memory/tech-stack.md`.

- `doit update` (and `doit init`) now detects missing `## Active Requirements`
  (with `### P1..P4` subsections) in roadmap.md and missing `## Tech Stack`
  (with `### Languages/Frameworks/Libraries`) in tech-stack.md, and
  inserts placeholder stubs in place, preserving all pre-existing prose
  byte-for-byte.
- New `doit memory enrich tech-stack` CLI deterministically extracts
  verbatim bullet content from the constitution's `## Tech Stack`,
  `## Infrastructure`, and `## Deployment` sections and places it in the
  corresponding tech-stack subsections.
- New `doit memory enrich roadmap` CLI seeds a placeholder Vision with
  the first sentence of the constitution's `### Project Purpose` and
  inserts an HTML-comment listing `completed_roadmap.md` items near the
  top of `## Active Requirements` — without populating priority items
  (that's product judgment, left to `/doit.roadmapit`).
- New `doit memory migrate` umbrella runs all three migrators
  (constitution + roadmap + tech-stack) in order.

## User Impact

| Before 0.4.0 | After 0.4.0 |
|:-------------|:------------|
| Legacy roadmap/tech-stack files fail `doit verify-memory` with errors on missing required sections; user must hand-author the skeleton. | `doit update` inserts the skeleton automatically with placeholder stubs. `verify-memory` passes with warnings only. |
| Users with tech-stack content embedded in the constitution had to hand-copy it into `tech-stack.md`. | `doit memory enrich tech-stack` copies the verbatim bullets. |
| Roadmap's `## Vision` and a "what's already shipped" reference had to be hand-managed. | `doit memory enrich roadmap` seeds Vision from the constitution and inserts a commented-out completed-items list. |
| `/doit.roadmapit` had no deterministic first-pass. | Skill runs `doit memory enrich roadmap --json` and focuses its LLM work on the `unresolved_fields`. |

## Architecture

The feature reuses spec 059's result types and crash-safe write helper
without duplication:

- **CLI** (`doit update`, `doit memory migrate`): guarantees valid file
  *shape* via `RoadmapMigrator` / `TechStackMigrator` — pure mechanical
  section insertion.
- **CLI** (`doit memory enrich <file>`): fills in valid *values* via
  deterministic, LLM-free parsing of the constitution and completed
  roadmap.
- **Skill** (`/doit.roadmapit`): calls the enrich CLI as a first pass,
  then uses LLM reasoning only for the `unresolved_fields` the CLI
  returns.

No new dependencies. No new top-level CLI commands. No new validator rules.

## Key Implementation Files

- New:
  - [src/doit_cli/services/_memory_shape.py](../../src/doit_cli/services/_memory_shape.py) — shared section-insertion helper.
  - [src/doit_cli/services/roadmap_migrator.py](../../src/doit_cli/services/roadmap_migrator.py) — `migrate_roadmap()`.
  - [src/doit_cli/services/tech_stack_migrator.py](../../src/doit_cli/services/tech_stack_migrator.py) — `migrate_tech_stack()`.
  - [src/doit_cli/services/roadmap_enricher.py](../../src/doit_cli/services/roadmap_enricher.py) — `enrich_roadmap()`.
  - [src/doit_cli/services/tech_stack_enricher.py](../../src/doit_cli/services/tech_stack_enricher.py) — `enrich_tech_stack()`.
- Modified:
  - [src/doit_cli/cli/init_command.py](../../src/doit_cli/cli/init_command.py) — migrator hooks sequential after spec 059's constitution block.
  - [src/doit_cli/cli/memory_command.py](../../src/doit_cli/cli/memory_command.py) — new `enrich` subgroup and `migrate` umbrella.
  - [src/doit_cli/templates/skills/doit.roadmapit/SKILL.md](../../src/doit_cli/templates/skills/doit.roadmapit/SKILL.md) — new Step 0 enrichment pre-pass.

## Tests

50 new tests across 4 new files:

- **Contract** (8): [tests/contract/test_memory_files_migration_contract.py](../../tests/contract/test_memory_files_migration_contract.py)
- **Unit** (10): [tests/unit/services/test_memory_shape.py](../../tests/unit/services/test_memory_shape.py)
- **Integration — roadmap** (17): [tests/integration/test_roadmap_migration.py](../../tests/integration/test_roadmap_migration.py) — US1 + US3 + CLI tests
- **Integration — tech-stack** (15): [tests/integration/test_tech_stack_migration.py](../../tests/integration/test_tech_stack_migration.py) — US1 + US2 + CLI tests

Full non-e2e suite: **2120 passed, 0 failed**.

## Requirements Traceability

All 20 functional requirements and 8 success criteria are covered by
automated tests — no manual MT items introduced.

## Related

- Spec 059 (constitution frontmatter migration) — introduced the reusable
  `MigrationAction`, `MigrationResult`, `EnrichmentAction`, `EnrichmentResult`,
  and `write_text_atomic` primitives.
- Future (out of scope): the same pattern could be applied to
  `personas.md` as a separate spec.
