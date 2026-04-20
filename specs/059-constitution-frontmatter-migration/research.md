# Research: Constitution Frontmatter Migration

**Feature**: `059-constitution-frontmatter-migration`
**Date**: 2026-04-20
**Status**: Complete — no open `NEEDS CLARIFICATION` markers in spec.md

This Phase 0 document captures the technical decisions that drive the Phase 1
design artifacts (data model, contracts, quickstart). No unknowns remain; each
decision below has a chosen path, a rationale, and an explicit rejection of
alternatives.

## 1. Migration hook location

**Decision**: Insert the migration step inside
`src/doit_cli/cli/init_command.py` at the end of `run_init(..., update=True)`,
immediately **after** `copy_memory_templates()` (line 502) and **before** the
config/hooks copy (line 504-511).

**Rationale**:

- This is the single code path both `doit update` and `doit init --update`
  traverse; placing the hook here guarantees one entry point for the migration.
- `copy_memory_templates()` already respects `overwrite=force` semantics, so
  the migration runs whether or not the user passed `--force`.
- Putting it *after* template copy means any freshly-written constitution.md
  (rare: only happens with `--force`) is already valid-shape and the migration
  becomes a no-op — good default.

**Alternatives considered**:

- *Top-level hook as a new `doit migrate` command*: rejected — splits the
  upgrade UX across two commands; users already use `doit update` for
  everything else.
- *Inside `copy_memory_templates()` in `template_manager.py`*: rejected —
  that service is about copying bundled template files, not rewriting
  user-authored content; mixing responsibilities would hurt future
  maintenance.
- *A `MemoryWriter` service parallel to `SkillWriter`*: rejected as premature
  — we have exactly one memory file to migrate right now. Revisit if
  equivalent migrations for `roadmap.md` and `tech-stack.md` land.

## 2. Placeholder token convention

**Decision**: Use square-bracketed uppercase tokens aligned with the existing
`PLACEHOLDER_TOKENS` tuple in
`src/doit_cli/services/memory_validator.py:35`. Define exactly seven new
tokens, one per required field:

| Field | Placeholder |
|:------|:------------|
| `id` | `[PROJECT_ID]` |
| `name` | `[PROJECT_NAME]` |
| `kind` | `[PROJECT_KIND]` |
| `phase` | `[PROJECT_PHASE]` |
| `icon` | `[PROJECT_ICON]` |
| `tagline` | `[PROJECT_TAGLINE]` |
| `dependencies` | `[[PROJECT_DEPENDENCIES]]` (yaml list with one sentinel item) |

**Rationale**:

- Reuses the existing convention (square-bracketed uppercase tokens) that
  `memory_validator.py` already recognizes for body placeholders. Extending
  the same mental model to frontmatter is consistent with the codebase.
- Exact-token matching (not regex) avoids false positives on legitimate
  user content containing brackets (spec edge case).
- For `dependencies`, which is schema-typed as an array, we emit a
  single-item list `[[PROJECT_DEPENDENCIES]]` so the YAML parses cleanly
  and the sentinel is still exact-match detectable.

**Alternatives considered**:

- *Use YAML null (`~`) for missing fields*: rejected — fails schema
  validation (`required` fields must be present **and** typed correctly;
  `id` must match a regex). Placeholders signal "fill me in" better than
  null.
- *`"TODO"` strings*: rejected — too common in user content, high false-
  positive risk for the enrichment detector.
- *Per-field regex patterns matching the schema*: rejected — harder to
  reason about, harder to pattern-match in the skill.

## 3. Warning-severity classification for placeholders

**Decision**: Extend the `ConstitutionFrontmatter.validate()` path in
`src/doit_cli/models/memory_contract.py:115-169` so that a placeholder
token — detected via exact-match against the placeholder registry — is
reported with `MemoryIssueSeverity.WARNING` instead of `ERROR`. All other
schema violations (wrong type, bad regex, missing required field) remain
`ERROR`.

**Rationale**:

- Keeps the existing `MemoryContractIssue` / severity infrastructure;
  no new types needed.
- Spec requires that a migrated file passes `verify-memory` with warnings
  not errors (SC-001, FR-015).
- Severity classification lives at the same layer as the schema check,
  so there's a single decision point.

**Alternatives considered**:

- *Introduce a third severity (`INFO`)*: rejected — overkill; WARNING is
  the right severity level because the user does need to act (run the
  skill or hand-edit) before shipping.
- *Skip validation entirely when placeholders detected*: rejected —
  hides real schema violations that co-exist with placeholders.

## 4. YAML serialization

**Decision**: Use `yaml.safe_dump()` from the already-declared PyYAML
dependency, matching the existing `split_frontmatter()` lazy-import pattern
in `memory_contract.py:229-242`. Serialize with
`sort_keys=False, default_flow_style=False, allow_unicode=True` so the
frontmatter reads left-to-right in schema order and preserves any unicode
in user values.

**Rationale**:

- PyYAML is already a declared dep (`pyyaml>=6.0`); no new dependency.
- `sort_keys=False` lets us emit required fields in schema order
  (`id, name, kind, phase, icon, tagline, dependencies`) for consistent
  diffs across projects.
- `default_flow_style=False` gives block style (one key per line) matching
  the spec.md example in `docs/templates/schemas.md`.

**Alternatives considered**:

- *`ruamel.yaml` for round-trip fidelity*: rejected — adds a dependency
  the project doesn't currently carry, and we're emitting frontmatter from
  scratch (skeleton) rather than round-tripping user YAML.
