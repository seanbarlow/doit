# Research: Personas.md Migration

**Feature**: 062-personas-migration
**Date**: 2026-04-21
**Spec**: [spec.md](spec.md)

---

## Context

This spec extends the migrator + enricher + validator pattern from specs 059 (constitution frontmatter) and 060 (roadmap + tech-stack shape) to the fourth and final `.doit/memory/*.md` file: `personas.md`. Spec 061's `matchers` helper extension is already available but not needed here (persona H2 titles are not decoration-prone). This research resolves the design questions specific to personas.md — principally: what to require, how to handle the opt-in semantic, and what the enricher can reasonably do.

---

## Decision 1: Required shape — minimum enforced by validator & migrator

**Decision**: The canonical personas.md shape requires exactly two H2 sections in this order:

```
## Persona Summary           (table of personas keyed by P-NNN ID)
## Detailed Profiles         (### Persona: P-NNN blocks)
```

No H3 subsections under either H2 are required by shape (persona entries are project-specific content, not structural scaffolding).

**Rationale**:

- These two sections are the minimum the downstream consumers need:
  - `context_loader.load_personas` (spec 056) parses persona summary rows + profile bodies into its context payload.
  - `/doit.specit` persona-matching (spec 057) looks up each persona's goals and pain points under `## Detailed Profiles`.
- Other sections in `personas-output-template.md` (`## Relationship Map`, `## Conflicts & Tensions Summary`, `## Traceability`, `## Next Steps`) are useful editorial scaffolding but not required by any downstream consumer. Enforcing them would force every project to maintain Mermaid diagrams and traceability tables even when unused.
- Matches the spec 060 pattern: enforce the minimum the code actually depends on, leave everything else optional.

**Alternatives considered**:

- *Require `## Relationship Map` too*: rejected — the context loader never reads it, and projects without persona relationships would always get validator warnings.
- *Require `## Traceability`*: rejected — that table is auto-managed by `/doit.specit` (spec 057) and its presence indicates mature persona use, not a shape requirement.
- *No H2 requirements, only ID-format enforcement*: rejected — the context loader uses `## Persona Summary` and `## Detailed Profiles` as navigation anchors. Losing them silently breaks persona loading.

---

## Decision 2: Opt-in semantic — absence of personas.md is valid

**Decision**: When `.doit/memory/personas.md` does not exist, the migrator returns `NO_OP` without creating the file; the enricher returns `NO_OP` with exit 0; the validator emits zero issues. `personas.md` is NOT auto-created by `doit init` or `doit update`.

**Rationale**:

- `/doit.roadmapit` (spec 056) generates project-level personas.md interactively; not every project uses personas. The context loader treats personas.md as optional context (priority 3, absent → skip).
- Auto-creating the file would force every project into a persona-required mental model, which is false.
- Constitution is a hard requirement (every project has purpose/goals); personas are a methodology choice.
- Aligns with the `spec.md` US2 "opt-in" framing, which is the user-visible contract.

**Alternatives considered**:

- *Auto-create a placeholder personas.md on `doit init`*: rejected — pollutes projects that don't use personas; users would have to delete or ignore it.
- *Emit a WARNING when absent*: rejected — warnings should signal remediable issues, and "this project doesn't use personas" is not an issue.
- *Create only when explicitly asked (e.g. `doit memory migrate --include-personas`)*: considered, but adds CLI surface for a use case already covered by `/doit.roadmapit`. The skill is the proper bootstrap path.

---

## Decision 3: Migrator structure — two H2 sections, zero required H3s

**Decision**: The personas migrator calls `_memory_shape.insert_section_if_missing` **twice** — once per required H2 — passing `h3_titles=()` (empty tuple) in each call. Each call is independent; the second call sees the updated source from the first.

**Rationale**:

- The shared helper's contract is designed around "one H2 + N required H3s". Personas has "two H2s + zero H3s" — the inverse shape.
- Iterating through two independent `insert_section_if_missing` calls correctly reuses the helper without extending it. Each call either finds the H2 (NO_OP for that H2) or appends a stub at EOF (PREPENDED-style for that H2).
- Adding multi-H2 support to the helper would be a spec-061-sized change with benefits only this spec needs. Keep the helper stable.
- The helper with `h3_titles=()` degenerates to "check H2 existence; if absent, insert empty H2 stub" — which is exactly what we want.

