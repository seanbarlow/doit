# Contract: Personas Migrator, Enricher, and Validator

**Feature**: 062-personas-migration
**Date**: 2026-04-21
**Scope**: Internal Python API + one new CLI subcommand. No file-format changes; no changes to existing migrators.

---

## 1. `personas_migrator.migrate_personas`

### Signature

```python
from pathlib import Path
from typing import Final

from .constitution_migrator import MigrationAction, MigrationResult

REQUIRED_PERSONAS_H2: Final[tuple[str, ...]] = (
    "Persona Summary",
    "Detailed Profiles",
)

def migrate_personas(path: Path) -> MigrationResult:
    ...
```

### Behaviour matrix

| Input state | Action | `added_fields` | `preserved_body_hash` | Disk side effect |
| ----------- | ------ | -------------- | --------------------- | ---------------- |
| File does not exist (opt-in) | `NO_OP` | `()` | `None` | None |
| File exists, both required H2s present | `NO_OP` | `()` | SHA-256 of bytes | None (byte-identical) |
| File exists, `## Persona Summary` missing | `PATCHED` | `("Persona Summary",)` | SHA-256 of pre-edit bytes | Atomic write |
| File exists, `## Detailed Profiles` missing | `PATCHED` | `("Detailed Profiles",)` | SHA-256 of pre-edit bytes | Atomic write |
| File exists, both required H2s missing | `PATCHED` | `("Persona Summary", "Detailed Profiles")` | SHA-256 of pre-edit bytes | Atomic write |
| I/O error on read or write | `ERROR` | `()` | `None` | None (atomic write failed fast) |
| UTF-8 decode error | `ERROR` | `()` | `None` | None |

**Invariants**:

- Never raises; always returns a `MigrationResult`.
- Never returns `PREPENDED` — see spec `data-model.md` for rationale (opt-in semantic precludes "file exists but entirely empty shape").
- Stub body for each inserted H2 carries ≥ 3 distinct `[TOKEN]` placeholders so the validator's `_is_placeholder` threshold classifies the file as needing enrichment.
- CRLF line endings preserved byte-for-byte via `_memory_shape._detect_newline`.
- Atomic-write via `doit_cli.utils.atomic_write.write_text_atomic`.

### Implementation contract

- MUST call `_memory_shape.insert_section_if_missing` exactly twice (once per required H2), in the canonical order, each with `h3_titles=()`. Intermediate source state (after the first call) is passed to the second.
- MUST pass `matchers=None` (or omit the argument) — exact-match is correct for personas.
- MUST NOT create the file when it does not exist.
- MUST NOT modify existing prose outside the inserted H2 stubs.

### Stub bodies

Both H2 stubs use a shared body generator returning a multi-line comment with placeholders. Example (Persona Summary):

```markdown
## Persona Summary

<!-- Add [PROJECT_NAME]'s personas table here.
     Each row references a persona defined under ## Detailed Profiles.
     Run /doit.roadmapit or /doit.researchit to populate interactively.
     See [PERSONA_EXAMPLE] and [SEE_ROADMAPIT] for guidance. -->

| ID | Name | Role | Archetype | Primary Goal |
|----|------|------|-----------|--------------|
```

The Detailed Profiles stub mirrors the pattern:

```markdown
## Detailed Profiles

<!-- Add [PROJECT_NAME]'s persona detail blocks here.
     Each block MUST use the heading `### Persona: P-NNN` where NNN is a
     three-digit zero-padded ID matching a row in ## Persona Summary.
     See [PERSONA_EXAMPLE] and [SEE_ROADMAPIT] for guidance. -->
```

---

## 2. `personas_enricher.enrich_personas`

### Signature

```python
from pathlib import Path

from .constitution_enricher import EnrichmentAction, EnrichmentResult

def enrich_personas(path: Path) -> EnrichmentResult:
    ...
