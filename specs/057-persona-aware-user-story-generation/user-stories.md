# User Stories: Persona-Aware User Story Generation

**Feature Branch**: `057-persona-aware-user-story-generation`
**Created**: 2026-03-26
**Derived From**: [research.md](research.md)

## Overview

This document contains user stories derived from the research phase. Each story follows the Given/When/Then format and is linked to a specific persona.

## Personas Reference

Quick reference for personas defined in [personas.md](personas.md):

| Persona | Role | Primary Goal |
|---------|------|--------------|
| P-001 (Product Owner) | Product Owner / Requirements Lead | Auto-tagged stories with correct persona IDs |
| P-002 (Developer) | Software Developer | Clear persona context per story |
| P-003 (AI Assistant) | AI Coding Assistant | Deterministic matching rules for mapping |

---

## User Stories

### US-001: Auto-Map Stories to Personas During Spec Generation (P1)

**Persona**: P-001 (Product Owner), P-003 (AI Assistant)

**Story**: As a Product Owner, I want `/doit.specit` to automatically tag each generated user story with the most relevant persona ID so that I don't need to manually cross-reference and map stories to personas.

**Acceptance Scenarios**:

1. **Given** personas are defined in `.doit/memory/personas.md` or `specs/{feature}/personas.md`
   **When** `/doit.specit` generates user stories
   **Then** each story includes a `**Persona**: P-NNN (Name)` field linking it to the most relevant persona

2. **Given** both project-level and feature-level personas exist
   **When** `/doit.specit` generates user stories
   **Then** feature-level personas take precedence over project-level personas (per spec 056 R-003)

3. **Given** personas are defined with goals, pain points, and usage context
   **When** the AI assistant matches a story to a persona
   **Then** the match is based on alignment between the story's intent and the persona's goals and pain points

**Notes**: This is the core capability — the mapping engine that powers the persona pipeline completion.

---

### US-002: View Persona Context in Generated Stories (P1)

**Persona**: P-002 (Developer)

**Story**: As a Developer, I want each user story in the generated spec to show which persona it serves so that I can understand the user context without cross-referencing separate files.

**Acceptance Scenarios**:

1. **Given** a generated `user-stories.md` with persona mappings
   **When** a Developer reads a user story
   **Then** the persona ID and name are visible directly in the story header

2. **Given** a user story mapped to persona P-001
   **When** a Developer wants more persona detail
   **Then** the persona ID links back to the full profile in `personas.md`

**Notes**: The Developer is a consumer of this feature's output — the story format must be immediately informative.

---

### US-003: Update Traceability Table After Story Generation (P1)

**Persona**: P-001 (Product Owner)

**Story**: As a Product Owner, I want the traceability table in `personas.md` to be automatically updated after `/doit.specit` runs so that I can see persona-to-story coverage at a glance.

**Acceptance Scenarios**:

1. **Given** `/doit.specit` has generated user stories with persona mappings
   **When** the generation completes
   **Then** the Traceability → Persona Coverage table in `personas.md` is updated with story IDs per persona

2. **Given** a persona with no stories mapped to it
   **When** the traceability table is updated
   **Then** the persona appears in the table with an empty "User Stories Addressing" column, signaling a coverage gap

**Notes**: This closes the traceability loop — personas.md shows which stories serve each persona, and user-stories.md shows which persona each story serves.

---

### US-004: Graceful Fallback When No Personas Exist (P1)

**Persona**: P-003 (AI Assistant)

**Story**: As an AI Assistant executing `/doit.specit`, I want clear fallback behavior when no personas are available so that the workflow doesn't break for projects that haven't defined personas.

**Acceptance Scenarios**:

1. **Given** no `.doit/memory/personas.md` and no `specs/{feature}/personas.md` exist
   **When** `/doit.specit` generates user stories
   **Then** stories are generated without persona mappings (existing behavior preserved)

2. **Given** a `personas.md` file exists but contains no valid persona entries
   **When** `/doit.specit` generates user stories
   **Then** stories are generated without persona mappings and no error is raised

**Notes**: Backward compatibility is non-negotiable. This ensures the feature is additive, not breaking.

---

### US-005: Read Personas from Existing Sources (P1)

**Persona**: P-001 (Product Owner), P-003 (AI Assistant)

**Story**: As a Product Owner, I want the mapping to use personas already defined in my project so that I don't need to redefine them for each feature.

