---
description: Pre-specification research workflow for Product Owners to capture business requirements through interactive Q&A, generating research artifacts for handoff to technical specification.
handoffs:
  - label: Create Technical Specification
    agent: doit.specit
    prompt: Create a specification using the research artifacts from this session.
---

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty). The user input is the feature name or description they want to research.

## Load Project Context

Before proceeding, load the project context to inform your responses:

```bash
doit context show
```

**If the command fails or doit is not installed**: Continue without context, but note that alignment with project principles cannot be verified.

**Use loaded context to**:

- Reference constitution principles when capturing requirements
- Consider roadmap priorities when discussing scope
- Identify connections to related features

## Outline

This command guides Product Owners through a structured Q&A session to capture business requirements **without** involving technology decisions. The AI asks questions, captures answers, and generates research artifacts.

**Important**: This is a business-focused workflow. Do NOT ask about:
- Programming languages, frameworks, or databases
- API designs or system architecture
- Technical implementation details

### Step 1: Check for Existing Research (Resume Support)

Before starting a new session, check if research artifacts already exist:

```bash
# Check if feature directory exists and has research files
ls specs/*/research.md 2>/dev/null | grep -i "$FEATURE_NAME" || echo "No existing research found"
```

**If existing research.md found for this feature**:
1. Ask the user: "I found existing research for this feature. Would you like to:
   - **Resume**: Continue adding to the existing research
   - **Start Fresh**: Create new research (existing files will be backed up)"
2. If Resume: Load existing content and identify unanswered questions
3. If Start Fresh: Back up existing files with `.bak` extension and proceed

**If no existing research found**: Proceed to Step 2.

### Step 2: Establish Feature Context

If `$ARGUMENTS` is empty, ask:
> "What feature or capability would you like to research? Please describe it in a sentence or two."

Once you have the feature description:
1. Generate a feature short-name (2-4 words, lowercase, hyphenated)
2. Create the feature directory path: `specs/{NNN-short-name}/`
3. Confirm with user: "I'll create research artifacts for **{feature-name}** in `specs/{path}/`. Does this look correct?"

### Step 3: Interactive Q&A Session

Guide the user through four phases of questions. Ask questions one at a time, waiting for responses before proceeding. Adapt follow-up questions based on their answers.

**Guidelines for Conducting Q&A**:
- Ask ONE question at a time and wait for response
- If an answer is too brief (< 10 words), gently prompt for more detail
- Acknowledge good answers before moving to the next question
- Skip questions that have already been answered in previous responses
- Take notes on key themes and personas that emerge

---

## Phase 1: Problem Understanding

**Goal**: Understand the core problem and its current impact.

### Question 1.1
> "What problem are you trying to solve with this feature?"

*Wait for response. If brief, follow up with:*
> "Can you tell me more about why this is a problem? What pain does it cause?"

### Question 1.2
> "Who currently experiences this problem? What types of people or roles?"

*Wait for response.*

### Question 1.3
> "What happens today without this solution? How do people work around it?"

*Wait for response.*

**Phase 1 Summary**: After all questions, briefly summarize:
> "Let me make sure I understand: [Summarize problem, affected users, current state]. Is this accurate?"

---

## Phase 2: Users and Goals

**Goal**: Identify target users and define what success looks like for them.

### Question 2.1
> "Who are the primary users of this feature? Can you describe them?"

*Wait for response. Note any distinct user types or personas.*

### Question 2.2
> "What does success look like for these users? When they use this feature, what should they be able to accomplish?"

*Wait for response.*

### Question 2.3
> "Are there different types of users with different needs? For example, some users who need basic functionality vs. power users?"

*Wait for response. If yes, note the distinctions.*

**Phase 2 Summary**: After all questions, confirm understanding:
> "So the main users are [personas] and success for them means [outcomes]. Did I capture that correctly?"

---

## Phase 3: Requirements and Constraints

**Goal**: Define must-haves, nice-to-haves, and boundaries.

### Question 3.1
> "What must this feature absolutely do? What are the non-negotiable requirements?"

*Wait for response. These become must-haves.*

### Question 3.2
> "What would be nice to have but isn't essential for the first version?"

*Wait for response. These become nice-to-haves or future enhancements.*

### Question 3.3
> "What should this feature explicitly NOT do? Are there boundaries we should set?"

*Wait for response. These become out-of-scope items.*

### Question 3.4
> "Are there any constraints we should know about? Things like timeline, budget, compliance requirements, or dependencies on other work?"

*Wait for response.*

**Phase 3 Summary**: Confirm scope:
> "To summarize the scope: Must-haves are [list], nice-to-haves are [list], and out-of-scope is [list]. Any corrections?"

---

## Phase 4: Success Metrics

**Goal**: Define how success will be measured.

### Question 4.1
> "How will you measure if this feature is successful? What metrics or outcomes would indicate it's working?"

*Wait for response.*

### Question 4.2
> "What would failure look like? What outcomes would tell you this feature isn't meeting its goals?"

*Wait for response.*

**Phase 4 Summary**: Confirm metrics:
> "Success will be measured by [metrics], and we'll know there's a problem if [failure indicators]. Does that sound right?"

---

## Step 4: Generate Research Artifacts

After completing all Q&A phases, generate the research artifacts.

### 4.1 Determine Feature Directory

If not already established, determine the feature number by finding the **highest** existing number (to handle gaps):

