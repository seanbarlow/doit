# Feature Specification: Personas.md Migration (closes the memory-file-migration pattern)

**Feature Branch**: `062-personas-migration`
**Created**: 2026-04-21
**Status**: Complete
**Input**: User description: "Personas.md migration (extends memory-file migrator pattern). Rationale: Closes the memory-file-migration pattern across all four files (constitution, roadmap, tech-stack, personas). Applies the same shape-migrator + enricher + atomic-write primitives from specs 059 and 060 to `.doit/memory/personas.md`. Flagged as natural follow-up in the spec 060 test-report. Aligns with: Spec 060 (memory-files-migration) closure, Persistent Memory principle (II)."

**Depends on**: Spec [060 — Memory Files Migration](../060-memory-files-migration/spec.md) (shipped) and spec [061 — Roadmap H3 Matching Fix](../061-fix-roadmap-h3-matching/spec.md) (shipped; contributes the per-H3 matcher primitive). This feature is the fourth and final `.doit/memory/*.md` to receive the migrator + enricher + validator treatment.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Existing personas.md with missing sections is shape-migrated (Priority: P1)

A developer runs `doit update` or `doit memory migrate .` on a project whose `.doit/memory/personas.md` exists but is missing one or more required top-level sections — e.g. an older roadmap-generated file that has `## Persona Summary` but no `## Detailed Profiles`, or the reverse. The migrator recognises the gap, inserts a placeholder stub for each missing required section, and preserves all pre-existing prose byte-for-byte. The result is a file that validates against the canonical personas shape.

**Why this priority**: Projects that used the pre-062 roadmapit or researchit flows may have a `.doit/memory/personas.md` with an inconsistent shape; the context loader and downstream commands (`specit`, `researchit`) assume a canonical layout. P1 because it's the behaviour users running `doit update` will see today — the shape-migration path.

**Independent Test**: Build a fixture `.doit/memory/personas.md` with `## Persona Summary` only (no `## Detailed Profiles`). Run `migrate_personas(path)`. Assert `action == PATCHED`, `added_fields == ("Detailed Profiles",)`, a stub block for Detailed Profiles is present, and the original `## Persona Summary` table content is preserved byte-for-byte.

**Acceptance Scenarios**:

1. **Given** a `personas.md` missing `## Detailed Profiles`, **When** the migrator runs, **Then** it returns `MigrationAction.PATCHED` with `added_fields == ("Detailed Profiles",)` and inserts a single stub block under the existing `## Persona Summary`.
2. **Given** a `personas.md` missing `## Persona Summary`, **When** the migrator runs, **Then** it returns `MigrationAction.PATCHED` with `added_fields == ("Persona Summary",)` and inserts a stub table header at the top of the file (before any existing H2s).
3. **Given** a `personas.md` with both required H2s present (but no `### Persona: P-NNN` entries), **When** the migrator runs, **Then** it returns `MigrationAction.NO_OP` (H2 shape is present — persona entries are project-specific and NOT auto-stubbed).
4. **Given** a `personas.md` completely missing required H2s but containing unrelated sections (e.g. `## Intro`), **When** the migrator runs, **Then** it returns `MigrationAction.PATCHED` (not `PREPENDED` — the file already exists and has content) with `added_fields == ("Persona Summary", "Detailed Profiles")`; both stubs are inserted.

---

### User Story 2 - Absent `.doit/memory/personas.md` is NO_OP — personas are opt-in (Priority: P1)

A developer runs `doit memory migrate .` on a project that has never used personas (no `.doit/memory/personas.md` file). The migrator returns `NO_OP` without creating the file. Personas remain an opt-in feature — only projects that have explicitly generated a `personas.md` (via `/doit.roadmapit` or `/doit.researchit`) get shape-enforced.

**Why this priority**: Unlike `constitution.md` (required) and `roadmap.md` / `tech-stack.md` (auto-created by `doit init` at migrator-template-level), `personas.md` is generated on-demand by persona-producing skills. Creating it unprompted would pollute projects that don't use personas. P1 because the opt-in semantics are a user-visible promise — auto-creating would surprise existing users.

**Independent Test**: Start with a `.doit/memory/` directory containing only `constitution.md`, `roadmap.md`, `tech-stack.md` (no `personas.md`). Run `migrate_personas(memory_dir / "personas.md")`. Assert `action == NO_OP`, `added_fields == ()`, and the file still does NOT exist on disk.

**Acceptance Scenarios**:

