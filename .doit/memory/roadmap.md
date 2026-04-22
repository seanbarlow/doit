# Project Roadmap

**Project**: Do-It
**Last Updated**: 2026-04-21
**Managed by**: `/doit.roadmapit`

## Vision

An AI-assisted spec-driven development CLI that streamlines the software development lifecycle through intelligent automation, from requirements gathering through implementation and testing.

---

## Active Requirements

<!-- [060] completed-items-hint START -->
<!-- Completed items from .doit/memory/completed_roadmap.md.
     Do not re-add unless there's a new change in scope. -->
<!--
  - [DONE] Personas.md migration (extends memory-file migrator pattern)
  - [DONE] Fix roadmap migrator H3 matching for decorated priority headings
  - [DONE] Memory files migration (roadmap.md, tech-stack.md)
  - [DONE] Constitution frontmatter migration
  - [DONE] Error recovery patterns in all commands
  - [DONE] Persona-aware user story generation
  - [DONE] Project-level personas with context injection
  - [DONE] MCP Server for doit Operations
  - [DONE] Research-to-Spec Auto-Pipeline
  - [DONE] Stakeholder Persona Templates
  - [DONE] Research command for Product Owners (`/doit.researchit`)
  - [DONE] macOS E2E testing infrastructure
  - [DONE] Windows E2E testing infrastructure
  - [DONE] GitLab git provider support
  - [DONE] Git provider configuration wizard
  - [DONE] Constitution and tech stack separation
  - [DONE] Azure DevOps git provider support
  - [DONE] Git provider abstraction layer
  - [DONE] Unified CLI package consolidation
  - [DONE] Team collaboration features (shared memory, notifications)
-->
<!-- [060] completed-items-hint END -->

### P1 - Critical (Must Have for MVP)

<!-- Items that are essential for minimum viable product or blocking other work -->

✅ **All P1 items completed!** See `.doit/memory/completed_roadmap.md` for history.

### P2 - High Priority (Significant Business Value)

<!-- Items with high business value, scheduled for near-term delivery -->

- [ ] GitHub Copilot Coding Agent support
  - **Rationale**: GitHub's Copilot coding agent can create PRs autonomously and supports MCP and custom agents. Add `.github/agents/` configuration for Copilot coding agent to use doit workflows. Competitive advantage with MCP server (`055-mcp-server`) already built
  - **Aligns with**: AI-Native Design principle (V), MCP server feature

### P3 - Medium Priority (Valuable)

<!-- Items that add value but can wait for later iterations -->

- [ ] Cross-platform CI & test infrastructure
  - **Rationale**: Expand GitHub Actions to run tests on Windows, Linux, and macOS in parallel with matrix strategy. Includes coverage reporting, performance benchmarking, and regression test suite across all platforms
  - **Aligns with**: Windows E2E CI/CD integration (US4), Cross-platform parity goals

- [ ] Workflow checkpoint validation
  - **Rationale**: Validate each workflow step completes successfully before allowing the next step (enforces opinionated workflow)
  - **Aligns with**: Opinionated Workflow principle (IV)

- [ ] Requirements Traceability Matrix
  - **Rationale**: Auto-generate traceability from research → spec → tasks → code. Track how business requirements flow through the entire workflow for audits, compliance, and ensuring nothing is lost
  - **Aligns with**: Cross-reference support (`033-spec-task-crossrefs`), researchit feature

- [ ] Remote triggers / scheduled agents
  - **Rationale**: Claude Code supports remote triggers that execute on cron schedules. Create triggers for automated spec validation, drift detection, or roadmap sync
  - **Aligns with**: CI/CD integration, workflow automation

- [ ] Batch command execution
  - **Rationale**: Run multiple specs through the workflow sequentially with a single command

- [ ] CLI plugin architecture
  - **Rationale**: Enable community extensions without core changes — prerequisite for VS Code extension and other integrations

- [ ] Template versioning and update notifications
  - **Rationale**: Alerts users when command templates have newer versions available

- [ ] Template diff on version updates
  - **Rationale**: Show diff view when unified templates are updated to help users understand changes

- [ ] Workflow analytics and cycle time tracking
  - **Rationale**: Measure how long each workflow phase takes (spec → plan → tasks → implement → test → checkin) across completed features. Surface bottlenecks and help prioritize process improvements using data from 33+ completed features
  - **Aligns with**: Spec analytics dashboard (`036-spec-analytics-dashboard`), AI-Native Design principle (V)