**Acceptance Scenarios**:

1. **Given** project-level personas exist in `.doit/memory/personas.md`
   **When** `/doit.specit` runs for any feature
   **Then** the project-level personas are available for story mapping

2. **Given** feature-level personas exist in `specs/{feature}/personas.md`
   **When** `/doit.specit` runs for that feature
   **Then** feature-level personas are used, overriding project-level personas

3. **Given** personas loaded via the context system (spec 056)
   **When** `/doit.specit` generates stories
   **Then** the same loaded persona context is used for mapping (no duplicate file reads)

**Notes**: Leverages the persona context injection from spec 056 — no new file loading mechanism needed.

---

### US-006: Multi-Persona Story Support (P2)

**Persona**: P-001 (Product Owner)

**Story**: As a Product Owner, I want to optionally tag a user story with multiple persona IDs when it genuinely serves more than one persona so that cross-cutting concerns are properly represented.

**Acceptance Scenarios**:

1. **Given** a user story that serves both P-001 and P-002
   **When** the AI assistant maps the story
   **Then** the story's Persona field lists both: `**Persona**: P-001 (Product Owner), P-002 (Developer)`

2. **Given** a multi-persona story
   **When** the traceability table is updated
   **Then** the story ID appears in the row for each mapped persona

**Notes**: P2 nice-to-have. Default behavior (P1) is 1:1 mapping with primary persona only.

---

### US-007: Persona Coverage Report (P2)

**Persona**: P-001 (Product Owner)

**Story**: As a Product Owner, I want a coverage summary after story generation showing which personas are well-served and which are underserved so that I can identify gaps in my requirements.

**Acceptance Scenarios**:

1. **Given** `/doit.specit` has completed story generation with persona mappings
   **When** the generation summary is displayed
   **Then** a coverage report shows each persona and the number of stories mapped to them

2. **Given** a persona with zero stories mapped
   **When** the coverage report is displayed
   **Then** the persona is flagged as "underserved" with a warning

**Notes**: P2 nice-to-have. Provides immediate feedback to the Product Owner about coverage gaps.

---

### US-008: Confidence Scoring for Mappings (P3)

**Persona**: P-003 (AI Assistant)

**Story**: As an AI Assistant, I want to indicate confidence level when mapping a story to a persona so that the Product Owner can prioritize which mappings to review.

**Acceptance Scenarios**:

1. **Given** a story with a clear match to a single persona's goals
   **When** the mapping is made
   **Then** the confidence is marked as "High"

2. **Given** a story that could plausibly match multiple personas
   **When** the mapping is made to the best-fit persona
   **Then** the confidence is marked as "Medium" with a note about alternative personas

**Notes**: P3 future enhancement. Helps Product Owners focus review effort on uncertain mappings.

---

## Story Map

### Priority 1 (Must-Have)

| ID | Story | Persona | Status |
|----|-------|---------|--------|
| US-001 | Auto-map stories to personas during spec generation | P-001, P-003 | Draft |
| US-002 | View persona context in generated stories | P-002 | Draft |
| US-003 | Update traceability table after story generation | P-001 | Draft |
| US-004 | Graceful fallback when no personas exist | P-003 | Draft |
| US-005 | Read personas from existing sources | P-001, P-003 | Draft |

### Priority 2 (Nice-to-Have)

| ID | Story | Persona | Status |
|----|-------|---------|--------|
| US-006 | Multi-persona story support | P-001 | Draft |
| US-007 | Persona coverage report | P-001 | Draft |

### Priority 3 (Future)

| ID | Story | Persona | Status |
|----|-------|---------|--------|
| US-008 | Confidence scoring for mappings | P-003 | Draft |

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
| Auto-map user stories to personas | US-001 |
| Use existing persona sources with precedence | US-005 |
| Maintain traceability | US-002, US-003 |
| Graceful fallback when no personas exist | US-004 |
| Update traceability section in personas.md | US-003 |
| Multi-persona stories (P2) | US-006 |
| Persona coverage report (P2) | US-007 |
| Confidence scoring (P3) | US-008 |

### Uncovered Requirements

- Interactive override (P2 nice-to-have) — deferred, may be addressed in a future spec

---

## Next Steps

After user stories are complete:

1. Review stories with stakeholders
2. Refine acceptance scenarios
3. Run `/doit.specit` to create technical specification
