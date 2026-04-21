# Contract: `_memory_shape.insert_section_if_missing` & Roadmap Migrator

**Feature**: 061-fix-roadmap-h3-matching
**Date**: 2026-04-21
**Scope**: Internal Python API contract (no CLI surface changes, no file
format changes).

This document defines the contract the implementation MUST honour.

---

## 1. `_memory_shape.insert_section_if_missing`

### Updated signature

```python
from collections.abc import Callable, Mapping

H3Matcher = Callable[[str], bool]

def insert_section_if_missing(
    source: str,
    h2_title: str,
    h3_titles: tuple[str, ...],
    *,
    stub_body: Callable[[str], str],
    matchers: Mapping[str, H3Matcher] | None = None,
) -> tuple[str, list[str]]:
    ...
```

### Parameter contracts

| Parameter | Type | Contract |
|-----------|------|----------|
| `source` | `str` | Full markdown source. May use LF / CRLF / CR line endings. Contract: preserved byte-for-byte on `NO_OP`. |
| `h2_title` | `str` | Required H2 heading text. Matched case-insensitively against existing H2 lines. |
| `h3_titles` | `tuple[str, ...]` | Required H3 titles, in canonical order. Order is preserved when inserting. |
| `stub_body` | `Callable[[str], str]` | Returns body for a freshly inserted H3. Receives H3 title. |
| `matchers` | `Mapping[str, H3Matcher] \| None` | **NEW**. Optional per-H3 matcher override. Defaults to `None`. |

### `matchers` contract

- **When `None`**: behaves exactly as in spec 060. Each required H3 is
  considered present iff some existing H3 title (case-insensitive, stripped)
  equals the required title (case-insensitive, stripped).
- **When a mapping**: for each required H3 title `t` in `h3_titles`:
  - If `t in matchers`: `t` is considered present iff any existing H3 title
    `e` (stripped) satisfies `matchers[t](e)`. The matcher is NOT called
    with the required title; it is closed over the required title at
    construction time.
  - If `t not in matchers`: fall back to exact-case-insensitive equality
    (same as the default-None path).
- **Invariants**:
  - Matchers do not influence insertion order; missing H3s are still
    inserted in `h3_titles` order.
  - Matchers do not influence H2 handling; the H2 match remains
    case-insensitive equality.
  - A matcher that returns True for multiple existing titles does not cause
    any insertion or change — the helper only asks "is there any existing
    H3 that satisfies the matcher?"
  - Matchers are pure: they must not mutate state or raise. (Violations are
    undefined behaviour; the helper does not wrap matcher calls in
    try/except.)
  - Keys in `matchers` that are not in `h3_titles` are silently ignored
    (treating the mapping as a look-up table is more ergonomic than
    forbidding extra keys).

### Return-value contract

- `(new_source, added_titles)` where `added_titles` is empty iff nothing
  was inserted.
- When `added_titles` is non-empty, `new_source != source` (byte-wise).
- When `added_titles` is empty, `new_source == source` (byte-wise). No
  re-normalisation, no line-ending change.

### Examples

```python
# Default behaviour (spec 060 compat):
new, added = insert_section_if_missing(
    src,
    "Tech Stack",
    ("Languages", "Frameworks", "Libraries"),
    stub_body=_ts_stub_body,
)
# matchers omitted → exact equality, current behaviour

# Opt-in per-H3 prefix matcher (roadmap):
matchers = {"P1": _priority_matcher("P1"), "P2": ..., "P3": ..., "P4": ...}
new, added = insert_section_if_missing(
    src,
    "Active Requirements",
    ("P1", "P2", "P3", "P4"),
    stub_body=_roadmap_stub_body,
    matchers=matchers,
)
# "### P1 - Critical" now satisfies "P1"; no duplicate stub inserted.
```

---

## 2. `roadmap_migrator` module contract

### New symbols

```python
_PRIORITY_MATCHERS: Mapping[str, H3Matcher]
```

- Frozen module-level mapping keyed by `REQUIRED_ROADMAP_H3_UNDER_ACTIVE_REQS`.
- Each value is a closure produced by `_priority_matcher(required_title)`
  that returns True iff the existing H3 title matches the regex
  `rf"^{re.escape(required_title.strip().lower())}\b"` with
  `re.IGNORECASE` against the stripped existing title.

### Unchanged public symbols

- `REQUIRED_ROADMAP_H2` — unchanged tuple.
- `REQUIRED_ROADMAP_H3_UNDER_ACTIVE_REQS` — unchanged tuple.
- `migrate_roadmap(path) -> MigrationResult` — unchanged signature. Only
  internals change: passes `_PRIORITY_MATCHERS` to the helper.

### Return-type contract (unchanged)

| Input shape | Action | `added_fields` |
|-------------|--------|----------------|
| File missing | `NO_OP` | `()` |
| H2 + all 4 priorities present (bare or decorated) | `NO_OP` | `()` |
| H2 present, some priorities truly missing | `PATCHED` | tuple of missing priorities |
| H2 absent | `PREPENDED` | `("Active Requirements", "P1", "P2", "P3", "P4")` |
| I/O or decode error | `ERROR` | `()` (error populated) |

Decorated priorities now route to NO_OP instead of spuriously to PATCHED.

---

## 3. `tech_stack_migrator` module contract

### Fully unchanged

- `migrate_tech_stack(path) -> MigrationResult` — does NOT pass `matchers`.
  Continues using the default (exact-case-insensitive) matching.
- All 15 existing integration tests pass unchanged.

---

## 4. Validator ↔ Migrator alignment contract (NEW)

### Invariant

For every H3 title `t` that `memory_validator._validate_roadmap` accepts as
a valid priority subsection — i.e. `re.match(r"^p[1-4]\b", t.strip(),
re.IGNORECASE)` is truthy — the roadmap migrator MUST treat `t` as
satisfying its canonical priority requirement. Formally:

```
∀ t : validator_accepts_priority(t) ⇒
      ∃ p ∈ {"P1","P2","P3","P4"} :
          _PRIORITY_MATCHERS[p](t.strip()) is True
```

### Test enforcement

`tests/contract/test_roadmap_validator_migrator_alignment.py` parameterises
over a corpus of decoration forms (at least 5 per priority) and asserts:

1. The validator's regex accepts the form.
2. `migrate_roadmap` on a roadmap containing exactly that form returns
   `NO_OP` (when no other priorities are missing) or `PATCHED` with
   `added_fields` that does NOT contain the priority in question.

### Negative cases

For H3 titles the validator does NOT accept (e.g. `### Priority 1`,
`### Critical`, `### p5`, `### 1. P1`), the migrator MUST treat them as
absent and add the canonical stub. The contract test covers this leg too.

---

## 5. Error handling contract (unchanged)

No new error codes, no new exception types. `ConstitutionMigrationError`,
`MigrationAction.ERROR`, and the `MigrationResult.error` field continue to
serve as they did in spec 059 / 060.

---

## 6. Out-of-scope (for explicitness)

- No change to `MigrationResult` dataclass.
- No change to `EnrichmentResult` or enricher modules.
- No new CLI flags, subcommands, or output formats.
- No change to template stub bodies.
- No change to `PLACEHOLDER_TOKENS` or validator placeholder detection.
- No change to `write_text_atomic` semantics.