**Alternatives considered**:

- *Extend `_memory_shape.insert_section_if_missing` to accept multiple H2s*: rejected — out-of-scope helper churn; two sequential calls are clean and readable.
- *Inline the H2 logic in personas_migrator without calling the helper*: rejected — duplicates the `_find_h2_span` / `_detect_newline` logic and re-introduces the drift risk that specs 059/060 deliberately eliminated by sharing the helper.
- *Model personas.md as one H2 ("Personas") with two required H3s ("Summary", "Detailed Profiles")*: rejected — doesn't match the template or the downstream consumers' heading expectations (both are H2s in the template and the context loader).

---

## Decision 4: Enricher scope — linter mode only (no content generation)

**Decision**: `enrich_personas` detects remaining `{...}` curly-brace template placeholders and reports them in `unresolved_fields`. It does NOT attempt to fill persona names, roles, goals, or pain points. `PARTIAL` when placeholders remain; `NO_OP` when zero placeholders; exit 1 for PARTIAL, exit 0 for NO_OP (matches spec 059/060 CLI convention).

**Rationale**:

- Persona content is intrinsically project-specific and comes from interactive elicitation (`/doit.roadmapit`, `/doit.researchit` Q&A). An enricher has no signal to pick between "Developer Dana", "PM Pat", or "Sales Sarah" — guessing would produce worse-than-useless output.
- The constitution enricher fills 8 structured frontmatter fields inferable from the body prose (id, name, kind, phase, icon, tagline, dependencies, …). The tech-stack enricher fills Languages/Frameworks/Libraries by parsing the constitution's Tech Stack H2. Personas has no analogous "upstream source" of project-specific content.
- Linter-mode is still useful: CI pipelines and `doit update` can surface incomplete personas.md files without requiring a human to manually re-read the whole file.
- User's remediation path is clear: `/doit.roadmapit` to populate (interactive Q&A).

**Alternatives considered**:

- *Enricher fills `{PROJECT_NAME}` or `{DATE}`*: rejected — those tokens are typically replaced by the template copy step, not expected to persist in a user-edited personas.md. If they do persist, it's a sign the file came straight from the template with no human editing.
- *Enricher calls `/doit.roadmapit` under the hood*: rejected — the enricher is a deterministic, non-interactive CLI. Calling an interactive skill from it breaks that contract.
- *No enricher at all — just the migrator*: considered, but spec 060 set the expectation that every memory file gets both a migrator and an enricher CLI for symmetry. A linter-mode enricher preserves the pattern without pretending to generate content.

---

## Decision 5: Persona ID validator regex and placement

