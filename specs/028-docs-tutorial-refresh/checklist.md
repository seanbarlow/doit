# Quality Checklist: Documentation and Tutorial Refresh

**Feature**: 028-docs-tutorial-refresh
**Created**: 2026-01-15

## Pre-Implementation Checklist

- [x] Spec reviewed and approved
- [x] Research completed (documentation audit)
- [x] Plan created
- [x] Tasks generated

## Implementation Checklist

### US1 - Complete Command Reference (P1)

- [x] quickstart.md: Add `sync-prompts` to command table
- [x] quickstart.md: Add `context` to command table
- [x] quickstart.md: Add `hooks` to command table
- [x] quickstart.md: Add `verify` to command table
- [x] README.md: Update "11 Commands" section with accurate count
- [x] README.md: Add CLI commands section separate from slash commands
- [x] installation.md: Add CLI commands to verification section

### US2 - Updated Feature Index (P1)

- [x] Run `/doit.documentit` to regenerate index
- [x] Verify docs/index.md shows all 19+ features
- [x] Verify all feature links are valid

### US3 - Context Injection Guide (P1)

- [x] quickstart.md: Add "Context Injection" section
- [x] Document `doit context show` command
- [x] Document `doit context show --format yaml`
- [x] Explain automatic context loading in slash commands
- [x] Document context.yaml configuration

### US4 - Git Hooks Workflow Documentation (P2)

- [x] Create hooks documentation (new guide or section)
- [x] Document `doit hooks install`
- [x] Document `doit hooks validate`
- [x] Document bypass mechanism (`--no-verify`)
- [x] Document hooks.yaml configuration

### US5 - Tutorial Updates (P2)

- [x] Tutorial 02: Add context injection mention
- [x] Tutorial 02: Add sync-prompts mention for multi-agent setups
- [x] Verify workflow diagrams are accurate

### US6 - CLI vs Slash Command Clarity (P2)

- [x] README.md: Separate CLI and slash commands visually
- [x] quickstart.md: Add Type column to command table
- [x] Ensure consistent terminology throughout

### US7 - Version Accuracy (P3)

- [x] Update README.md version to match pyproject.toml
- [x] Verify CHANGELOG.md exists and is current
- [x] Document features 023-027 in changelog if missing

## Verification Checklist

- [x] All internal links working (no 404s)
- [x] All code examples copy-paste runnable
- [x] No broken markdown syntax
- [x] Consistent terminology throughout
- [x] Version numbers accurate

## Final Review

- [x] All FR requirements met (FR-001 through FR-012)
- [x] All SC success criteria verified
- [x] Documentation reads well end-to-end
- [x] No outdated information remains
