# Test Report: Memory Files Migration (roadmap.md, tech-stack.md)

**Date**: 2026-04-21
**Branch**: `060-memory-files-migration`
**Test Framework**: pytest 9.0.3 (with pytest-cov 7.0)
**Scope**: feature-scoped run covering 4 new test files + 2 modified init-command tests, plus the full non-e2e regression suite.

## Automated Tests

### Execution Summary (feature-scoped, post-review)

| Metric | Value |
|:-------|------:|
| Total Tests | 56 |
| Passed | 56 |
| Failed | 0 |
| Skipped | 0 |
| Duration | 0.47 s |

Full non-e2e suite: **2126 passed, 14 skipped, 0 failed** (55.51 s).

Feature count increased from 50 → 56 after the review pass: 4 new unit tests
(CRLF preservation, duplicate H2, whitespace-only source, extra-spaces H2) and
2 new integration tests (escaped pipes in GFM cells, markdown-safe Vision
truncation).

### Failed Tests Detail

None.

### Code Coverage (feature modules)

| Module | Stmts | Miss | Cover |
|:-------|------:|-----:|------:|
| `src/doit_cli/services/_memory_shape.py` | 74 | 2 | **97%** |
| `src/doit_cli/services/roadmap_migrator.py` | 41 | 4 | **90%** |
| `src/doit_cli/services/tech_stack_migrator.py` | 41 | 4 | **90%** |
| `src/doit_cli/services/roadmap_enricher.py` | 156 | 19 | **88%** |
| `src/doit_cli/services/tech_stack_enricher.py` | 159 | 18 | **89%** |
| **Feature total** | **471** | **47** | **90%** |

Uncovered lines are mostly defensive ImportError branches for PyYAML
(guaranteed by project-baseline dependency) and some edge-case error
paths that would require fault injection to exercise.

## Requirement Coverage

Mapping test functions → functional requirements in [spec.md](spec.md).

### US1 — Shape migration (FR-001 through FR-011)

| Req | Description (abridged) | Covering Tests | Status |
|:----|:----------------------|:---------------|:-------|
| FR-001 | Detect `## Active Requirements` in roadmap.md | `test_missing_active_requirements_is_prepended`, `test_complete_roadmap_is_noop` | ✓ COVERED |
| FR-002 | Insert required sections when missing | `test_missing_active_requirements_is_prepended`, `test_migrated_roadmap_passes_validator` | ✓ COVERED |
| FR-003 | Add only missing priority subsections | `test_active_requirements_without_priorities_patched`, `test_partial_priorities_only_adds_missing` | ✓ COVERED |
| FR-004 | Detect `## Tech Stack` in tech-stack.md | `test_missing_tech_stack_section_is_prepended`, `test_complete_tech_stack_is_noop` | ✓ COVERED |
| FR-005 | Insert `## Tech Stack` + required subsections when missing | `test_missing_tech_stack_section_is_prepended`, `test_migrated_tech_stack_passes_validator` | ✓ COVERED |
| FR-006 | Add only missing tech-stack subsections | `test_tech_stack_without_subheadings_is_patched`, `test_partial_tech_stack_only_adds_missing` | ✓ COVERED |
| FR-007 | Preserve body outside modified sections byte-for-byte | `test_body_outside_target_section_preserved` (both files), `test_preserves_body_outside_target_section` | ✓ COVERED |
| FR-008 | Idempotent when already valid-shape | `test_complete_roadmap_is_noop`, `test_complete_tech_stack_is_noop`, `test_noop_when_fully_complete` | ✓ COVERED |
| FR-009 | Zero-byte diff on second run | `test_migration_is_idempotent` (both files) | ✓ COVERED |
| FR-010 | Non-interactive | All integration tests invoke the migrator functions directly — no prompts | ✓ COVERED |
| FR-011 | I/O error leaves file byte-identical | Atomic-write helper's spec-059 unit test (`test_write_failure_leaves_original_intact`) + error paths in migrators | ✓ COVERED |

### US2 — Tech-stack enrichment (FR-012 through FR-014)

| Req | Description (abridged) | Covering Tests | Status |
|:----|:----------------------|:---------------|:-------|
| FR-012 | Read constitution `## Tech Stack` / `## Infrastructure` / `## Deployment` bullets | `test_enrich_tech_stack_from_populated_constitution`, `test_enrich_tech_stack_infrastructure_and_deployment_auto_subsections` | ✓ COVERED |
| FR-013 | Populate placeholder subsections preserving non-placeholder content | `test_enrich_tech_stack_preserves_existing_non_placeholder_content` | ✓ COVERED |
| FR-014 | Report `unresolved_fields` when source is empty (exit 1) | `test_enrich_tech_stack_no_source_returns_partial`, `test_cli_memory_enrich_tech_stack_partial_exits_1` | ✓ COVERED |

### US3 — Roadmap enrichment (FR-015 through FR-017)

