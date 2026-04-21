# Quickstart: Fix Roadmap Migrator H3 Matching

**Feature**: 061-fix-roadmap-h3-matching
**Date**: 2026-04-21

End-to-end validation scenarios for the prefix-matching fix. These double
as the manual smoke tests for `/doit.testit` and as the basis for the
integration/contract tests written in `/doit.taskit`.

---

## Prerequisites

- Python 3.11+
- Local build of doit with the spec 061 fix installed:
  `uv build && uv tool install . --reinstall --force`
- A scratch directory with a `.doit/memory/roadmap.md` file.

---

## Scenario 1 — The bug: decorated priorities before the fix

**Purpose**: Reproduce the regression to confirm the fix is needed.

1. Create `/tmp/sc1/.doit/memory/roadmap.md` with:

   ```markdown
   # Project Roadmap

   **Project**: Scenario 1

   ## Active Requirements

   ### P1 - Critical (Must Have for MVP)

   - [ ] Ship the thing

   ### P2 - High Priority (Significant Business Value)

   ### P3 - Medium Priority (Valuable)

   ### P4 - Low Priority (Nice to Have)
   ```

2. With the **pre-fix** build installed, run `doit memory migrate /tmp/sc1`.

3. **Expected (pre-fix, bug present)**: action reports `PATCHED`,
   `added_fields: ["P1","P2","P3","P4"]`, file gains four duplicate stubs
   at the bottom of `## Active Requirements`. This is the defect.

4. With the **post-fix** build, repeat. **Expected**: action `NO_OP`,
   `added_fields: []`, file byte-identical.

---

## Scenario 2 — Bare priorities (template default) remain NO_OP

**Purpose**: Ensure the fix doesn't regress the already-passing template
path.

1. Create `/tmp/sc2/.doit/memory/roadmap.md` with bare priorities:

   ```markdown
   # Project Roadmap

   ## Active Requirements

   ### P1

   ### P2

   ### P3

   ### P4
   ```

2. Run `doit memory migrate /tmp/sc2`.

3. **Expected**: action `NO_OP`, file unchanged.

---

## Scenario 3 — Genuinely missing priority is still patched

**Purpose**: Ensure the fix doesn't falsely suppress real insertions.

1. Create `/tmp/sc3/.doit/memory/roadmap.md` with P3 genuinely absent:

   ```markdown
   # Project Roadmap

   ## Active Requirements

   ### P1 - Critical

   ### P2 - High Priority

   ### P4 - Low Priority
   ```

2. Run `doit memory migrate /tmp/sc3`.

3. **Expected**: action `PATCHED`, `added_fields: ["P3"]`. Exactly one
   `### P3` stub inserted. `P1`, `P2`, `P4` unchanged.

---

## Scenario 4 — H2 absent: still PREPENDED with bare stubs

**Purpose**: Ensure the prepend path is unchanged.

1. Create `/tmp/sc4/.doit/memory/roadmap.md` missing `## Active Requirements`:

   ```markdown
   # Project Roadmap

   ## Vision

   Do the thing.
   ```

2. Run `doit memory migrate /tmp/sc4`.

3. **Expected**: action `PREPENDED`,
   `added_fields: ["Active Requirements","P1","P2","P3","P4"]`. Full block
   appended with bare canonical titles (canonical form — not decorated,
   matching current spec 060 behaviour).

---

## Scenario 5 — Case-insensitive prefix accepted

**Purpose**: Cover the `### p1 - Critical` / `### P1:Urgent` shapes.

1. Create `/tmp/sc5/.doit/memory/roadmap.md`:

   ```markdown
   ## Active Requirements

   ### p1 - Urgent

   ### P2: High Priority

   ### P3. Valuable

   ### P4 (Nice to have)
   ```

2. Run `doit memory migrate /tmp/sc5`.

3. **Expected**: action `NO_OP`, file unchanged.

---

## Scenario 6 — Rejected decoration forms remain absent

**Purpose**: Ensure the prefix matcher does NOT accept titles the validator
rejects.

1. Create `/tmp/sc6/.doit/memory/roadmap.md`:

   ```markdown
   ## Active Requirements

   ### Priority 1

   ### 1. P1

   ### Critical
   ```

2. Run `doit memory migrate /tmp/sc6`.

3. **Expected**: action `PATCHED`, `added_fields: ["P1","P2","P3","P4"]`.
   None of the existing headings satisfy `^p[1-4]\b`. Then run
   `doit verify-memory /tmp/sc6`; zero priority-related errors for
   roadmap.md.

---

## Scenario 7 — CRLF sources preserved

**Purpose**: Regression guard for spec 060's CRLF fix. Fix must not
re-introduce newline translation.

1. Create `/tmp/sc7/.doit/memory/roadmap.md` with explicit CRLF line
   endings (e.g. via `printf` with `\r\n`) and decorated priorities.

2. Run `doit memory migrate /tmp/sc7`.

3. **Expected**: action `NO_OP`. Verify: `file /tmp/sc7/.doit/memory/roadmap.md`
   still reports `CRLF line terminators`. Inspect bytes:
   `xxd /tmp/sc7/.doit/memory/roadmap.md | head` confirms `0d0a` unchanged.

---

## Scenario 8 — Tech-stack unaffected

**Purpose**: Ensure tech-stack's exact-match semantics are not broken.

1. Create `/tmp/sc8/.doit/memory/tech-stack.md` missing `### Libraries`
   under `## Tech Stack`:

   ```markdown
   ## Tech Stack

   ### Languages

   Python 3.11

   ### Frameworks

   Typer
   ```

2. Run `doit memory migrate /tmp/sc8`.

3. **Expected**: action `PATCHED`, `added_fields: ["Libraries"]`. Tech-stack
   continues to use default exact matching.

---

## Scenario 9 — Dogfood against doit's own repo

**Purpose**: The exact case that drove this spec.

1. In the doit repo: `doit memory migrate .` (or `doit update`).

2. **Expected**: action `NO_OP` for roadmap.md. Zero PATCHED/added fields.
   Git diff against develop shows no changes to `.doit/memory/roadmap.md`.

---

## Scenario 10 — Full test suite passes

**Purpose**: Confirm no regression to the 2127-test baseline from spec 060.

```bash
pytest tests/ -x --tb=short
```

**Expected**: all tests pass. The spec-060 integration-test counts
remain: 20 roadmap-migration + 15 tech-stack migration tests. The new
contract test (`test_roadmap_validator_migrator_alignment.py`) adds its
own parameterized cases and all pass.

---

## Success Criteria mapping

| Scenario | Validates SC |
|----------|--------------|
| SC-001 (decorated → NO_OP) | Scenarios 1, 5, 9 |
| SC-002 (roadmap test count unchanged) | Scenario 10 |
| SC-003 (tech-stack test count unchanged) | Scenarios 8, 10 |
| SC-004 (≥5 decoration forms covered) | Scenarios 1, 5, and the parameterized contract test |
| SC-005 (doit repo roadmap stabilizes) | Scenario 9 |
| SC-006 (no new CLI surface, services-only) | `doit memory migrate --help` output unchanged |
