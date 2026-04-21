# Test Report: Fix Roadmap Migrator H3 Matching for Decorated Priority Headings

**Date**: 2026-04-21
**Branch**: `061-fix-roadmap-h3-matching`
**Test Framework**: pytest 9.0.2 (Python 3.11.14)

## Automated Tests

### Execution Summary (spec 061 feature tests)

| Metric | Value |
| ------ | ----- |
| Total Tests | 77 |
| Passed | 77 |
| Failed | 0 |
| Skipped | 0 |
| Duration | 0.35s |

### Execution Summary (full project suite)

| Metric | Value |
| ------ | ----- |
| Total Tests | 2,438 |
| Passed | 2,256 |
| Failed | 0 |
| Skipped | 182 |
| Duration | 64.16s |

Notes:

- 182 skipped tests are platform-conditional (macOS/Windows markers, E2E suites).
- 1 collection-level error excluded via `--ignore=tests/unit/test_mcp_server.py`: the `mcp` module is an optional runtime dependency and is not installed in the local `.venv` (documented in CLAUDE.md as optional). Not a regression.

### Failed Tests Detail

None.

### Breakdown by tier

| Tier | File | Tests | Passed |
| ---- | ---- | ----- | ------ |
| Unit (helper) | `tests/unit/services/test_memory_shape.py` | 19 (14 pre-existing + 5 new for spec 061) | 19 |
| Integration (roadmap) | `tests/integration/test_roadmap_migration.py` | 24 (20 pre-existing + 4 new for spec 061) | 24 |
| Contract (alignment) | `tests/contract/test_roadmap_validator_migrator_alignment.py` (NEW) | 34 (28 positive + 5 negative + 1 guard) | 34 |

### Code Coverage (spec 061 touched modules)

| File | Statements | Miss | Cover | Missing lines |
| ---- | ---------- | ---- | ----- | ------------- |
| `src/doit_cli/services/_memory_shape.py` | 91 | 1 | 99% | 219 (bare-CR old-Mac line-ending branch — untested since spec 060, not regressed) |
| `src/doit_cli/services/roadmap_migrator.py` | 50 | 6 | 88% | 129-136 (OSError + UnicodeDecodeError paths), 166-167 (`_ = DoitError` re-export guard) |
| **Total (spec 061 files)** | **141** | **7** | **95%** | — |

### Quality checks

| Check | Scope | Result |
| ----- | ----- | ------ |
| `ruff check` | spec 061 files only | ✓ All checks passed |
| `ruff check` | `src/ tests/` (full tree) | 3 warnings — ALL pre-existing (B904 in `memory_command.py:317`, F401 in `models/__init__.py`, SIM110 in `memory_validator.py`). None from spec 061. Tracked as spec-060 follow-ups. |
| `pre-commit run mypy --hook-stage manual --all-files` | Full tree | ✓ Passed |

## Requirement Coverage

| Requirement | Description | Test(s) | Status |
| ----------- | ----------- | ------- | ------ |
| FR-001 | Migrator recognises `^p[1-4]\b` prefix in H3 | `test_decorated_priority_headings_yield_no_op`, `test_validator_accepted_forms_are_present_for_migrator[...]` (28 parameterisations) | ✅ COVERED |
| FR-002 | No duplicate `### P<n>` stubs when matching H3 exists | `test_decorated_priority_headings_yield_no_op`, `test_decorated_priorities_with_one_missing_patches_only_missing` | ✅ COVERED |
| FR-003 | Bare `### P1..P4` still recognised (no regression) | `test_bare_priority_headings_yield_no_op`, `test_complete_roadmap_is_noop` (pre-existing), parameterised `{p}` form in alignment test | ✅ COVERED |
| FR-004 | `PATCHED` returned for genuinely-missing subsections | `test_decorated_priorities_with_one_missing_patches_only_missing`, `test_partial_priorities_only_adds_missing` (pre-existing) | ✅ COVERED |
| FR-005 | `PREPENDED` with full H2 + bare H3 block | `test_absent_active_requirements_prepends_full_block`, `test_missing_active_requirements_is_prepended` (pre-existing) | ✅ COVERED |
| FR-006 | Helper accepts optional per-H3 matcher | `test_matcher_honoured_for_one_h3_only`, `test_matchers_none_preserves_exact_match`, `test_matcher_extra_keys_ignored`, `test_matcher_receives_stripped_existing_title`, `test_matcher_never_called_for_absent_h3` | ✅ COVERED |
| FR-007 | Default (no matcher) = exact case-insensitive equality | `test_matchers_none_preserves_exact_match` + every pre-existing helper test (14 still pass with default-None path) | ✅ COVERED |
| FR-008 | Tech-stack migrator unchanged, 15 tests unchanged | T005 verification run (`tests/integration/test_tech_stack_migration.py`: 15/15 + `tests/contract/test_memory_files_migration_contract.py`: 8/8) | ✅ COVERED |
| FR-009 | Roadmap migrator opts into prefix matcher mirroring validator | `test_validator_accepted_forms_are_present_for_migrator` (bijection via closure regex) | ✅ COVERED |
| FR-010 | Every spec-060 roadmap integration test passes unchanged | Pre-existing 20 tests in `test_roadmap_migration.py` — all passed in full suite run | ✅ COVERED |
| FR-011 | Contract test over validator-accepted decoration corpus (≥5 per priority) | `test_validator_accepted_forms_are_present_for_migrator` — 7 decoration forms × 4 priorities = 28 positive cases, plus 5 negative cases, plus 1 warning-drift guard | ✅ COVERED |

