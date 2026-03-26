# User Stories: Error Recovery Patterns in All Commands

**Feature Branch**: `feature/058-error-recovery-patterns`
**Created**: 2026-03-26
**Derived From**: [research.md](research.md)

## Overview

This document contains user stories derived from the research phase. Each story follows the Given/When/Then format and is linked to a specific persona.

## Personas Reference

Quick reference for personas defined in [research.md](research.md):

| Persona | Role | Primary Goal |
|---------|------|--------------|
| P-001: Dev Dana | Software Developer / Team Lead | Recover quickly and resume workflow |
| P-002: PO Pat | Product Owner | Complete sessions without developer help |
| P-003: Agent Alex | AI Assistant | Execute recovery autonomously from templates |

---

## User Stories

### US-001: Recover from mid-workflow errors using documented steps (P1) | Persona: P-001

**Persona**: Dev Dana (P-001) — Power User

**Story**: As a developer running the SDD workflow, I want each command template to include structured error recovery steps so that I can quickly resolve failures and resume work without restarting from scratch.

**Acceptance Scenarios**:

1. **Given** I am executing `implementit` and a task fails due to a missing dependency
   **When** I consult the error recovery section of the implementit template
   **Then** I find numbered steps specific to dependency failures, including diagnostic commands and recovery actions

2. **Given** I am running `testit` and the test framework is not detected
   **When** I look at the error recovery section of the testit template
   **Then** I find steps to verify framework installation, configure detection, and retry — not just "fix and retry"

3. **Given** I encounter an error in `checkin` because a GitHub API call fails
   **When** I check the error recovery section
   **Then** I find steps to diagnose authentication issues, retry with backoff, or complete the checkin manually

**Notes**: Recovery steps must include specific CLI commands (e.g., `doit status`, `git status`, `ls .doit/state/`) — not generic instructions.

---

### US-002: Understand error impact on work-in-progress (P1) | Persona: P-001

**Persona**: Dev Dana (P-001) — Power User

**Story**: As a developer who has invested significant work in a workflow session, I want error recovery sections to clearly indicate whether my progress is preserved so that I can make informed decisions about recovery vs. restart.

**Acceptance Scenarios**:

1. **Given** an error occurs during `implementit` after 5 of 8 tasks are completed
   **When** I read the error recovery section
   **Then** I understand that completed tasks are preserved in `.doit/state/` and only the failed task needs to be retried

2. **Given** a state file becomes corrupted during `researchit`
   **When** I consult the error recovery section
   **Then** I find steps to inspect the draft file (`.research-draft.md`), understand what's recoverable, and resume from the last good state

**Notes**: Each error scenario should state explicitly: "Your progress IS/IS NOT preserved."

---

### US-003: Get plain-language error guidance during research sessions (P1) | Persona: P-002

**Persona**: PO Pat (P-002) — Casual User

**Story**: As a product owner conducting a research session, I want error messages and recovery guidance to be written in plain language so that I can resolve issues without needing a developer's help.

**Acceptance Scenarios**:

1. **Given** I am in the middle of a `researchit` Q&A session and an error occurs
   **When** the AI assistant reads the error recovery section
   **Then** it explains what happened in non-technical terms and offers safe recovery options (e.g., "Your answers are saved. We can continue from where we left off.")

2. **Given** I am running `specit` and file creation fails due to permissions
   **When** the error recovery section is consulted
   **Then** the guidance starts with a plain summary ("The specification file couldn't be saved") before providing technical steps

**Notes**: Error recovery sections should lead with a one-sentence plain-language summary before diving into technical recovery steps.

---

### US-004: Follow structured recovery procedures autonomously (P1) | Persona: P-003

**Persona**: Agent Alex (P-003) — Power User

**Story**: As an AI assistant executing doit commands, I want error recovery sections in every template to use a consistent, structured format so that I can parse and follow recovery procedures without improvising.

**Acceptance Scenarios**:

1. **Given** I encounter an error while executing any doit command
   **When** I read the template's `## Error Recovery` section
   **Then** I find structured subsections with "If [condition] → then [numbered steps]" format that I can follow programmatically

2. **Given** an error occurs that I cannot recover from autonomously
   **When** the error recovery section includes escalation criteria
   **Then** I can clearly determine when to stop attempting recovery and inform the user, including what information to report

3. **Given** I am executing `planit` and the prerequisite `spec.md` is missing
   **When** I consult the error recovery section
   **Then** I find specific guidance: check if spec exists, suggest running specit first, or help locate a misnamed spec file — rather than a generic "On Error: missing spec.md"

**Notes**: Consistent format across all 13 templates is critical for AI parsing. The fixit template's pattern (subsection per error type, numbered steps, specific commands) should be the standard.

---

### US-005: Migrate existing On Error subsections to full Error Recovery (P1) | Persona: P-003

**Persona**: Agent Alex (P-003) — Power User

**Story**: As an AI assistant, I want the existing `### On Error` subsections in 6 templates to be expanded and standardized into `## Error Recovery` sections so that error handling is consistent across all commands.

**Acceptance Scenarios**:

1. **Given** I am executing `specit` which currently has a minimal `### On Error` subsection
   **When** the template is updated with a full `## Error Recovery` section
   **Then** the new section covers at least 3 error scenarios (not just "missing spec.md") including branch creation failures, GitHub API errors, and input validation issues

