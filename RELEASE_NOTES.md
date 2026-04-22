# Release Notes - v0.3.0

**Release Date**: 2026-04-21

## Highlights

This release **closes the memory-file migration pattern across all four
`.doit/memory/*.md` files**. Constitution (#059), roadmap + tech-stack
(#060), the roadmap H3 prefix-match regression fix (#061), and personas
(#062) all now share the same migrator + enricher + validator + umbrella
plumbing. `doit update` and `doit memory migrate` give every project
a consistent upgrade path from any legacy shape to the 0.3.0 contract,
preserving user prose byte-for-byte.

Highlights:

- **Four migrators, one pattern** — constitution, roadmap, tech-stack,
  and personas each get a shape migrator that patches in placeholder
  stubs without touching existing prose. SHA-256 body-preservation is
  verified by integration tests.
- **Four enrichers, one contract** — constitution and tech-stack fill
  placeholders deterministically from body text; roadmap seeds Vision
  and a completed-items hint; personas runs as a linter (reports
  `{placeholder}` tokens, never modifies content — persona authoring
  belongs to `/doit.roadmapit` or `/doit.researchit`).
- **Umbrella CLI** — `doit memory migrate` reports 4 deterministic rows
  (constitution → roadmap → tech-stack → personas). Each file's row is
  emitted even when the file is absent (opt-in semantic for personas).
- **Validator parity** — `memory_validator.verify_memory_contract` now
  validates all four files consistently. Contract tests lock required
  H2 sets and ID regex semantics between migrators and validators.

**Coming next in 0.4.0** (on `develop`): TBD. The P2 roadmap is narrow
(GitHub Copilot Coding Agent support as the sole remaining P2 item);
several productive P3 candidates (`doit doctor`, workflow checkpoint
validation, cross-platform CI) are in consideration. See
[.doit/memory/roadmap.md](.doit/memory/roadmap.md).

No breaking changes. `doit memory migrate` adds a fourth output row —
JSON consumers that parsed a fixed 3-row shape will need to expect 4.
All other behaviour is additive.

## What's New

### Constitution frontmatter auto-migration (#059)

`doit update` (and `doit init --update`) now detect a
`.doit/memory/constitution.md` with missing or incomplete YAML
frontmatter and prepend a placeholder skeleton containing every
required field from the canonical
[frontmatter schema](src/doit_cli/schemas/frontmatter.schema.json).
Existing field values are preserved verbatim; unknown/extra keys are
preserved too. Body bytes are SHA-256 verified. Malformed YAML
frontmatter surfaces a clear error without modifying the file (atomic
write).

The `/doit.constitution` skill gains an enrichment branch that detects
`[PROJECT_*]` sentinels and infers real values by reading the body and
`doit context show` output — no interactive prompts required.

### Roadmap + tech-stack shape migration (#060)

`doit update` detects legacy roadmap/tech-stack files missing required
H2/H3 sections and inserts placeholder stubs in place:

- **Roadmap**: `## Active Requirements` with `### P1..P4` subsections.
- **Tech-stack**: `## Tech Stack` with `### Languages`, `### Frameworks`,
  `### Libraries` subsections.

Both migrations are idempotent, body-preserving, and CRLF-safe.
Deterministic enrichers (`doit memory enrich roadmap`, `doit memory
enrich tech-stack`) populate Vision, completed-items hints, and
tech-stack groupings from constitution context.

### Roadmap H3 prefix-match regression fix (#061)

Patched a regression in #060's migrator that appended duplicate empty
`### P1..P4` stubs to roadmaps whose priority headings carried suffix
decoration (e.g. `### P1 - Critical (Must Have for MVP)`). The
migrator now uses the same `^p[1-4]\b` prefix semantics the validator
does, so decorated priorities are recognised as present. The shared
`_memory_shape.insert_section_if_missing` helper gained an optional
per-H3 `matchers` parameter so callers can opt into custom matching;
tech-stack continues using exact-match. A dogfood regression test
locks the exact case that drove the fix.

### Personas.md migration (#062) — closes the pattern

The fourth and final `.doit/memory/*.md` file gets the migrator +
enricher + validator treatment, with two deliberate twists:

- **Opt-in**: personas.md is NOT auto-created. Absence is a valid
  state. Projects that don't use persona-driven workflows continue to
  work without emitting errors.
- **Linter-only enricher**: `doit memory enrich personas` detects
  `{placeholder}` tokens and reports `PARTIAL` with a sorted,
  deduplicated `unresolved_fields` list, but never modifies the file.
  Persona content is intrinsically project-specific — authoring belongs
  to `/doit.roadmapit` or `/doit.researchit`.

The validator enforces canonical `### Persona: P-NNN` three-digit IDs
under `## Detailed Profiles`. Contract tests lock the validator ↔
migrator ID bijection over a representative corpus.

### Umbrella CLI

`doit memory migrate` emits a deterministic 4-row report:

```json
[
  {"file": "constitution.md", "action": "no_op", ...},
  {"file": "roadmap.md",      "action": "no_op", ...},
  {"file": "tech-stack.md",   "action": "no_op", ...},
  {"file": "personas.md",     "action": "no_op", ...}
]
```

The personas.md row is emitted even when the file is absent (opt-in
semantic), so JSON consumers can assume a fixed shape.

## Breaking Changes

None, but note:

- `doit memory migrate` now reports **4 rows** instead of 3. JSON
  consumers that hardcoded `len(payload) == 3` will need to update.
  Per-row shape is unchanged.

## Deprecations

None new in 0.3.0.

Carried forward from 0.2.0:

- Flat `.claude/commands/doit.<name>.md` templates continue to work in
  0.3.0 but are deprecated in favor of the Skills layout. A future
  minor release will remove the flat-command generator.

## Upgrade Instructions

### 0.2.x → 0.3.0

1. Upgrade the CLI:

   ```bash
   uv tool install doit-toolkit-cli --force
   ```

2. Run the memory-file migration on existing projects:

   ```bash
   doit memory migrate .
   ```

   The output reports 4 rows — one per memory file. Expected actions:
   - First run on a 0.2.x project: some `patched` or `prepended`
     entries as missing shape gets filled in.
   - Subsequent runs: all `no_op`, byte-identical.

3. Verify the contract:

   ```bash
   doit verify-memory .
   ```

   Expect `0 error(s), 0 warning(s)` on a clean project. Placeholder
   warnings surface when files still contain unresolved `[TOKEN]` or
   `{Placeholder}` tokens — run the appropriate enricher:

   ```bash
   doit memory enrich roadmap
   doit memory enrich tech-stack
   doit memory enrich personas   # linter-only; never modifies the file
   ```

4. If an earlier 0.2.x migration run accidentally appended duplicate
   bare `### P1..P4` stubs to your `roadmap.md` (surfaced during spec
   062 dogfooding as a spec-060 regression, fixed in spec 061), delete
   the duplicates manually. Future migrations will stabilise to
   `no_op`.

See the [Upgrade Guide](docs/upgrade.md) for the full migration matrix.

## Contributors

- Claude Code implementation assistance across specs 059, 060, 061, 062

## Full Changelog

See [CHANGELOG.md](./CHANGELOG.md) for complete release history.
