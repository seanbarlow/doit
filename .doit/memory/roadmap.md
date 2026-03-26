# Project Roadmap

**Project**: Do-It
**Last Updated**: 2026-03-26
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

- [ ] Project-level personas in memory with context injection
  - **Rationale**: Generate `.doit/memory/personas.md` during roadmap creation using the existing persona-output-template. Add personas as a context source so `/doit.researchit`, `/doit.planit`, and `/doit.specit` automatically reference project personas, making every workflow session persona-aware
  - **Aligns with**: AI-Native Design principle (V), Persistent Memory principle (II), Stakeholder Persona Templates (`053-stakeholder-persona-templates`)

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

- [ ] Persona-aware user story generation
  - **Rationale**: When `/doit.specit` generates user stories, automatically map each story to the most relevant persona from `.doit/memory/personas.md` using existing P-NNN traceability IDs
  - **Aligns with**: Requirements Traceability Matrix (P3), Stakeholder Persona Templates (`053-stakeholder-persona-templates`)

- [ ] Requirements Traceability Matrix
  - **Rationale**: Auto-generate traceability from research → spec → tasks → code. Track how business requirements flow through the entire workflow for audits, compliance, and ensuring nothing is lost.
  - **Aligns with**: Cross-reference support (`033-spec-task-crossrefs`), researchit feature

- [ ] GitHub Copilot Coding Agent support
  - **Rationale**: GitHub's Copilot coding agent can create PRs autonomously and supports MCP and custom agents. Add `.github/agents/` configuration for Copilot coding agent to use doit workflows
  - **Aligns with**: AI integration strategy, MCP server feature

- [ ] Remote triggers / scheduled agents
  - **Rationale**: Claude Code supports remote triggers that execute on cron schedules. Create triggers for automated spec validation, drift detection, or roadmap sync
  - **Aligns with**: CI/CD integration, workflow automation

- [ ] Error recovery patterns in all commands
  - **Rationale**: Only some commands document what to do when things fail. Add structured `## Error Recovery` section to each command template
  - **Aligns with**: Documentation quality, user experience

### P4 - Low Priority (Nice to Have)

<!-- Items in the backlog, considered for future development -->

- [ ] Research Version History
  - **Rationale**: Track iterations of research.md as understanding evolves. Requirements often change during discovery; version history shows how thinking evolved and supports "why" questions later.
  - **Aligns with**: Persistent Memory principle, researchit feature

- [ ] Additional scaffolding templates (Rust, Kotlin, Swift, Next.js, Django)
  - **Rationale**: Expand language/framework coverage beyond current 8 templates
  - **Aligns with**: Community adoption, scaffoldit feature

- [ ] Persona impact analysis on roadmap changes
  - **Rationale**: When adding or reprioritizing roadmap items, show which personas are most affected by the change to help with prioritization decisions
  - **Aligns with**: Project-level personas feature, AI-Native Design principle

- [ ] Context-aware persona refinement
  - **Rationale**: As features complete and research sessions accumulate, offer to refine `.doit/memory/personas.md` based on new learnings, keeping project personas current as understanding evolves
  - **Aligns with**: Research Version History (P4), Persistent Memory principle

- [ ] Architecture Decision Records (ADRs)
  - **Rationale**: Document key design decisions (multi-provider abstraction, template vs MCP, skills architecture) in `docs/adr/`
  - **Aligns with**: Documentation quality, project governance

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
| v0.1.16 | 2026-01-30 | Windows symlink fix, researchit enhancements                                        |
| v0.1.15 | 2026-01-30 | Research command for product owners                                                 |
| v0.1.14 | 2026-01-27 | Windows E2E Testing - 146 tests, PowerShell 7.x, cross-platform parity, CI/CD (#645)|
| v0.1.13 | 2026-01-22 | GitLab Git Provider Support - full REST API implementation, tutorials (#637)        |
| v0.1.12 | 2026-01-22 | Git provider configuration wizard - interactive setup for GitHub/ADO/GitLab (#636)  |

---

## Notes

- Items marked with `[###-feature-name]` reference link to feature branches for tracking
- When a feature completes via `/doit.checkin`, matching items are moved to `completed_roadmap.md`
- Use `/doit.roadmapit add [item]` to add new items
- Use `/doit.roadmapit defer [item]` to move items to deferred section
- Use `/doit.roadmapit reprioritize` to change item priorities
