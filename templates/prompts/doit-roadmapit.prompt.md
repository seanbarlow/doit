---
agent: true
description: Create or update the project roadmap with prioritized requirements and AI-suggested enhancements
---

# Doit Roadmapit - Roadmap Manager

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty).

## Outline

This command creates or updates the project roadmap at `.doit/memory/roadmap.md`. The roadmap captures high-level requirements prioritized by business value, deferred items, and project vision.

### 1. Parse Command Arguments

Extract the operation and details from `$ARGUMENTS`:

| Pattern | Operation | Example |
|---------|-----------|---------|
| `create [vision]` | Create new roadmap | `#doit-roadmapit create a task management app` |
| `add [item]` | Add item to roadmap | `#doit-roadmapit add user authentication` |
| `defer [item]` | Move item to deferred | `#doit-roadmapit defer social login` |
| `reprioritize` | Review and change priorities | `#doit-roadmapit reprioritize` |
| (empty or `update`) | Interactive update | `#doit-roadmapit` |

If no arguments provided or unrecognized pattern, proceed to step 2 for detection.

### 2. Check for Existing Roadmap

Check if `.doit/memory/roadmap.md` exists:

- **If NOT exists**: Proceed to Step 3 (Create Workflow)
- **If exists**: Proceed to Step 4 (Update Workflow)

### 3. Create Workflow (New Roadmap)

#### 3.1 Ensure Directory Exists

```bash
mkdir -p .doit/memory
```

#### 3.2 Gather Project Context

Read these files if they exist to understand project context:

- `.doit/memory/constitution.md` - Project principles and tech stack
- `README.md` - Project description
- `package.json` or `pyproject.toml` - Project metadata

#### 3.3 Ask Clarifying Questions

Present questions to establish roadmap foundation. Use the user's input (if provided) as context:

**Question 1: Project Vision**
> What is the primary goal or vision for this project?

**Question 2: Initial Priority Items**
> What are the most critical features or requirements for your MVP?

**Question 3: Known Constraints**
> Are there any constraints or limitations to consider?

#### 3.4 Build Roadmap Structure

Using the gathered information, create the roadmap:

1. Load template from `.doit/templates/roadmap-template.md`
2. Replace placeholders with project information
3. Populate priority sections based on user's answers:
   - Add confirmed critical items to P1
   - Add important but not blocking items to P2
   - Add nice-to-have items to P3/P4
4. Leave Deferred Items empty for new roadmaps

#### 3.5 Write Roadmap

Write the populated roadmap to `.doit/memory/roadmap.md`

### 4. Update Workflow (Existing Roadmap)

#### 4.1 Load Current Roadmap

Read `.doit/memory/roadmap.md` and parse:

- Current vision statement
- All items in P1, P2, P3, P4 sections with their status
- All deferred items
- Last updated date

#### 4.2 Display Current State

Show the user the current roadmap state:

```markdown
## Current Roadmap State

**Vision**: [Current vision statement]
**Last Updated**: [Date]

### Active Items
| Priority | Item | Feature Branch | Status |
|----------|------|----------------|--------|
| P1 | [item] | [branch-ref] | [ ] |
| P2 | [item] | [branch-ref] | [ ] |
...

### Deferred Items
| Item | Original Priority | Reason |
|------|-------------------|--------|
...
```

#### 4.3 Handle Specific Operations

Based on the parsed operation from Step 1:

**Add Operation (`add [item]`)**:
1. Ask: "What priority should this item have? (P1/P2/P3/P4)"
2. Ask: "What's the business rationale for this priority?"
3. Ask: "Is there a feature branch reference? (e.g., `[###-feature-name]`)"
4. Add the item to the appropriate section

**Defer Operation (`defer [item]`)**:
1. Search for the item in active sections
2. If not found: List available items and ask user to select
3. If found: Ask "What's the reason for deferring?"
4. Move item to Deferred section with original priority and reason

**Reprioritize Operation (`reprioritize`)**:
1. List all active items with current priorities
2. Ask: "Which items need priority changes?"
3. For each item to change, get new priority and rationale
4. Update items in their new sections

**Interactive Update (no specific operation)**:
1. Ask: "What would you like to do?"
   - A. Add a new item
   - B. Defer an item
   - C. Reprioritize items
   - D. Update the vision statement
   - E. Mark an item as complete
2. Execute the selected operation

### 5. AI Enhancement Suggestions

After any create or update operation, analyze the roadmap and project context to suggest enhancements.

#### 5.1 Gather Context

Read additional context if available:

- `.doit/memory/constitution.md` - Project principles
- `.doit/memory/completed_roadmap.md` - Past completed items
- Current roadmap items and gaps

#### 5.2 Generate Suggestions

Based on context, generate 2-5 complementary feature suggestions:

```markdown
## Enhancement Suggestions

Based on your roadmap and project context, here are some features you might consider:

### Suggestion 1: [Feature Name]
**Rationale**: [Why this complements existing items]
**Suggested Priority**: P[N]
**Aligns with**: [Related existing item or principle]

### Suggestion 2: [Feature Name]
...

---

**Actions**:
- Type the suggestion number to add it (e.g., "1" or "1, 3")
- Type "skip" to finish without adding suggestions
- Type "modify [N]" to customize a suggestion before adding
```

### 6. Completion Report

Output a summary of changes:

```markdown
## Roadmap Update Complete

**File**: `.doit/memory/roadmap.md`
**Operation**: [Create/Add/Defer/Reprioritize]
**Date**: [Current date]

### Changes Made
- [List of specific changes]

### Current Statistics
| Priority | Count |
|----------|-------|
| P1 | [N] |
| P2 | [N] |
| P3 | [N] |
| P4 | [N] |
| Deferred | [N] |

### Next Steps
- Run `#doit-specit` to create specs for top priority items
- Run `#doit-roadmapit` again to continue updating
- Review completed items in `.doit/memory/completed_roadmap.md`
```

## Key Rules

- Always preserve existing content when updating
- Ask clarifying questions before making changes
- Provide AI suggestions after every operation
- Use feature branch references `[###-feature-name]` for traceability
- Maintain maximum 3-5 P1 items (truly critical only)
- Back up malformed roadmaps before recreating