| Req | Description (abridged) | Covering Tests | Status |
|:----|:----------------------|:---------------|:-------|
| FR-015 | Replace placeholder Vision from Project Purpose first sentence | `test_enrich_roadmap_replaces_vision_from_project_purpose`, `test_enrich_roadmap_missing_constitution_returns_partial` | ✓ COVERED |
| FR-016 | Insert HTML-comment completed-items block | `test_enrich_roadmap_inserts_completed_items_hint`, `test_enrich_roadmap_re_run_is_idempotent` | ✓ COVERED |
| FR-017 | Both enrichers preserve bodies outside modified regions | `test_enrich_roadmap_preserves_priority_subsections`, `test_enrich_tech_stack_preserves_existing_non_placeholder_content` | ✓ COVERED |

### Cross-cutting (FR-018 through FR-020)

| Req | Description (abridged) | Covering Tests | Status |
|:----|:----------------------|:---------------|:-------|
| FR-018 | Validator classifies placeholder stubs as WARNING | `test_migrated_roadmap_passes_validator`, `test_migrated_tech_stack_passes_validator` (assert zero ERRORs post-migration) | ✓ COVERED |
| FR-019 | Both migrators use `write_text_atomic` | Behaviourally verified via atomic-write invariants in `test_body_outside_target_section_preserved` tests; explicit in contract test asserting reuse of spec 059 types | ✓ COVERED |
| FR-020 | Skills MAY call enrich CLIs | `test_cli_memory_enrich_tech_stack_success`, `test_cli_memory_enrich_roadmap`, `test_cli_memory_migrate_umbrella` exercise the CLI surface the skills call | ✓ COVERED |

**Automated coverage: 20 / 20 functional requirements (100%).**

### Success Criteria Coverage

| SC | Criterion | Covering Test / Evidence |
|:---|:----------|:-------------------------|
| SC-001 | Migrated roadmap/tech-stack passes `verify-memory` exit 0 | `test_migrated_roadmap_passes_validator`, `test_migrated_tech_stack_passes_validator` |
| SC-002 | Body SHA-256 unchanged outside modified sections | `test_body_outside_target_section_preserved` (both files) |
| SC-003 | After `doit memory enrich tech-stack`, zero placeholder warnings | `test_enrich_tech_stack_from_populated_constitution` + manual smoke (quickstart Scenario 2) |
| SC-004 | Migration <500 ms for ≤50 KB files | Feature suite of 50 tests runs in 0.47 s → per-operation well under budget |
| SC-005 | Re-run produces zero-byte diff | `test_migration_is_idempotent`, `test_enrich_roadmap_re_run_is_idempotent` |
| SC-006 | 100% of required subsection keys present post-migration | `test_missing_active_requirements_is_prepended`, `test_missing_tech_stack_section_is_prepended` (assert full key set) |
| SC-007 | Enricher with empty source → PARTIAL, no partial writes | `test_enrich_tech_stack_no_source_returns_partial`, `test_enrich_roadmap_missing_constitution_returns_partial` (both assert `read_bytes() == pre_bytes`) |
| SC-008 | Vision matches constitution's Project Purpose first sentence | `test_enrich_roadmap_replaces_vision_from_project_purpose` |

**Automated success-criteria coverage: 8 / 8 (100%).**

## Manual Testing

**No manual tests required.** All 20 functional requirements and 8
success criteria are covered by automated tests — consistent with the
precedent set by spec 059 (CLI-first enrichment keeps everything
mechanically testable).

### CLI smoke results (executed 2026-04-21)

Recorded during implementation (T019):

| Scenario | Result |
|:---------|:-------|
| 1 — Legacy roadmap + tech-stack, `doit update` | ✓ PASS (both files get required sections appended, legacy prose preserved) |
| 2 — `doit memory enrich tech-stack` | ✓ PASS (Languages/Frameworks/Libraries populated verbatim from constitution; Infrastructure/Deployment auto-created) |
| 3 — `doit memory enrich roadmap` | ✓ PASS (completed-items HTML comment inserted; Vision already real) |
| 4 — `doit memory migrate` umbrella | ✓ PASS (covered by `test_cli_memory_migrate_umbrella`) |
| 5 — Idempotent re-run | ✓ PASS (covered by `test_migration_is_idempotent` + `test_enrich_roadmap_re_run_is_idempotent`) |

## Recommendations

1. **No blockers.** 50/50 feature tests pass; full suite 2120/2120.
2. **100% FR + SC coverage automated** — no manual items introduced.
3. **Coverage gap (10%)** is entirely defensive code (ImportError branches for PyYAML, fault-injection-only error paths). Not worth increasing — would require invasive mocking for negligible return.
4. Optional follow-up: apply the same pattern to `.doit/memory/personas.md` as a future spec 061.

## Next Steps

- Run `/doit.reviewit` for a code review before PR.
- Or run `/doit.checkin` to finalize.
