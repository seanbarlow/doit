# Feature Specification: Constitution Frontmatter Migration

**Feature Branch**: `059-constitution-frontmatter-migration`
**Created**: 2026-04-20
**Status**: Complete
**Input**: User description: "Auto-migrate legacy .doit/memory/constitution.md (no frontmatter) to the 0.2.0 memory-contract shape. `doit update` should detect a missing-or-incomplete YAML frontmatter block, prepend a frontmatter skeleton with placeholder values for every required field defined in src/doit_cli/schemas/frontmatter.schema.json, and preserve the existing body byte-for-byte. Downstream, the `/doit.constitution` skill (LLM-driven) should learn to recognize placeholder frontmatter and enrich it by reading the body — inferring `name`, `tagline`, `kind`, `phase`, `id`, `dependencies` without the user needing to hand-edit."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Legacy project upgrades cleanly without manual edits (Priority: P1)

A developer maintaining a project that was initialized on doit 0.1.x runs `doit update` after installing 0.2.0. Their `.doit/memory/constitution.md` has no YAML frontmatter (pre-0.2.0 format). The update command detects the missing frontmatter, prepends a placeholder skeleton, and leaves the existing prose body untouched. `doit verify-memory` now reports zero errors (warnings only, for the placeholders).

**Why this priority**: This is the blocking upgrade path. Without it, every user upgrading from 0.1.x to 0.2.0 gets a hard validation error on their constitution and cannot use `doit verify-memory` or any downstream tool (MCP server, platform-docs-site) until they hand-write frontmatter. This path makes the 0.2.0 upgrade frictionless.

**Independent Test**: On a project whose `.doit/memory/constitution.md` has no frontmatter, run `doit update`. Confirm the file now begins with a `---` fenced YAML block containing all seven required fields from `frontmatter.schema.json`, followed by the original body byte-for-byte. Then run `doit verify-memory .` and confirm exit code 0 with warnings (not errors) for the placeholder values.

**Acceptance Scenarios**:

1. **Given** a project with `.doit/memory/constitution.md` that has no YAML frontmatter, **When** the developer runs `doit update`, **Then** the file is rewritten with a placeholder frontmatter block prepended and the original body preserved byte-for-byte.
2. **Given** the file has been migrated to placeholder frontmatter, **When** the developer runs `doit verify-memory .`, **Then** the command exits with code 0 and reports warnings (not errors) for the placeholder fields.
3. **Given** a project whose `.doit/memory/constitution.md` already contains a complete, valid frontmatter block, **When** the developer runs `doit update`, **Then** the file is left unchanged (idempotent).

---

### User Story 2 - AI assistant enriches placeholder frontmatter (Priority: P2)

After `doit update` has written placeholder frontmatter, the developer opens Claude Code and runs `/doit.constitution`. The skill detects the placeholder values, reads the constitution body to infer project identity (name, tagline, kind, phase, id), and rewrites the frontmatter with real values. The body remains untouched. `doit verify-memory` now reports zero errors and zero warnings.

**Why this priority**: This is the path from "valid shape" to "real values." Users could fill in placeholders manually (P1 covers that escape hatch), but having the AI do it eliminates the manual step and is the primary value-add of the migration story. Lower than P1 because it requires P1 to already have run.

**Independent Test**: Starting from a constitution.md with placeholder frontmatter (the P1 output), invoke `/doit.constitution` without any argument. Confirm every `[PLACEHOLDER]` token has been replaced with a concrete value inferred from the body, the body text is unchanged, and `doit verify-memory .` passes with zero warnings.

**Acceptance Scenarios**:

1. **Given** `.doit/memory/constitution.md` has placeholder frontmatter with tokens like `[PROJECT_NAME]`, `[PROJECT_ID]`, `[PROJECT_KIND]`, **When** the developer runs `/doit.constitution` in an AI assistant, **Then** every placeholder token is replaced with a real value inferred from the body and project context.
2. **Given** the AI has rewritten the frontmatter, **When** the developer runs `doit verify-memory .`, **Then** the command reports zero errors and zero warnings.
3. **Given** `.doit/memory/constitution.md` already has fully populated (non-placeholder) frontmatter, **When** the developer runs `/doit.constitution`, **Then** the skill proceeds with its normal update flow without triggering the enrichment path.

---

### User Story 3 - Partial frontmatter is completed, not overwritten (Priority: P3)

A developer has a constitution.md that already has some frontmatter fields (perhaps they hand-wrote `id` and `name` earlier) but is missing `icon`, `tagline`, `phase`, `kind`, or `dependencies`. Running `doit update` adds only the missing fields as placeholders; the existing hand-written values are preserved verbatim.