```

### Behaviour matrix

| Input state | Action | `enriched_fields` | `unresolved_fields` | Disk side effect |
| ----------- | ------ | ----------------- | ------------------- | ---------------- |
| File does not exist | `NO_OP` | `()` | `()` | None |
| File exists, zero `{placeholder}` tokens detected | `NO_OP` | `()` | `()` | None |
| File exists, ≥ 1 `{placeholder}` tokens detected | `PARTIAL` | `()` | tuple of distinct placeholder names (deduplicated, sorted) | None |
| I/O error | `ERROR` | `()` | `()` | None |
| UTF-8 decode error | `ERROR` | `()` | `()` | None |

**Invariants**:

- Never returns `ENRICHED`. The enricher is linter-only; it never modifies the file.
- `unresolved_fields` contains bare placeholder names without surrounding braces (e.g. `"Persona Name"`, `"FEATURE_NAME"`), sorted alphabetically for deterministic output.
- The placeholder regex is `\{([A-Za-z_][A-Za-z0-9_ .-]*)\}` — matches template-style tokens without swallowing JSON or shell-variable syntax.

### CLI contract — `doit memory enrich personas`

| Scenario | Exit code | `--json` output |
| -------- | --------- | --------------- |
| File absent | `0` | `{"path": "...", "action": "no_op", "enriched_fields": [], "unresolved_fields": [], "error": null}` |
| NO_OP (no placeholders) | `0` | Same shape; `action: no_op` |
| PARTIAL | `1` | Same shape; `action: partial`; `unresolved_fields: ["Persona Name", "Role", ...]` |
| ERROR | `2` | Same shape; `action: error`; `error: "<message>"` |

Exit codes match `doit memory enrich roadmap` and `doit memory enrich tech-stack` conventions.

Human-readable CLI output (non-JSON) for PARTIAL includes a hint:

```
[yellow]Partial enrichment[/yellow] — 3 placeholder(s) remain:
  - {Persona Name}
  - {Role}
  - {FEATURE_NAME}

Run /doit.roadmapit to populate personas interactively.
```

---

## 3. `memory_command.memory_migrate_cmd` — umbrella extension

### Behaviour change

The existing `doit memory migrate` JSON output grows from 3 rows to 4 rows. Row order is deterministic:

1. `constitution.md`
2. `roadmap.md`
3. `tech-stack.md`
4. **`personas.md`** ← new

### Output contract (JSON)

```json
[
  {"path": "...", "file": "constitution.md", "action": "...", "added_fields": [...], "error": null},
  {"path": "...", "file": "roadmap.md",     "action": "...", "added_fields": [...], "error": null},
  {"path": "...", "file": "tech-stack.md",  "action": "...", "added_fields": [...], "error": null},
  {"path": "...", "file": "personas.md",    "action": "...", "added_fields": [...], "error": null}
]
```

**Invariants**:

- The `personas.md` row is ALWAYS emitted, even when the file doesn't exist (action=`no_op`). This matches the spec's opt-in contract: "absence is a valid state worth reporting".
- No new command-line flags added. No `--no-personas` / `--include-personas` opt-out.
- The Rich (non-JSON) table grows by one row too; same column layout.

---

## 4. `memory_validator._validate_personas` — new rule

### Signature

```python
def _validate_personas(
    memory_dir: Path, placeholder_files: list[str]
) -> list[MemoryContractIssue]:
    """Validate .doit/memory/personas.md when present."""
```

Same signature as the other `_validate_*` helpers. Called from `verify_memory_contract` immediately after `_validate_roadmap`.

### Rules (evaluated in order)

1. File does not exist → return `[]` (no issues, not even a warning).
2. File is placeholder-heavy (≥ `PLACEHOLDER_THRESHOLD` distinct `[TOKEN]` names) → WARNING and early return; structural checks are noise at this point.
3. `## Persona Summary` H2 missing → ERROR.
4. `## Detailed Profiles` H2 missing → ERROR.
5. For each `### Persona: <text>` heading under `## Detailed Profiles`:
   - If `text` does not match `P-\d{3}` → ERROR per heading: "malformed persona ID `<text>` — expected `P-NNN` (three-digit zero-padded)".
