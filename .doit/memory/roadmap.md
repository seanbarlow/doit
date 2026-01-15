# Project Roadmap

**Project**: Do-It
**Last Updated**: 2026-01-15 (added template context injection)
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

- [ ] Template context injection (command-level integration)
  - **Rationale**: Add instructions to command templates to load project context via `doit context show`, completing the context injection workflow
  - **Related**: `[026-ai-context-injection]` infrastructure
  - **Approach**: Modify templates to include "Load project context" step that calls CLI before executing

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

- [ ] Spec status dashboard command (`doit status`)
  - **Rationale**: Shows all specs, their statuses, and validation readiness - helps developers see what's blocking commits

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

- [ ] Hook configuration wizard
  - **Rationale**: Interactive wizard for customizing git hook validation rules (exempt branches, require artifacts)

- [ ] Hook bypass report in CI/CD
  - **Rationale**: Surface bypass events in GitHub Actions as PR check for team visibility into workflow compliance

- [ ] Template diff on version updates
  - **Rationale**: Show diff view when unified templates are updated to help users understand changes

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
