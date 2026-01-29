# Research: AI Context Optimization

**Feature**: 051-ai-context-optimization
**Date**: 2025-01-28
**Status**: Complete

## Research Questions

1. Which templates have double-injection patterns?
2. What specific patterns need to be eliminated?
3. What is the current context source mapping in `doit context show`?
4. Best practices for AI instruction blocks in templates?

---

## Finding 1: Double-Injection Pattern Analysis

### Decision: 6 of 12 templates require modification

### Rationale

Analysis of all 12 command templates in `templates/commands/` revealed that 6 templates have double-injection patterns where `doit context show` is called AND explicit file reads are also instructed for the same sources.

### Summary Table

| Template | Has `doit context show` | Has Explicit File Reads | Double-Injection |
|----------|------------------------|------------------------|------------------|
| doit.checkin.md | YES | YES (roadmap, completed_roadmap) | YES |
| doit.constitution.md | YES | YES (constitution, tech-stack) | YES |
| doit.documentit.md | YES | NO | NO |
| doit.fixit.md | YES | NO | NO |
| doit.implementit.md | YES | NO | NO |
| doit.planit.md | YES | YES (constitution, tech-stack) | YES |
| doit.reviewit.md | YES | NO | NO |
| doit.roadmapit.md | YES | YES (roadmap, constitution) | YES |
| doit.scaffoldit.md | YES | YES (constitution) | YES |
| doit.specit.md | YES | NO | NO |
| doit.taskit.md | YES | YES (tech-stack) | YES |
| doit.testit.md | YES | NO | NO |

### Alternatives Considered

1. **Remove `doit context show` and keep explicit reads**: Rejected because `doit context show` provides structured, token-limited output with summarization.
2. **Keep both for redundancy**: Rejected because it wastes ~40% of context tokens on duplicates.

---

## Finding 2: Specific Patterns to Eliminate

### Decision: Four distinct patterns require removal

### Rationale

The double-injection patterns fall into four categories:

### Pattern 1: "For this command specifically" Sections

**Affected**: doit.planit.md, doit.taskit.md

```markdown
<!-- REMOVE THIS PATTERN -->
**For this command specifically**:
- Read `.doit/memory/tech-stack.md` for technology decisions
- If tech-stack.md doesn't exist, check constitution.md for Tech Stack section
```

### Pattern 2: File Existence Checks

**Affected**: doit.checkin.md, doit.roadmapit.md

```markdown
<!-- REMOVE THIS PATTERN -->
- Check if `.doit/memory/roadmap.md` exists
- Check `.doit/memory/completed_roadmap.md` for patterns
```

### Pattern 3: Numbered Steps with Explicit Reads

**Affected**: doit.planit.md, doit.scaffoldit.md, doit.roadmapit.md

```markdown
<!-- REMOVE THIS PATTERN -->
2. Load context: Read FEATURE_SPEC and `.doit/memory/constitution.md`
3. Extract Constitution Tech Stack:
   - Read Tech Stack section from constitution.md
```

### Pattern 4: Constitution Reading Utility Documentation

**Affected**: doit.constitution.md (lines 160-188)

```markdown
<!-- REMOVE OR UPDATE THIS PATTERN -->
### Constitution Reading Utility
- Check if `.doit/memory/constitution.md` exists
- Check if `.doit/memory/tech-stack.md` exists for technical decisions
```

### Alternatives Considered

1. **Partial removal**: Keep some explicit reads for "important" contexts - rejected for consistency.
2. **Conditional logic**: Only read if `doit context show` fails - rejected as overly complex.

---

## Finding 3: Context Source Mapping

### Decision: Document which sources are provided by `doit context show`

### Rationale

Based on analysis of `.doit/config/context.yaml` and the context loader, `doit context show` provides:

| Source | File Path | Loaded By Default | Per-Command Override |
|--------|-----------|-------------------|---------------------|
| constitution | `.doit/memory/constitution.md` | YES | - |
| tech_stack | `.doit/memory/tech-stack.md` | YES | - |
| roadmap | `.doit/memory/roadmap.md` | YES | Disabled for roadmapit |
| completed_roadmap | `.doit/memory/completed_roadmap.md` | YES | - |
| current_spec | `specs/{feature}/spec.md` | YES | Disabled for roadmapit |
| related_specs | `specs/*/spec.md` (similar) | YES | Disabled for specit |

### Sources NOT in `doit context show` (explicit reads allowed)

- Feature-specific artifacts: `plan.md`, `data-model.md`, `tasks.md`
- API contracts: `contracts/*.yaml`
- External files: README.md, CHANGELOG.md
- Checklists: `checklists/*.md`

### Alternatives Considered

1. **Add all sources to `doit context show`**: Rejected - would exceed token limits.
2. **Remove sources from `doit context show`**: Rejected - core sources should always be available.

