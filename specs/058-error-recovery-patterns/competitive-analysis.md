# Competitive Analysis: Error Recovery Patterns in All Commands

**Feature Branch**: `feature/058-error-recovery-patterns`
**Created**: 2026-03-26
**Derived From**: [research.md](research.md)

## Purpose

This document captures competitive landscape analysis for error recovery documentation patterns in developer workflow tools, to inform the design of doit's error recovery sections.

---

## Market Overview

### Problem Space

Developer workflow tools (CLI-based and AI-assisted) inevitably encounter errors — missing files, API failures, state corruption, and misconfiguration. The quality of error recovery documentation directly impacts developer productivity and tool adoption. Most tools handle the happy path well but diverge dramatically in how they guide users through failures.

### Target Segment

Developers and product owners using opinionated, multi-step workflow tools where errors in one step can cascade through subsequent steps.

---

## Identified Competitors

### Direct Competitors

Solutions that provide structured, multi-step developer workflows with documentation:

| Competitor | Type | Target Audience | Pricing Model |
|------------|------|-----------------|---------------|
| Nx (Monorepo) | CLI Tool | Monorepo developers | Free/Enterprise |
| Turborepo | CLI Tool | Monorepo developers | Free/Enterprise |
| Angular CLI | CLI Tool | Angular developers | Free |
| Rails Generators | CLI Framework | Rails developers | Free |
| GitHub Actions | CI/CD Platform | All developers | Free/Paid |

### Indirect Competitors

Alternative approaches to workflow error documentation:

| Alternative | Approach | Limitations |
|-------------|----------|-------------|
| Stack Overflow / forums | Community-sourced troubleshooting | Fragmented, not workflow-aware, may be outdated |
| AI chat (generic) | Ask ChatGPT/Claude for help | No project-specific context, may hallucinate recovery steps |
| Manual runbooks | Team-maintained recovery docs | Quickly become stale, not integrated into workflow |
| Trial and error | Developer guesses at recovery | Time-consuming, risks data loss, inconsistent results |

---

## Feature Comparison Matrix

Compare error recovery documentation patterns across tools:

### Core Features

| Feature | doit (Current) | doit (Planned) | Nx | Angular CLI | GitHub Actions |
|---------|---------------|----------------|-----|-------------|----------------|
| Structured error recovery docs | 1/13 commands | 13/13 commands | Partial | Yes | Yes |
| Command-specific error scenarios | Minimal | 3-5 per command | Yes | Yes | Yes |
| Recovery steps with commands | fixit only | All commands | Yes | Yes | Partial |
| State preservation guidance | No | Yes | N/A | N/A | Yes (re-run) |
| Escalation paths | fixit only | All commands | No | No | Partial |

### Extended Features

| Feature | doit (Current) | doit (Planned) | Nx | Angular CLI | GitHub Actions |
|---------|---------------|----------------|-----|-------------|----------------|
| Severity indicators | No | P2 | No | Yes (warnings/errors) | Yes (annotations) |
| Prevention tips | No | P2 | Partial | Yes | Partial |
| Diagnostic commands | No | P2 | Yes (`nx report`) | Yes (`ng version`) | Yes (`gh run view`) |
| AI-parseable format | No | P1 | No | No | No |
| Cross-command patterns | No | P3 | Partial | No | Yes (reusable workflows) |

### Legend

- **Yes**: Fully supports this feature
- **Partial**: Limited support or requires workaround
- **No**: Does not support
- **Planned**: In doit roadmap
- **N/A**: Not applicable to this tool

---

## Competitor Deep Dives

### Nx (Monorepo Tool)

**Type**: CLI tool for monorepo management

#### Strengths

- Comprehensive `nx report` diagnostic command that captures environment details for troubleshooting
- Detailed error messages with links to relevant documentation pages
- Community-driven troubleshooting recipes in official docs

#### Weaknesses

- Error recovery is scattered across docs — no single "Error Recovery" section per command
- Recovery steps often assume deep knowledge of the build graph
- No AI-parseable format for automated recovery

#### Key Takeaways

- **Diagnostic command pattern is valuable** — a single command that captures system state for troubleshooting
- **Linking errors to docs** is effective but requires maintaining those links

---

### Angular CLI

**Type**: CLI framework for Angular development

#### Strengths

- Error messages include error codes (e.g., NG0100) that link to specific documentation pages
- Each error code page includes: description, debugging steps, and common causes
- Warning vs. error severity distinction in output
- `ng version` provides quick environment diagnostics

#### Weaknesses

- Recovery guidance is in external docs, not in the CLI output or command templates
- No workflow state recovery — errors require full restart of the affected command
- Recovery steps don't account for partial completion

#### Key Takeaways

- **Error codes with linked documentation** is a mature, effective pattern
- **Severity indicators** (warning vs. error) help users prioritize
- doit can improve on Angular by embedding recovery in templates (where the AI reads them) rather than external docs

---

### GitHub Actions

**Type**: CI/CD workflow platform

#### Strengths

- Error annotations surface directly in the PR interface — high visibility
- Failed steps can be re-run individually without restarting the entire workflow
- Job-level granularity for recovery (re-run failed jobs only)
- Comprehensive troubleshooting docs organized by error category

