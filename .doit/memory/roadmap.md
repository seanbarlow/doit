# Project Roadmap

**Project**: Do-It
**Last Updated**: 2026-01-29 (Added: Research command for Product Owners)
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

- [ ] Cross-platform CI matrix testing
  - **Rationale**: Expand GitHub Actions workflow to run tests on Windows, Linux, and macOS in parallel, ensuring comprehensive platform validation on every PR. Matrix strategy with parallel execution, unified reporting, and platform-specific artifact collection
  - **Aligns with**: Windows E2E CI/CD integration (US4), Cross-platform parity goals

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

- [ ] Test Coverage Reporting Dashboard
  - **Rationale**: Generate comprehensive test coverage reports showing which Windows-specific features, edge cases, and platform behaviors are tested. Includes line coverage, branch coverage, and platform-specific code path analysis with visual dashboards for tracking coverage trends over time
  - **Aligns with**: Windows E2E testing infrastructure (`049-e2e-windows-tests`), Test suite quality goals

- [ ] Performance Benchmarking Suite
  - **Rationale**: Automated performance testing to measure and track CLI command execution times, script performance, and resource usage across Windows/Linux/macOS. Establishes baseline metrics and detects performance regressions before they reach production
  - **Aligns with**: Cross-platform testing, CI/CD quality gates

- [ ] Automated Regression Test Suite
  - **Rationale**: Dedicated regression test suite that runs on every commit to catch platform-specific issues early. Includes tests for previously fixed bugs, edge cases, and critical user workflows to prevent feature breakage
  - **Aligns with**: Windows E2E testing (`049-e2e-windows-tests`), Continuous quality improvement

- [ ] Research-to-Spec Auto-Pipeline
  - **Rationale**: Automatic handoff from researchit → specit with context preservation. When research is complete, prompt to run `/doit.specit` with research artifacts pre-loaded.
  - **Aligns with**: Opinionated Workflow, researchit feature (`052-researchit-command`)

- [ ] Stakeholder Persona Templates
  - **Rationale**: Pre-built persona templates for common stakeholder types (end-user, admin, power-user). Helps Product Owners structure user research consistently with guided questions about goals, pain points, and success metrics.
  - **Aligns with**: researchit Q&A mode, user-stories.md output

- [ ] Requirements Traceability Matrix
  - **Rationale**: Auto-generate traceability from research → spec → tasks → code. Track how business requirements flow through the entire workflow for audits, compliance, and ensuring nothing is lost.
  - **Aligns with**: Cross-reference support (`033-spec-task-crossrefs`), researchit feature

### P4 - Low Priority (Nice to Have)

<!-- Items in the backlog, considered for future development -->

- [ ] Research Version History
  - **Rationale**: Track iterations of research.md as understanding evolves. Requirements often change during discovery; version history shows how thinking evolved and supports "why" questions later.
  - **Aligns with**: Persistent Memory principle, researchit feature

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
| v0.1.14 | 2026-01-27 | Windows E2E Testing - 146 tests, PowerShell 7.x, cross-platform parity, CI/CD (#645) |
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
