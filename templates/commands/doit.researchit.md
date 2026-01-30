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

### Flag Detection

Check for the following flags in `$ARGUMENTS`:

- `--auto-continue`: Skip handoff prompt and automatically invoke `/doit.specit` after research completes
- `--skip-issues`: Skip GitHub issue creation (existing behavior)

**Extract the feature description** by removing any flags from the arguments. For example:
- Input: `user-authentication --auto-continue` → Feature: `user-authentication`, Auto-continue: true
- Input: `payment-system` → Feature: `payment-system`, Auto-continue: false

Store the `auto-continue` flag value for use in Step 7 (Handoff to Specification).

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

**Goal**: Identify target users and build comprehensive persona profiles using the persona template.

> **Template Reference**: Use `.doit/templates/persona-template.md` for the complete persona field structure.

### Question 2.1 - User Identification
> "Who are the primary users of this feature? Can you describe them?"

*Wait for response. Note any distinct user types or personas. Assign each a preliminary ID (P-001, P-002, etc.).*

### Question 2.2 - User Roles and Archetypes
> "For each user type you mentioned, what is their job role or title? Would you classify them as:
> - **Power User** (frequent, advanced needs)
> - **Casual User** (occasional, basic needs)
> - **Administrator** (manages system/config)
> - **Approver** (reviews/approves work)
> - **Observer** (views but doesn't interact directly)"

*Wait for response. Assign an archetype to each persona.*

### Question 2.3 - Experience and Context
> "For your main users:
> - What is their typical experience level (Junior/Mid/Senior/Executive)?
> - Do they work solo, in small teams, large teams, or enterprise settings?
> - What domain expertise do they bring?"

*Wait for response. Capture demographics for each persona.*

### Question 2.4 - Goals and Success
> "What does success look like for these users? When they use this feature, what should they be able to accomplish? Are there any secondary goals or nice-to-haves?"

*Wait for response. Note primary and secondary goals per persona.*

### Question 2.5 - Pain Points
> "What are the top 3 frustrations or pain points for each user type? Please prioritize them from most critical to least critical."

*Wait for response. Capture prioritized pain points.*

### Question 2.6 - Behavioral Patterns
> "How would you describe how these users typically work?
> - Technology proficiency (Low/Medium/High)?
> - Work style (methodical, quick iterations, collaborative)?
> - How do they make decisions (data-driven, intuitive, consensus-seeking)?"

*Wait for response. Capture behavioral patterns.*

### Question 2.7 - Usage Context
> "When and where do users encounter this problem? What is their typical workflow when they would use this feature?"

*Wait for response. Capture usage context.*

**Phase 2 Summary**: After all questions, confirm understanding:
> "Let me confirm the personas I've captured:
> - **P-001**: [Name] - [Role], [Archetype], primary goal: [goal], top pain point: [pain point]
> - **P-002**: [Name] - [Role], [Archetype], primary goal: [goal], top pain point: [pain point]
>
> Is this accurate?"

---

## Phase 2.5: Persona Relationships (if multiple personas)

**Goal**: Capture how personas relate to each other for workflow understanding.

> **Skip this phase** if only one persona was identified.

### Question 2.5.1 - Working Relationships
> "How do these personas work together? For example:
> - Does one manage or supervise another?
> - Do they collaborate as peers?
> - Does one need to approve the other's work?
> - Does one's work block another from proceeding?"

*Wait for response. Map relationships to types: manages, reports_to, collaborates, approves, blocks.*

### Question 2.5.2 - Relationship Context
> "Can you describe the context of these relationships? For example, how often do they interact, and in what situations?"

*Wait for response. Capture context for each relationship.*

### Question 2.5.3 - Conflicts and Tensions
> "Are there any situations where these personas might have conflicting goals or competing priorities? What tradeoffs might need to be made?"

*Wait for response. Document conflicts for the Conflicts & Tensions section.*

**Phase 2.5 Summary**: Confirm relationships:
> "I've captured these relationships:
> - P-001 [relationship] P-002: [context]
> - [Any conflicts noted]
>
> Is this accurate?"

**Bidirectional Documentation**: When documenting relationships:
- If A manages B, add to both profiles (A: "manages P-002", B: "reports_to P-001")
- If no relationships exist for a persona, document as "No direct relationships identified"

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

### 4.3 Generate personas.md

Create comprehensive persona profiles from Phase 2 Q&A:

**File**: `specs/{feature}/personas.md`

Use the template at `.doit/templates/personas-output-template.md`. For each persona identified:

1. **Assign unique ID**: P-001, P-002, etc.
2. **Populate all profile fields** from Q&A answers:
   - Identity (name, role, archetype from Q2.1, Q2.2)
   - Demographics (experience, team size, domain from Q2.3)
   - Goals (primary, secondary from Q2.4)
   - Pain Points (prioritized list from Q2.5)
   - Behavioral Patterns (tech proficiency, work style, decision making from Q2.6)
   - Success Criteria (what success means for this persona)
   - Usage Context (from Q2.7)
   - Relationships (from Phase 2.5 relationship questions, if asked)
   - Conflicts & Tensions (competing goals with other personas)

3. **Create Persona Summary table** at the top with quick reference

4. **Generate Relationship Map** (mermaid diagram) showing persona connections

5. **Document Conflicts & Tensions** summary if any competing goals exist

**Validation**: Ensure each persona has:
- Unique ID in format P-NNN
- All required fields populated
- Archetype from valid enum (Power User, Casual User, Administrator, Approver, Observer)

### 4.4 Generate user-stories.md

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

## Step 5: Validate Research Artifacts

Before presenting the summary, validate that all required artifacts were created successfully:

```bash
# Check required artifacts exist
ls specs/{feature}/research.md 2>/dev/null || echo "WARNING: research.md not found"
ls specs/{feature}/user-stories.md 2>/dev/null || echo "WARNING: user-stories.md not found"
```

**Build Artifact Status Table**:

| Artifact | Status | Required |
|----------|--------|----------|
| research.md | ✓ or ✗ | Yes |
| user-stories.md | ✓ or ✗ | Yes |
| personas.md | ✓ or ✗ | No |
| interview-notes.md | ✓ or ✗ | No |
| competitive-analysis.md | ✓ or ✗ | No |

**Validation Rules**:
- If `research.md` is missing: **ERROR** - Cannot proceed to specification without research
- If `user-stories.md` is missing: **WARNING** - Specification may be incomplete
- Optional artifacts: Note their presence for handoff summary

Store the artifact status for display in the handoff prompt.

---

## Step 6: Present Summary and Artifact Status

After generating all artifacts, present a summary with the artifact status from Step 5:

```markdown
---

## Research Session Complete

### Artifact Status

| Artifact | Status | Description |
|----------|--------|-------------|
| `specs/{feature}/research.md` | ✓ Created | Problem statement, users, goals, requirements |
| `specs/{feature}/user-stories.md` | ✓ Created | User stories in Given/When/Then format |
| `specs/{feature}/personas.md` | [✓ or ✗] | Comprehensive persona profiles with relationships |
| `specs/{feature}/interview-notes.md` | [✓ or ✗] | Stakeholder interview templates |
| `specs/{feature}/competitive-analysis.md` | [✓ or ✗] | Competitor analysis framework |

### Key Findings Summary

**Problem**: [One sentence summary]
**Target Users**: [Persona list]
**Core Requirements**: [Top 3 must-haves]
**Success Metric**: [Primary success measure]
```

---

## Step 7: Handoff to Specification

### 7.1 Workflow Progress Indicator

Display the current workflow position:

```markdown
┌─────────────────────────────────────────────────────────────────┐
│  Workflow Progress                                              │
│  ● researchit → ○ specit → ○ planit → ○ taskit → ○ implementit │
└─────────────────────────────────────────────────────────────────┘
```

### 7.2 Auto-Continue Check

**If `--auto-continue` flag was detected in Step 1**:
- Skip the handoff prompt
- Display: "Auto-continuing to specification phase..."
- Proceed directly to invoke `/doit.specit {feature-name}`
- **Go to Step 7.5**

**If no `--auto-continue` flag**: Continue to Step 7.3

### 7.3 Handoff Prompt

Present the interactive handoff prompt:

```markdown
---

## Continue to Specification?

Your research artifacts are ready to be used for technical specification.

**Options**:
1. **Continue** - Run `/doit.specit` now with research context pre-loaded
2. **Later** - Exit and resume specification later

The specification phase will:
- Use your research.md as context for requirements
- Reference your user stories for acceptance scenarios
- Create a formal specification ready for development planning

Your choice: _
```

Wait for user response.

### 7.4 Handle User Choice

**If user selects "Continue" (or "1" or "yes")**:
- Confirm: "Continuing to specification phase..."
- Proceed to Step 7.5 to invoke specit

**If user selects "Later" (or "2" or "no")**:
- Display resume instructions:

```markdown
---

## Session Saved

Your research artifacts are saved in `specs/{feature}/`.

To resume the specification phase later, run:
```
/doit.specit {feature-name}
```

The specification phase will automatically load your research context.

┌─────────────────────────────────────────────────────────────────┐
│  Workflow Progress                                              │
│  ✓ researchit → ○ specit → ○ planit → ○ taskit → ○ implementit │
└─────────────────────────────────────────────────────────────────┘
```

- End the session

### 7.5 Invoke Specification Phase

When continuing to specification (either via auto-continue or user choice):

1. **Invoke** `/doit.specit {feature-name}` where `{feature-name}` is the feature directory name (e.g., `054-research-spec-pipeline`)
2. **Pass context**: The feature directory path so specit knows where to find research artifacts
3. **Report**: "Starting specification phase with research context from `specs/{feature}/`..."

The specit command will automatically detect and load the research artifacts.

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
| 2.1 | Who are the primary users? | Target personas (assign P-IDs) |
| 2.2 | What are their roles/archetypes? | Persona classification |
| 2.3 | Experience and context? | Demographics |
| 2.4 | What does success look like? | Goals (primary, secondary) |
| 2.5 | Top 3 pain points? | Prioritized frustrations |
| 2.6 | How do they work? | Behavioral patterns |
| 2.7 | When/where do they use this? | Usage context |
| 2.5.1 | How do personas work together? | Relationships |
| 2.5.2 | Relationship context? | Interaction details |
| 2.5.3 | Any conflicting goals? | Conflicts & Tensions |
| 3.1 | What must it absolutely do? | Must-have requirements |
| 3.2 | What's nice to have? | Future enhancements |
| 3.3 | What should it NOT do? | Out of scope |
| 3.4 | Any constraints? | Timeline, budget, compliance |
| 4.1 | How will you measure success? | Success metrics |
| 4.2 | What would failure look like? | Failure indicators |
