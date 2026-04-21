# Research: Fix Roadmap Migrator H3 Matching for Decorated Priority Headings

**Feature**: 061-fix-roadmap-h3-matching
**Date**: 2026-04-21
**Spec**: [spec.md](spec.md)

---

## Context

Spec 060 shipped a shared `_memory_shape.insert_section_if_missing` helper that
both the roadmap and tech-stack migrators route through. Its `_normalise`
function (`title.strip().lower()`) matches H3 subsection titles by exact
case-insensitive equality. The validator (`memory_validator._validate_roadmap`)
uses a different rule for roadmap priorities: `re.match(r"^p[1-4]\b", title,
re.IGNORECASE)` — a prefix regex that accepts decoration.

Dogfooding spec 060 against doit's own `.doit/memory/roadmap.md` (whose
priority H3s read `### P1 - Critical (Must Have for MVP)` etc.) revealed the
semantic gap: the migrator spuriously PATCHES four duplicate empty stubs at
the bottom of `## Active Requirements`. This research pins down the minimal
way to realign the migrator with the validator without loosening tech-stack's
semantics.

---

## Decision 1: Where does the matcher customization live?

**Decision**: Add an optional `matchers` parameter to
`_memory_shape.insert_section_if_missing`. Default is `None` (preserves current
exact-case-insensitive behaviour). Callers may pass a mapping
`{h3_title: Callable[[str], bool]}` keyed by canonical required title.

**Rationale**:

- The matching logic lives in `_memory_shape` today. Duplicating it inside
  `roadmap_migrator` (e.g. pre-checking the source for matching H3s before
  calling the helper) would cause the two code paths to drift and duplicate
  H3-scanning logic — the exact problem the shared helper was introduced to
  avoid in spec 060.
- A per-H3 matcher is more flexible than a per-call matcher because it allows
  heterogeneous matching strategies in one invocation. Roadmap only needs
  uniform prefix matching across `P1..P4`, but tech-stack could later opt in
  per field (e.g. loose match for `Languages` only) without forcing a helper
  redesign.
- Defaulting to `None` keeps spec 060's byte-for-byte compatibility for
  tech-stack and for any future caller that doesn't need custom matching.

**Alternatives considered**:

- *Single matcher callable for the whole call*: simpler signature but less
  flexible. Rejected because it couples all H3s in a call to one strategy;
  future callers might mix strategies.
- *Predicate on the required title instead of a callable*: e.g. a regex or
  prefix string. Rejected because it constrains extension — tech-stack might
  one day want full-regex match and roadmap's validator uses a regex, so
  a callable cleanly wraps either option.
- *Move matching into the migrator and drop the helper*: rejected because
  spec 060 explicitly introduced the helper to avoid duplication. Splitting
  up now re-introduces the exact duplication.
- *Expose a classmethod-style strategy registry*: rejected as over-design for
  two callers.

---

## Decision 2: How is the roadmap's prefix matcher defined?

**Decision**: Define a module-level constant in `roadmap_migrator`:

```python
_PRIORITY_H3_RE = re.compile(r"^p[1-4]\b", re.IGNORECASE)

def _priority_matcher(required: str) -> Callable[[str], bool]:
    target = required.strip().lower()
    token_re = re.compile(rf"^{re.escape(target)}\b", re.IGNORECASE)
    return lambda existing: bool(token_re.match(existing.strip()))
```

The migrator builds a mapping `{"P1": _priority_matcher("P1"), "P2": …}` and
passes it through to the helper.

**Rationale**:

- The matcher's semantics MUST mirror
  `memory_validator._validate_roadmap`'s `^p[1-4]\b` regex (case-insensitive,
  word-boundary). Using `re.escape(target) + \b` per required title gives the
  right semantic for any priority token (`P1..P4`) without hard-coding
  `[1-4]` again in the migrator — the enumeration is already in
  `REQUIRED_ROADMAP_H3_UNDER_ACTIVE_REQS`.
- The closure binds the canonical required title at construction, so the
  helper's inner loop just invokes `matcher(existing_h3_title)` without
  needing the required title separately.

**Alternatives considered**:

- *Reuse the validator's compiled regex directly*: rejected because the
  validator's regex is hard-coded to `P[1-4]`; the matcher abstraction wants
  to parameterize over the required title so the migrator can be extended
  later without edits to the helper.
- *Inline string-prefix check (`existing.lower().startswith("p1")`)*:
  rejected because it accepts `### P10 - Critical` as matching `P1`. The
  word-boundary regex is explicit about what counts.

---

## Decision 3: Matcher callable signature — `(existing) -> bool` vs `(existing, required) -> bool`?