**Why this priority**: Covers the mid-migration user — someone who has partially adopted the new format but not completed it. Without this, these users would either lose their hand-written values (if migration overwrote) or hit a validation error (if migration skipped). P3 because it's a smaller audience than P1 and less automated than P2.

**Independent Test**: On a constitution.md with partial frontmatter (e.g., only `id` and `name` present), run `doit update`. Confirm the original `id` and `name` values are unchanged and the missing required fields have been added as placeholders.

**Acceptance Scenarios**:

1. **Given** a constitution.md with frontmatter containing only a subset of required fields, **When** the developer runs `doit update`, **Then** existing field values are preserved unchanged and each missing required field is added with a placeholder value.
2. **Given** frontmatter contains fields not listed in `frontmatter.schema.json` (unknown fields), **When** the developer runs `doit update`, **Then** those unknown fields are preserved verbatim (migration does not strip them); `doit verify-memory` surfaces them separately per the schema's validation rules.

---

### Edge Cases

- **Malformed YAML frontmatter**: When the file has a `---` block but the YAML inside cannot be parsed, `doit update` must surface a clear error identifying the problem and leave the file unmodified. Migration does not attempt to repair syntactically broken YAML.
- **Missing constitution file**: When `.doit/memory/constitution.md` does not exist at all, this feature does not apply; `doit init` (not `doit update`) is the command that creates the file.
- **Empty or trivial body**: When the file has no body or only a single heading, migration still runs — frontmatter is prepended regardless of body content. Validation of body headings (e.g., the required `## Purpose & Goals` section) is a separate memory-contract concern.
- **Idempotent re-run**: Running `doit update` twice in a row on a freshly-migrated file produces no further changes on the second run.
- **Unknown frontmatter fields**: The schema declares `additionalProperties: false`. Migration preserves unknown fields (does not delete them); `doit verify-memory` reports them as errors per the schema. Users decide whether to remove or keep them.
- **Placeholder-detection false positives**: A legitimate user value that happens to contain square brackets (e.g., a tagline "Build [fast] software") must not be treated as a placeholder. The placeholder convention uses an exact-token whitelist (e.g., `[PROJECT_NAME]`), not a regex match on any bracketed text.
- **Enrichment with insufficient body context**: When the body is too sparse for the AI to infer a value (e.g., the `kind` field cannot be determined from content), the `/doit.constitution` skill leaves that field as a placeholder and warns the user rather than guessing.

## User Journey Visualization

<!-- BEGIN:AUTO-GENERATED section="user-journey" -->
```mermaid
flowchart LR
    subgraph "User Story 1 - Legacy project upgrades cleanly"
        US1_S[Legacy constitution.md<br/>no frontmatter] --> US1_A[doit update] --> US1_E[Valid-shape file<br/>verify-memory warnings only]
    end
    subgraph "User Story 2 - AI enriches placeholders"
        US2_S[Placeholder frontmatter] --> US2_A[/doit.constitution] --> US2_E[Real values inferred<br/>verify-memory zero warnings]
    end
    subgraph "User Story 3 - Partial frontmatter completed"
        US3_S[Partial frontmatter] --> US3_A[doit update] --> US3_E[Existing values preserved<br/>missing fields filled]
    end
```
<!-- END:AUTO-GENERATED -->

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: `doit update` MUST detect whether `.doit/memory/constitution.md` begins with a YAML frontmatter block delimited by `---` lines.
- **FR-002**: When no frontmatter block is present, `doit update` MUST prepend a frontmatter block containing every required field defined in `src/doit_cli/schemas/frontmatter.schema.json` (`id`, `name`, `kind`, `phase`, `icon`, `tagline`, `dependencies`), each populated with a recognizable placeholder value.
- **FR-003**: Placeholder values MUST follow a uniform, exact-token convention (e.g., `[PROJECT_ID]`, `[PROJECT_NAME]`, `[PROJECT_KIND]`) that `doit verify-memory` recognizes and reports as warnings rather than errors.
- **FR-004**: When prepending or updating frontmatter, the body (every byte after any existing frontmatter block, or the entire file when no frontmatter existed) MUST be preserved byte-for-byte.
- **FR-005**: When an existing frontmatter block is present but is missing one or more required fields, `doit update` MUST add only the missing fields using the placeholder convention and MUST NOT modify any existing field values.
- **FR-006**: When an existing frontmatter block already contains every required field with non-placeholder values, `doit update` MUST leave `.doit/memory/constitution.md` unchanged.
- **FR-007**: When an existing frontmatter block contains fields not defined in `frontmatter.schema.json`, `doit update` MUST preserve those fields verbatim (neither deleting nor modifying them).
- **FR-008**: `doit update` MUST be non-interactive — it MUST NOT prompt the user for input during the migration step.
- **FR-009**: When the existing frontmatter block exists but contains syntactically invalid YAML, `doit update` MUST surface a clear error identifying the problem and leave the file unmodified.
- **FR-010**: Running `doit update` on a freshly-migrated file MUST be a no-op (idempotent); the second run MUST produce no further changes.
- **FR-011**: The `/doit.constitution` skill MUST detect placeholder tokens in an existing frontmatter block using the same exact-token convention defined in FR-003.
- **FR-012**: The `/doit.constitution` skill MUST infer replacement values for each placeholder by reading the constitution body and available project context (e.g., repository directory name, roadmap, tech stack).
- **FR-013**: The `/doit.constitution` skill MUST preserve the body byte-for-byte when replacing placeholder frontmatter values.
- **FR-014**: When the `/doit.constitution` skill cannot confidently infer a value for a placeholder, it MUST leave that field as a placeholder and report which fields could not be enriched.
- **FR-015**: `doit verify-memory` MUST emit warnings (not errors) for every recognized placeholder token so that a freshly-migrated file passes validation without requiring immediate user action.