6. After counting valid `### Persona: P-NNN` entries: if zero → WARNING "`## Detailed Profiles` has no persona entries — nothing for the docs generator to pick up".

### Non-rules (explicit out-of-scope)

- Does NOT validate `## Relationship Map`, `## Conflicts & Tensions Summary`, `## Traceability`, or `## Next Steps`. Their presence/absence is neutral.
- Does NOT validate content within persona blocks (Primary Goal, Pain Points, etc. are free-form).
- Does NOT cross-reference `## Persona Summary` table rows against `## Detailed Profiles` headings. Mismatches (e.g. P-001 in summary but not in details) are user-authoring concerns, not shape violations.
- Does NOT validate persona ID uniqueness (duplicate IDs get a WARNING per the edge-case list in the spec, but this is deferred to a future spec if implemented at all).

---

## 5. Contract tests (new)

### Location

`tests/contract/test_memory_files_migration_contract.py` — extend the existing file from spec 060 with two new test functions. No new test file.

### Test 1: `test_personas_required_h2_matches_validator`

Assert `REQUIRED_PERSONAS_H2` tuple contains exactly the H2 titles that `_validate_personas` checks for. Prevents drift between the migrator's inserted stubs and the validator's requirements.

### Test 2: `test_personas_migrator_reuses_constitution_migration_types`

Assert `personas_migrator.migrate_personas` returns a `MigrationResult` whose `action` is a `MigrationAction` instance. Mirrors the constitution/roadmap/tech-stack migrator type-reuse tests.

### Location (ID bijection)

`tests/contract/test_personas_validator_migrator_alignment.py` — NEW file, mirrors spec 061's `test_roadmap_validator_migrator_alignment.py`.

### Test 3: `test_validator_accepted_ids_round_trip`

Parameterised over a valid-ID corpus (`["P-001", "P-042", "P-099", "P-100", "P-500", "P-999"]`). For each ID:

- Build a minimal personas.md with `## Persona Summary`, `## Detailed Profiles`, and one `### Persona: <id>` entry.
- Assert `validate_project` emits zero ERRORs for personas.md.
- Assert `migrate_personas` returns `NO_OP` with `added_fields == ()`.

### Test 4: `test_validator_rejected_ids_error`

Parameterised over a malformed-ID corpus (`["P-1", "P-01", "P-1000", "p-001", "Persona-001", "X-001", "P001", "P 001"]`). For each heading:

- Build a minimal personas.md with the rejected heading under `## Detailed Profiles`.
- Assert `validate_project` emits exactly one ERROR for personas.md citing the malformed ID in the message.

### Test 5: `test_personas_absent_emits_no_issues`

Build a project with constitution.md + roadmap.md + tech-stack.md but NO personas.md. Assert `validate_project` emits zero issues mentioning personas.md.

### Test 6: `test_umbrella_migrator_output_order`

Run `doit memory migrate` on a project with all four memory files. Assert the JSON output has exactly four rows in the canonical order: constitution → roadmap → tech-stack → personas.

---

## 6. Out-of-scope (for explicitness)

- No changes to `MigrationResult`, `MigrationAction`, `EnrichmentResult`, `EnrichmentAction` dataclasses.
- No changes to `_memory_shape.insert_section_if_missing` signature or behaviour.
- No changes to `constitution_migrator`, `constitution_enricher`, `roadmap_migrator`, `roadmap_enricher`, `tech_stack_migrator`, `tech_stack_enricher`.
- No changes to the `PLACEHOLDER_TOKENS` / `PLACEHOLDER_REGISTRY` primitives.
- No new `doit init` / `doit update` / `doit verify-memory` CLI surface (new validator rule is internal plumbing).
- Feature-level `specs/{feature}/personas.md` is untouched by all new services.
- No changes to the `context_loader.load_personas` function — it continues to load whatever shape it finds and the validator is the one enforcing the shape.