**Decision**: Internal matcher signature is `Callable[[str], bool]` — closed
over the required title. Public contract surfaces as
`Mapping[str, Callable[[str], bool]]` keyed by required H3 title.

**Rationale**:

- Inside the helper's iteration over required titles we already have the
  required title as the mapping key; the matcher then only needs the
  candidate existing title. Simpler inner loop, harder to misuse.
- The mapping key is the canonical form (`"P1"`), which also serves as the
  documentation of what this matcher is responsible for. A two-arg callable
  would re-check the required title inside every call — redundant.

**Alternatives considered**:

- *`Callable[[str, str], bool]`* (as sketched in the spec): cleaner in the
  abstract but the helper would always pass the same required title that
  the map key already identifies. Decision 2's closure pattern is
  functionally equivalent and idiomatic.

---

## Decision 4: Test parameterization — unit vs contract test?

**Decision**: Two complementary test tiers.

- **Unit** (helper level): Parameterize `test_memory_shape.py` over
  `(required_title, existing_heading, expected_added)` with a custom matcher
  mapping. Covers the helper contract mechanically.
- **Contract** (validator ↔ migrator alignment): New
  `tests/contract/test_roadmap_validator_migrator_alignment.py` that for
  each decoration form the validator accepts (generated from a fixture
  corpus: `P1`, `p1`, `P1 - Critical`, `P1 : Urgent`, `P1. Must-Have`,
  `P1 (MVP)`, `P1<trailing spaces>`) builds a minimal roadmap, runs both
  `memory_validator` and `migrate_roadmap`, and asserts:
  - validator emits no `missing required P1..P4` error, AND
  - migrator returns `NO_OP` for that priority (may return `PATCHED` only
    for other priorities explicitly omitted by the fixture).

**Rationale**:

- Unit tests lock the helper's behaviour; contract tests lock the
  cross-module invariant that caused the bug. Spec 060's contract tests
  caught constant-alignment (`REQUIRED_*` ↔ validator headings) but missed
  semantic alignment — that's the gap US3 fills.
- Parameterization over a decoration corpus is cheap and enumerates the
  specific cases the user ran into (`### P1 - Critical`).

**Alternatives considered**:

- *Only contract test*: rejected — unit coverage is needed to exercise the
  helper's mapping plumbing directly (e.g. matcher for one priority but
  not another).
- *Hypothesis / property-based test*: attractive but overkill for a
  narrow regex. A parameterized corpus is more auditable and the
  decoration forms are already enumerated in the spec's edge cases.

---

## Decision 5: Preserving CRLF / atomic writes / stub bodies

**Decision**: No changes. Spec 060's CRLF-preservation (`_detect_newline`,
`read_bytes().decode("utf-8")`) and atomic-write (`write_text_atomic`)
machinery remain unchanged. Stub body generation (`_roadmap_stub_body`)
remains unchanged. This fix is purely at the H3-matching step inside
`insert_section_if_missing`.

**Rationale**: Keeps blast radius minimal. The regression is about matching,
not writing.

---

## Decision 6: Tech-stack migrator — should it also opt in?

**Decision**: No. Tech-stack continues to use default exact matching.

**Rationale**:

- The validator has no prefix semantics for tech-stack subsections — it
  checks for the presence of the literal `Languages` / `Frameworks` /
  `Libraries` headings (see `_validate_tech_stack`). No semantic gap, no
  bug.
- Users decorating `### Languages (Python, TS)` probably mean something
  specific (e.g. a parenthetical they want to keep). Prefix matching would
  silently swallow that as "Languages already present" and might surprise
  them. Exact match is the correct default here.
- Out-of-scope for this spec. A future spec can revisit per field.

**Alternatives considered**: none worth listing — covered by spec's
"Out of Scope" section.

---

## Summary table

| Decision | Choice | Key rationale |
|----------|--------|---------------|
| 1. Where | Per-H3 `matchers` param on `_memory_shape.insert_section_if_missing` | No duplication; tech-stack opt-out; future-proof |
| 2. How  | `re.compile(rf"^{re.escape(target)}\b", IGNORECASE)` closure per priority | Mirrors validator's `^p[1-4]\b` regex |
| 3. Signature | `Callable[[str], bool]` closed over required title | Simpler inner loop, matches canonical key |
| 4. Tests | Unit (helper) + contract (validator↔migrator alignment) | Locks both behaviour and bidirectional invariant |
| 5. CRLF/atomic | Unchanged | Fix is matching-layer only |
| 6. Tech-stack | Unchanged (default exact) | No validator gap, opt-in is explicit |

All NEEDS CLARIFICATION items resolved. Ready for Phase 1.
