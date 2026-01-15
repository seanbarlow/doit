# Project Roadmap

**Project**: Do-It
**Last Updated**: 2026-01-15
**Managed by**: `/doit.roadmapit`

## Vision

An AI-assisted spec-driven development CLI that streamlines the software development lifecycle through intelligent automation, from requirements gathering through implementation and testing.

---

## Active Requirements

### P1 - Critical (Must Have for MVP)

<!-- Items that are essential for minimum viable product or blocking other work -->

- [x] Core workflow commands (specit, planit, taskit, implementit, testit, reviewit, checkin)
  - **Rationale**: Complete spec-driven development workflow - foundation of the CLI

- [x] Multi-agent prompt synchronization (`sync-prompts` command)
  - **Rationale**: Enables consistent prompt files across Claude, Copilot, and other AI agents
  - **Feature**: `[023-copilot-prompts-sync]`

- [x] Unified template management (single source of truth for commands)
  - **Rationale**: Eliminates duplicate templates, simplifies maintenance
  - **Feature**: `[024-unified-templates]`

### P2 - High Priority (Significant Business Value)

<!-- Items with high business value, scheduled for near-term delivery -->

- [ ] Interactive guided workflows with validation
  - **Rationale**: Improves user experience by guiding through each command step-by-step

- [ ] Spec validation and linting
  - **Rationale**: Catches specification errors before implementation, enforces quality standards

- [x] Git hook integration for workflow enforcement
  - **Rationale**: Ensures team compliance with spec-first workflow via pre-commit/push hooks
  - **Feature**: `[025-git-hooks-workflow]`

- [ ] Cross-reference support between specs and tasks
  - **Rationale**: Maintains traceability from requirements through implementation

- [ ] Automatic Mermaid diagram generation from specs
  - **Rationale**: Aligns with constitution principle III - auto-generate architecture diagrams from specifications

- [x] AI context injection for commands
  - **Rationale**: Automatically inject relevant project context (constitution, roadmap, related specs) into command execution
  - **Feature**: `[027-template-context-injection]`

### P3 - Medium Priority (Valuable)

<!-- Items that add value but can wait for later iterations -->

- [ ] Spec analytics and metrics dashboard
  - **Rationale**: Provides insights on spec completion, cycle times, and team velocity

- [ ] Template versioning and update notifications
  - **Rationale**: Alerts users when command templates have newer versions available

- [ ] VS Code extension for doit commands
  - **Rationale**: Integrates workflow commands directly into the IDE

- [ ] Memory search and query across project context
  - **Rationale**: Enables finding relevant context in constitution, roadmap, completed specs

- [ ] Workflow checkpoint validation
  - **Rationale**: Validate each workflow step completes successfully before allowing the next step (enforces opinionated workflow)

### P4 - Low Priority (Nice to Have)

<!-- Items in the backlog, considered for future development -->

- [ ] Web dashboard for project visualization
  - **Rationale**: Visual representation of project architecture and progress

- [ ] Team collaboration features (shared memory, notifications)
  - **Rationale**: Enables multi-developer workflows with shared context

---

## Deferred Items

<!-- Items that were considered but intentionally deferred with reason -->

| Item                         | Original Priority | Deferred Date | Reason                                       |
|------------------------------|-------------------|---------------|----------------------------------------------|
| Task management app features | P1-P3             | 2026-01-15    | Vision pivot to spec-driven development CLI  |

---

## Notes

- Items marked with `[###-feature-name]` reference link to feature branches for tracking
- When a feature completes via `/doit.checkin`, matching items are moved to `completed_roadmap.md`
- Use `/doit.roadmapit add [item]` to add new items
- Use `/doit.roadmapit defer [item]` to move items to deferred section
- Use `/doit.roadmapit reprioritize` to change item priorities