1. **Given** a project with no `.doit/memory/personas.md`, **When** the migrator runs, **Then** it returns `MigrationAction.NO_OP`, no file is created, and the result carries no error.
2. **Given** `doit memory migrate .` on a project with no personas file, **When** the umbrella CLI runs, **Then** the JSON output includes a row for `personas.md` with `action: no_op`, consistent with the other three memory files' reporting shape.
3. **Given** `doit verify-memory .` on a project with no personas file, **When** the validator runs, **Then** no warnings or errors are emitted for personas.md (absence is a valid state).

---

### User Story 3 - `doit memory enrich personas` reports deterministic placeholder state (Priority: P2)

When the enricher runs on a personas.md file, it detects remaining template placeholders (`{Persona Name}`, `{Role}`, `{Archetype}`, `{FEATURE_NAME}`, etc. — the curly-brace tokens from `personas-output-template.md`) and reports `PARTIAL` with an `unresolved_fields` list. Because personas are intrinsically project-specific (an enricher can't reasonably pick names, roles, pain points), the enricher does NOT attempt to fill them — it points the user at `/doit.roadmapit` or `/doit.researchit` to populate interactively. When no placeholders remain, it returns `NO_OP`.

**Why this priority**: Deterministic reporting is useful in CI pipelines and as part of the `doit update` flow (mirrors the constitution and roadmap enrichers). P2 because the user experience still requires a follow-up interactive step — the enricher is primarily a linter, not a content generator.

**Independent Test**: Write a fixture `personas.md` containing `{Persona Name}` and `{Role}` in one profile and real content in another. Run `enrich_personas(path)`. Assert `action == PARTIAL`, `unresolved_fields` lists both placeholder names (deduplicated), `enriched_fields == ()`, and file bytes on disk are unchanged. Rerun on a fully-populated file → `action == NO_OP`.

**Acceptance Scenarios**:

1. **Given** a `personas.md` with one or more `{…}` curly-brace template placeholders, **When** `enrich_personas` runs, **Then** it returns `EnrichmentAction.PARTIAL`, lists each distinct placeholder token in `unresolved_fields`, and does NOT modify the file on disk.
2. **Given** a `personas.md` with zero placeholders, **When** the enricher runs, **Then** it returns `EnrichmentAction.NO_OP`, `unresolved_fields == ()`, and file bytes are unchanged.
3. **Given** `doit memory enrich personas --json` with `PARTIAL` result, **When** the CLI exits, **Then** its exit code is `1` (matching spec 059/060 convention) and the JSON includes a machine-readable `unresolved_fields` list plus a human-readable hint pointing the user at `/doit.roadmapit` or `/doit.researchit`.
4. **Given** `doit memory enrich personas` is invoked on a project with no `personas.md` file, **When** the CLI runs, **Then** it returns `action: no_op` with exit `0` (same "opt-in" semantics as the migrator — not an error).

---

### User Story 4 - Validator enforces shape when file exists; umbrella CLI includes personas (Priority: P2)

`memory_validator.verify_memory_contract` gains a `_validate_personas` rule: when `.doit/memory/personas.md` exists, validate that `## Persona Summary` and `## Detailed Profiles` are present, and that every `### Persona: …` heading under `## Detailed Profiles` follows the canonical `Persona: P-NNN` (three-digit zero-padded) ID format. When the file does not exist, emit no issues. `doit memory migrate` extends its report to include a fourth row for `personas.md`; its behaviour mirrors the other three migrators' reporting shape. Contract tests lock the new validator↔migrator alignment.

**Why this priority**: Validator enforcement and umbrella-CLI wiring complete the pattern parity across all four memory files — the "closure" motivation for this spec. P2 because the migrator (US1) already covers the user-visible behavioural change; validator/umbrella are the plumbing that prevents future regressions.

**Independent Test**: Build a personas.md with `### Persona: P-1` (wrong ID format — missing leading zeros). Run `doit verify-memory .`. Assert one ERROR is emitted citing the malformed ID. Repeat with `### Persona: P-001` → no errors. Also: `doit memory migrate .` JSON output has exactly four rows, one per memory file, in deterministic order.

**Acceptance Scenarios**:

1. **Given** a `personas.md` with a persona heading `### Persona: P-1` (non-canonical ID), **When** `doit verify-memory .` runs, **Then** it emits an `ERROR`-severity issue for that file with a message identifying the malformed ID pattern.
2. **Given** a `personas.md` missing `## Persona Summary`, **When** the validator runs, **Then** it emits an `ERROR`-severity issue (matching roadmap/tech-stack validator severity for missing required H2s).
3. **Given** a `personas.md` with `## Persona Summary` present but empty (no table rows) and `## Detailed Profiles` containing no `### Persona:` entries, **When** the validator runs, **Then** it emits a `WARNING`-severity issue noting "no persona entries defined" (shape is correct, content is absent — warning not error, matching roadmap's approach).
4. **Given** `doit memory migrate .` on a project with all four memory files present, **When** the command runs, **Then** the JSON output contains exactly four rows in the order: `constitution.md`, `roadmap.md`, `tech-stack.md`, `personas.md`.

---

### Edge Cases

- **Multiple personas.md files present** (feature-level `specs/{feature}/personas.md` AND project-level `.doit/memory/personas.md`): this spec targets ONLY the project-level file. Feature-level personas.md remains under the `/doit.researchit` / `/doit.specit` ownership and is NOT validated or migrated by `doit memory migrate`. The context loader's feature-level-takes-precedence semantic (spec 056) is unchanged.
- **Persona ID with gaps** (e.g. `P-001`, `P-003` with no `P-002`): allowed. The canonical format regex checks each ID individually; gaps are a user-authoring choice, not a shape violation.
- **Persona ID collision** (two `### Persona: P-001` headings): validator emits a WARNING (same severity as roadmap duplicate-priority handling from spec 061). Migrator treats as "already present" and does not re-insert.
- **Persona with more than 999 entries** (four-digit ID needed): out of scope. The P-NNN three-digit format is documented in the persona template and considered sufficient. Project teams needing more can file a follow-up to widen the regex.
- **CRLF line endings**: preserved byte-for-byte, matching spec 060's `_detect_newline` guarantee. Inherited from the shared helper.
- **Placeholder tokens inside code fences**: the enricher's placeholder detection scans plain text only — `{FEATURE_NAME}` inside a fenced code block counts as a placeholder and triggers PARTIAL. Users wanting literal braces in code examples can escape them per their preferred convention (documented in the migration note).

## User Journey Visualization

<!-- BEGIN:AUTO-GENERATED section="user-journey" -->
```mermaid
flowchart LR
    subgraph "US1 - Existing personas.md shape-migrated"
        US1_S[.doit/memory/personas.md with missing H2] --> US1_A[doit memory migrate] --> US1_E[PATCHED — stubs inserted, prose preserved]
    end
    subgraph "US2 - Absent personas.md is NO_OP"
        US2_S[No .doit/memory/personas.md] --> US2_A[doit memory migrate] --> US2_E[NO_OP — no file created]
    end
    subgraph "US3 - Enricher reports placeholder state"
        US3_S[personas.md with `{Placeholder}` tokens] --> US3_A[doit memory enrich personas] --> US3_E[PARTIAL with unresolved_fields]
    end
    subgraph "US4 - Validator + umbrella wired"
        US4_S[personas.md with malformed ID] --> US4_A[doit verify-memory] --> US4_E[ERROR on Persona: P-1]
    end
```
<!-- END:AUTO-GENERATED -->

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: A migrator function `migrate_personas(path: Path) -> MigrationResult` MUST be provided, reusing the `MigrationAction` / `MigrationResult` types from `constitution_migrator`. No new result-type hierarchy.
- **FR-002**: When `.doit/memory/personas.md` does not exist, the migrator MUST return `MigrationAction.NO_OP` and MUST NOT create the file. Personas are opt-in.
- **FR-003**: When `.doit/memory/personas.md` exists and has both required H2 sections (`## Persona Summary` and `## Detailed Profiles`), the migrator MUST return `MigrationAction.NO_OP` with byte-for-byte file preservation.
- **FR-004**: When `.doit/memory/personas.md` exists but is missing one or more required H2 sections, the migrator MUST return `MigrationAction.PATCHED`, insert stubs for the missing sections in canonical order (`## Persona Summary` first, then `## Detailed Profiles`), and list the added H2 titles in `added_fields`.
- **FR-005**: The migrator MUST preserve all pre-existing prose outside the inserted stubs byte-for-byte, matching the spec 060 `preserved_body_hash` guarantee.
- **FR-006**: Inserted stubs MUST carry at least three distinct `[TOKEN]`-style placeholders so the validator's placeholder detector (`_is_placeholder` threshold ≥ 3) classifies freshly-migrated files as "needs enrichment" — consistent with spec 059/060.
- **FR-007**: An enricher function `enrich_personas(path: Path) -> EnrichmentResult` MUST be provided, reusing the `EnrichmentAction` / `EnrichmentResult` types from the constitution enricher. No new result-type hierarchy.
- **FR-008**: The enricher MUST detect remaining template placeholders (curly-brace tokens of the form `{...}` that match the canonical set in `personas-output-template.md`) and report them in `unresolved_fields` when placeholders remain.
- **FR-009**: The enricher MUST NOT attempt to fill persona-specific content (names, roles, pain points). When placeholders remain, it returns `PARTIAL` with a CLI hint pointing users at `/doit.roadmapit` or `/doit.researchit`. When no placeholders remain, it returns `NO_OP`.
- **FR-010**: When `.doit/memory/personas.md` does not exist, the enricher MUST return `EnrichmentAction.NO_OP` with exit code `0` (same opt-in semantic as the migrator).
- **FR-011**: A new CLI subcommand `doit memory enrich personas` MUST be provided, following the conventions of `doit memory enrich roadmap` and `doit memory enrich tech-stack` (exit codes: `0` NO_OP or ENRICHED; `1` PARTIAL; `2` file error).
- **FR-012**: The `doit memory migrate` umbrella command MUST include `.doit/memory/personas.md` as a fourth entry in its report. The output order MUST be deterministic: constitution → roadmap → tech-stack → personas.
- **FR-013**: `memory_validator.verify_memory_contract` MUST gain a `_validate_personas` rule that, when `.doit/memory/personas.md` exists, enforces: (a) `## Persona Summary` H2 is present (ERROR if missing), (b) `## Detailed Profiles` H2 is present (ERROR if missing), (c) every `### Persona: …` heading under Detailed Profiles matches the regex `^Persona: P-\d{3}$` (ERROR per violation), (d) at least one `### Persona: P-NNN` entry is defined (WARNING if zero — shape-correct but content-empty).
- **FR-014**: The validator MUST emit no issues when `.doit/memory/personas.md` does not exist (absence is valid — personas are opt-in).
- **FR-015**: A contract test MUST assert that the migrator's required H2 titles exactly match the validator's required H2 titles (`REQUIRED_PERSONAS_H2` constant ↔ `_validate_personas` heading checks). This mirrors the `test_roadmap_required_h2_matches_validator` pattern from spec 060.
- **FR-016**: A contract test MUST assert that for every persona ID regex the validator accepts (`P-001`..`P-999`), a migrator/validator round-trip on a minimal personas.md containing a single `### Persona: P-NNN` heading under `## Detailed Profiles` returns no issues. Mirrors the bijection pattern from spec 061's US3.
- **FR-017**: All 24 existing spec-060 roadmap-migration integration tests and all 15 spec-060 tech-stack migration tests MUST continue to pass unchanged. Spec 061's 77 tests must also remain green. This spec's changes MUST NOT regress prior migrators.

### Key Entities

- **PersonasMigrator**: Service module at `src/doit_cli/services/personas_migrator.py` exposing `migrate_personas(path)` and the module-level constant `REQUIRED_PERSONAS_H2 = ("Persona Summary", "Detailed Profiles")`. Reuses `_memory_shape.insert_section_if_missing` with `matchers=None` (exact-match is correct here — persona H2 titles are not decoration-prone in practice).
- **PersonasEnricher**: Service module at `src/doit_cli/services/personas_enricher.py` exposing `enrich_personas(path)`. Uses shared `EnrichmentResult` / `EnrichmentAction` primitives. Placeholder detection scans for curly-brace tokens matching a template-derived vocabulary.
- **Persona ID**: The canonical three-digit zero-padded form `P-\d{3}` (e.g. `P-001`, `P-042`, `P-999`). Authoritative source: the personas-output-template.md pattern. Validator rejects any other form under `## Detailed Profiles`.
- **Required H2 set**: `("Persona Summary", "Detailed Profiles")`. Fixed two-entry tuple; matches the minimum shape required by the context loader and the `/doit.specit` persona-matching rules.
- **Migration stub bodies**: Each inserted H2 carries a brief placeholder block with ≥3 `[TOKEN]` references (e.g. `[PROJECT_NAME]`, `[PERSONA_EXAMPLE]`, `[SEE_ROADMAPIT]`) so the validator classifies the freshly-migrated file as needing enrichment.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Running `doit memory migrate .` on a project with no `.doit/memory/personas.md` reports `personas.md: no_op` alongside the three pre-existing files, with zero file-system side effects.
- **SC-002**: Running `doit memory migrate .` on a project with a `personas.md` missing one or both required H2s patches in the missing stubs exactly once; rerunning is idempotent (`NO_OP` on second invocation).
- **SC-003**: Running `doit memory migrate .` on a project with a complete `personas.md` (required H2s plus valid persona entries) reports `no_op` with byte-for-byte file preservation.
- **SC-004**: Running `doit verify-memory .` on a project with a canonical personas.md reports zero errors and zero warnings for personas.md. On a personas.md with a malformed persona ID (e.g. `Persona: P-1`), it reports exactly one error citing the malformed ID.
- **SC-005**: All 24 spec-060 roadmap integration tests, 15 spec-060 tech-stack integration tests, and 77 spec-061 tests continue to pass unchanged after this spec ships.
- **SC-006**: The contract test from FR-015 (migrator ↔ validator H2 alignment for personas) passes. The contract test from FR-016 (migrator ↔ validator ID bijection) passes over ≥5 valid IDs and ≥5 invalid IDs.
- **SC-007**: No new runtime dependencies are added. The feature stays within `src/doit_cli/services/` and `src/doit_cli/cli/memory_command.py`. Public CLI surface extends by exactly one subcommand (`doit memory enrich personas`); the umbrella `doit memory migrate` gains one row of output but no new flags.

## Assumptions

- `.doit/memory/personas.md` is opt-in: absence is a valid state. Projects that don't use personas continue to work without emitting errors or warnings.
- The personas template at `src/doit_cli/templates/personas-output-template.md` (shipped by specs 053 + 056) is the authoritative source of "required section names" for this spec. The required H2 set (`Persona Summary`, `Detailed Profiles`) is derived from that template.
- The persona ID format `P-\d{3}` is the established convention in both the template and the context loader's downstream consumers (`/doit.specit` persona matching in spec 057). Widening to `P-\d{4}` or alternate prefixes is out of scope.
- Enricher cannot reasonably fill persona names, roles, or pain points — these are intrinsically project-specific. The enricher's role is to detect + report, not to generate content. This differs from the constitution and roadmap enrichers which can seed deterministic values.
- The existing `_memory_shape.insert_section_if_missing` primitive (extended in spec 061 with the optional `matchers` parameter) is sufficient. The personas migrator calls the helper with `matchers=None` — exact-case-insensitive H2 matching is correct because persona section titles are not subject to the decoration problem that drove spec 061.
- `MigrationAction`, `MigrationResult`, `EnrichmentAction`, `EnrichmentResult`, `write_text_atomic`, and `PLACEHOLDER_TOKENS` primitives remain unchanged. This spec only adds new callers.
- CRLF preservation and atomic-write semantics are inherited from the shared helpers; no new edge cases introduced.

## Out of Scope

- **Creating `.doit/memory/personas.md` when it does not exist**: opt-in semantics are deliberate. Users invoke `/doit.roadmapit` or `/doit.researchit` to generate the file; `doit memory migrate` does not bootstrap it.
- **Interactively populating persona content**: the enricher does NOT generate persona names, roles, goals, or pain points. Content authoring belongs to `/doit.roadmapit` and `/doit.researchit`. The enricher's scope is placeholder detection and CLI reporting only.
- **Feature-level `specs/{feature}/personas.md`**: this spec targets only the project-level `.doit/memory/personas.md`. Feature-level files remain under the ownership of the researchit/specit workflow and are not covered by `doit memory migrate` or `doit verify-memory`.
- **Validating `## Relationship Map`, `## Conflicts & Tensions Summary`, `## Traceability`, or `## Next Steps`**: these optional sections are not part of the required-shape contract. Projects may include or omit them at will.
- **Persona-level content validation** (e.g. "every persona must have a Primary Goal"): only the H2 + ID structure is enforced. Content within each `### Persona: P-NNN` block is free-form.
- **Broadening the persona ID format**: P-NNN three-digit is the established contract. Changes require a separate spec.
- **Changing `/doit.roadmapit` or `/doit.researchit` to auto-run the migrator or enricher as part of their interactive flows**: those skills already manage personas.md content. This spec adds infrastructure; wiring it into those skills is a follow-up (trivially done via `doit memory migrate` calls in their error-recovery sections if needed).
- **Migration from a hypothetical pre-053 persona file format**: no such format ships in doit today. The migrator handles "file exists but missing required H2s" (the only real-world case) and nothing more exotic.
- **Extending the `_memory_shape.insert_section_if_missing` helper**: spec 061 already added the optional `matchers` parameter, which this spec does not use (exact-match is correct for personas). No further helper changes needed.
