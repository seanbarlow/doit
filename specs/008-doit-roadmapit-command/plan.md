# Implementation Plan: Doit Roadmapit Command

**Branch**: `008-doit-roadmapit-command` | **Date**: 2026-01-10 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/008-doit-roadmapit-command/spec.md`

## Summary

Add a new `/doit.roadmapit` slash command for creating and updating project roadmaps with prioritized requirements, deferred functionality, and AI-suggested enhancements. The command will store roadmaps in `.doit/memory/roadmap.md` and archive completed items to `completed_roadmap.md`. Implementation requires creating command and content templates, updating the scaffold system to include the new command, and integrating with the checkin workflow.

## Technical Context

**Language/Version**: Markdown (command definitions), Bash 5.x (helper scripts)
**Primary Dependencies**: Claude Code slash command system, existing doit command templates
**Storage**: File-based (`.doit/memory/roadmap.md`, `.doit/memory/completed_roadmap.md`)
**Testing**: Manual verification via command execution
**Target Platform**: macOS, Linux (where Claude Code runs)
**Project Type**: Single project - template/CLI tool
**Performance Goals**: N/A (file-based template system)
**Constraints**: Must integrate with existing 9-command doit suite
**Scale/Scope**: Single new command + templates + integration updates

## Architecture Overview

<!-- BEGIN:AUTO-GENERATED section="architecture" -->
```mermaid
flowchart TD
    subgraph "User Interaction"
        CMD[/doit.roadmapit command]
    end
    subgraph "Templates"
        CMDTPL[doit.roadmapit.md]
        CONTPL[roadmap-template.md]
        ARCTPL[completed-roadmap-template.md]
    end
    subgraph "Memory Files"
        RM[roadmap.md]
        CRM[completed_roadmap.md]
    end
    subgraph "Integration"
        SCAFFOLD[doit.scaffoldit]
        CHECKIN[doit.checkin]
        SPECIT[doit.specit]
        PLANIT[doit.planit]
    end

    CMD --> CMDTPL
    CMDTPL --> CONTPL
    CMDTPL --> RM
    CMDTPL --> CRM
    SCAFFOLD -.->|copies| CMDTPL
    CHECKIN -.->|triggers archive| CRM
    SPECIT -.->|references| RM
    PLANIT -.->|references| RM
```
<!-- END:AUTO-GENERATED -->

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Gate | Status | Notes |
|------|--------|-------|
| Follows existing command patterns | ✅ PASS | Uses same YAML frontmatter + markdown structure |
| File-based storage | ✅ PASS | Uses `.doit/memory/` directory like constitution |
| Template-driven | ✅ PASS | Creates roadmap-template.md like other templates |
| Scaffold integration | ✅ PASS | Updates scaffoldit to copy new command (10 total) |
| Cross-command references | ✅ PASS | Follows established patterns for command linking |

## Project Structure

### Documentation (this feature)

```text
specs/008-doit-roadmapit-command/
├── plan.md              # This file
├── spec.md              # Feature specification
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
└── tasks.md             # Phase 2 output (/doit.taskit)
```

### Source Code (repository root)

```text
.claude/commands/
└── doit.roadmapit.md        # NEW: Active command file

.doit/templates/
├── commands/
│   └── doit.roadmapit.md    # NEW: Command template for distribution
├── roadmap-template.md      # NEW: Content template for roadmap.md
└── completed-roadmap-template.md  # NEW: Template for archived items

.doit/memory/
├── roadmap.md               # Created by command (user project)
└── completed_roadmap.md     # Created when items complete (user project)

templates/commands/
└── doit.roadmapit.md        # NEW: Distribution copy
```

**Structure Decision**: Single project structure. This feature adds 3 new template files and updates 2 existing command files (scaffoldit, checkin).

## File Changes Summary

| File | Action | Purpose |
|------|--------|---------|
| `.claude/commands/doit.roadmapit.md` | CREATE | Active command for this repo |
| `.doit/templates/commands/doit.roadmapit.md` | CREATE | Command template for distribution |
| `templates/commands/doit.roadmapit.md` | CREATE | Distribution copy |
| `.doit/templates/roadmap-template.md` | CREATE | Content template |
| `.doit/templates/completed-roadmap-template.md` | CREATE | Archive template |
| `.claude/commands/doit.scaffoldit.md` | UPDATE | Add roadmapit to copied commands (10 total) |
| `.claude/commands/doit.checkin.md` | UPDATE | Add roadmap archive trigger |
| `.doit/templates/commands/doit.scaffoldit.md` | UPDATE | Sync with active command |
| `templates/commands/doit.scaffoldit.md` | UPDATE | Sync distribution copy |

## Complexity Tracking

> No constitution violations. Feature follows established patterns.

| Aspect | Decision | Rationale |
|--------|----------|-----------|
| Template count | 2 new content templates | Minimum needed for roadmap + archive |
| Command count | 10 total (was 9) | One new command added |
| Integration points | 2 commands updated | scaffold + checkin for full workflow |
