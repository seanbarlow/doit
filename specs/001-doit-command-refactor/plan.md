# Implementation Plan: Doit Command Refactoring

**Branch**: `001-doit-command-refactor` | **Date**: 2026-01-09 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/001-doit-command-refactor/spec.md`

## Summary

Refactor the speckit command system to use "doit" branding, consolidating 9 commands down to 9 restructured commands (4 removed, 4 new added). The refactoring includes:
- Renaming all `speckit.*` commands to `doit.*`
- Consolidating clarify/analyze/checklist into specify and review
- Adding new scaffold, review, test, and checkin commands
- Enhancing constitution to capture tech stack and infrastructure
- Creating GitHub issue templates for Epic/Feature/Task hierarchy
- Integrating GitHub issue creation into specify and tasks commands

## Technical Context

**Language/Version**: Markdown (command definitions), Bash 5.x (scripts), Python 3.11+ (CLI)
**Primary Dependencies**: Claude Code slash command system, GitHub MCP server, typer, rich, httpx
**Storage**: File-based (markdown files in `.claude/commands/`, `.specify/templates/`, `.specify/memory/`)
**Testing**: Manual testing via command execution; validation through workflow completion
**Target Platform**: Cross-platform (macOS, Linux, Windows via WSL) - wherever Claude Code runs
**Project Type**: Single CLI tool
**Performance Goals**: Commands execute in < 30 seconds for typical operations
**Constraints**: Must maintain backward-compatible file structures for specs/plans/tasks
**Scale/Scope**: 9 command files, 5 bash scripts, 6 templates, 1 Python CLI package

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

**Status**: Constitution template exists but is not yet populated for this project. This is expected since this feature is building the tool that creates constitutions.

**Applicable Principles** (from template structure):
- [ ] Library-First: Commands should be modular and independently testable ✓
- [ ] CLI Interface: All commands use text in/out protocol ✓
- [ ] Test-First: Manual test scenarios defined in spec ✓
- [ ] Simplicity: Reducing command count from 9 to 9 consolidated ✓

**Gate Status**: PASS - No constitution violations; proceeding with design.

## Project Structure

### Documentation (this feature)

```text
specs/001-doit-command-refactor/
├── spec.md              # Feature specification (complete)
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output (command interfaces)
├── checklists/          # Quality validation checklists
│   └── requirements.md  # Specification quality checklist
├── current-functionality.md  # Analysis of existing commands
└── tasks.md             # Phase 2 output (/speckit.tasks command)
```

### Source Code (repository root)

```text
# Command Files (primary deliverables)
.claude/commands/
├── doit.constitution.md  # Enhanced: + tech stack, infrastructure prompts
├── doit.scaffold.md      # NEW: project structure generation
├── doit.specify.md       # Modified: + clarify + analyze + Epic/Feature issues
├── doit.plan.md          # Modified: technical design only
├── doit.tasks.md         # Modified: + taskstoissues (Task issues)
├── doit.implement.md     # Modified: keeps checklist gate
├── doit.review.md        # NEW: code review + manual testing + sign-off
├── doit.test.md          # NEW: test execution + reporting
└── doit.checkin.md       # NEW: close issues + roadmaps + docs + PR

# Supporting Scripts
.specify/scripts/bash/
├── common.sh             # Shared utilities (update references)
├── create-new-feature.sh # Branch creation (update references)
├── setup-plan.sh         # Plan setup (update references)
├── check-prerequisites.sh # Prerequisite checks (update references)
└── update-agent-context.sh # Agent context updates (update references)

# Templates
.specify/templates/
├── spec-template.md      # Keep as-is
├── plan-template.md      # Update command references
├── tasks-template.md     # Update command references
├── checklist-template.md # Update command references
└── agent-file-template.md # Update command references

# Constitution Memory
.specify/memory/
└── constitution.md       # Enhanced template with new sections

# GitHub Issue Templates (NEW)
.github/ISSUE_TEMPLATE/
├── epic.md               # Epic issue template
├── feature.md            # Feature issue template
└── task.md               # Task issue template

# Python CLI
src/specify_cli/
└── __init__.py           # Update branding to "doit"

