---
name: doit.specit
description: Create or update the feature specification from a natural language feature description, with integrated ambiguity
  resolution and GitHub issue creation.
when_to_use: 'Use when the user wants to create or update a feature specification: capture requirements, user stories, acceptance
  criteria, and optionally create matching GitHub issues.'
allowed-tools: Read Write Edit Glob Grep Bash
argument-hint: '[feature description]'
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

**For this command specifically**:

- Reference constitution principles when defining requirements
- Align new features with roadmap priorities
- Check for overlap with existing specifications
- **Reference project personas** (if `.doit/memory/personas.md` is loaded in context): When generating user stories, include `Persona: P-NNN` references in each user story header matching the most relevant persona. If both project-level personas (from context) and feature-level personas (from `specs/{feature}/personas.md`) exist, feature-level personas take precedence.

## Code Quality Guidelines

Before generating or modifying code:

1. **Search for existing implementations** - Use Glob/Grep to find similar functionality before creating new code
2. **Follow established patterns** - Match existing code style, naming conventions, and architecture
3. **Avoid duplication** - Reference or extend existing utilities rather than recreating them
4. **Check imports** - Verify required dependencies already exist in the project

**Context already loaded** (DO NOT read these files again):

- Constitution principles and tech stack
- Roadmap priorities
- Current specification
- Related specifications

## Artifact Storage

- **Temporary scripts**: Save to `.doit/temp/{purpose}-{timestamp}.sh` (or .py/.ps1)
- **Status reports**: Save to `specs/{feature}/reports/{command}-report-{timestamp}.md`
- **Create directories if needed**: Use `mkdir -p` before writing files
- Note: `.doit/temp/` is gitignored - temporary files will not be committed

## Load Research Artifacts (if available)

Before generating a specification, check if research artifacts exist from a prior `/doit.researchit` session:

```bash
# Check for research artifacts in the feature directory
# Pattern: specs/{NNN-feature-name}/research.md
ls specs/*/research.md 2>/dev/null | head -5
```

**If research.md exists for this feature**:

1. **Load research.md** - Read the problem statement, target users, goals, and requirements
2. **Load user-stories.md** (if exists) - Read the user stories to inform acceptance scenarios
3. **Use research as context**:
   - Map Problem Statement section to spec Summary
   - Map Target Users/Personas to user story actors
   - Map Must-Have requirements to P1 functional requirements
   - Map Nice-to-Have requirements to P2/P3 functional requirements
   - Map Success Metrics to spec Success Criteria
   - Map Out of Scope items directly to spec Out of Scope section

4. **Reference research in spec**: Add a "Research Reference" link at the top of the generated spec:

   ```markdown
   **Research**: [research.md](research.md) | [user-stories.md](user-stories.md)
   ```

**If research artifacts also include**:

- `interview-notes.md`: Review for additional user insights and quote notable findings
- `competitive-analysis.md`: Review for differentiation opportunities and market context
- `personas.md`: Load comprehensive persona profiles for user story generation (see below)

**If NO research artifacts found**: Proceed normally with user-provided feature description.

### Research Context Confirmation

**When research artifacts ARE loaded**, display a confirmation message to the user:

```markdown
## Research Context Loaded

Found research artifacts from prior `/doit.researchit` session:

| Artifact | Status |
|----------|--------|
| research.md | ✓ Loaded |
| user-stories.md | [✓ Loaded or ✗ Not found] |
| personas.md | [✓ Loaded or ✗ Not found] |
| interview-notes.md | [✓ Loaded or ✗ Not found] |
| competitive-analysis.md | [✓ Loaded or ✗ Not found] |

These artifacts will inform the specification. Requirements from research.md will be mapped to functional requirements.
```

This confirmation helps users understand that their research is being used and provides transparency about which artifacts were found.

## Load Personas (if available)

Check if comprehensive persona profiles exist from `/doit.researchit`:

