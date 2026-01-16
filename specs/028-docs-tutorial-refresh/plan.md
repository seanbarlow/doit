# Implementation Plan: Documentation and Tutorial Refresh

**Branch**: `028-docs-tutorial-refresh` | **Date**: 2026-01-15 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/028-docs-tutorial-refresh/spec.md`

## Summary

Update all Do-It documentation to reflect features 023-027, including adding missing CLI commands (`sync-prompts`, `context`, `hooks`, `verify`) to command references, regenerating the feature index, creating context injection documentation, and adding git hooks workflow guide. This is a **documentation-only** feature with no code changes.

## Technical Context

**Language/Version**: N/A (Markdown documentation only)
**Primary Dependencies**: N/A
**Storage**: N/A
**Testing**: Manual verification of documentation accuracy
**Target Platform**: GitHub Pages (MkDocs), GitHub README
**Project Type**: single (documentation files)
**Performance Goals**: N/A
**Constraints**: All documentation must be valid Markdown, no broken links
**Scale/Scope**: ~10 files to update, ~3 new sections to write

## Architecture Overview

<!--
  AUTO-GENERATED: Documentation-only feature has simplified architecture.
-->

<!-- BEGIN:AUTO-GENERATED section="architecture" -->
```mermaid
flowchart LR
    subgraph "Source of Truth"
        SPEC[Feature Specs] --> FEATURES[Feature Docs]
        CLI[CLI Implementation] --> COMMANDS[Command Reference]
    end

    subgraph "Documentation"
        README[README.md]
        QS[quickstart.md]
        INST[installation.md]
        INDEX[index.md]
        TUT[tutorials/]
    end

    subgraph "Sync"
        DOC[/doit.documentit] --> INDEX
    end

    FEATURES --> INDEX
    COMMANDS --> QS
    COMMANDS --> README
```
<!-- END:AUTO-GENERATED -->

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| I. Specification-First | PASS | Spec created before implementation |
| II. Persistent Memory | PASS | Updates to .doit/memory/ docs follow pattern |
| III. Auto-Generated Diagrams | PASS | Will use /doit.documentit for index generation |
| IV. Opinionated Workflow | PASS | Following specit → planit → taskit workflow |
| V. AI-Native Design | PASS | Documenting slash commands and CLI commands |

**Tech Stack Alignment**: N/A - Documentation-only feature does not introduce new technology.

## Project Structure

### Documentation (this feature)

```text
specs/028-docs-tutorial-refresh/
├── spec.md              # Feature specification (complete)
├── plan.md              # This file
├── research.md          # Documentation audit findings (complete)
├── checklist.md         # Quality checklist (complete)
├── quickstart.md        # Implementation guide (Phase 1)
└── tasks.md             # Task breakdown (/doit.taskit)
```

### Files to Modify (repository root)

```text
# Root Level
README.md                           # Update command count, add CLI section

# Documentation
docs/
├── quickstart.md                   # Add context section, update command table
├── installation.md                 # Add CLI commands to verification
├── index.md                        # Regenerate via /doit.documentit
└── tutorials/
    └── 02-existing-project-tutorial.md  # Add context injection mentions

# Optional (if exists)
CHANGELOG.md                        # Document features 023-027
```

**Structure Decision**: No new directories or structural changes. Updates to existing documentation files only.

## Implementation Approach

### Phase 1: Command Reference Updates (P1)

1. **quickstart.md Command Table**
   - Add row for `doit sync-prompts`
   - Add row for `doit context`
   - Add row for `doit hooks`
   - Add row for `doit verify`
   - Add "Type" column (CLI/Slash)

2. **README.md Commands Section**
   - Change "The 11 Commands" to "The Commands" or accurate count
   - Add CLI Commands subsection
   - Keep slash commands in existing table

3. **installation.md Verification**
   - Add CLI command verification steps
   - Show `doit --help` output

### Phase 2: Feature Index Regeneration (P1)

1. Run `/doit.documentit` to scan docs/features/
2. Verify all 19+ feature docs appear in index.md
3. Validate all links work

### Phase 3: Context Injection Documentation (P1)

1. **New Section in quickstart.md**: "Project Context"
   - Explain what context injection does
   - Show `doit context show` usage
   - Document context.yaml configuration
   - Explain automatic loading in slash commands

### Phase 4: Git Hooks Documentation (P2)

1. **New Section in quickstart.md**: "Workflow Enforcement"
   - Explain spec-first validation
   - Document `doit hooks install`
   - Document `doit hooks validate`
   - Document bypass mechanism (`--no-verify`)
   - Reference hooks.yaml configuration

### Phase 5: Tutorial Updates (P2)

1. **Tutorial 02 Updates**
   - Add note about automatic context loading
   - Mention sync-prompts for multi-agent setups
   - Update workflow diagrams if needed

### Phase 6: Version and Changelog (P3)

1. Update README.md version to 0.1.4
2. Update CHANGELOG.md with features 023-027

## No Code Changes Required

This feature involves **only documentation updates**:
- No Python code changes
- No template changes
- No CLI command changes
- No test changes

All changes are to `.md` files in `docs/` and root-level documentation.

## Complexity Tracking

> No constitution violations. Documentation-only feature aligns with all principles.

| Aspect | Assessment |
|--------|------------|
| New Technology | None |
| Infrastructure Changes | None |
| Breaking Changes | None |
| External Dependencies | None |

## Dependencies

- Feature 026-ai-context-injection (completed) - context command implementation
- Feature 027-template-context-injection (completed) - template changes
- Feature 025-git-hooks-workflow (completed) - hooks command implementation

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Documentation becomes stale again | Medium | Low | Regular /doit.documentit runs |
| Broken links | Low | Medium | Manual link verification |
| Inconsistent terminology | Low | Low | Checklist review |

## Next Steps

1. Run `/doit.taskit` to generate task breakdown
2. Execute documentation updates following task order
3. Run `/doit.documentit` to regenerate index
4. Verify all changes via review

---

*Plan generated by /doit.planit on 2026-01-15*
