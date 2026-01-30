# Quickstart: Research-to-Spec Auto-Pipeline

**Feature Branch**: `054-research-spec-pipeline`
**Spec**: [spec.md](spec.md) | **Plan**: [plan.md](plan.md)

## Overview

This feature enables seamless handoff from `/doit.researchit` to `/doit.specit` with full context preservation.

## Prerequisites

- [ ] Spec.md reviewed and approved
- [ ] Plan.md reviewed and approved
- [ ] Feature branch checked out: `054-research-spec-pipeline`

## Implementation Steps

### Step 1: Update doit.researchit.md - Add Flag Detection

**File**: `templates/commands/doit.researchit.md`
**Location**: User Input section (near top)

Add flag detection logic:

```markdown
## User Input

```text
$ARGUMENTS
```

**Check for flags**:
- `--auto-continue`: Skip handoff prompt and invoke specit automatically
- `--skip-issues`: Skip GitHub issue creation (existing flag)

Extract feature description by removing flags from arguments.
```

### Step 2: Update doit.researchit.md - Add Handoff Prompt

**File**: `templates/commands/doit.researchit.md`
**Location**: After Step 5 (Present Summary and Next Steps)

Add new Step 6 with handoff logic:

```markdown
## Step 6: Handoff to Specification

### 6.1 Validate Research Artifacts

Before prompting for handoff, verify artifacts exist:

```bash
# Check required artifact
ls specs/{feature}/research.md 2>/dev/null

# Check optional artifacts
ls specs/{feature}/user-stories.md 2>/dev/null
ls specs/{feature}/personas.md 2>/dev/null
```

**If research.md missing**: ERROR - cannot proceed to specification

### 6.2 Display Artifact Summary

Present what was created and will be passed to specit:

```markdown
## Research Artifacts Ready

| Artifact | Status |
|----------|--------|
| research.md | ✓ Created |
| user-stories.md | ✓ Created |
| personas.md | [✓ or ✗] |
| interview-notes.md | [✓ or ✗] |
| competitive-analysis.md | [✓ or ✗] |
```

### 6.3 Handoff Decision

**If --auto-continue flag was set**:
- Skip prompt
- Invoke `/doit.specit {feature-name}` directly
- Report: "Auto-continuing to specification..."

**If no --auto-continue flag**:
Present interactive prompt:

```markdown
---

## Continue to Specification?

**Options**:
1. **Continue** - Run `/doit.specit` now with research pre-loaded
2. **Later** - Exit and resume later

Your choice: _
```

### 6.4 Handle User Choice

**If "Continue" (or 1)**:
- Invoke `/doit.specit {feature-name}`
- Pass feature directory context

**If "Later" (or 2)**:
Display resume instructions:

```markdown
---

## Session Saved

Your research artifacts are saved in `specs/{feature}/`.

To resume later, run:
```
/doit.specit {feature-name}
```

The specification phase will automatically load your research context.
```
```

### Step 3: Update doit.specit.md - Add Context Confirmation

**File**: `templates/commands/doit.specit.md`
**Location**: After "Load Research Artifacts" section

Add confirmation message when research is found:

```markdown
**When research artifacts are loaded**, display confirmation:

```markdown
## Research Context Loaded

Found research artifacts from prior `/doit.researchit` session:
- research.md ✓
- user-stories.md ✓
- [other artifacts]

These will be used to inform the specification.
```
```

### Step 4: Update doit.specit.md - Add Feature Suggestion

**File**: `templates/commands/doit.specit.md`
**Location**: In "Outline" section, when no arguments provided

Add logic to suggest recent feature:

```markdown
If `$ARGUMENTS` is empty:
1. Check for recently modified research.md files:
   ```bash
   ls -t specs/*/research.md 2>/dev/null | head -1
   ```
2. If found, extract feature name and suggest:
   ```markdown
   No feature specified. Did you mean to continue with **{feature-name}**?

   Research artifacts were recently created for this feature.

   - **Yes** - Continue with {feature-name}
   - **No** - Enter a new feature description
   ```
3. If no recent research found, prompt for feature description as usual.
```

## File Checklist

### Files to Modify

- [x] `templates/commands/doit.researchit.md`
  - [x] Add --auto-continue flag detection
  - [x] Add Step 5: Validate Research Artifacts
  - [x] Add Step 7: Handoff to Specification
  - [x] Add artifact validation
  - [x] Add handoff prompt
  - [x] Add resume instructions

- [x] `templates/commands/doit.specit.md`
  - [x] Add research context confirmation message
  - [x] Add recent feature suggestion when no args

### No New Files Required

This feature modifies existing templates only.

## Testing

### Manual Test Cases

1. **Complete research, select "Continue"**
   - Run `/doit.researchit test-feature`
   - Complete Q&A
   - Select "Continue" at handoff prompt
   - Verify specit starts with research loaded

2. **Complete research, select "Later"**
   - Run `/doit.researchit test-feature`
   - Complete Q&A
   - Select "Later" at handoff prompt
   - Verify resume instructions displayed
   - Run `/doit.specit test-feature` later
   - Verify research loaded

3. **Auto-continue flag**
   - Run `/doit.researchit test-feature --auto-continue`
   - Complete Q&A
   - Verify specit starts automatically (no prompt)

4. **Recent feature suggestion**
   - Complete research for a feature
   - Run `/doit.specit` with no arguments
   - Verify recent feature is suggested

## Success Criteria Validation

| Criterion | How to Verify |
|-----------|---------------|
| SC-001: 90% proceed to specit | Track user choices in testing |
| SC-002: < 5 second transition | Time the handoff process |
| SC-003: 100% artifacts available | Verify all artifacts loaded in specit |
| SC-004: Zero data loss | Confirm artifacts exist after handoff |