**Decision**: Validator enforces the ID regex `^Persona: P-\d{3}$` (case-sensitive "Persona:"; three-digit zero-padded after `P-`) for every `### Persona: …` heading under `## Detailed Profiles`. Headings outside that H2 section are not scanned (e.g. a `### Persona: example` in a `## Glossary` section doesn't trigger).

**Rationale**:

- Three-digit zero-padded is the established convention in `personas-output-template.md` (lines show `P-001`, `P-002`) and the `/doit.specit` spec-template.md references (`Persona: P-NNN`).
- Case sensitivity on "Persona:" avoids accidental false positives on unrelated `### persona` headings elsewhere.
- Scoping to `## Detailed Profiles` avoids validation noise from glossary/example usages (users sometimes paste persona examples into a Glossary section for reference).
- Strict regex is easy to document and easy to test bijectively (spec 061's pattern).

**Alternatives considered**:

- *Accept `P-N` / `P-NN` / `P-NNN` (any digit count)*: rejected — the downstream consumers (`/doit.specit` persona matcher) parse using the three-digit assumption; widening here creates drift between validator and consumers.
- *Case-insensitive "persona:"*: rejected — `### persona: p-001` is likely user error; flag it as an ERROR so the user fixes the typo.
- *Allow arbitrary IDs (like `P-DEV`, `ADMIN-01`)*: rejected — the numeric convention is load-bearing for sort order and auto-generation in templates.

---

## Decision 6: CLI surface extensions

**Decision**: Add exactly one new subcommand: `doit memory enrich personas`. The `doit memory migrate` umbrella gains a fourth output row but no new flag. No changes to `doit init`, `doit update`, or `doit verify-memory`'s surface — the new validator rule is wired internally into `verify_memory_contract`.

**Rationale**:

- `doit memory enrich personas` mirrors the existing `doit memory enrich roadmap` and `doit memory enrich tech-stack` subcommands — users expect the parity.
- Keeping umbrella migrator at one-flag-free call preserves idempotence: rerunning `doit memory migrate` always reports state, never adds surface.
- `doit verify-memory` is implemented as a single entry point; the new validator rule is internal plumbing.

**Alternatives considered**:

- *Add `doit memory migrate --no-personas`*: rejected — users never want to skip a memory file check. The umbrella being exhaustive is the feature.
- *Separate `doit personas` command*: rejected — violates the `doit memory ...` namespace convention established in spec 060.

---

## Decision 7: Contract tests — ID bijection

**Decision**: New contract test `test_personas_validator_migrator_alignment.py` with two parametrized test functions:

1. **Positive corpus**: for each ID in a representative set (`P-001`, `P-042`, `P-099`, `P-100`, `P-500`, `P-999`), build a minimal valid personas.md and assert the validator accepts it AND the migrator returns NO_OP.
2. **Negative corpus**: for each malformed ID (`P-1`, `P-01`, `P-1000`, `p-001`, `Persona-001`, `X-001`), assert the validator emits an ERROR for the malformed heading.

Plus a header-alignment contract test mirroring spec 060's `test_roadmap_required_h2_matches_validator`: `REQUIRED_PERSONAS_H2` must exactly match the H2 titles `_validate_personas` checks for.

**Rationale**:

- Spec 061's validator↔migrator bijection test pattern proved its worth — it catches drift that pure unit tests miss.
- The ID regex is the one novel concept in this spec (constitution/roadmap had structural checks only); bijective testing over a representative corpus is appropriate.

**Alternatives considered**: none — the pattern is established.

---

## Decision 8: No changes to `_memory_shape.insert_section_if_missing`

**Decision**: This spec does NOT modify the shared helper. Spec 061's `matchers` parameter is not used (exact-match is correct for persona H2 titles). The helper's existing `h3_titles=()` degenerate case is already functional.

**Rationale**:

- Preserves spec 061's byte-for-byte compatibility for all prior callers (roadmap, tech-stack).
- Personas H2 titles (`Persona Summary`, `Detailed Profiles`) are unlikely to be decorated — the decoration problem was specific to priority headings that users commonly embellish with categories. Plain H2s are stable.

**Alternatives considered**: none — the helper is not the right place to change for this spec.

---

## Summary table

| Decision | Choice | Key rationale |
|----------|--------|---------------|
| 1. Required shape | Two H2s (`Persona Summary`, `Detailed Profiles`); no required H3s | Minimum downstream consumers need; other template sections stay optional |
| 2. Opt-in semantic | Absence = NO_OP + zero issues; no auto-create | Personas are a methodology, not a requirement |
| 3. Migrator structure | Two sequential `insert_section_if_missing` calls with `h3_titles=()` | Reuses shared helper without extending it |
| 4. Enricher scope | Linter-only — detect placeholders, report PARTIAL/NO_OP, never fill | No project-specific content can be inferred |
| 5. Persona ID regex | `^Persona: P-\d{3}$`, scoped to `## Detailed Profiles` | Matches established convention + downstream consumers |
| 6. CLI surface | +1 subcommand (`doit memory enrich personas`); umbrella +1 row | Matches spec 060 pattern exactly |
| 7. Contract tests | Bijective ID corpus + H2 header alignment | Pattern established by specs 060 + 061 |
| 8. Helper changes | None | Exact-match is correct; spec 061's matchers not needed |

All NEEDS CLARIFICATION items resolved. Ready for Phase 1.
