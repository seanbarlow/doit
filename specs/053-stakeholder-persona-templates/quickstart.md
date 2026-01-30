# Quickstart: Stakeholder Persona Templates

**Branch**: `053-stakeholder-persona-templates` | **Date**: 2026-01-30

## Overview

This feature adds a comprehensive persona template system to the `/doit.researchit` workflow. Implementation is template-only (no Python code).

## Prerequisites

- Access to `.doit/templates/` directory
- Access to `templates/commands/` directory

## Implementation Steps

### Step 1: Create persona-template.md

Create `.doit/templates/persona-template.md` with the comprehensive persona profile structure.

**Key sections**:
- Identity (name, role, archetype)
- Demographics (experience, team size)
- Goals (primary, secondary)
- Pain Points (prioritized list)
- Behavioral Patterns (tech proficiency, work style)
- Success Criteria
- Usage Context
- Relationships (to other personas)
- Conflicts & Tensions

### Step 2: Create personas-output-template.md

Create `.doit/templates/personas-output-template.md` defining the format for generated `personas.md` artifacts.

**Key sections**:
- Persona Summary table
- Detailed Profiles (one per persona)
- Relationship Map
- Conflicts & Tensions summary

### Step 3: Update doit.researchit.md

Modify `templates/commands/doit.researchit.md` to:

1. Add persona-specific questions in Phase 2 (Users and Goals)
2. Reference `persona-template.md` for field structure
3. Generate `personas.md` using `personas-output-template.md`

**Questions to add**:
- Technology proficiency level?
- Team size and work context?
- How do personas relate to each other?
- Any conflicting goals between personas?

### Step 4: Update doit.specit.md

Modify `templates/commands/doit.specit.md` to:

1. Check for `personas.md` in specs directory
2. Load persona IDs and names if found
3. Reference persona IDs in user story generation
4. Link each user story to a specific persona (e.g., `Persona: P-001`)

## Verification

After implementation, verify:

1. [ ] `persona-template.md` contains 10+ fields
2. [ ] `personas-output-template.md` includes summary table format
3. [ ] `/doit.researchit` asks enhanced persona questions
4. [ ] Generated `personas.md` includes unique IDs (P-001, P-002)
5. [ ] `/doit.specit` loads and references personas in user stories

## Example Usage

```bash
# Start research session with persona capture
/doit.researchit customer-portal

# Answer enhanced persona questions during Phase 2
# Artifacts generated include personas.md with full profiles

# Run spec generation (personas auto-loaded)
/doit.specit

# User stories reference persona IDs
# US-001: Persona: P-001 (Admin Alice)
```

## File Checklist

| File | Action | Status |
|------|--------|--------|
| `.doit/templates/persona-template.md` | Create | ☐ |
| `.doit/templates/personas-output-template.md` | Create | ☐ |
| `templates/commands/doit.researchit.md` | Update | ☐ |
| `templates/commands/doit.specit.md` | Update | ☐ |
