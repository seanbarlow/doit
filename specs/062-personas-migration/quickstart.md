# Quickstart: Personas.md Migration

**Feature**: 062-personas-migration
**Date**: 2026-04-21

End-to-end validation scenarios for the personas.md migrator, enricher, and validator rule. Every scenario below is covered by the automated test suite; this doc doubles as the hand-testing checklist for `/doit.testit` and as the basis for integration tests written in `/doit.taskit`.

---

## Prerequisites

- Python 3.11+
- Local build: `uv build && uv tool install . --reinstall --force`
- A scratch directory (these scenarios never touch the doit repo's own `.doit/` files)

---

## Scenario 1 — Absent personas.md is opt-in NO_OP

**Purpose**: Core US2 — personas are opt-in; no auto-create.

1. Create `/tmp/sc1/.doit/memory/` with `constitution.md`, `roadmap.md`, `tech-stack.md` (valid content). Do NOT create `personas.md`.
2. Run `doit memory migrate /tmp/sc1 --json`.
3. **Expected**: JSON output is exactly four rows. The personas.md row reads `{"file": "personas.md", "action": "no_op", "added_fields": [], "error": null}`.
4. Verify: `ls /tmp/sc1/.doit/memory/personas.md` — the file MUST NOT exist.
5. Run `doit verify-memory /tmp/sc1`. **Expected**: zero errors, zero warnings. No mention of personas.md.

---

## Scenario 2 — Partial personas.md: missing `## Detailed Profiles`

**Purpose**: Core US1 — shape migration patches in the missing H2.

1. Create `/tmp/sc2/.doit/memory/personas.md`:

   ```markdown
   # Personas

   ## Persona Summary

   | ID | Name | Role | Archetype | Primary Goal |
   |----|------|------|-----------|--------------|
   | P-001 | Dana | Dev | Power User | Rapid iteration |
   ```

2. Run `doit memory migrate /tmp/sc2 --json`.
3. **Expected**: personas.md row `{"action": "patched", "added_fields": ["Detailed Profiles"]}`.
4. Inspect the file:
   - `## Persona Summary` with Dana row is PRESERVED byte-for-byte.
   - `## Detailed Profiles` stub is APPENDED at end of file with the placeholder comment.
   - Three `[TOKEN]` placeholders are present (triggers the "still contains template placeholders" validator warning until the user populates).
5. Rerun `doit memory migrate /tmp/sc2`. **Expected**: personas.md row is now `no_op` with `added_fields: []`; file bytes unchanged from step 4.

---

## Scenario 3 — Partial personas.md: missing `## Persona Summary`

**Purpose**: US1 — the OTHER H2 gap.

1. Create `/tmp/sc3/.doit/memory/personas.md`:

   ```markdown
   # Personas

   ## Detailed Profiles

   ### Persona: P-001

   Dana the developer.
   ```

2. Run `doit memory migrate /tmp/sc3`.
3. **Expected**: `{"action": "patched", "added_fields": ["Persona Summary"]}`.
4. Inspect file: `## Persona Summary` stub inserted in canonical order (appended, because inserting at top-of-file would displace `# Personas`). The existing `## Detailed Profiles` block is byte-preserved.
5. Rerun → `no_op`.

---

## Scenario 4 — Both H2s missing (file exists but unrelated content only)

**Purpose**: US1 — both stubs inserted in one invocation.

1. Create `/tmp/sc4/.doit/memory/personas.md`:

   ```markdown
   # Old notes

   Some unrelated prose about personas in general.
   ```

2. Run `doit memory migrate /tmp/sc4`.
3. **Expected**: `{"action": "patched", "added_fields": ["Persona Summary", "Detailed Profiles"]}`.
4. Inspect file: original prose preserved byte-for-byte; both H2 stubs appended in canonical order.

---

## Scenario 5 — Complete personas.md is NO_OP

**Purpose**: US1 regression guard — fully-shaped files stay NO_OP.

1. Create `/tmp/sc5/.doit/memory/personas.md` with both required H2s present and at least one `### Persona: P-001` block under Detailed Profiles.
2. Capture bytes: `sha256sum /tmp/sc5/.doit/memory/personas.md`.
3. Run `doit memory migrate /tmp/sc5`.
4. **Expected**: `{"action": "no_op", "added_fields": []}`; bytes unchanged.

---

## Scenario 6 — Enricher: placeholder-laden file → PARTIAL

**Purpose**: US3 — linter-mode reporting.

1. Copy `src/doit_cli/templates/personas-output-template.md` verbatim to `/tmp/sc6/.doit/memory/personas.md`. The template contains `{Persona Name}`, `{Role}`, `{Archetype}`, `{FEATURE_NAME}`, etc.
2. Run `doit memory enrich personas --project-dir /tmp/sc6 --json`.
3. **Expected**: exit code `1`. Output includes `"action": "partial"` and `"unresolved_fields": [...]` with the distinct placeholder names sorted alphabetically.
4. Verify: the file on disk is UNCHANGED (bytes identical to the template copy).
5. Run `doit memory enrich personas --project-dir /tmp/sc6` (without --json). **Expected**: Rich output includes the hint "Run /doit.roadmapit to populate personas interactively."

---

## Scenario 7 — Enricher: placeholder-free file → NO_OP

**Purpose**: US3 — linter passes clean files.

1. Create `/tmp/sc7/.doit/memory/personas.md` with no `{placeholder}` tokens (real content in every field).
2. Run `doit memory enrich personas --project-dir /tmp/sc7 --json`.
3. **Expected**: exit code `0`. `"action": "no_op"`, `"unresolved_fields": []`.
4. File bytes unchanged.

---

## Scenario 8 — Enricher on absent file

**Purpose**: US3 — opt-in semantic also applies to the enricher.

1. `/tmp/sc8/.doit/memory/` contains no personas.md.
2. Run `doit memory enrich personas --project-dir /tmp/sc8 --json`.
3. **Expected**: exit code `0`. `"action": "no_op"`, `"unresolved_fields": []`, `"error": null`. File still does not exist.

---

## Scenario 9 — Validator: malformed persona ID is an ERROR

**Purpose**: US4 — ID format enforcement.

1. Create `/tmp/sc9/.doit/memory/personas.md` with a valid-shape body but one non-canonical heading:

   ```markdown
   ## Persona Summary

   | ID | Name |
   |----|------|
   | P-1 | Dana |

   ## Detailed Profiles

   ### Persona: P-1

   Dana the developer.
   ```

2. Run `doit verify-memory /tmp/sc9 --json`.
3. **Expected**: exit code `1`. Output includes one ERROR for personas.md with a message like "malformed persona ID `P-1` — expected `P-NNN`".

---

## Scenario 10 — Validator: missing H2 is an ERROR

**Purpose**: US4 — shape enforcement.

1. Create `/tmp/sc10/.doit/memory/personas.md` with only `## Persona Summary` (no `## Detailed Profiles`).
2. Run `doit verify-memory /tmp/sc10 --json`.
3. **Expected**: exit code `1`. Output includes one ERROR "missing required `## Detailed Profiles` section".

---

## Scenario 11 — Validator: empty-but-shape-valid → WARNING

**Purpose**: US4 — content-empty is warning, not error.

1. Create `/tmp/sc11/.doit/memory/personas.md`:

   ```markdown
   ## Persona Summary

   | ID | Name |
   |----|------|

   ## Detailed Profiles

   <!-- No personas yet -->
   ```

2. Run `doit verify-memory /tmp/sc11`.
3. **Expected**: exit code `0` (warnings don't fail). Output includes one WARNING "`## Detailed Profiles` has no persona entries".

---

## Scenario 12 — Validator: absent personas.md → no issues

**Purpose**: US4 — opt-in semantic mirrored in validator.

1. `/tmp/sc12/.doit/memory/` with constitution.md, roadmap.md, tech-stack.md (valid); no personas.md.
2. Run `doit verify-memory /tmp/sc12 --json`.
3. **Expected**: zero errors and zero warnings for personas.md. (The other three files are validated as usual.)

---

## Scenario 13 — Tech-stack & roadmap still work

**Purpose**: Regression guard — spec 060/061 invariants unbroken.

1. Run `pytest tests/integration/test_roadmap_migration.py tests/integration/test_tech_stack_migration.py tests/contract/test_memory_files_migration_contract.py tests/contract/test_roadmap_validator_migrator_alignment.py -v`.
2. **Expected**: ALL tests pass (24 roadmap + 15 tech-stack + 8 contract + 34 validator-alignment = 81 tests, plus spec 062's new contract tests).

---

## Scenario 14 — Full quality gauntlet

**Purpose**: Full suite green before merge.

```bash
ruff check src/ tests/                                     # must pass
pre-commit run mypy --hook-stage manual --all-files        # must pass
pytest tests/ --ignore=tests/unit/test_mcp_server.py -q    # must pass (>= 2257 + new spec 062 tests)
```

Target: **+77 new tests (est.)** for spec 062 on top of the 2,257 spec-061 baseline.

---

## Scenario 15 — Dogfood on doit repo itself

**Purpose**: Ensure the new validator rule doesn't break doit's own memory contract. (doit doesn't use personas.md, so this is an "absence path" smoke test.)

1. In the doit repo root: `doit memory migrate . --json`.
2. **Expected**: JSON includes all four rows; personas.md row is `no_op`. No file created at `.doit/memory/personas.md`.
3. `doit verify-memory .`. **Expected**: `0 error(s), 0 warning(s)`. No personas-related output.
4. `git status`. **Expected**: working tree clean.

---

## Success Criteria mapping

| Scenario | Validates SC |
| -------- | ------------ |
| SC-001 (absent personas.md → no_op) | Scenarios 1, 12, 15 |
| SC-002 (missing H2s → patched + idempotent) | Scenarios 2, 3, 4 |
| SC-003 (complete personas.md → no_op byte-identical) | Scenario 5 |
| SC-004 (malformed ID → ERROR; valid → clean) | Scenarios 9, 11, 12 |
| SC-005 (spec 060/061 tests pass unchanged) | Scenarios 13, 14 |
| SC-006 (contract tests pass) | New contract tests from `/doit.taskit`; verified in Scenario 14 |
| SC-007 (no new deps, one new subcommand only) | `doit memory --help` shows +1 subcommand; `pyproject.toml` unchanged |