```bash
# Check for personas.md in the feature directory
ls specs/*/personas.md 2>/dev/null | head -5
```

**If personas.md exists for this feature**:

1. **Load personas.md** - Read the persona summary table and detailed profiles
2. **Extract persona data for matching**:
   - Parse the Persona Summary table for ID (P-001, P-002) and Name columns
   - Parse the Detailed Profiles section for each persona's Goals (primary and secondary) and Pain Points fields
   - Store as a list: `[{id: "P-001", name: "Developer Dana", role: "Senior Developer", archetype: "Power User", primary_goal: "...", pain_points: ["...", "..."], usage_context: "..."}, ...]`
   - These fields are the primary inputs for persona matching (see Persona Matching Rules below)
3. **Use personas for user story generation**:
   - Each user story MUST reference a persona ID in the header
   - Format: `### User Story N - [Title] (Priority: PN) | Persona: P-XXX`
   - Match user stories to the persona whose goals/pain points they address
4. **Reference personas in spec**: Add a "Personas Reference" link at the top of the generated spec:

   ```markdown
   **Personas**: [personas.md](personas.md)
   ```

**When generating user stories with personas**:

- Review each persona's primary goal and pain points
- Create user stories that directly address those goals/pain points
- Include the persona's name, ID, archetype, and primary goal in the story context
- After determining the matching persona, include the persona ID in the story header using the format from spec-template.md: `### User Story N - [Title] (Priority: PN) | Persona: P-NNN`
- In the story body, reference the persona's name, archetype, and primary goal to give developers immediate context without cross-referencing personas.md
- Example:

  ```markdown
  ### User Story 1 - Quick Task Creation (Priority: P1) | Persona: P-001

  As **Developer Dana (P-001)**, a Power User whose primary goal is rapid task entry,
  I want to create tasks with a single command so that I can stay in flow...
  ```

**If NO personas.md found**:

- Proceed normally without persona references
- Use generic "As a user..." format for user stories
- If the feature requires specific user types, use a default "Primary User" placeholder
- If `personas.md` exists but contains no valid persona entries (no P-NNN IDs found), treat as no personas available

**When No Personas Are Available**:

- Skip all persona matching rules below
- Generate stories using the standard header format without `| Persona: P-NNN` suffix
- Skip the traceability table update step
- Skip the persona coverage report
- Do NOT raise errors or warnings about missing personas — this is a valid state

## Persona Matching Rules (when personas loaded)

When generating user stories with persona context available, follow these matching rules in priority order to assign the most relevant persona to each story:

1. **Direct goal match**: If a story directly addresses a persona's primary goal, assign that persona. Confidence: High.
2. **Pain point match**: If a story addresses one of the persona's top 3 pain points, assign that persona. Confidence: High.
3. **Usage context match**: If a story fits the persona's described usage context but not a specific goal, assign that persona. Confidence: Medium.
4. **Role/archetype match**: If a story aligns with the persona's role or archetype but not specific goals, assign that persona. Confidence: Medium.
5. **Multi-persona**: If a story equally addresses the goals of 2 or more personas, list all relevant IDs comma-separated in the header: `| Persona: P-001, P-002`. In the story body, reference all matched personas. Limit multi-persona tagging to stories that genuinely serve multiple personas — most stories should map to a single primary persona.
6. **No match**: If no persona clearly matches, generate the story without a Persona tag. Flag it in the coverage report as "unmapped."

For each user story you generate, review the loaded personas and assign the persona whose goals/pain points are most directly addressed by the story.

### Update Persona Traceability

After generating all user stories with persona mappings:

1. Read the feature's `specs/{feature}/personas.md` file (if it exists)
2. Find the `## Traceability` → `### Persona Coverage` table
3. Replace the table content with current mappings:
   - For each persona, list all story IDs (from the spec) that reference it
   - Include personas with zero mapped stories (empty "User Stories Addressing" column) to signal coverage gaps
   - Set "Primary Focus" to the main theme of the mapped stories