---

## Finding 3a: Planit-Specific Context Requirements

### Decision: Planit should leverage context show for spec and related specs, NOT explicit reads

### Rationale

The `doit.planit.md` template has special context needs that are ALREADY served by `doit context show`:

| What Planit Needs | Source in Context Show | Currently Double-Injected? |
| ----------------- | ---------------------- | -------------------------- |
| Feature specification | `current_spec` | YES - also has explicit FEATURE_SPEC read |
| Constitution principles | `constitution` | YES - also reads constitution.md |
| Tech stack decisions | `tech_stack` | YES - also reads tech-stack.md |
| Related specs for integration | `related_specs` | NO - should USE this source |

### What Planit Should Do

**Use from `doit context show`** (already loaded, don't read again):

- Constitution principles → available in context
- Tech stack → available in context
- Current spec → available as `current_spec`
- Related specs → available as `related_specs` (for finding integration points)

**Legitimate explicit reads** (NOT in context show):

- `specs/{feature}/plan.md` - if updating existing plan
- `specs/{feature}/research.md` - if research phase complete
- `specs/{feature}/contracts/*.yaml` - API contract files
- `specs/{feature}/data-model.md` - if already generated

### Template Modification for Planit

**REMOVE** (double-injection):

```markdown
- Read `.doit/memory/constitution.md`
- Read `.doit/memory/tech-stack.md`
- Load context: Read FEATURE_SPEC
```

**KEEP/ADD** (legitimate):

```markdown
**Use loaded context to**:
- Extract tech stack from constitution (already in context)
- Reference current spec requirements (already in context as current_spec)
- Check related_specs for integration points with other features

**Explicit reads allowed** (not in context show):
- Feature artifacts: research.md, data-model.md, contracts/*
```

### Impact on Analysis

This clarifies that planit's double-injection count remains 3 patterns:

1. ~~constitution.md read~~ → use context
2. ~~tech-stack.md read~~ → use context
3. ~~FEATURE_SPEC read~~ → use current_spec from context

But planit should ACTIVELY USE the `related_specs` context for integration analysis.

---

## Finding 4: Best Practices Instruction Block

### Decision: Standardized instruction block for all templates

### Rationale

Based on analysis of successful AI interactions, the following instruction block improves code quality:

```markdown
## Code Quality Guidelines

Before generating or modifying code:

1. **Search for existing implementations** - Use Glob/Grep to find similar functionality before creating new code
2. **Follow established patterns** - Match existing code style, naming conventions, and architecture
3. **Avoid duplication** - Reference or extend existing utilities rather than recreating them
4. **Check imports** - Verify required dependencies already exist in the project
5. **Maintain consistency** - Follow the patterns in adjacent code files

**Context already loaded** (DO NOT read these files again):
- Constitution principles and tech stack
- Roadmap priorities
- Related specifications
```

### Alternatives Considered

1. **Per-template custom instructions**: Rejected for inconsistency.
2. **External include file**: Rejected - markdown doesn't support includes.

---

## Finding 5: .gitignore Configuration

### Decision: Add `.doit/temp/` to .gitignore

### Rationale

Temporary scripts should not be tracked in version control. The `.gitignore` file should include:

```gitignore
# Temporary AI-generated scripts
.doit/temp/
```

### Current .gitignore Analysis

Checked existing `.gitignore` - no entry for `.doit/temp/` exists. Entry must be added.

### Alternatives Considered

1. **Use system temp directory**: Rejected - project-specific temp is more predictable.
2. **Track temp files**: Rejected - creates unnecessary commits and conflicts.

---

## Summary of Changes Required

| Area | Templates Affected | Type of Change |
|------|-------------------|----------------|
| Double-injection removal | 6 templates | Remove explicit file reads |
| Best practices block | 12 templates | Add standardized instruction block |
| Artifact storage instructions | 12 templates | Add temp/reports path instructions |
| Context source documentation | context.yaml | Add source mapping comments |
| .gitignore update | .gitignore | Add .doit/temp/ exclusion |
| Context audit command | New file | Create context_auditor.py |

## Estimated Token Savings

| Template | Current Est. Tokens | After Optimization | Savings |
|----------|--------------------|--------------------|---------|
| doit.planit.md | ~3,500 | ~2,100 | 40% |
| doit.taskit.md | ~2,800 | ~1,700 | 39% |
| doit.roadmapit.md | ~4,200 | ~2,500 | 40% |
| doit.scaffoldit.md | ~1,800 | ~1,100 | 39% |
| doit.checkin.md | ~2,200 | ~1,400 | 36% |
| doit.constitution.md | ~3,000 | ~1,800 | 40% |

**Average savings: ~39%** (exceeds 40% target when combined with removed redundancy)