# Project Configuration
pyproject.toml            # Update project name to "doit-cli"
```

**Structure Decision**: Single project structure maintained. The tool is a CLI that generates markdown artifacts; no web frontend or mobile components required.

## Complexity Tracking

> No constitution violations requiring justification.

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| N/A | N/A | N/A |

## Architecture Decisions

### AD-001: Command File Naming Convention

**Decision**: Use `doit.<command>.md` naming pattern for all command files.

**Rationale**: Maintains consistency with existing speckit pattern; clear namespace for commands.

### AD-002: Absorbing Clarify into Specify

**Decision**: Integrate clarification Q&A directly into the specify command flow.

**Rationale**: Reduces workflow steps; spec generation naturally requires clarification.

**Implementation**: Add 8-category ambiguity scan from clarify.md into specify.md between feature description analysis and spec generation.

### AD-003: Absorbing Analyze into Specify and Review

**Decision**: Split analyze functionality:
- Pre-spec validation → specify command
- Post-implementation audit → review command

**Rationale**: Analysis makes sense at both ends of the workflow, not as standalone step.

### AD-004: GitHub Issue Integration Strategy

**Decision**: Create issues inline during specify (Epic + Features) and tasks (Tasks) commands.

**Rationale**: Immediate traceability; reduces manual steps; issues exist from workflow start.

**Implementation**:
- doit.specify: Create Epic issue from spec summary, Feature issues from user stories
- doit.tasks: Create Task issues linked to parent Features

### AD-005: Constitution Enhancement Strategy

**Decision**: Add structured sections for tech stack, infrastructure, and deployment to constitution template.

**Rationale**: Enables context-aware code generation in downstream commands.

**Implementation**: New sections in constitution.md template:
- Purpose & Goals
- Tech Stack (languages, frameworks, libraries)
- Infrastructure (hosting, cloud provider)
- Deployment (CI/CD, deployment strategy)

### AD-006: Scaffold Command Design

**Decision**: Scaffold reads from constitution.md to generate appropriate project structure.

**Rationale**: Constitution captures tech decisions; scaffold operationalizes them.

**Implementation**:
- Read tech stack from constitution
- Match to predefined structure templates
- Generate folder structure, config files, starter files, .gitignore

### AD-007: Checkin Command as Workflow Finalizer

**Decision**: Checkin command handles all post-implementation cleanup in one step.

**Rationale**: Single command for: close issues → update roadmaps → generate docs → commit → PR

**Implementation**: Sequential operations with graceful error handling for each step.

## Command Dependency Map

```text
doit.constitution ──┐
                    ├──> doit.scaffold ──┐
                    │                    │
                    └────────────────────┼──> doit.specify ──> doit.plan ──> doit.tasks
                                         │           │             │             │
                                         │     Creates Epic   Generates    Creates Task
                                         │     + Feature      plan.md      issues
                                         │       issues
                                         │
                                         └──> doit.implement ──> doit.review ──> doit.test ──> doit.checkin
                                                    │                │               │              │
                                              Checklist gate    Code review     Test run      Close issues
                                              Task execution    Manual test     Report        Update roadmaps
                                                               Sign-off                      Generate docs
                                                                                            Create PR
```

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| GitHub MCP server unavailable | Low | Medium | Graceful fallback to local-only mode |
| Complex migration for existing projects | Medium | Low | Document manual migration steps |
| Command handoff references break | Medium | Medium | Comprehensive find/replace; test all handoffs |
| Issue template format incompatible | Low | Low | Use standard GitHub issue template format |

## Implementation Phases Summary

1. **Phase 1: Foundation** - Rename commands, update references, create new command stubs
2. **Phase 2: Constitution & Scaffold** - Enhance constitution, implement scaffold command
3. **Phase 3: Specify Enhancement** - Integrate clarify, add issue creation
4. **Phase 4: New Commands** - Implement review, test, checkin commands
5. **Phase 5: Issue Templates** - Create Epic, Feature, Task templates
6. **Phase 6: Integration & Testing** - End-to-end workflow validation

## Next Steps

1. Generate `research.md` with dependency research and best practices
2. Generate `data-model.md` with entity definitions
3. Generate `contracts/` with command interface specifications
4. Generate `quickstart.md` with development setup guide
5. Run `/speckit.tasks` to generate implementation tasks
