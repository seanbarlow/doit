# Research: Error Recovery Patterns in All Commands

**Feature Branch**: `feature/058-error-recovery-patterns`
**Created**: 2026-03-26
**Status**: Draft

## Problem Statement

### Core Problem

Only 1 of 13 command templates (`doit.fixit.md`) has a structured `## Error Recovery` section. When users encounter failures during any workflow step, they lack documented guidance on how to diagnose, recover, and re-enter the workflow — leading to frustration, abandoned sessions, and lost work.

### Current State

- **fixit** is the only command with a comprehensive, structured error recovery section covering 5+ error types with numbered recovery steps and specific CLI commands
- **6 commands** (specit, planit, implementit, testit, reviewit, checkin) have minimal `### On Error` subsections buried at the end of "Next Steps" sections — these cover only 1-2 generic cases like "missing prerequisite file"
- **6 commands** (researchit, scaffoldit, documentit, constitution, roadmapit, taskit) have **zero** error handling guidance in their templates
- The codebase itself has **68 custom exception classes**, a **state persistence system** with interrupted-state recovery, and a **backup service** with restore capability — none of which are surfaced to users through template documentation
- Users encountering errors must either guess at recovery, abandon the workflow, or seek help externally

### Impact

- **Workflow abandonment**: Users who hit errors mid-workflow (e.g., during `implementit` or `taskit`) have no documented path to resume, leading to wasted effort and rework
- **State corruption**: Without recovery guidance, users may manually edit state files incorrectly, creating harder-to-fix problems
- **Reduced confidence**: The opinionated workflow (Constitution Principle IV) loses credibility when it can't handle its own failure modes gracefully
- **Support burden**: Questions about "what to do when X fails" become recurring issues rather than self-service answers
- **Inconsistent experience**: The stark quality gap between `fixit` (excellent recovery docs) and all other commands undermines the polished SDD experience

---

## Target Users

### Primary Personas

#### Developer (Solo/Team Lead)

- **Role**: Software developer using doit CLI to drive the SDD workflow from spec through implementation
- **Goals**: Complete the full workflow (spec → plan → task → implement → test → review → checkin) without interruption; quickly recover when things go wrong
- **Pain Points**: Encounters cryptic errors mid-workflow with no guidance; loses progress when forced to restart; doesn't know which state files to inspect or reset
- **Usage Context**: Daily development workflow; errors are most disruptive during implementation and testing phases where significant work has been invested

#### Product Owner (Non-Technical)

- **Role**: Stakeholder who uses research/spec phases to capture requirements; less comfortable with CLI tools
- **Goals**: Complete researchit and specit sessions without needing developer help; understand what went wrong in plain language
- **Pain Points**: Technical error messages are intimidating; doesn't know if an error means lost work or a simple retry; reluctant to experiment with recovery steps that might make things worse
- **Usage Context**: Weekly/bi-weekly research and specification sessions; errors during interactive Q&A sessions are especially frustrating because they interrupt creative flow

#### AI Assistant (Claude/Copilot Agent)

- **Role**: The AI executing doit commands via slash commands; relies on template instructions to handle errors
- **Goals**: Follow documented recovery procedures autonomously without needing to ask the user; maintain workflow continuity
- **Pain Points**: Without error recovery instructions in templates, must improvise recovery or escalate to user; inconsistent handling across commands; no standard format to parse
- **Usage Context**: Every command execution; the AI is the primary "reader" of command templates and needs structured, unambiguous recovery procedures

### User Goals

| Persona | Primary Goal | Secondary Goal |
|---------|--------------|----------------|
| Developer | Recover from errors quickly and resume workflow | Understand root causes to prevent recurrence |
| Product Owner | Know that work isn't lost when errors occur | Complete sessions without developer assistance |
| AI Assistant | Execute recovery steps autonomously | Provide clear error context to user when escalation is needed |

---

## Business Goals

### Primary Objectives

1. **Every command template has a structured `## Error Recovery` section** following the pattern established by `doit.fixit.md`
2. **Reduce workflow abandonment** by providing clear, actionable recovery steps for the most common failure modes per command
3. **Enable AI-driven recovery** by giving command templates enough structure for AI assistants to autonomously handle errors

### Success Definition

The SDD workflow handles failure as gracefully as it handles the happy path — users (human and AI) can recover from any documented error type without leaving the workflow or losing meaningful progress.

---

## Requirements

### Must-Have (P1)

