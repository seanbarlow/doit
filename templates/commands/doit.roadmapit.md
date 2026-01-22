---
description: Create or update the project roadmap with prioritized requirements, deferred functionality, and AI-suggested enhancements.
handoffs:
  - label: Create Specification
    agent: doit.specit
    prompt: Create a feature specification for the top roadmap item...
  - label: Update Constitution
    agent: doit.constitution
    prompt: Update the project constitution based on roadmap priorities...
---

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty).

## Load Project Context

Before proceeding, load the project context to inform your responses:

```bash
doit context show
```

**If the command fails or doit is not installed**: Continue without context, but note that alignment with project principles cannot be verified.

**Use loaded context to**:

- Reference constitution principles when making decisions
- Consider roadmap priorities
- Identify connections to related specifications

## Outline

This command creates or updates the project roadmap at `.doit/memory/roadmap.md`. The roadmap captures high-level requirements prioritized by business value, deferred items, and project vision.

### 1. Parse Command Arguments

Extract the operation and details from `$ARGUMENTS`:

| Pattern | Operation | Example |
|---------|-----------|---------|
| `create [vision]` | Create new roadmap | `/doit.roadmapit create a task management app` |
| `add [item]` | Add item to roadmap | `/doit.roadmapit add user authentication` |
| `defer [item]` | Move item to deferred | `/doit.roadmapit defer social login` |
| `reprioritize` | Review and change priorities | `/doit.roadmapit reprioritize` |
| `sync-milestones` | Sync priorities to GitHub milestones | `/doit.roadmapit sync-milestones` |
| `sync-milestones --dry-run` | Preview milestone sync | `/doit.roadmapit sync-milestones --dry-run` |
| (empty or `update`) | Interactive update | `/doit.roadmapit` |

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
>
> Based on your input "[USER_INPUT]", I understand the project is about [INTERPRETATION].
>
> Please confirm or provide a more detailed vision statement.

**Question 2: Initial Priority Items**
> What are the most critical features or requirements for your MVP?
>
> Suggested based on your description:
> - [SUGGESTION_1]
> - [SUGGESTION_2]
>
> Which of these are correct? What would you add or change?

**Question 3: Known Constraints**
> Are there any constraints or limitations to consider?
>
> Options:
> A. Timeline constraints (specific deadline)
> B. Technical constraints (must use specific tech)
> C. Resource constraints (limited team/budget)
> D. No significant constraints
> E. Custom (please specify)

#### 3.4 Build Roadmap Structure

Using the gathered information, create the roadmap:

1. Load template from `.doit/templates/roadmap-template.md`
2. Replace `[PROJECT_NAME]` with project name from constitution or package metadata
3. Replace `[DATE]` with current date
4. Replace `[PROJECT_VISION]` with the confirmed vision statement
5. Populate priority sections based on user's answers:
   - Add confirmed critical items to P1
   - Add important but not blocking items to P2
   - Add nice-to-have items to P3/P4
6. Leave Deferred Items empty for new roadmaps

#### 3.5 Write Roadmap

Write the populated roadmap to `.doit/memory/roadmap.md`

#### 3.6 Offer Enhancement Suggestions

After creating the roadmap, proceed to Step 6 (AI Suggestions).

---

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
3. For each item to change:
   - Show current priority
   - Ask for new priority (P1/P2/P3/P4)
   - Ask for rationale for the change
4. Update items in their new sections

**Sync Milestones Operation (`sync-milestones` or `sync-milestones --dry-run`)**:

1. Execute the milestone sync command:

   ```bash
   doit roadmapit sync-milestones [--dry-run]
   ```

2. The command will:
   - Create GitHub milestones for each priority level (P1-P4) if they don't exist
   - Assign roadmap epics to their corresponding priority milestones
   - Display a summary of changes made
3. After sync completes, show:
   - Milestones created count
   - Epics assigned count
   - Link to view milestones on GitHub
4. **Complete this operation** - Do not proceed to other steps

**Interactive Update (no specific operation)**:
1. Ask: "What would you like to do?"
   - A. Add a new item
   - B. Defer an item
   - C. Reprioritize items
   - D. Update the vision statement
   - E. Mark an item as complete (moves to completed_roadmap.md)
   - F. Sync priorities to GitHub milestones
2. Execute the selected operation

#### 4.4 Preserve Unmodified Content

When updating the roadmap:

- Keep all items not explicitly changed
- Maintain existing rationales unless updated
- Preserve feature branch references
- Update only the `Last Updated` date

#### 4.5 Write Updated Roadmap

Write the modified roadmap back to `.doit/memory/roadmap.md`

#### 4.6 Offer Enhancement Suggestions

After updating, proceed to Step 6 (AI Suggestions).

---

### 5. Handle Edge Cases

#### 5.1 Malformed Roadmap

If existing roadmap cannot be parsed:

1. Create backup: `mv .doit/memory/roadmap.md .doit/memory/roadmap.md.bak`
2. Notify user: "The existing roadmap appears to be malformed. A backup has been created."
3. Try to extract any readable content
4. Offer to create fresh roadmap incorporating salvaged content

#### 5.2 Item Not Found (for defer/update)

If specified item cannot be found:

1. List all current items in a table
2. Ask user to select from the list or provide exact item text
3. Use fuzzy matching to suggest closest matches

#### 5.3 Conflicting Priorities

If user assigns multiple P1 items:

1. Show warning: "You have [N] P1 items. P1 should be reserved for truly critical items."
2. Ask: "Would you like to compare these items to determine which is most critical?"
3. If yes, present pairwise comparison for each P1 item

---

### 6. AI Enhancement Suggestions

After any create or update operation, analyze the roadmap and project context to suggest enhancements.

#### 6.1 Gather Context

Read additional context if available:

- `.doit/memory/constitution.md` - Project principles
- `.doit/memory/completed_roadmap.md` - Past completed items
- Current roadmap items and gaps

#### 6.2 Generate Suggestions

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

#### 6.3 Handle Suggestion Response

- If user selects suggestions: Add them to the appropriate priority sections
- If user modifies: Apply customizations then add
- If user skips: Complete without changes

---

### 7. Completion Report

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
- Run `/doit.specit` to create specs for top priority items
- Run `/doit.roadmapit` again to continue updating
- Review completed items in `.doit/memory/completed_roadmap.md`
```

---

## Key Rules

- Always preserve existing content when updating
- Ask clarifying questions before making changes
- Provide AI suggestions after every operation
- Use feature branch references `[###-feature-name]` for traceability
- Maintain maximum 3-5 P1 items (truly critical only)
- Back up malformed roadmaps before recreating

---

## Next Steps

After completing this command, display a recommendation section based on the outcome:

### On Success (roadmap created or updated)

Display the following at the end of your output:

```markdown
---

## Next Steps

**Roadmap updated!**

**Recommended**: Run `/doit.specit [top priority item]` to create a specification for your highest priority feature.

**Alternative**: Run `/doit.roadmapit add [item]` to add more items to the roadmap.
```

### On Item Added

If a new item was added to the roadmap:

```markdown
---

## Next Steps

**Item added to roadmap!**

**Recommended**: Run `/doit.specit [item description]` to create a specification for this item.

**Alternative**: Run `/doit.roadmapit reprioritize` to review and adjust priorities.
```
