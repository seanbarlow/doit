# User Stories: {FEATURE_NAME}

**Feature Branch**: `{BRANCH_NAME}`
**Created**: {DATE}
**Derived From**: [research.md](research.md)

## Overview

This document contains user stories derived from the research phase. Each story follows the Given/When/Then format and is linked to a specific persona.

## Personas Reference

Quick reference for personas defined in [research.md](research.md):

| Persona | Role | Primary Goal |
|---------|------|--------------|
| {Persona 1} | {Role} | {Goal} |
| {Persona 2} | {Role} | {Goal} |

---

## User Stories

### US-001: {Story Title} (P1)

**Persona**: {Persona Name}

**Story**: As a {persona}, I want to {action} so that {benefit}.

**Acceptance Scenarios**:

1. **Given** {initial context/state}
   **When** {action is taken}
   **Then** {expected outcome}

2. **Given** {alternative context}
   **When** {action is taken}
   **Then** {expected outcome}

**Notes**: {Any additional context or constraints}

---

### US-002: {Story Title} (P1)

**Persona**: {Persona Name}

**Story**: As a {persona}, I want to {action} so that {benefit}.

**Acceptance Scenarios**:

1. **Given** {initial context/state}
   **When** {action is taken}
   **Then** {expected outcome}

**Notes**: {Any additional context or constraints}

---

### US-003: {Story Title} (P2)

**Persona**: {Persona Name}

**Story**: As a {persona}, I want to {action} so that {benefit}.

**Acceptance Scenarios**:

1. **Given** {initial context/state}
   **When** {action is taken}
   **Then** {expected outcome}

**Notes**: {Any additional context or constraints}

---

## Story Map

### Priority 1 (Must-Have)

| ID | Story | Persona | Status |
|----|-------|---------|--------|
| US-001 | {Title} | {Persona} | Draft |
| US-002 | {Title} | {Persona} | Draft |

### Priority 2 (Nice-to-Have)

| ID | Story | Persona | Status |
|----|-------|---------|--------|
| US-003 | {Title} | {Persona} | Draft |

### Priority 3 (Future)

| ID | Story | Persona | Status |
|----|-------|---------|--------|
| US-004 | {Title} | {Persona} | Draft |

---

## Acceptance Criteria Checklist

For each user story, verify:

- [ ] Story follows "As a... I want... so that..." format
- [ ] Story is linked to a specific persona
- [ ] Story has at least one Given/When/Then scenario
- [ ] Story is testable and verifiable
- [ ] Story does not include implementation details
- [ ] Priority is assigned based on must-have vs. nice-to-have

---

## Traceability

### Requirements Coverage

| Requirement (from research.md) | Covered By Stories |
|-------------------------------|-------------------|
| {Must-have 1} | US-001, US-002 |
| {Must-have 2} | US-003 |
| {Nice-to-have 1} | US-004 |

### Uncovered Requirements

- {Any requirements from research that don't have stories yet}

---

## Next Steps

After user stories are complete:

1. Review stories with stakeholders
2. Refine acceptance scenarios
3. Run `/doit.specit` to create technical specification