```bash
# Find the highest feature number across all existing directories
# This handles gaps (e.g., if 001, 002, 005 exist, next is 006)
ls -d specs/[0-9][0-9][0-9]-* 2>/dev/null | sed 's/.*specs\/\([0-9]*\)-.*/\1/' | sort -n | tail -1 | awk '{printf "%03d", $1+1}'
```

If no existing directories found, start with `001`.

Create the feature directory: `specs/{NNN-feature-short-name}/`

### 4.2 Generate research.md

Load the research template and populate it with Q&A answers:

**File**: `specs/{feature}/research.md`

Use the template at `.doit/templates/research-template.md` as a guide. Map Q&A answers to sections:

| Q&A Phase | Template Section |
|-----------|------------------|
| Phase 1 (Problem) | Problem Statement, Current State |
| Phase 2 (Users) | Target Users, Personas, User Goals |
| Phase 3 (Requirements) | Must-Haves, Nice-to-Haves, Out of Scope, Constraints |
| Phase 4 (Metrics) | Success Metrics, Failure Indicators |

### 4.3 Generate user-stories.md

Derive user stories from the Q&A responses:

**File**: `specs/{feature}/user-stories.md`

Use the template at `.doit/templates/user-stories-template.md`. For each identified persona and goal:

1. Create a user story in Given/When/Then format:
   - **Given** [user context/state]
   - **When** [user action]
   - **Then** [expected outcome]

2. Assign priorities based on must-have vs. nice-to-have:
   - Must-have requirements = P1 priority
   - Nice-to-have requirements = P2/P3 priority

3. Link each story to the persona it serves

### 4.4 Generate interview-notes.md

Create a template for stakeholder interviews:

**File**: `specs/{feature}/interview-notes.md`

Use the template at `.doit/templates/interview-notes-template.md`. Populate with:

- Suggested interview questions for each identified persona
- Space for capturing additional insights
- Key topics to probe based on requirements

### 4.5 Generate competitive-analysis.md

Create a framework for competitive analysis:

**File**: `specs/{feature}/competitive-analysis.md`

Use the template at `.doit/templates/competitive-analysis-template.md`. Set up:

- Competitor identification section
- Feature comparison matrix based on must-have requirements
- Differentiation opportunities based on user goals

---

## Step 5: Present Summary and Next Steps

After generating all artifacts, present a summary:

```markdown
---

## Research Session Complete

### Files Created

| File | Description |
|------|-------------|
| `specs/{feature}/research.md` | Problem statement, users, goals, requirements |
| `specs/{feature}/user-stories.md` | User stories in Given/When/Then format |
| `specs/{feature}/interview-notes.md` | Stakeholder interview templates |
| `specs/{feature}/competitive-analysis.md` | Competitor analysis framework |

### Key Findings Summary

**Problem**: [One sentence summary]
**Target Users**: [Persona list]
**Core Requirements**: [Top 3 must-haves]
**Success Metric**: [Primary success measure]

---

## Next Steps

┌─────────────────────────────────────────────────────────────────┐
│  Workflow Progress                                              │
│  ● researchit → ○ specit → ○ planit → ○ taskit → ○ implementit │
└─────────────────────────────────────────────────────────────────┘

**Recommended**: Run `/doit.specit` to create a technical specification from this research.

The specification phase will:
- Use your research.md as context for requirements
- Reference your user stories for acceptance scenarios
- Create a formal specification ready for development planning
```

---

## Edge Case Handling

### Minimal or Empty Answers

If the user provides very brief answers (< 10 words):

> "Could you tell me a bit more? For example, [suggest specific aspects to consider]."

If still minimal after follow-up, document as "[Brief: user's answer]" and note that more detail may be needed.

### Conflicting Requirements

If requirements appear to conflict:

> "I noticed that [requirement A] might conflict with [requirement B]. How would you prioritize these, or is there a way to reconcile them?"

Document the resolution or flag as "[Needs Prioritization]".

### Session Interruption

If the session is interrupted before completion:

1. Save all captured answers to a draft file: `specs/{feature}/.research-draft.md`
2. Include a marker indicating which questions have been answered
3. On resume, load the draft and continue from the next unanswered question

### Draft Cleanup After Completion

After successfully generating all research artifacts:

1. Delete the draft file: `specs/{feature}/.research-draft.md`
2. Verify all four artifact files exist and are populated
3. Do NOT leave draft files in the feature directory

### Existing Research Files

If `research.md` already exists for this feature:

1. **Update mode**: Merge new answers with existing content, preserving valuable information
2. **Version mode**: Archive existing file as `research.v1.md` and create fresh `research.md`

Ask user which approach they prefer before proceeding.

---

## Q&A Reference Summary

| Phase | Question | Purpose |
|-------|----------|---------|
| 1.1 | What problem are you solving? | Core problem statement |
| 1.2 | Who experiences this problem? | Affected users |
| 1.3 | What happens today without this? | Current state/workarounds |
| 2.1 | Who are the primary users? | Target personas |
| 2.2 | What does success look like? | User goals |
| 2.3 | Different user types? | Persona differentiation |
| 3.1 | What must it absolutely do? | Must-have requirements |
| 3.2 | What's nice to have? | Future enhancements |
| 3.3 | What should it NOT do? | Out of scope |
| 3.4 | Any constraints? | Timeline, budget, compliance |
| 4.1 | How will you measure success? | Success metrics |
| 4.2 | What would failure look like? | Failure indicators |
