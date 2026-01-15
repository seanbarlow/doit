# Doit Specit

Create or update the feature specification from a natural language feature description, with integrated ambiguity resolution and GitHub issue creation.

## User Input

Consider any arguments or options the user provides.

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

## Outline

The text the user typed after `/doit.doit` in the triggering message **is** the feature description. Assume you always have it available in this conversation even if `the user's input` appears literally below. Do not ask the user to repeat it unless they provided an empty command.

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

   d. Run the script `.doit/scripts/bash/create-new-feature.sh --json "the user's input"` with the calculated number and short-name:
      - Pass `--number N+1` and `--short-name "your-short-name"` along with the feature description
      - Bash example: `.doit/scripts/bash/create-new-feature.sh --json "the user's input" --json --number 5 --short-name "user-auth" "Add user authentication"`
      - PowerShell example: `.doit/scripts/bash/create-new-feature.sh --json "the user's input" -Json -Number 5 -ShortName "user-auth" "Add user authentication"`

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
       If empty: ERROR "No feature description provided"
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

## General Guidelines

## Quick Guidelines

- Focus on **WHAT** users need and **WHY**.
- Avoid HOW to implement (no tech stack, APIs, code structure).
- Written for business stakeholders, not developers.
- DO NOT create any checklists that are embedded in the spec. That will be a separate command.

### Section Requirements

- **Mandatory sections**: Must be completed for every feature
- **Optional sections**: Include only when relevant to the feature
- When a section doesn't apply, remove it entirely (don't leave as "N/A")

### For AI Generation

When creating this spec from a user prompt:

1. **Make informed guesses**: Use context, industry standards, and common patterns to fill gaps
2. **Document assumptions**: Record reasonable defaults in the Assumptions section
3. **Limit clarifications**: Maximum 3 [NEEDS CLARIFICATION] markers - use only for critical decisions that:
   - Significantly impact feature scope or user experience
   - Have multiple reasonable interpretations with different implications
   - Lack any reasonable default
4. **Prioritize clarifications**: scope > security/privacy > user experience > technical details
5. **Think like a tester**: Every vague requirement should fail the "testable and unambiguous" checklist item
6. **Common areas needing clarification** (only if no reasonable default exists):
   - Feature scope and boundaries (include/exclude specific use cases)
   - User types and permissions (if multiple conflicting interpretations possible)
   - Security/compliance requirements (when legally/financially significant)

