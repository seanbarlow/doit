# Research: Documentation Branding Cleanup

**Feature**: 015-docs-branding-cleanup
**Date**: 2026-01-12

## Summary

Analysis of all documentation files requiring updates to remove legacy "Spec Kit" and "specify" branding references.

## File Analysis

### High Priority Files (Phase 1)

#### docs/upgrade.md (40 occurrences)

| Pattern | Count | Context |
| ------- | ----- | ------- |
| `specify-cli` | 6 | Package name in install commands |
| `specify` | 20 | CLI command references |
| `github/spec-kit` | 8 | GitHub URLs |
| `Spec Kit` | 2 | Prose references |
| `spec-kit` | 4 | Package/repo names |

**Decision**: Full rewrite of command examples replacing `specify` with `doit` and `specify-cli` with `doit-toolkit-cli`.

#### docs/docfx.json (4 occurrences)

| Pattern | Count | Context |
| ------- | ----- | ------- |
| `Spec Kit` | 3 | `_appTitle`, `_appName`, `_appFooter` |
| `github/spec-kit` | 1 | `_gitContribute.repo` |

**Decision**: Update JSON metadata values to use "DoIt" branding and correct repository URL.

#### docs/installation.md (6 occurrences)

| Pattern | Count | Context |
| ------- | ----- | ------- |
| `gemini` | 2 | AI agent option |
| `codebuddy` | 2 | AI agent option |
| Other legacy refs | 2 | Various |

**Decision**: Remove gemini and codebuddy from supported agents list, keep only claude and copilot.

### Medium Priority Files (Phase 2-3)

#### docs/templates/commands.md (7 occurrences)

References to old command naming conventions and spec-kit terminology.

#### docs/features/006-docs-doit-migration.md (13 occurrences)

Historical documentation about the migration from Spec Kit to DoIt. Contains intentional references documenting the change - these should be reviewed but may be intentional historical references.

#### docs/features/003-scaffold-doit-commands.md (8 occurrences)

Feature documentation with legacy command references.

### Low Priority Files (Phase 3)

Files with 1-4 occurrences that need simple find/replace updates.

## Replacement Strategy

### Safe Replacements (Global Find/Replace)

1. `git+https://github.com/github/spec-kit.git` → `doit-toolkit-cli`
2. `github.com/github/spec-kit` → `github.com/seanbarlow/doit`
3. `github.github.io/spec-kit` → `seanbarlow.github.io/doit`
4. `specify-cli` → `doit-toolkit-cli`

### Context-Sensitive Replacements (Manual Review)

1. `specify` → `doit` (verify it's a CLI command, not the English word "specify")
2. `Spec Kit` → `DoIt` (proper noun replacement)
3. `spec-kit` → `doit` (in package/repo contexts)

### AI Agent Removal (Manual Edit)

Remove these from supported agent lists while preserving list structure:
- `gemini` / `Gemini` / `Gemini CLI`
- `codebuddy` / `Codebuddy` / `Codebuddy CLI`

Keep only:
- `claude` / `Claude` / `Claude Code`
- `copilot` / `Copilot` / `GitHub Copilot`

## Alternatives Considered

| Alternative | Decision | Rationale |
| ----------- | -------- | --------- |
| Automated sed script | Rejected | Risk of breaking Markdown/JSON syntax |
| Delete feature docs entirely | Rejected | Historical value, just update references |
| Keep gemini/codebuddy as "community" | Rejected | User explicitly wants only Claude and Copilot |

## Dependencies

None - this is a documentation-only change with no code dependencies.

## Risks

| Risk | Mitigation |
| ---- | ---------- |
| Breaking JSON syntax in docfx.json | Validate with JSON linter after edit |
| Missing occurrences | Grep verification after each phase |
| Breaking Markdown links | Manual review of all hyperlinks |