- [ ] `doit doctor` — project health check
  - **Rationale**: Single command that audits the entire project: validates constitution, checks roadmap staleness, runs context audit, verifies template versions, detects orphaned specs/branches, and reports overall health score
  - **Aligns with**: Workflow checkpoint validation (P3), Error recovery patterns (P2)

- [ ] Interactive onboarding for new projects (`doit quickstart`)
  - **Rationale**: Guided walkthrough of the first spec-plan-implement cycle for new projects. Walks users through constitution → first roadmap item → first spec → first plan to improve adoption
  - **Aligns with**: Opinionated Workflow principle (IV), community adoption goals

### P4 - Low Priority (Nice to Have)

<!-- Items in the backlog, considered for future development -->

- [ ] VS Code extension for doit commands
  - **Rationale**: Integrates workflow commands directly into the IDE. Depends on CLI plugin architecture (P3)
  - **Aligns with**: AI-Native Design principle (V)

- [ ] Research Version History
  - **Rationale**: Track iterations of research.md as understanding evolves. Requirements often change during discovery; version history shows how thinking evolved and supports "why" questions later
  - **Aligns with**: Persistent Memory principle (II), researchit feature

- [ ] Additional scaffolding templates (Rust, Kotlin, Swift, Next.js, Django)
  - **Rationale**: Expand language/framework coverage beyond current 8 templates
  - **Aligns with**: Community adoption, scaffoldit feature

- [ ] Persona impact analysis on roadmap changes
  - **Rationale**: When adding or reprioritizing roadmap items, show which personas are most affected by the change to help with prioritization decisions
  - **Aligns with**: Project-level personas feature, AI-Native Design principle (V)

- [ ] Context-aware persona refinement
  - **Rationale**: As features complete and research sessions accumulate, offer to refine `.doit/memory/personas.md` based on new learnings, keeping project personas current as understanding evolves
  - **Aligns with**: Research Version History (P4), Persistent Memory principle (II)

- [ ] Architecture Decision Records (ADRs)
  - **Rationale**: Document key design decisions (multi-provider abstraction, template vs MCP, skills architecture) in `docs/adr/`
  - **Aligns with**: Documentation quality, project governance

- [ ] Web dashboard for project visualization
  - **Rationale**: Visual representation of project architecture and progress

---

## Deferred Items

<!-- Items that were considered but intentionally deferred with reason -->

| Item                         | Original Priority | Deferred Date | Reason                                                      |
|------------------------------|-------------------|---------------|-------------------------------------------------------------|
| Task management app features | P1-P3             | 2026-01-15    | Vision pivot to spec-driven development CLI                 |
| Spec dependencies graph      | P3                | 2026-03-26    | Low demand; Mermaid diagrams cover most visualization needs  |
| Hook configuration wizard    | P3                | 2026-03-26    | Current YAML config is sufficient for hook customization     |
| Hook bypass report in CI/CD  | P3                | 2026-03-26    | Niche use case; can be added when specific need arises       |

---

## Recent Releases

| Version      | Date       | Key Changes                                                                                                           |
|--------------|------------|-----------------------------------------------------------------------------------------------------------------------|
| v0.3.0       | 2026-04-21 | Memory-file migration closure: constitution (#059), roadmap+tech-stack (#060), roadmap H3 fix (#061), personas (#062) |
| v0.2.0       | 2026-04-20 | Agent Skills template layout, native Copilot `.prompt.md` schema, `DoitError`/`ExitCode`/`format_option` foundation   |
| v0.1.17      | 2026-03-26 | MCP Server (#055), project-level personas (#056), persona-aware user stories (#057), error-recovery patterns (#058)   |
| v0.1.16      | 2026-01-30 | Windows symlink fix, researchit enhancements                                                                          |
| v0.1.15      | 2026-01-30 | Research command for product owners                                                                                   |
| v0.1.14      | 2026-01-27 | Windows E2E Testing - 146 tests, PowerShell 7.x, cross-platform parity, CI/CD (#645)                                  |

---

## Notes

- Items marked with `[###-feature-name]` reference link to feature branches for tracking
- When a feature completes via `/doit.checkin`, matching items are moved to `completed_roadmap.md`
- Use `/doit.roadmapit add [item]` to add new items
- Use `/doit.roadmapit defer [item]` to move items to deferred section
- Use `/doit.roadmapit reprioritize` to change item priorities
