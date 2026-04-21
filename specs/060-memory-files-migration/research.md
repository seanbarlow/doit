# Research: Memory Files Migration (roadmap.md, tech-stack.md)

**Feature**: `060-memory-files-migration`
**Date**: 2026-04-21
**Status**: Complete — no open `NEEDS CLARIFICATION` markers in spec.md

This Phase 0 document captures the technical decisions that drive Phase 1
artifacts. The feature inherits most of its primitives from spec
[059](../059-constitution-frontmatter-migration/plan.md) — atomic write,
placeholder-WARNING severity, CLI-first design. The decisions below cover
only the delta.

## 1. Migrator boundary

**Decision**: Introduce **two** dedicated migrators —
`RoadmapMigrator` and `TechStackMigrator` — sharing a tiny internal
helper for "insert an H2/H3 section if missing." Both live at
`src/doit_cli/services/` alongside the existing
`constitution_migrator.py`.

**Rationale**:

- Each file has a different required-section set; parameterising a
  single generic migrator by a schema tuple would obscure the
  per-file logic (default stub content, ordering, edge cases).
- Two small modules (~150 lines each) read more easily than one
  300-line generic one.
- The shared helper stays private (`_insert_section_if_missing`) —
  promoted to a public utility only if a third migrator lands.

**Alternatives considered**:

- *Single `MemoryFileMigrator` with strategy objects*: rejected — the
  strategy objects ended up being the migrator, plus glue.
- *Extend `ConstitutionMigrator` with a `MigrationTarget` enum*:
  rejected — conflates YAML-frontmatter and markdown-section
  concerns; noise in the main constitution flow.

## 2. Init hook orchestration

**Decision**: Run all three migrators sequentially inside
`run_init()` — constitution (already wired per spec 059), then
roadmap, then tech-stack — immediately after
`copy_memory_templates()`. If any returns `ERROR`, surface the first
error and stop (short-circuit).

**Rationale**:

- Constitution ordering first preserves spec 059's existing contract.
- Roadmap and tech-stack are independent of each other; ordering
  between them is arbitrary — roadmap first is alphabetical.
- Short-circuit keeps error semantics simple: users see one root
  cause, not three chained errors.
- Consolidating into one hook block keeps the init surface contained.

**Alternatives considered**:

- *Run all three in parallel via `ThreadPoolExecutor`*: rejected —
  the work is I/O on tiny files; parallelism adds complexity without
  measurable speedup.
- *Continue on error, aggregate results*: rejected — hides the
  original failure; users prefer "fix one thing at a time."

## 3. Required-section schema

**Decision**: Declare the required-section contracts as module-level
constants mirroring the `REQUIRED_FRONTMATTER_FIELDS` pattern from
spec 059:

```python
# roadmap_migrator.py
REQUIRED_ROADMAP_H2: Final = ("Active Requirements",)
REQUIRED_ROADMAP_H3_UNDER_ACTIVE: Final = ("P1", "P2", "P3", "P4")

# tech_stack_migrator.py
REQUIRED_TECHSTACK_H2: Final = ("Tech Stack",)
REQUIRED_TECHSTACK_H3_UNDER_TECHSTACK: Final = (
    "Languages", "Frameworks", "Libraries",
)
```

A contract test asserts these match the `_validate_roadmap` and
`_validate_tech_stack` rules in `memory_validator.py` (same bijection
pattern spec 059 used for the frontmatter registry).

**Rationale**:

- Single source of truth; the validator's required-section rules
  stay authoritative.
- Contract tests catch drift at CI time.

**Alternatives considered**:

- *Parse `memory_validator.py` at runtime to derive the list*:
  rejected — fragile. Explicit constants + a contract test is the
  better discipline.

## 4. Placeholder stub content

**Decision**: Stubs use the existing `PLACEHOLDER_TOKENS` from
`memory_validator.py` (the body-level registry, not spec 059's
frontmatter registry). Concretely:

- **Roadmap** `## Active Requirements` stub inserts
  ```
  ### P1 - Critical

  <!-- Add [PROJECT_NAME]'s P1 items here -->

  ### P2 - High Priority

  <!-- Add [PROJECT_NAME]'s P2 items here -->

  ### P3 - Medium Priority

  <!-- Add [PROJECT_NAME]'s P3 items here -->

  ### P4 - Low Priority (Nice to Have)

  <!-- Add [PROJECT_NAME]'s P4 items here -->
  ```
  Each HTML comment contains `[PROJECT_NAME]` — already in
  `PLACEHOLDER_TOKENS`. The existing `_is_placeholder` threshold of 3
  distinct tokens still triggers: four `[PROJECT_NAME]` instances
  count as one *distinct* token, so we also scatter `[PROJECT_PURPOSE]`
  and `[SUCCESS_CRITERIA]` in the comment text to cross the threshold.

- **Tech-stack** `## Tech Stack` stub inserts three subsections each
  with `<!-- Add [PROJECT_NAME]'s <Group> here -->`. Same pattern.

**Rationale**:

- Reuses existing placeholder machinery — no new tokens to register.
- HTML comments keep stubs invisible in rendered markdown but
  detectable by the validator.
- The enrichers replace the comments entirely (no partial-rewrite
  concerns with comment fragments).

**Alternatives considered**:

- *Inventing `[ROADMAP_P1_ITEMS]` / `[TECHSTACK_LANGUAGES]` tokens*:
  rejected — expands the placeholder registry for marginal benefit.
  The existing `[PROJECT_*]` tokens are sufficient.