**Examples of reasonable defaults** (don't ask about these):

- Data retention: Industry-standard practices for the domain
- Performance targets: Standard web/mobile app expectations unless specified
- Error handling: User-friendly messages with appropriate fallbacks
- Authentication method: Standard session-based or OAuth2 for web apps
- Integration patterns: RESTful APIs unless specified otherwise

### Success Criteria Guidelines

Success criteria must be:

1. **Measurable**: Include specific metrics (time, percentage, count, rate)
2. **Technology-agnostic**: No mention of frameworks, languages, databases, or tools
3. **User-focused**: Describe outcomes from user/business perspective, not system internals
4. **Verifiable**: Can be tested/validated without knowing implementation details

**Good examples**:

- "Users can complete checkout in under 3 minutes"
- "System supports 10,000 concurrent users"
- "95% of searches return results in under 1 second"
- "Task completion rate improves by 40%"

**Bad examples** (implementation-focused):

- "API response time is under 200ms" (too technical, use "Users see results instantly")
- "Database can handle 1000 TPS" (implementation detail, use user-facing metric)
- "React components render efficiently" (framework-specific)
- "Redis cache hit rate above 80%" (technology-specific)

---

## Integrated Ambiguity Scan

After creating the initial spec, perform a structured ambiguity scan using this 8-category taxonomy. For each category, assess status: Clear / Partial / Missing.

### Category Taxonomy

1. **Functional Scope & Behavior**
   - Core user goals & success criteria
   - Explicit out-of-scope declarations
   - User roles / personas differentiation

2. **Domain & Data Model**
   - Entities, attributes, relationships
   - Identity & uniqueness rules
   - Lifecycle/state transitions

3. **Interaction & UX Flow**
   - Critical user journeys / sequences
   - Error/empty/loading states
   - Accessibility or localization notes

4. **Non-Functional Quality Attributes**
   - Performance (latency, throughput targets)
   - Scalability assumptions
   - Security & privacy requirements

5. **Integration & External Dependencies**
   - External services/APIs
   - Data import/export formats

6. **Edge Cases & Failure Handling**
   - Negative scenarios
   - Conflict resolution

7. **Constraints & Tradeoffs**
   - Technical constraints
   - Explicit tradeoffs

8. **Terminology & Consistency**
   - Canonical glossary terms
   - Avoided synonyms

### Clarification Process

If Partial or Missing categories exist that require user input:

1. Generate up to **5 clarification questions** maximum
2. Each question must be answerable with:
   - Multiple-choice (2-5 options), OR
   - Short answer (≤5 words)
3. Present questions sequentially, one at a time
4. After each answer, integrate into the appropriate spec section
5. Ensure **no [NEEDS CLARIFICATION] markers remain** in final output

---

## GitHub Issue Integration (FR-048, FR-049)

After the spec is complete and validated, create GitHub issues if a remote is available.

### Issue Creation Process

1. **Detect GitHub Remote**:

   ```bash
   git remote get-url origin 2>/dev/null
   ```

   If no remote or not a GitHub URL, skip issue creation gracefully.

2. **Create Epic Issue**:
   - Title: `[Epic]: {Feature Name from spec}`
   - Labels: `epic`
   - Body: Summary section from spec + link to spec file
   - Store Epic issue number for linking

3. **Create Feature Issues for Each User Story**:
   - Title: `[Feature]: {User Story Title}`
   - Labels: `feature`, `priority:{P1|P2|P3}`
   - Body: User story content + acceptance scenarios
   - Add `Part of Epic #XXX` reference

4. **Skip Flag Option**:
   - If `--skip-issues` provided in arguments, skip GitHub issue creation
   - Example: `/doit.doit "my feature" --skip-issues`

5. **Graceful Fallback**:
   - If `gh` CLI not available: warn and continue without issues
   - If GitHub API fails: log error, continue with spec creation
   - Never fail the entire command due to GitHub issues

### Issue Creation Commands

```bash
# Create Epic
gh issue create --title "[Epic]: {FEATURE_NAME}" \
  --label "epic" \
  --body "$(cat <<'EOF'
## Summary
{SPEC_SUMMARY}

## Success Criteria
{SUCCESS_CRITERIA}

---
Spec file: `{SPEC_FILE_PATH}`
EOF
)"

# Create Feature for each user story
gh issue create --title "[Feature]: {USER_STORY_TITLE}" \
  --label "feature,priority:{PRIORITY}" \
  --body "$(cat <<'EOF'
## Description
{USER_STORY_CONTENT}

## Acceptance Scenarios
{ACCEPTANCE_SCENARIOS}

---
Part of Epic #{EPIC_NUMBER}
EOF
)"
```

### Output

Report created issues at the end:

```markdown
## GitHub Issues Created

- Epic: #{EPIC_NUMBER} - {EPIC_TITLE}
- Features:
  - #{FEATURE_1_NUMBER} - {FEATURE_1_TITLE} (P1)
  - #{FEATURE_2_NUMBER} - {FEATURE_2_TITLE} (P2)
```

If issues were skipped or failed, note the reason.

---

## Next Steps

After completing this command, display a recommendation section based on the outcome:

### On Success (spec created)

Display the following at the end of your output:

```markdown
---

## Next Steps

┌─────────────────────────────────────────────────────────────┐
│  Workflow Progress                                          │
│  ● specit → ○ planit → ○ taskit → ○ implementit → ○ checkin │
└─────────────────────────────────────────────────────────────┘

**Recommended**: Run `/doit.planit` to create an implementation plan for this feature.
```

### On Success with Clarifications Needed

If the spec contains [NEEDS CLARIFICATION] markers:

```markdown
---

## Next Steps

┌─────────────────────────────────────────────────────────────┐
│  Workflow Progress                                          │
│  ● specit → ○ planit → ○ taskit → ○ implementit → ○ checkin │
└─────────────────────────────────────────────────────────────┘

**Recommended**: Resolve N open questions in the spec before proceeding to planning.
```

### On Error

If the command fails (e.g., branch creation failed):

```markdown
---

## Next Steps

**Issue**: [Brief description of what went wrong]

**Recommended**: [Specific recovery action based on the error]
```
