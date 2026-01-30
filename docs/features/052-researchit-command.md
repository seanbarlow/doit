# Research Command for Product Owners

**Completed**: 2026-01-29
**Branch**: 052-researchit-command
**PR**: Pending

## Overview

The `/doit.researchit` command is a pre-specification workflow stage designed for Product Owners to capture business requirements through interactive AI-assisted Q&A. It focuses purely on business value and user needs without involving technology decisions.

The command guides users through a structured 12-question session across four phases:
1. **Problem Understanding**: Core problem and impact
2. **Users and Goals**: Target personas and success criteria
3. **Requirements and Constraints**: Must-haves, nice-to-haves, boundaries
4. **Success Metrics**: How to measure success and failure

## Requirements Implemented

| ID | Description | Status |
|----|-------------|--------|
| FR-001 | Interactive Q&A session guides user | Done |
| FR-002 | Questions about problem, users, goals, metrics, constraints | Done |
| FR-003 | No technology questions asked | Done |
| FR-004 | Accept free-form text answers | Done |
| FR-005 | Generate research.md with structured format | Done |
| FR-006 | Generate user-stories.md with Given/When/Then | Done |
| FR-007 | Derive stories from captured user needs | Done |
| FR-008 | Identify distinct personas | Done |
| FR-009 | Generate interview-notes.md | Done |
| FR-010 | Generate competitive-analysis.md | Done |
| FR-011 | Create artifacts in specs/{feature}/ | Done |
| FR-012 | Create feature directory if needed | Done |
| FR-013 | Format for /doit.specit consumption | Done |
| FR-014 | Include metadata in artifacts | Done |
| FR-015 | Summary output with next steps | Done |
| FR-016 | Save progress when interrupted | Done |
| FR-017 | Offer resume from draft | Done |
| FR-018 | Clean up draft after completion | Done |

## Technical Details

This is a **template-based slash command** that AI assistants (Claude Code, GitHub Copilot, Cursor) read and execute. No Python code was written - only markdown templates.

### Key Design Decisions

1. **Template-only implementation**: Unlike CLI commands, this is executed by AI assistants reading the template
2. **Four-phase Q&A structure**: Organized questions for logical flow and complete coverage
3. **Business-focused**: Deliberately excludes technology questions to keep focus on user value
4. **Specit integration**: Modified `/doit.specit` to automatically load research artifacts

### Architecture

```
templates/
└── commands/
    └── doit.researchit.md          # Command template (12KB)

.doit/
└── templates/
    ├── research-template.md        # research.md artifact template
    ├── user-stories-template.md    # user-stories.md artifact template
    ├── interview-notes-template.md # interview-notes.md template
    └── competitive-analysis-template.md # competitive-analysis.md template
```

## Files Changed

### New Files

| File | Purpose |
|------|---------|
| `templates/commands/doit.researchit.md` | Main command template |
| `.doit/templates/research-template.md` | research.md output format |
| `.doit/templates/user-stories-template.md` | user-stories.md output format |
| `.doit/templates/interview-notes-template.md` | interview-notes.md template |
| `.doit/templates/competitive-analysis-template.md` | competitive-analysis.md template |

### Modified Files

| File | Change |
|------|--------|
| `templates/commands/doit.specit.md` | Added "Load Research Artifacts" section |

## Testing

- **Automated tests**: N/A (template-based feature, no Python code)
- **Manual tests**: 5/5 passed
  - Q&A session initiates correctly
  - 12 questions across 4 phases present
  - No technology questions asked
  - Free-form answers captured
  - Artifact templates validated

## Related Issues

- Epic: N/A (no GitHub CLI available)
- Features: N/A
- Tasks: N/A

## User Stories Delivered

1. **US1 - Interactive Research Session**: Product Owners can capture requirements through Q&A
2. **US2 - User Story Generation**: System generates Given/When/Then user stories
3. **US3 - Full Research Package**: System generates all 4 artifact templates
4. **US4 - Research-to-Spec Handoff**: `/doit.specit` loads research artifacts
5. **US5 - Resume Incomplete Research**: Sessions can be resumed from draft

## Workflow Integration

```
┌─────────────────────────────────────────────────────────────────┐
│  doit Workflow (NEW stage added)                                │
│  ● researchit → ○ specit → ○ planit → ○ taskit → ○ implementit │
└─────────────────────────────────────────────────────────────────┘
```

The researchit command is positioned as the **first stage** of the workflow, specifically for Product Owners who want to capture business requirements before technical specification.