### Key Entities

- **Constitution File**: The markdown document at `.doit/memory/constitution.md`, composed of an optional YAML frontmatter block followed by a prose body.
- **Frontmatter Block**: A YAML document at the head of the file, delimited by `---` lines, containing metadata fields constrained by the constitution frontmatter JSON Schema.
- **Required Field**: A frontmatter key listed in `frontmatter.schema.json`'s `required` array: `id`, `name`, `kind`, `phase`, `icon`, `tagline`, `dependencies`.
- **Placeholder Token**: An exact-match sentinel value (e.g., `[PROJECT_NAME]`) used in place of a real field value during the migration-to-enrichment handoff. Recognized by both `doit verify-memory` and `/doit.constitution`.
- **Memory Contract**: The rules enforced by `doit verify-memory` that define valid shape for `.doit/memory/*.md` files.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A project whose `.doit/memory/constitution.md` has no frontmatter passes `doit verify-memory .` with exit code 0 (warnings allowed, zero errors) immediately after `doit update` completes.
- **SC-002**: The body content hash (SHA-256 of every byte after any existing frontmatter block) is identical before and after `doit update` runs on the constitution file.
- **SC-003**: After a user runs `/doit.constitution` on a constitution whose frontmatter was freshly migrated, `doit verify-memory .` reports zero warnings related to placeholder tokens.
- **SC-004**: `doit update` completes the constitution migration step in under 500 milliseconds for a constitution file up to 50 KB.
- **SC-005**: Re-running `doit update` on a migrated file produces a zero-byte diff on `.doit/memory/constitution.md` (idempotency).
- **SC-006**: 100% of the seven required frontmatter fields defined in `frontmatter.schema.json` are present in the file after `doit update` runs, regardless of whether the pre-existing frontmatter had zero, some, or all of them.
- **SC-007**: When `doit update` encounters malformed YAML frontmatter, the file's bytes on disk remain exactly as they were before the command ran (no partial writes, no corruption).

## Assumptions

- The `frontmatter.schema.json` file committed in `src/doit_cli/schemas/` is the canonical source of required fields and field constraints for this migration. Schema changes after this feature ships will require a follow-up migration.
- The existing memory-contract validator (`src/doit_cli/services/memory_validator.py`) is the single place where placeholder tokens are treated as warnings vs errors. Adding the warning classification is in scope.
- The `/doit.constitution` skill is the only AI-driven enrichment entry point in scope. Other skills (`/doit.roadmapit`, etc.) may gain similar enrichment behavior later but are out of scope here.
- `doit update` delegates to the same `run_init(..., update=True)` code path that is already registered, so the migration logic integrates as a step within that path rather than as a new top-level command.

## Out of Scope

- Migrating other memory files (`roadmap.md`, `tech-stack.md`, `personas.md`). Only `constitution.md` is addressed in this spec; equivalent migrations for other files are separate features.
- Interactive prompts during `doit update`. The command remains strictly non-interactive.
- Creating a brand-new constitution when the file is missing entirely — that is `doit init`'s responsibility, not this migration.
- Rewriting body content. Body prose (and body heading validation such as required `## Purpose & Goals` sections) is strictly out of scope; only the frontmatter block is touched.
- Calling an external LLM API from the CLI. Enrichment runs inside the AI assistant via the `/doit.constitution` skill, never from `doit update` itself.
- Schema evolution. This spec assumes the frontmatter schema is fixed; future schema changes that require migrating already-populated fields are a separate concern.