1. **Standardized `## Error Recovery` section** added to all 13 command templates, positioned consistently (after main workflow steps, before "Next Steps")
2. **Command-specific error scenarios** covering the 3-5 most common failure modes per command (not generic — tailored to each command's unique failure points)
3. **Numbered recovery steps** with specific CLI commands where applicable (following the fixit pattern)
4. **State recovery guidance** for commands that use workflow state persistence (implementit, fixit, researchit)
5. **Escalation path** for each error scenario — when recovery isn't possible, what to do next (cancel, restart, seek help)

### Nice-to-Have (P2/P3)

1. **Error severity indicators** (WARNING vs ERROR vs FATAL) to help users gauge urgency
2. **Prevention tips** alongside recovery steps — "To avoid this in the future..."
3. **Cross-command error patterns** documented in a shared reference (e.g., "GitHub API errors" that apply to specit, checkin, fixit)
4. **Diagnostic commands** section — quick checks users can run to assess state before attempting recovery
5. **Recovery validation** — "After recovery, verify by running..." confirmation steps

### Out of Scope

- Changes to the Python codebase error handling (this is template/documentation only)
- New CLI commands for error recovery (e.g., `doit recover`)
- Automated error detection or self-healing mechanisms
- Error telemetry or analytics collection
- Changes to the state persistence format or backup service behavior

---

## Constraints

### Timeline

Low effort feature — roadmap classifies this as "low effort, high impact." Templates are markdown files requiring no code changes, testing, or build steps.

### Budget

No external costs. All work is documentation/template authoring.

### Compliance/Regulatory

N/A — internal documentation improvement.

### Dependencies

- **doit.fixit.md** serves as the reference implementation and pattern to follow
- Existing `### On Error` subsections in 6 templates should be migrated/expanded into the new `## Error Recovery` format
- No code dependencies — purely template changes

### Technical Constraints

- Templates must remain compatible with both Claude Code slash commands and GitHub Copilot prompt files
- Error recovery sections must be parseable by AI assistants — structured format with clear conditionals ("If [X] → then [Y]")
- Template file sizes should remain reasonable — error recovery adds ~40-80 lines per template

---

## Success Metrics

### Quantitative Measures

| Metric | Target | Measurement Method |
|--------|--------|-------------------|
| Templates with Error Recovery | 13/13 (100%) | File audit of `.doit/templates/commands/` |
| Error scenarios per template | 3-5 minimum | Manual review of each template |
| Recovery steps specificity | 100% include CLI commands | Template audit — no generic "fix and retry" steps |

### Qualitative Measures

- AI assistants can follow recovery procedures without improvising
- Users report feeling confident when encountering workflow errors
- Error recovery sections feel natural within the template flow (not bolted on)

### Failure Indicators

If we see these, the feature isn't meeting its goals:

- Users still asking "what do I do when X fails?" for documented error types
- AI assistants ignoring error recovery sections or generating their own conflicting guidance
- Error recovery sections become stale — describing scenarios that no longer apply to current code

---

## Open Questions

1. Should error recovery sections be identical in Claude Code commands (`.claude/commands/`) and Copilot prompts (`.github/prompts/`), or should they be tailored to each AI platform's capabilities?
2. Should there be a shared "Common Error Patterns" reference file that templates link to, or should each template be self-contained?
3. What is the right level of detail for Product Owners vs Developers — should recovery steps assume CLI proficiency?

---

## Research Session Notes

**Session Date**: 2026-03-26
**Conducted By**: AI Assistant
**Participant**: Product Owner (self-service research using existing project artifacts)

### Key Insights

- The codebase has **sophisticated error handling** (68 custom exceptions, state recovery, backup service) that is completely invisible to users through templates — this is a documentation gap, not a capability gap
- The `doit.fixit.md` template is an excellent reference implementation — its error recovery section covers 5 error types with specific commands and escalation paths
- 6 templates have embryonic `### On Error` sections that can be expanded rather than written from scratch
- Constitution Principle IV (Opinionated Workflow) implicitly requires error recovery — an opinionated workflow that doesn't handle its own failures breaks user trust
- The AI assistant persona is arguably the most important user — it reads templates literally and needs structured, unambiguous recovery instructions
- Feature docs/012-command-recommendations.md already identifies "FR-006: Error conditions provide recovery recommendations" as a desired feature

### Follow-Up Actions

- [ ] Review fixit.md error recovery section as the pattern template
- [ ] Inventory existing `### On Error` sections across 6 templates for migration
- [ ] Catalog the 3-5 most common error scenarios per command (from exception classes and service code)
- [ ] Determine whether shared error patterns warrant a reference file
- [ ] Proceed to specification phase