4. Write the updated personas.md

This is a full replacement on each `/doit.specit` run — the table should always reflect the current spec state.

### Persona Coverage Report

After story generation and traceability update, display a Persona Coverage summary:

```markdown
## Persona Coverage

| Persona | Stories | Coverage |
| ------- | ------- | -------- |
| P-001 (Name) | US-001, US-003 | ✓ Covered |
| P-002 (Name) | US-002 | ✓ Covered |
| P-003 (Name) | — | ⚠ Underserved |
```

- Mark personas with ≥1 mapped story as "✓ Covered"
- Mark personas with 0 mapped stories as "⚠ Underserved"
- If any personas are underserved, add: "> ⚠ {N} persona(s) have no user stories mapped. Consider adding stories that address their goals."
- Only display this section when personas are available (skip when no personas loaded)

## Outline

The text the user typed after `/doit.doit` in the triggering message **is** the feature description. Assume you always have it available in this conversation even if `$ARGUMENTS` appears literally below. Do not ask the user to repeat it unless they provided an empty command.

Given that feature description, do this:

1. **Generate a concise short name** (2-4 words) for the branch:
   - Analyze the feature description and extract the most meaningful keywords
   - Create a 2-4 word short name that captures the essence of the feature
   - Use action-noun format when possible (e.g., "add-user-auth", "fix-payment-bug")
   - Preserve technical terms and acronyms (OAuth2, API, JWT, etc.)
   - Keep it concise but descriptive enough to understand the feature at a glance
   - Examples:
     - "I want to add user authentication" → "user-auth"
     - "Implement OAuth2 integration for the API" → "oauth2-api-integration"
     - "Create a dashboard for analytics" → "analytics-dashboard"
     - "Fix payment processing timeout bug" → "fix-payment-timeout"

2. **Check for existing branches before creating new one**:

   a. First, fetch all remote branches to ensure we have the latest information:

      ```bash
      git fetch --all --prune
      ```

   b. Find the highest feature number across all sources for the short-name:
      - Remote branches: `git ls-remote --heads origin | grep -E 'refs/heads/[0-9]+-<short-name>$'`
      - Local branches: `git branch | grep -E '^[* ]*[0-9]+-<short-name>$'`
      - Specs directories: Check for directories matching `specs/[0-9]+-<short-name>`

   c. Determine the next available number:
      - Extract all numbers from all three sources
      - Find the highest number N
      - Use N+1 for the new branch number

   d. Run the script `.doit/scripts/bash/create-new-feature.sh --json "$ARGUMENTS"` with the calculated number and short-name:
      - Pass `--number N+1` and `--short-name "your-short-name"` along with the feature description
      - Bash example: `.doit/scripts/bash/create-new-feature.sh --json "$ARGUMENTS" --json --number 5 --short-name "user-auth" "Add user authentication"`
      - PowerShell example: `.doit/scripts/bash/create-new-feature.sh --json "$ARGUMENTS" -Json -Number 5 -ShortName "user-auth" "Add user authentication"`

   **IMPORTANT**:
   - Check all three sources (remote branches, local branches, specs directories) to find the highest number
   - Only match branches/directories with the exact short-name pattern
   - If no existing branches/directories found with this short-name, start with number 1
   - You must only ever run this script once per feature
   - The JSON is provided in the terminal as output - always refer to it to get the actual content you're looking for
   - The JSON output will contain BRANCH_NAME and SPEC_FILE paths
   - For single quotes in args like "I'm Groot", use escape syntax: e.g 'I'\''m Groot' (or double-quote if possible: "I'm Groot")

3. Load `.doit/templates/spec-template.md` to understand required sections.