- *Empty subsections*: rejected — the validator's
  `_subheadings_under` check would pass, but users would see silent
  empty sections without a hint that enrichment is available.

## 5. Idempotency detection

**Decision**: "Already migrated" is defined by two checks, in order:

1. The H2 section exists (`_has_heading(source, 2, title)`).
2. Every required H3 subsection exists under the H2 (via
   `_subheadings_under`).

If both pass, the migrator returns `MigrationAction.NO_OP` and writes
nothing. If only some H3s exist, `PATCHED` (inserts only the missing
ones). If the H2 is missing, `PREPENDED` (inserts the full block at
the end of the file, or immediately after the `# Title` line when
the file contains only a title).

**Rationale**:

- Same state model as spec 059: `NO_OP / PREPENDED / PATCHED / ERROR`.
- Insertion location matters less than the insertion happening —
  users reorder sections themselves during normal editing.

**Alternatives considered**:

- *Insert at the top of file*: rejected — breaks the reading flow of
  user-authored content.
- *Insert at a marker comment*: rejected — too clever; users don't
  know to add markers, and adding one silently is a surprise.

## 6. Tech-stack enrichment source parsing

**Decision**: The `TechStackEnricher` reads `.doit/memory/constitution.md`
and extracts bullet items from three known headings:

- `## Tech Stack` → any `### Languages`, `### Frameworks`,
  `### Libraries` subsections → copied verbatim to the matching
  subsections in `tech-stack.md`.
- `## Infrastructure` → bullet items → appended under an auto-inserted
  `### Infrastructure` subsection in `tech-stack.md` (creates the
  subsection if missing — the tech-stack contract allows extra
  subsections beyond Languages/Frameworks/Libraries).
- `## Deployment` → bullet items → appended under `### Deployment`
  subsection, same logic.

A small regex-based markdown parser extracts `### <Title>\n\n- item\n- item\n\n`
blocks. No external markdown library needed.

**Rationale**:

- Constitution-based tech stack content is the single biggest deterministic
  source. Pre-0.3.0 project templates put tech stack inside the
  constitution; users have non-trivial content there even after
  `/doit.constitution cleanup`.
- "Verbatim" means no smartening — preserves formatting exactly so
  users see their own words.

**Alternatives considered**:

- *Parse `pyproject.toml` / `package.json` to derive tech stack*:
  rejected — out of scope and leaks "language file parsing" into
  memory migration. Separate feature.
- *LLM-driven extraction*: rejected by spec constraint (no LLM calls
  from the CLI).

## 7. Roadmap enrichment narrowness

**Decision**: `RoadmapEnricher` does exactly two things:

1. Replace a placeholder Vision paragraph with the first sentence of
   the constitution's `### Project Purpose` (same helper used by
   `ConstitutionEnricher._infer_tagline`).
2. Insert an HTML-comment block near the top of `## Active Requirements`
   listing every item from `.doit/memory/completed_roadmap.md` (if
   present), so users don't accidentally re-add shipped work.

It does **not** populate P1/P2/P3/P4 item lists. Priority-ranking is
product judgment — delegated to the `/doit.roadmapit` skill.

**Rationale**:

- Spec's `Out of Scope` section is explicit about this.
- Narrow scope keeps the automated tests deterministic.
- Leaves the `/doit.roadmapit` skill a clear remaining responsibility.

**Alternatives considered**:

- *Extract open P1/P2 candidates from in-progress spec files*:
  considered but rejected — would need spec-status parsing,
  dependency-graph reasoning, and still produce low-quality
  suggestions.

## 8. CLI command placement

**Decision**: Add enrich commands under the existing `memory_app`
group:

- `doit memory enrich roadmap [PATH] [--json]`
- `doit memory enrich tech-stack [PATH] [--json]`

Rather than separate `doit roadmap enrich` and `doit tech-stack enrich`
top-level groups. Also add an umbrella:

- `doit memory migrate [PATH]` — runs all three migrators
  (constitution, roadmap, tech-stack) in sequence. Equivalent to the
  block that `doit update` calls internally; exposed for diagnostic
  use.

For `spec 059`'s existing `doit constitution enrich`: leave it where
it is for back-compat. Document that `doit memory enrich constitution`
is a future alias.

**Rationale**:

- Grouping under `memory` keeps the mental model tight — these
  commands all operate on `.doit/memory/*.md`.
- A shared `doit memory migrate` is useful outside of `doit init/update`
  (e.g. CI dry-run to check if memory is up-to-shape without touching
  anything else).

**Alternatives considered**:

- *Keep commands top-level (`doit roadmap enrich`, `doit tech-stack
  enrich`)*: rejected — pollutes top-level surface with feature-specific
  verbs.

## Summary of decisions

| # | Decision | Primary impact |
|:--|:---------|:---------------|
| 1 | Two dedicated migrators; tiny shared helper | Clear per-file logic |
| 2 | Sequential init hook, short-circuit on error | Simple error semantics |
| 3 | Explicit required-section constants + contract test | No drift with validator |
| 4 | Reuse existing `PLACEHOLDER_TOKENS`; HTML-comment stubs | No new token registry |
| 5 | State model: NO_OP / PREPENDED / PATCHED / ERROR | Consistent with spec 059 |
| 6 | Constitution-based deterministic tech-stack extraction | Highest-yield inference |
| 7 | Narrow roadmap enrichment (Vision + completed-hint only) | Defends against inference-quality trap |
| 8 | CLIs live under `doit memory` subgroup | Tidy namespace |

All `NEEDS CLARIFICATION` markers: **zero**. Spec is complete and ready for
Phase 1.