2. **Given** I am executing any of the 13 commands
   **When** I look for error recovery guidance
   **Then** I find it in the same location (`## Error Recovery` as a top-level section) with the same format in every template

**Notes**: Existing `### On Error` content should be preserved and expanded, not discarded.

---

### US-006: Know when to recover vs. restart (P2) | Persona: P-001

**Persona**: Dev Dana (P-001) — Power User

**Story**: As a developer encountering a workflow error, I want error recovery sections to include severity indicators so that I can quickly decide whether to attempt recovery or start fresh.

**Acceptance Scenarios**:

1. **Given** a state corruption error occurs during `implementit`
   **When** I read the error recovery section
   **Then** I see a severity indicator (e.g., WARNING, ERROR, FATAL) that tells me this is recoverable with specific steps

2. **Given** a fundamental prerequisite is missing (e.g., no git repo, no `.doit/` directory)
   **When** I read the error recovery section
   **Then** I see a FATAL indicator suggesting I need to reinitialize rather than attempt in-place recovery

**Notes**: Nice-to-have enhancement. Could be implemented as simple text labels or emoji indicators.

---

### US-007: Prevent recurring errors with tips (P2) | Persona: P-001

**Persona**: Dev Dana (P-001) — Power User

**Story**: As a developer who has recovered from an error, I want prevention tips alongside recovery steps so that I can avoid hitting the same issue again.

**Acceptance Scenarios**:

1. **Given** I have recovered from a GitHub authentication error during `checkin`
   **When** I read the recovery steps
   **Then** I also find a "To avoid this in the future" tip suggesting to verify `gh auth status` before starting the checkin workflow

**Notes**: Nice-to-have. One-liner tips, not extensive documentation.

---

### US-008: Verify recovery was successful (P2) | Persona: P-001

**Persona**: Dev Dana (P-001) — Power User

**Story**: As a developer who has followed recovery steps, I want a verification step at the end so that I can confirm the error is resolved before continuing the workflow.

**Acceptance Scenarios**:

1. **Given** I have followed recovery steps for a state file issue in `implementit`
   **When** I reach the end of the recovery procedure
   **Then** I find a "Verify recovery" step with a specific command (e.g., `doit status` or `ls .doit/state/`) that confirms the workflow can resume

**Notes**: Nice-to-have. Simple verification commands, not elaborate test suites.

---

### US-009: Access common error patterns across commands (P3) | Persona: P-003

**Persona**: Agent Alex (P-003) — Power User

**Story**: As an AI assistant, I want common error patterns (GitHub API failures, git conflicts, file permission errors) to be documented in a shared reference so that I don't need to find the same guidance repeated in 13 different templates.

**Acceptance Scenarios**:

1. **Given** a GitHub API rate limit error occurs in any command that uses GitHub
   **When** the template references a common error pattern
   **Then** I find consistent guidance regardless of which command I'm executing

**Notes**: Future enhancement. Could be a shared `error-patterns.md` reference file linked from individual templates.

---

## Story Map

### Priority 1 (Must-Have)

| ID | Story | Persona | Status |
|----|-------|---------|--------|
| US-001 | Recover from mid-workflow errors using documented steps | P-001: Dev Dana | Draft |
| US-002 | Understand error impact on work-in-progress | P-001: Dev Dana | Draft |
| US-003 | Get plain-language error guidance during research sessions | P-002: PO Pat | Draft |
| US-004 | Follow structured recovery procedures autonomously | P-003: Agent Alex | Draft |
| US-005 | Migrate existing On Error subsections to full Error Recovery | P-003: Agent Alex | Draft |

### Priority 2 (Nice-to-Have)

| ID | Story | Persona | Status |
|----|-------|---------|--------|
| US-006 | Know when to recover vs. restart | P-001: Dev Dana | Draft |
| US-007 | Prevent recurring errors with tips | P-001: Dev Dana | Draft |
| US-008 | Verify recovery was successful | P-001: Dev Dana | Draft |

### Priority 3 (Future)

| ID | Story | Persona | Status |
|----|-------|---------|--------|
| US-009 | Access common error patterns across commands | P-003: Agent Alex | Draft |

---

## Acceptance Criteria Checklist

For each user story, verify:

- [x] Story follows "As a... I want... so that..." format
- [x] Story is linked to a specific persona
- [x] Story has at least one Given/When/Then scenario
- [x] Story is testable and verifiable
- [x] Story does not include implementation details
- [x] Priority is assigned based on must-have vs. nice-to-have

---

## Traceability

### Requirements Coverage

| Requirement (from research.md) | Covered By Stories |
|-------------------------------|-------------------|
| Standardized `## Error Recovery` section in all 13 templates | US-001, US-004, US-005 |
| Command-specific error scenarios (3-5 per command) | US-001, US-005 |
| Numbered recovery steps with specific CLI commands | US-001, US-004 |
| State recovery guidance for stateful commands | US-002 |
| Escalation path for each error scenario | US-004 |
| Error severity indicators (P2) | US-006 |
| Prevention tips alongside recovery steps (P2) | US-007 |
| Cross-command error patterns reference (P2) | US-009 |
| Diagnostic commands section (P2) | US-008 |
| Recovery validation steps (P2) | US-008 |

### Uncovered Requirements

- None — all must-have and nice-to-have requirements are covered by at least one story

---

## Next Steps

After user stories are complete:

1. Review stories with stakeholders
2. Refine acceptance scenarios
3. Run `/doit.specit` to create technical specification
