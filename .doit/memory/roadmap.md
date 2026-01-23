# Project Roadmap

**Project**: Do-It
**Last Updated**: 2026-01-22 (Completed: GitLab git provider support)
**Managed by**: `/doit.roadmapit`

## Vision

An AI-assisted spec-driven development CLI that streamlines the software development lifecycle through intelligent automation, from requirements gathering through implementation and testing.

---

## Active Requirements

### P1 - Critical (Must Have for MVP)

<!-- Items that are essential for minimum viable product or blocking other work -->

✅ **All P1 items completed!** See `.doit/memory/completed_roadmap.md` for history.

### P2 - High Priority (Significant Business Value)

<!-- Items with high business value, scheduled for near-term delivery -->

✅ **All P2 items completed!** See `.doit/memory/completed_roadmap.md` for history.

### P3 - Medium Priority (Valuable)

<!-- Items that add value but can wait for later iterations -->

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

### P4 - Low Priority (Nice to Have)

<!-- Items in the backlog, considered for future development -->

- [ ] Web dashboard for project visualization
  - **Rationale**: Visual representation of project architecture and progress

---

## Deferred Items

<!-- Items that were considered but intentionally deferred with reason -->

| Item                         | Original Priority | Deferred Date | Reason                                       |
|------------------------------|-------------------|---------------|----------------------------------------------|
| Task management app features | P1-P3             | 2026-01-15    | Vision pivot to spec-driven development CLI  |

---

## Recent Releases

| Version | Date       | Key Changes                                                                         |
|---------|------------|-------------------------------------------------------------------------------------|
| v0.1.13 | 2026-01-22 | GitLab Git Provider Support - full REST API implementation, tutorials (#637)        |
| v0.1.12 | 2026-01-22 | Git provider configuration wizard - interactive setup for GitHub/ADO/GitLab (#636)  |
| v0.1.11 | 2026-01-22 | Fixed CLI ModuleNotFoundError - included `doit_toolkit_cli` in wheel package (#598) |

---

## Notes

- Items marked with `[###-feature-name]` reference link to feature branches for tracking
- When a feature completes via `/doit.checkin`, matching items are moved to `completed_roadmap.md`
- Use `/doit.roadmapit add [item]` to add new items
- Use `/doit.roadmapit defer [item]` to move items to deferred section
- Use `/doit.roadmapit reprioritize` to change item priorities
