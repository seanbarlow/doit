# Research: Persona-Aware User Story Generation

**Feature Branch**: `057-persona-aware-user-story-generation`
**Created**: 2026-03-26
**Status**: Draft

## Problem Statement

### Core Problem

When `/doit.specit` generates user stories, there is no automatic mapping between stories and the personas defined in `.doit/memory/personas.md` or `specs/{feature}/personas.md`. Users must manually cross-reference persona IDs (P-NNN) when writing stories, which is error-prone and breaks the traceability chain from persona → user story → spec → implementation.

### Current State

Currently, spec 056 injects persona context into `/doit.specit`, but the actual story-to-persona mapping is manual. Users either:

1. Manually add persona IDs (P-NNN) to user stories after generation
2. Skip the mapping entirely, breaking the traceability chain
3. Rely on the AI assistant to infer mappings without structured guidance, leading to inconsistent results

### Impact

Without automatic mapping, the persona pipeline established by specs 053 (Stakeholder Persona Templates) and 056 (Project-Level Personas with Context Injection) remains incomplete. The traceability chain breaks at the story generation step, reducing the value of persona definitions and making it harder for developers to understand who they're building for.

---

## Target Users

### Primary Personas

#### Product Owner (P-001)

- **Role**: Product Owner / Requirements Lead
- **Goals**: Every generated user story automatically tagged with the correct persona ID — no manual fixup needed
- **Pain Points**: Manual persona-to-story mapping is tedious, error-prone, and leads to inconsistent traceability
- **Usage Context**: During the `/doit.specit` phase, after completing `/doit.researchit`. Expects personas to carry forward into user stories automatically.

#### Developer (P-002)

- **Role**: Software Developer
- **Goals**: Instantly see which persona each story serves, enabling targeted implementation decisions
- **Pain Points**: Stories without persona context lack clarity on who they're building for; must cross-reference separate files
- **Usage Context**: When reading generated specs and `user-stories.md` during `/doit.planit` and `/doit.implementit`.

#### AI Assistant (P-003)

- **Role**: AI Coding Assistant (Claude/Copilot)
- **Goals**: Clear matching rules to deterministically map stories to personas based on goals, pain points, and context
- **Pain Points**: No structured rules for matching — relies on inference with no fallback behavior defined
- **Usage Context**: At execution time of `/doit.specit`, when generating user stories from research artifacts.

### User Goals

| Persona | Primary Goal | Secondary Goal |
|---------|--------------|----------------|
| P-001 (Product Owner) | Auto-tagged stories with correct persona IDs | Ability to review/override mappings |
| P-002 (Developer) | Clear persona context per story | Traceability from story back to persona pain points |
| P-003 (AI Assistant) | Deterministic matching rules | Graceful handling of missing/ambiguous personas |

---

## Business Goals

### Primary Objectives

1. Complete the persona pipeline: persona definition → context injection → story mapping → implementation traceability
2. Eliminate manual persona-to-story mapping effort during spec creation
3. Ensure every generated user story is traceable to at least one defined persona

### Success Definition

The feature is successful when `/doit.specit` automatically produces user stories with correct P-NNN persona mappings, maintaining full traceability from persona through to implementation without manual intervention.

---

## Requirements

### Must-Have (P1)

These are non-negotiable requirements for the feature to deliver value:

1. Auto-map user stories to personas: When `/doit.specit` generates stories, each story must be tagged with the most relevant P-NNN ID from available personas
2. Use existing persona sources: Read from `.doit/memory/personas.md` (project-level) and `specs/{feature}/personas.md` (feature-level), respecting the precedence rules from spec 056
3. Maintain traceability: Generated `user-stories.md` must include persona ID references that link back to persona profiles
4. Graceful fallback: If no personas exist, generate stories without persona mapping (don't break the workflow)
5. Update the Traceability section in `personas.md` with the story-to-persona coverage table

### Nice-to-Have (P2/P3)

These enhance the feature but aren't required for initial release:

1. Multi-persona stories: Support tagging a single story with multiple persona IDs when it genuinely serves more than one persona
2. Persona coverage report: After generation, show which personas have stories and which are underserved
3. Confidence scoring: Indicate how strongly a story maps to a persona (high/medium/low match)
4. Interactive override: Allow the Product Owner to review and adjust mappings before finalizing

### Out of Scope

These are explicitly NOT part of this feature:

- Creating new personas — this feature maps to existing personas only (persona generation is `/doit.roadmapit`'s responsibility per spec 056)
- Requiring personas to function — `/doit.specit` must still work without personas (backward compatible)

---

## Constraints

### Dependencies

- **Spec 056** (persona-context-injection): Must be complete — provides the context loading mechanism for personas. Status: Complete (merged in commit 137e30e).
- **Spec 053** (stakeholder-persona-templates): Defines the P-NNN format and comprehensive persona structure used for matching.

### Technical Constraints

- Changes should follow the 056 pattern — template/prompt updates only, no new Python modules (per R-005 from spec 056)
- Must work with both project-level (`.doit/memory/personas.md`) and feature-level (`specs/{feature}/personas.md`) persona sources
- Feature-level personas take precedence over project-level (per R-003 from spec 056)

---

## Success Metrics

### Quantitative Measures

| Metric | Target | Measurement Method |
|--------|--------|-------------------|
| Auto-mapping rate | 100% of stories mapped when personas available | Count stories with P-NNN IDs vs total stories |
| Persona coverage | 100% of personas have ≥1 story | Check traceability table completeness |
| Traceability completeness | Personas.md traceability table auto-populated | Verify table exists after specit run |
| Workflow regression | 0 failures without personas | Run specit without personas.md present |

### Qualitative Measures

- Product Owners report no manual persona tagging needed
- Developers find persona context immediately useful in generated stories

### Failure Indicators

If we see these, the feature isn't meeting its goals:

- Stories consistently mapped to the wrong persona, requiring manual correction
- Stories generated without persona IDs despite personas being available
- `/doit.specit` fails or errors when personas are missing or malformed
- Personas exist with zero stories mapped, indicating matching logic missed them

---

## Open Questions

1. What matching algorithm should the AI use to determine the "most relevant" persona for a story — keyword matching on goals/pain points, or semantic similarity?
2. How should multi-persona stories be formatted in the user-stories.md template (for the P2 nice-to-have)?
3. Should the traceability table update in personas.md be append-only or full replacement on each specit run?

---

## Research Session Notes

**Session Date**: 2026-03-26
**Conducted By**: AI Assistant
**Participant**: Product Owner

### Key Insights

- This feature is the natural completion of the persona pipeline started by specs 053 and 056
- All three persona types (Product Owner, Developer, AI Assistant) benefit from automatic mapping
- The primary tension is between multi-persona richness (P-001 wants) and deterministic 1:1 mapping (P-003 needs)
- Template-only changes align with the established pattern from spec 056

### Follow-Up Actions

- [ ] Define matching rules for persona-to-story mapping in the specification
- [ ] Determine traceability table update strategy (append vs replace)
- [ ] Design fallback behavior for edge cases (no personas, ambiguous matches)