4. Follow this execution flow:

    1. Parse user description from Input
       If empty, check for recent research:
       ```bash
       # Find most recently modified research.md
       ls -t specs/*/research.md 2>/dev/null | head -1
       ```

       **If recent research found**:
       - Extract the feature name from the directory path (e.g., `specs/054-my-feature/research.md` → `054-my-feature`)
       - Present suggestion to user:
         ```markdown
         No feature specified. Did you mean to continue with **{feature-name}**?

         Research artifacts were recently created for this feature.

         - **Yes** - Continue with {feature-name}
         - **No** - Enter a new feature description
         ```
       - Wait for user response
       - If "Yes": Use the suggested feature name and load its research artifacts
       - If "No": Prompt user for new feature description

       **If NO recent research found**:
       ERROR "No feature description provided"
    2. Extract key concepts from description
       Identify: actors, actions, data, constraints
    3. For unclear aspects:
       - Make informed guesses based on context and industry standards
       - Only mark with [NEEDS CLARIFICATION: specific question] if:
         - The choice significantly impacts feature scope or user experience
         - Multiple reasonable interpretations exist with different implications
         - No reasonable default exists
       - **LIMIT: Maximum 3 [NEEDS CLARIFICATION] markers total**
       - Prioritize clarifications by impact: scope > security/privacy > user experience > technical details
    4. Fill User Scenarios & Testing section
       If no clear user flow: ERROR "Cannot determine user scenarios"
    5. Generate Functional Requirements
       Each requirement must be testable
       Use reasonable defaults for unspecified details (document assumptions in Assumptions section)
    6. Define Success Criteria
       Create measurable, technology-agnostic outcomes
       Include both quantitative metrics (time, performance, volume) and qualitative measures (user satisfaction, task completion)
       Each criterion must be verifiable without implementation details
    7. Identify Key Entities (if data involved)
    8. Return: SUCCESS (spec ready for planning)

5. Write the specification to SPEC_FILE using the template structure, replacing placeholders with concrete details derived from the feature description (arguments) while preserving section order and headings.