- *Hand-written string templating*: rejected — brittle against quoting
  edge cases (strings containing colons, quotes, unicode).

## 5. Atomic file write

**Decision**: Use the `tempfile.NamedTemporaryFile` + `Path.replace()`
pattern in a new helper `write_text_atomic(path, content)` inside
`src/doit_cli/utils/atomic_write.py`. Migration callers use this helper.

**Rationale**:

- Spec SC-007 requires that a malformed-YAML error leaves the file on
  disk byte-identical. The simplest way to guarantee this is to never
  write partial content — write to a sibling temp file in the same
  directory (so rename is atomic on POSIX and Windows), then
  `Path.replace()` to the final path only on success.
- No shared atomic helper exists today (explored). Introducing one now
  is low-risk and reusable by future migration code.

**Alternatives considered**:

- *`Path.write_text()` directly (current project default)*: rejected for
  this feature — a crash or exception mid-write would leave the
  constitution truncated. Acceptable for ephemeral files, not for user
  memory.
- *Write in-place with a `.bak` fallback*: rejected — still leaves a
  window of partial state; renames are simpler.

## 6. Skill enrichment workflow placement

**Decision**: Extend
`src/doit_cli/templates/skills/doit.constitution/SKILL.md` with a new
**Step 2b** between existing Step 1 (Load Constitution Template) and
Step 2 (Determine update scope). Step 2b:

1. Reads existing `.doit/memory/constitution.md`.
2. Parses frontmatter via `doit verify-memory . --json`.
3. If any required field value exactly matches a placeholder token from
   the registry, enter **enrichment mode**:
   - Read the body and available project context (repo dir, tech-stack,
     roadmap from `doit context show`).
   - For each placeholder, derive a concrete value or leave it as
     placeholder with a flagged note.
   - Use the atomic-write helper (exposed via `doit` as a new subcommand
     if needed, or direct file write from the skill — see §7) to
     rewrite the frontmatter block without touching the body.
4. If no placeholders detected, skip enrichment and fall through to the
   normal Step 2 update flow.

**Rationale**:

- The existing skill already reads the constitution and drafts content;
  adding enrichment as a pre-step avoids disrupting the main flow.
- The skill can detect placeholders itself by reading the file — no new
  CLI API surface is strictly required on the CLI side.
- Enrichment-only edits (no body rewrite) fit the byte-for-byte
  preservation requirement (FR-013).

**Alternatives considered**:

- *Build a separate `/doit.enrichit` skill*: rejected — duplicates
  context loading and confuses the user about which skill does what.
- *Make `doit update` call an LLM*: rejected per spec — the CLI must
  not depend on an external LLM API.

## 7. Skill ↔ CLI interface for frontmatter rewrites

**Decision**: No new CLI API surface. The `/doit.constitution` skill
writes `.doit/memory/constitution.md` directly using its existing file
write primitives, followed by a `doit verify-memory .` sanity check. The
body-preservation guarantee is a skill authoring rule, not a CLI API
contract.

**Rationale**:

- Keeps the CLI surface minimal and aligned with "additive, non-breaking"
  principle.
- The skill already writes `.doit/memory/constitution.md` today; we're
  narrowing the operation to "frontmatter only" via skill instruction,
  not adding a new code path.

**Alternatives considered**:

- *New `doit memory patch-frontmatter` CLI subcommand*: rejected as
  premature — the skill is the only consumer, and exposing a public CLI
  for a single internal flow creates maintenance burden.

## 8. Integration-test fixture strategy

**Decision**: Model tests on
`tests/integration/test_memory_command.py` — use
`tempfile.TemporaryDirectory()` to build a `.doit/memory/` fixture,
then invoke via `typer.testing.CliRunner`. Add two new fixtures:

1. `constitution_legacy.md` — no frontmatter, ~30 lines of body.
2. `constitution_partial.md` — frontmatter with only `id` and `name`;
   other required fields missing.

Integration tests live at
`tests/integration/test_constitution_frontmatter_migration.py`.
Contract tests live at
`tests/contract/test_constitution_frontmatter_contract.py`.

**Rationale**:

- Matches existing project style — one representative was reviewed and
  confirmed the pattern.
- Contract test covers the placeholder-token registry (fixed surface);
  integration test covers the end-to-end CLI invocation.

**Alternatives considered**:

- *Snapshot-style golden files*: rejected — brittle on line endings and
  dates; byte-identical body comparisons are better expressed as hash
  assertions.

---

## Summary of decisions

| # | Decision | Primary impact |
|:--|:---------|:---------------|
| 1 | Migration hook inside `run_init()` after memory copy | One entry point for migration |
| 2 | Exact-token `[PROJECT_*]` placeholders, one per required field | Shared convention with existing body validator |
| 3 | Warning severity for placeholder detection | Migrated file passes verify-memory |
| 4 | PyYAML `safe_dump` with ordered keys | No new dependency |
| 5 | Atomic write via `tempfile` + `Path.replace()` | No partial-write corruption |
| 6 | Skill gets a Step 2b enrichment branch | AI populates real values |
| 7 | No new CLI API; skill writes file directly | Minimal public surface |
| 8 | Tests modeled on `test_memory_command.py` | Consistent with existing style |

All `NEEDS CLARIFICATION` markers: **zero**. Spec is complete and ready for
Phase 1.
