# Fix Roadmap Migrator H3 Matching for Decorated Priority Headings

**Completed**: 2026-04-21
**Branch**: `061-fix-roadmap-h3-matching`
**Type**: Bug fix (regression from spec 060)

## Overview

`doit memory migrate` on a `.doit/memory/roadmap.md` with decorated priority headings — e.g. `### P1 - Critical (Must Have for MVP)` — now correctly recognises those subsections as satisfying the `P1..P4` contract. Before the fix, the migrator appended four duplicate empty `### P1..P4` stubs at the bottom of `## Active Requirements` on every real-world roadmap, because its H3 matching was exact-equality while the memory validator used a prefix regex (`^p[1-4]\b`).

The shared `_memory_shape.insert_section_if_missing` helper gained an optional per-H3 `matchers` parameter (default `None` preserves spec 060 behaviour byte-for-byte). The roadmap migrator opts in with regex-based prefix matchers mirroring the validator; the tech-stack migrator is unchanged.

## Regression provenance

Discovered by dogfooding spec 060 against doit's own repo: the roadmap at [.doit/memory/roadmap.md](../../.doit/memory/roadmap.md) uses decorated headings, and `doit memory migrate .` reported `PATCHED` with four spurious `added_fields`. Pure unit/integration tests in spec 060 missed the case because they used bare `P1/P2/P3/P4` headings.

## Requirements Implemented

| ID | Description | Status |
|----|-------------|--------|
| FR-001 | Migrator recognises `^p[1-4]\b` prefix in H3 | Done |
| FR-002 | No duplicate `### P<n>` stubs when matching H3 exists | Done |
| FR-003 | Bare `### P1..P4` still recognised (no regression) | Done |
| FR-004 | `PATCHED` returned for genuinely-missing subsections | Done |
| FR-005 | `PREPENDED` with full H2 + bare H3 block | Done |
| FR-006 | Helper accepts optional per-H3 matcher | Done |
| FR-007 | Default (no matcher) = exact case-insensitive equality | Done |
| FR-008 | Tech-stack migrator unchanged, 15 tests unchanged | Done |
| FR-009 | Roadmap migrator opts into prefix matcher mirroring validator | Done |
| FR-010 | Every spec-060 roadmap integration test passes unchanged | Done |
| FR-011 | Contract test covers ≥5 decoration forms × 4 priorities | Done |

## Technical Details

### Helper change (`_memory_shape.py`)

New keyword-only parameter on `insert_section_if_missing`:

```python
from collections.abc import Mapping

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

Semantics: when `matchers[required_title]` is present, "required H3 present" becomes `any(matcher(existing) for existing in existing_titles)`. When absent, fall back to exact-case-insensitive equality. Keys not in `h3_titles` are silently ignored.

### Roadmap opt-in (`roadmap_migrator.py`)

```python
def _priority_matcher(required_title: str) -> H3Matcher:
    token = required_title.strip().lower()
    pattern = re.compile(rf"^{re.escape(token)}\b", re.IGNORECASE)
    return lambda existing: bool(pattern.match(existing.strip()))

_PRIORITY_MATCHERS: Final[Mapping[str, H3Matcher]] = {
    p: _priority_matcher(p) for p in REQUIRED_ROADMAP_H3_UNDER_ACTIVE_REQS
}
```

Mirrors `memory_validator._validate_roadmap`'s `^p[1-4]\b` regex (case-insensitive, word-boundary-anchored). Does NOT accept `P10 - Critical` as matching `P1`.

### Tech-stack migrator unchanged

`tech_stack_migrator` does NOT opt into custom matchers — its canonical titles (`Languages`, `Frameworks`, `Libraries`) have no validator prefix semantics and exact-match remains correct.

## Files Changed

- [src/doit_cli/services/_memory_shape.py](../../src/doit_cli/services/_memory_shape.py) — +30 lines (`H3Matcher` alias, `matchers` param, `_present` predicate closure)
- [src/doit_cli/services/roadmap_migrator.py](../../src/doit_cli/services/roadmap_migrator.py) — +30 lines (`_priority_matcher`, `_PRIORITY_MATCHERS`)
- [tests/unit/services/test_memory_shape.py](../../tests/unit/services/test_memory_shape.py) — +117 lines (5 new parameterised tests)
- [tests/integration/test_roadmap_migration.py](../../tests/integration/test_roadmap_migration.py) — +120 lines (4 new decorated-priority tests)
- [tests/contract/test_roadmap_validator_migrator_alignment.py](../../tests/contract/test_roadmap_validator_migrator_alignment.py) — NEW, 280 lines (34 parameterised assertions + repo-dogfood regression guard)
- [CHANGELOG.md](../../CHANGELOG.md) — `[Unreleased]` Changed + Fixed entries

## Testing

### Automated

- **77 feature tests** pass (19 unit + 24 integration + 34 contract).
- **Full suite**: 2,257 passed / 182 skipped / 0 failed.
- **Coverage on touched files**: 95% (`_memory_shape.py` 99%, `roadmap_migrator.py` 88%; missed lines are error-path + re-export guards).
- **Ruff on spec 061 files**: clean.
- **Mypy**: clean (full tree).

### Dogfood

- `doit memory migrate .` on the doit repo returns `no_op` for all three memory files; `git diff` shows no changes.
- Permanent regression lock: `test_roadmap_migrator_is_noop_on_doit_own_repo` copies the committed roadmap to `tmp_path`, migrates the copy, and asserts byte-equality.

### Manual tests

None — all 10 `quickstart.md` scenarios are covered by automated tests.

## Related

- **Introducer**: #060 — Memory files migration (the fix lands on top of its infrastructure)
- **Ancestor**: #059 — Constitution frontmatter migration (introduced `MigrationResult`/`MigrationAction` types)
- **Follow-ups**: 3 pre-existing ruff warnings in untouched files (B904 in `memory_command.py`, F401 in `models/__init__.py`, SIM110 in `memory_validator.py`) remain for a separate cleanup spec.
