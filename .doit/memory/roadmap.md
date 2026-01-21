# Project Roadmap

**Project**: Do-It
**Last Updated**: 2026-01-22 (Updated: Promoted GitHub Milestone Generation to P3)
**Managed by**: `/doit.roadmapit`

## Vision

An AI-assisted spec-driven development CLI that streamlines the software development lifecycle through intelligent automation, from requirements gathering through implementation and testing.

---

## Active Requirements

### P1 - Critical (Must Have for MVP)

<!-- Items that are essential for minimum viable product or blocking other work -->

✅ **All P1 items completed!** See `.doit/memory/completed_roadmap.md` for history.

- [x] Bug-fix workflow command (`doit.fixit`)
  - **Rationale**: Provides structured bug-fix process integrated with GitHub issues - investigation plan, AI-assisted root cause analysis, fix planning, reuses existing reviewit/testit commands
  - **Feature**: `[034-fixit-workflow]` ✅ COMPLETED 2026-01-16

### P2 - High Priority (Significant Business Value)

<!-- Items with high business value, scheduled for near-term delivery -->

- [ ] GitHub epic and issue integration for roadmap command
  - **Rationale**: Unifies roadmap with GitHub tracking (keeps roadmap synchronized with GitHub epics/issues, reduces manual duplication, provides single source of truth), enables better project visibility (team members can see roadmap status through GitHub issues without accessing .doit files), automates roadmap maintenance (reduces manual effort by pulling GitHub epic/issue data automatically)
  - **Details**: When executing roadmapit command, check for open GitHub issues labeled as epics and any features attached to open epics; include them in the roadmap; ensure each roadmap item has a corresponding GitHub epic when GitHub is configured

---

**Completed P2 Items**: See `.doit/memory/completed_roadmap.md` for history.

### P3 - Medium Priority (Valuable)

<!-- Items that add value but can wait for later iterations -->

**Completed P3 Items**: See `.doit/memory/completed_roadmap.md` for history.

- [ ] Auto-create GitHub Epics from Roadmap Items
  - **Rationale**: Completes bi-directional sync - when adding roadmap items via `/doit.roadmapit add`, automatically creates corresponding GitHub epic with proper labels and description. Aligns with GitHub epic integration feature and AI-Native Design principle (automates manual work)

- [ ] GitHub Issue Auto-linking in Spec Creation
  - **Rationale**: When `/doit.specit` creates a new spec, automatically link it to the corresponding GitHub epic from the roadmap. Provides traceability from roadmap → spec → GitHub issue. Aligns with Persistent Memory principle (maintains links in markdown files)

- [ ] Roadmap Status Sync from GitHub
  - **Rationale**: Automatically update roadmap item status (pending/in-progress/completed) based on GitHub epic state. Reduces manual status updates and keeps roadmap current. Aligns with GitHub epic integration to automate maintenance overhead

- [ ] Batch command execution
  - **Rationale**: Run multiple specs through the workflow sequentially with a single command

- [ ] Spec dependencies graph
  - **Rationale**: Visualize spec dependencies to complement cross-references and Mermaid diagrams

- [ ] CLI plugin architecture
  - **Rationale**: Enable community extensions without core changes - prepares for VS Code extension

- [ ] Template versioning and update notifications
  - **Rationale**: Alerts users when command templates have newer versions available

- [ ] VS Code extension for doit commands
  - **Rationale**: Integrates workflow commands directly into the IDE

- [ ] Workflow checkpoint validation
  - **Rationale**: Validate each workflow step completes successfully before allowing the next step (enforces opinionated workflow)

- [ ] Hook configuration wizard
  - **Rationale**: Interactive wizard for customizing git hook validation rules (exempt branches, require artifacts)

- [ ] Hook bypass report in CI/CD
  - **Rationale**: Surface bypass events in GitHub Actions as PR check for team visibility into workflow compliance

- [ ] Template diff on version updates
  - **Rationale**: Show diff view when unified templates are updated to help users understand changes

- [ ] GitHub Milestone Generation from Priorities
  - **Rationale**: Automatically create GitHub milestones for each roadmap priority level (P1, P2, P3, P4) and assign epics to appropriate milestones. Provides GitHub-native view of roadmap priorities and enables team visibility through GitHub interface. Builds on recent GitHub integration momentum (039, 040).
  - **Why promoted from P4**: Completes the GitHub integration ecosystem started with epic sync and auto-linking. Natural next step to organize epics into milestones by priority.

### P4 - Low Priority (Nice to Have)

<!-- Items in the backlog, considered for future development -->

- [ ] GitHub Milestone Generation from Priorities
  - **Rationale**: Automatically create GitHub milestones for each roadmap priority level (P1, P2, P3, P4) and assign epics to appropriate milestones. Provides GitHub-native view of roadmap priorities and enables team visibility through GitHub interface

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