#### Weaknesses

- Error recovery relies heavily on the web UI — not great for CLI users
- Limited guidance for "why did this fail" — often just the error output
- No prevention tips or root cause analysis in the workflow definition

#### Key Takeaways

- **Granular re-run capability** (individual steps/jobs) is analogous to doit's task-level state recovery
- doit should surface that `.doit/state/` enables similar granular recovery — this capability exists but isn't documented

---

## Differentiation Opportunities

Based on competitor analysis and user research, doit's opportunities to differentiate:

### Unique Value Propositions

1. **AI-first error recovery**: doit is unique in that AI assistants are a primary consumer of command templates. Structured, parseable error recovery sections enable autonomous error handling that no competitor offers.
   - Competitor gap: No competing tool designs error documentation for AI consumption
   - User need: P-003 (Agent Alex) needs structured instructions to handle errors without improvising

2. **Embedded recovery in workflow templates**: Unlike Angular (external docs) and GitHub Actions (web UI), doit embeds recovery guidance directly in the templates that the AI reads during execution — zero context-switching.
   - Competitor gap: Recovery guidance is separate from the execution context
   - User need: P-001 and P-003 need recovery steps available at the point of failure

3. **Workflow-aware state recovery**: doit already has state persistence with interrupted-state detection and backup/restore. Documenting this in templates makes it the only tool where multi-step workflow recovery is both implemented AND documented.
   - Competitor gap: Most tools require full restart on failure; GitHub Actions offers re-run but not state-aware recovery
   - User need: P-001 needs to know progress is preserved; P-002 needs reassurance work isn't lost

### Feature Gaps in Market

| Gap | User Need | Opportunity |
|-----|-----------|-------------|
| AI-parseable error recovery | AI assistants handling errors autonomously | Structured If/Then format in templates |
| Plain-language error summaries | Non-technical users understanding failures | Lead with summary, follow with technical steps |
| Integrated escalation criteria | Knowing when to recover vs. restart | Decision trees embedded in recovery sections |

### Areas to Avoid

- **Error code systems** (like Angular NG0100): Adds overhead for a CLI tool with 13 commands — not enough error surface to justify the infrastructure
- **External troubleshooting portals**: doit's strength is self-contained templates; moving recovery to external docs would fragment the experience

---

## Market Positioning

### Positioning Statement

For developers and product owners using SDD workflows who encounter errors that disrupt their progress, doit's error recovery documentation provides structured, AI-parseable recovery guidance embedded directly in command templates, unlike competing tools which scatter recovery guidance across external docs and require manual context-switching.

### Value Proposition Canvas

| Customer Jobs | Pains | Gains |
|---------------|-------|-------|
| Complete multi-step workflow | Errors with no recovery path → restart and rework | Structured recovery steps → resume in place |
| Use AI assistant for workflow | AI improvises on errors → inconsistent results | AI follows documented procedures → reliable recovery |
| Run research sessions (non-technical) | Technical errors are intimidating → need developer help | Plain-language guidance → self-service recovery |

### Win/Loss Factors

**Win Factors**:
- Only tool with AI-first error recovery documentation
- Recovery embedded at point of execution (not separate docs)
- State-aware recovery leveraging existing backup/restore infrastructure

**Potential Loss Factors**:
- Template-only solution — no runtime error detection or automated recovery
- Relies on AI assistants to read and follow structured text — quality depends on AI capability

---

## Recommendations for Specification

Based on competitive analysis, consider these for the specification phase:

### Must Address

Competitive table stakes — must have to be considered:

- Structured error recovery section in every command template (table stakes for any mature CLI tool)
- Command-specific error scenarios with actionable recovery steps (matches Angular CLI, Nx)
- Diagnostic guidance to help users capture system state (matches Nx `nx report` pattern)

### Should Differentiate

Where to focus for competitive advantage:

- AI-parseable format with consistent If/Then structure (unique differentiator)
- Embedded in templates at point of execution (better than external docs approach)
- Plain-language summaries before technical steps (serves non-technical users)
- State recovery guidance leveraging existing `.doit/state/` and backup infrastructure

### Consider Later

Competitive features that can wait:

- Error code system with linked documentation pages (Angular pattern — overkill for now)
- Shared error pattern reference file (P3 — evaluate after initial rollout)
- Runtime error detection and automated recovery suggestions (requires code changes)

---

## Research Sources

- Codebase analysis: `.doit/templates/commands/` (13 command templates)
- Reference implementation: `.doit/templates/commands/doit.fixit.md` (error recovery section)
- Roadmap: `.doit/memory/roadmap.md` (P2 item for error recovery patterns)
- Feature request: `docs/features/012-command-recommendations.md` (FR-006)
- Exception hierarchy: `src/doit_cli/services/providers/exceptions.py`, `src/doit_cli/models/team_errors.py`
- State management: `src/doit_cli/services/state_manager.py`
- Backup service: `src/doit_cli/services/backup_service.py`

---

## Next Steps

- [ ] Validate differentiators with stakeholder interviews
- [ ] Update requirements based on competitive insights
- [ ] Proceed to `/doit.specit` with competitive context
