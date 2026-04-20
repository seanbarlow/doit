# Constitution Frontmatter Migration

**Completed**: 2026-04-20
**Branch**: `059-constitution-frontmatter-migration`
**Spec**: [specs/059-constitution-frontmatter-migration/spec.md](../../specs/059-constitution-frontmatter-migration/spec.md)
**Plan**: [specs/059-constitution-frontmatter-migration/plan.md](../../specs/059-constitution-frontmatter-migration/plan.md)

## Overview

`doit update` (and `doit init --update`) now detects legacy
`.doit/memory/constitution.md` files that predate the 0.2.0+ memory
contract — either missing a YAML frontmatter block entirely, or missing
one or more required fields — and repairs them in place. The user's
prose body is preserved byte-for-byte; only the frontmatter block is
added or extended, with placeholder `[PROJECT_*]` sentinels for any
missing required fields.

Downstream, the `/doit.constitution` skill gains an enrichment branch
that detects these sentinels and replaces them with concrete values
inferred from the constitution body and `doit context show` output —
no interactive interview required.

## User impact

| Before 0.3.0 | After 0.3.0 |
|:-------------|:------------|
| Legacy constitutions fail `doit verify-memory` with an error on the missing frontmatter; user must hand-author the YAML block. | `doit update` writes a valid-shape frontmatter block automatically; `verify-memory` passes with warnings only. |
| Partial frontmatter (e.g. `id` + `name` only) blocks downstream tools (MCP server, docs generator) on schema violations. | Missing required fields are patched in as placeholders; existing values are preserved verbatim. |
| A user fixing their constitution had to know the exact field set and regex constraints. | `/doit.constitution` reads the body and fills in real values (`name`, `tagline`, `kind`, etc.) with no prompts. |

## Architecture

The feature splits responsibilities across the CLI and the AI assistant:

- **CLI (`doit update`)**: guarantees a valid-*shape* file via
  `ConstitutionMigrator` — pure mechanical work. Non-interactive,
  crash-safe, preserves every byte of the body.
- **Skill (`/doit.constitution`)**: fills in valid *values* by reading
  the body and project context. Uses the placeholder registry as its
  detection signal.

No new CLI dependencies, no new CLI subcommands, no LLM calls from the
CLI.

## Key implementation files

- [src/doit_cli/services/constitution_migrator.py](../../src/doit_cli/services/constitution_migrator.py) —
  `migrate_constitution()` plus `MigrationAction` / `MigrationResult`
  public API.
- [src/doit_cli/utils/atomic_write.py](../../src/doit_cli/utils/atomic_write.py) —
  `write_text_atomic()` helper used wherever partial-write corruption
  would be unsafe.
- [src/doit_cli/models/memory_contract.py](../../src/doit_cli/models/memory_contract.py) —
  authoritative `PLACEHOLDER_REGISTRY` and `is_placeholder_value()`;
  `ConstitutionFrontmatter.validate()` emits WARNING (not ERROR) for
  placeholder values.
- [src/doit_cli/cli/init_command.py](../../src/doit_cli/cli/init_command.py) —
  migrator hook inside `run_init(update=True or force=True)`.
- [src/doit_cli/templates/skills/doit.constitution/SKILL.md](../../src/doit_cli/templates/skills/doit.constitution/SKILL.md) —
  new "Placeholder-frontmatter enrichment" section.

## Tests

- **Contract**:
  [tests/contract/test_constitution_frontmatter_contract.py](../../tests/contract/test_constitution_frontmatter_contract.py)
  enforces the `REQUIRED_FIELDS` ↔ `frontmatter.schema.json` ↔
  `PLACEHOLDER_REGISTRY` bijection so the three layers cannot drift.
- **Unit**:
  [tests/unit/test_atomic_write.py](../../tests/unit/test_atomic_write.py)
  covers the atomic-write helper (happy path, failure preserves
  original, UTF-8 round-trip, no line-ending rewriting).
- **Integration**:
  [tests/integration/test_constitution_frontmatter_migration.py](../../tests/integration/test_constitution_frontmatter_migration.py)
  exercises all five migration scenarios end-to-end against real
  filesystems.

## Requirements traceability

All 15 functional requirements and 7 success criteria from the spec
are covered; see the spec and `quickstart.md` scenario table for the
full matrix.

## Related

- Introduces the first consumer of the
  [src/doit_cli/schemas/frontmatter.schema.json](../../src/doit_cli/schemas/frontmatter.schema.json)
  contract that ships with 0.2.0.
- Paves the way for equivalent migrations on `roadmap.md`,
  `tech-stack.md`, and `personas.md` (out of scope here — separate
  features).