**Coverage**: 11 / 11 functional requirements (100%).

### Success Criteria Coverage

| Criterion | Validated by | Status |
| --------- | ------------ | ------ |
| SC-001 (decorated → no_op, zero byte changes) | `test_decorated_priority_headings_yield_no_op` + T008 dogfood | ✅ MET |
| SC-002 (20 spec-060 roadmap tests pass unchanged) | Integration tier 20/20 pre-existing passed | ✅ MET |
| SC-003 (15 spec-060 tech-stack tests pass unchanged) | T005 verification: 15/15 + 8/8 contract | ✅ MET |
| SC-004 (≥5 decoration forms × 4 priorities covered) | 7 decoration forms × 4 priorities = 28 in alignment test | ✅ MET |
| SC-005 (doit repo roadmap → NO_OP, zero `added_fields`) | T008 dogfood: `{"file": "roadmap.md", "action": "no_op", "added_fields": []}` | ✅ MET |
| SC-006 (no new deps, no new CLI surface) | No change to `cli/memory_command.py`, no new dependencies in `pyproject.toml` | ✅ MET |

**Success Criteria**: 6 / 6 (100%).

## Manual Testing

### Checklist Status

All behavioural scenarios from `quickstart.md` are covered by the automated suite — no manual tests remain. Retained here as a trace of which scenarios map to which automated guards.

| Scenario | Description | Automated By | Status |
| -------- | ----------- | ------------ | ------ |
| SC-1 | Decorated priorities → NO_OP | `test_decorated_priority_headings_yield_no_op` | ✅ AUTOMATED |
| SC-2 | Bare priorities still NO_OP | `test_bare_priority_headings_yield_no_op`, `test_complete_roadmap_is_noop` | ✅ AUTOMATED |
| SC-3 | Genuinely-missing P3 → PATCHED with only P3 | `test_decorated_priorities_with_one_missing_patches_only_missing` | ✅ AUTOMATED |
| SC-4 | H2 absent → PREPENDED with bare canonical block | `test_absent_active_requirements_prepends_full_block` | ✅ AUTOMATED |
| SC-5 | Case-insensitive decoration forms accepted | Alignment test covers `{p}`, `{p} - Critical`, `{p}: Urgent`, `{p}. Must-Have`, `{p} (MVP)`, trailing whitespace, em-dash | ✅ AUTOMATED |
| SC-6 | Rejected decoration forms still trigger insertion | `test_validator_rejected_forms_are_absent_for_migrator` (5 forms) | ✅ AUTOMATED |
| SC-7 | CRLF preservation | Pre-existing `test_migrator_preserves_crlf_line_endings` + helper unit `test_crlf_line_endings_are_preserved` | ✅ AUTOMATED |
| SC-8 | Tech-stack unaffected | T005 regression verification (15/15) | ✅ AUTOMATED |
| SC-9 | Dogfood on doit repo | T008 — `doit memory migrate .` returned `no_op`, file byte-identical, `doit verify-memory` clean | ✅ MANUAL (one-off smoke test complete) |
| SC-10 | Full suite passes | 2,256 passed, 0 failed | ✅ AUTOMATED |

## Recommendations

1. **Ship as-is.** All 11 FRs and 6 SCs are automated or dogfood-verified. 77 new/modified tests green; full suite 2,256 passed. Coverage on touched files 95%. Ruff clean on 061 files, mypy clean.
2. **Follow-up (unrelated to 061)**: the three pre-existing ruff warnings (B904 in `memory_command.py`, F401 in `models/__init__.py`, SIM110 in `memory_validator.py`) remain open from spec 060. Track as a separate cleanup spec — out of scope for 061.
3. **Release notes**: `CHANGELOG.md` `[Unreleased]` entry already mentions the regression source (#060) and the manual-cleanup guidance for any roadmaps already corrupted by the pre-fix migrator.

## Next Steps

- Run `/doit.reviewit` for a code review before finalizing.
- Run `/doit.checkin` to merge and archive the roadmap item.
