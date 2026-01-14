# Documentation Branding Cleanup

**Completed**: 2026-01-12
**Branch**: 015-docs-branding-cleanup
**PR**: Pending

## Overview

Clean up all documentation files to remove legacy "Spec Kit" and "specify" branding references, replacing them with correct "Do-It" and "doit" branding. Updated all AI agent references to reflect the officially supported agents: Claude and GitHub Copilot only (removing references to Gemini, Codebuddy, and other unsupported agents).

## Requirements Implemented

| ID | Description | Status |
|----|-------------|--------|
| FR-001 | Replace "Spec Kit" with "Do-It" (proper noun) | Done |
| FR-002 | Replace "spec-kit" with "doit" in package/repo names | Done |
| FR-003 | Replace "specify" CLI command with "doit" | Done |
| FR-004 | Replace "specify-cli" with "doit-toolkit-cli" in package names | Done |
| FR-005 | Update docfx.json metadata to reference "Do-It" | Done |
| FR-006 | Replace "github.com/github/spec-kit" with "github.com/seanbarlow/doit" | Done |
| FR-007 | Replace "github.github.io/spec-kit" with "seanbarlow.github.io/doit" | Done |
| FR-008 | Update docfx.json `_gitContribute.repo` URL | Done |
| FR-009 | Remove references to Gemini as supported agent | Done |
| FR-010 | Remove references to Codebuddy as supported agent | Done |
| FR-011 | installation.md lists only Claude and GitHub Copilot | Done |
| FR-012 | upgrade.md shows only --ai claude and --ai copilot | Done |
| FR-013 | Update docs/upgrade.md | Done |
| FR-014 | Update docs/docfx.json | Done |
| FR-015 | Update any other docs with legacy references | Done |

## Technical Details

- **Language/Version**: Markdown documentation updates only
- **Dependencies**: None
- **Testing**: Manual verification via grep commands

### Key Decisions

1. Historical feature documentation in `docs/features/` was preserved as it documents past migrations
2. Script files in `.doit/scripts/` and other locations outside `docs/` were out of scope
3. The English verb "specify" was preserved where it appears naturally in prose
4. Updated installation.md to list all 11 doit commands (discovered during review)

## Files Changed

### Modified

- `docs/upgrade.md` - 40 occurrences fixed (spec-kit, specify, gemini, GitHub URLs)
- `docs/docfx.json` - 4 occurrences fixed (appTitle, appName, appFooter, gitContribute URL)
- `docs/installation.md` - 6 occurrences fixed + all 11 commands listed
- `docs/local-development.md` - 1 occurrence fixed (--ai gemini to --ai claude)

### Preserved (Historical)

- `docs/features/006-docs-doit-migration.md` - Historical migration documentation
- `docs/features/003-scaffold-doit-commands.md` - Historical migration documentation
- `docs/features/update-doit-templates.md` - Historical migration documentation
- `docs/features/004-review-template-commands.md` - Historical migration documentation
- `docs/features/005-mermaid-visualization.md` - Historical command refs

## Testing

### Automated Tests

N/A - Documentation-only feature

### Manual Tests

| Test | Result |
|------|--------|
| MT-001: Commands in upgrade.md use correct CLI names | PASS |
| MT-002: Zero results for "spec-kit" or "Spec Kit" | PASS |
| MT-003: docfx.json references "Do-It" and correct GitHub URLs | PASS |
| MT-004: Zero results for "github/spec-kit" | PASS |
| MT-005: installation.md shows only Claude and GitHub Copilot | PASS |
| MT-006: Zero results for "gemini" | PASS |
| MT-007: Zero results for "codebuddy" | PASS |
| MT-008: upgrade.md --ai examples show only claude and copilot | PASS |
| MT-009: GitHub links go to seanbarlow/doit | PASS |
| MT-010: Release notes links point to seanbarlow/doit/releases | PASS |
| MT-011: docfx.json gitContribute.repo URL is correct | PASS |

## Success Criteria

| ID | Criterion | Status |
|----|-----------|--------|
| SC-001 | Zero "spec-kit" matches in docs/ (excluding historical) | PASS |
| SC-002 | Zero "Spec Kit" matches in docs/ (excluding historical) | PASS |
| SC-003 | Zero "specify" CLI matches in docs/ (excluding historical) | PASS |
| SC-004 | Zero "github/spec-kit" matches in docs/ | PASS |
| SC-005 | Zero "gemini" matches in docs/ | PASS |
| SC-006 | Zero "codebuddy" matches in docs/ | PASS |
| SC-007 | All GitHub URLs point to seanbarlow/doit | PASS |
| SC-008 | docfx.json contains correct branding and URL | PASS |

## Related Issues

- Epic: #31 - Documentation Branding Cleanup
- Features: #32, #33, #34