6. **Generate Mermaid Visualizations** (FR-001, FR-002, FR-003):

   After writing the spec content, generate visual diagrams to enhance understanding:

   a. **User Journey Visualization**:
      - Parse all user stories from the spec (### User Story N - [Title])
      - For each user story, extract the key action flow from acceptance scenarios
      - Generate a flowchart with one subgraph per user story
      - Use format: `US{N}_S[Start] --> US{N}_A[Action] --> US{N}_E[End]`
      - Replace the placeholder in `<!-- BEGIN:AUTO-GENERATED section="user-journey" -->` markers

      ```mermaid
      flowchart LR
          subgraph "User Story 1 - [Actual Title]"
              US1_S[User Starts] --> US1_A[Key Action] --> US1_E[Expected Outcome]
          end
          subgraph "User Story 2 - [Actual Title]"
              US2_S[User Starts] --> US2_A[Key Action] --> US2_E[Expected Outcome]
          end
      ```

   b. **Entity Relationships** (FR-002, FR-003):
      - Check if Key Entities section exists and has content
      - **IF Key Entities defined**:
        - Parse entity names and relationships from the Key Entities section
        - Generate an ER diagram showing entities and their relationships
        - Replace content in `<!-- BEGIN:AUTO-GENERATED section="entity-relationships" -->` markers
      - **IF NO Key Entities defined**:
        - **REMOVE the entire Entity Relationships section** (from `## Entity Relationships` to before `## Requirements`)
        - Do NOT leave an empty placeholder section

      ```mermaid
      erDiagram
          ENTITY1 ||--o{ ENTITY2 : "relationship description"

          ENTITY1 {
              string id PK
              string key_attribute
          }
      ```

   c. **Diagram Validation**:
      - Verify mermaid syntax is valid (proper diagram type, matching brackets)
      - Check node count does not exceed 20 per diagram (split into subgraphs if needed)
      - Ensure all entity names from Key Entities are represented

7. **Specification Quality Validation**: After writing the initial spec, validate it against quality criteria:

   a. **Create Spec Quality Checklist**: Generate a checklist file at `FEATURE_DIR/checklists/requirements.md` using the checklist template structure with these validation items:

      ```markdown
      # Specification Quality Checklist: [FEATURE NAME]
      
      **Purpose**: Validate specification completeness and quality before proceeding to planning
      **Created**: [DATE]
      **Feature**: [Link to spec.md]
      
      ## Content Quality
      
      - [ ] No implementation details (languages, frameworks, APIs)
      - [ ] Focused on user value and business needs
      - [ ] Written for non-technical stakeholders
      - [ ] All mandatory sections completed
      
      ## Requirement Completeness
      
      - [ ] No [NEEDS CLARIFICATION] markers remain
      - [ ] Requirements are testable and unambiguous
      - [ ] Success criteria are measurable
      - [ ] Success criteria are technology-agnostic (no implementation details)
      - [ ] All acceptance scenarios are defined
      - [ ] Edge cases are identified
      - [ ] Scope is clearly bounded
      - [ ] Dependencies and assumptions identified
      
      ## Feature Readiness
      
      - [ ] All functional requirements have clear acceptance criteria
      - [ ] User scenarios cover primary flows
      - [ ] Feature meets measurable outcomes defined in Success Criteria
      - [ ] No implementation details leak into specification
      
      ## Notes
      
      - Items marked incomplete require spec updates before `/doit.planit`
      ```

   b. **Run Validation Check**: Review the spec against each checklist item:
      - For each item, determine if it passes or fails
      - Document specific issues found (quote relevant spec sections)

   c. **Handle Validation Results**:

      - **If all items pass**: Mark checklist complete and proceed to step 6

      - **If items fail (excluding [NEEDS CLARIFICATION])**:
        1. List the failing items and specific issues
        2. Update the spec to address each issue
        3. Re-run validation until all items pass (max 3 iterations)
        4. If still failing after 3 iterations, document remaining issues in checklist notes and warn user

      - **If [NEEDS CLARIFICATION] markers remain**:
        1. Extract all [NEEDS CLARIFICATION: ...] markers from the spec
        2. **LIMIT CHECK**: If more than 3 markers exist, keep only the 3 most critical (by scope/security/UX impact) and make informed guesses for the rest
        3. For each clarification needed (max 3), present options to user in this format:

           ```markdown
           ## Question [N]: [Topic]
           
           **Context**: [Quote relevant spec section]
           
           **What we need to know**: [Specific question from NEEDS CLARIFICATION marker]
           
           **Suggested Answers**:
           
           | Option | Answer | Implications |
           |--------|--------|--------------|
           | A      | [First suggested answer] | [What this means for the feature] |
           | B      | [Second suggested answer] | [What this means for the feature] |
           | C      | [Third suggested answer] | [What this means for the feature] |
           | Custom | Provide your own answer | [Explain how to provide custom input] |
           
           **Your choice**: _[Wait for user response]_
           ```

        4. **CRITICAL - Table Formatting**: Ensure markdown tables are properly formatted:
           - Use consistent spacing with pipes aligned
           - Each cell should have spaces around content: `| Content |` not `|Content|`
           - Header separator must have at least 3 dashes: `|--------|`
           - Test that the table renders correctly in markdown preview
        5. Number questions sequentially (Q1, Q2, Q3 - max 3 total)
        6. Present all questions together before waiting for responses
        7. Wait for user to respond with their choices for all questions (e.g., "Q1: A, Q2: Custom - [details], Q3: B")
        8. Update the spec by replacing each [NEEDS CLARIFICATION] marker with the user's selected or provided answer
        9. Re-run validation after all clarifications are resolved

   d. **Update Checklist**: After each validation iteration, update the checklist file with current pass/fail status

8. Report completion with branch name, spec file path, checklist results, and readiness for the next phase (`/doit.planit`).

**NOTE:** The script creates and checks out the new branch and initializes the spec file before writing.

## Additional Reference

For the full set of sections that follow this playbook, see [reference.md](reference.md). Claude loads it on demand when the content is needed.
