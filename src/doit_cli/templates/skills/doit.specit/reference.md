# doit.specit — detailed reference

This file continues the playbook in [SKILL.md](SKILL.md) for sections that don't need to sit in the main context at all times.

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

## Error Recovery

### Branch Creation Failure

The feature branch could not be created from the current repository state.

**ERROR** | If the branch creation script fails:

1. Check if you have uncommitted changes: `git status`
2. If there are conflicts, stash your changes: `git stash`
3. Ensure the base branch is up to date: `git fetch origin && git pull`
4. Retry branch creation by re-running `/doit.specit`
5. Verify: `git branch --show-current` shows the new feature branch

> Prevention: Commit or stash pending changes before starting a new specification

If the above steps don't resolve the issue: manually create the branch with `git checkout -b {NNN-feature-name}` and create the spec file manually.

### GitHub API Authentication Error

GitHub issues could not be created because authentication failed.

**ERROR** | If GitHub issue creation fails with an authentication error:

1. Check your GitHub CLI authentication: `gh auth status`
2. If not authenticated, log in: `gh auth login`
3. Verify you have access to the repository: `gh repo view`
4. Re-run `/doit.specit` — it will retry issue creation
5. Verify: `gh issue list --limit 5` shows recent issues

> Prevention: Run `gh auth status` before starting specification work

If the above steps don't resolve the issue: add `--skip-issues` to skip GitHub issue creation and create issues manually later.

### File Write Permission Denied

The specification file could not be saved to the expected location.

**ERROR** | If the spec file cannot be written:

1. Check directory permissions: `ls -la specs/`
2. Verify the feature directory exists: `ls -d specs/{NNN-feature-name}/`
3. If the directory doesn't exist, create it: `mkdir -p specs/{NNN-feature-name}/`
4. Check disk space: `df -h .`
5. Verify: touch a test file in the directory: `touch specs/{NNN-feature-name}/test && rm specs/{NNN-feature-name}/test`

If the above steps don't resolve the issue: check if the filesystem is read-only or if you need elevated permissions.

### Missing Research Artifacts

Research artifacts from a prior session were expected but not found.

**WARNING** | If research.md or other artifacts are not found:

1. Check if research was completed: `ls specs/*/research.md`
2. If research exists in a different directory, verify the feature name matches
3. If no research exists, proceed without it — the specification will be generated from the feature description alone
4. Verify: the spec generation continues without errors

> Prevention: Run `/doit.researchit` before `/doit.specit` for richer specifications

If the above steps don't resolve the issue: provide a detailed feature description when running `/doit.specit` to compensate for missing research.

### Ambiguity Resolution Timeout

The interactive clarification session stalled or the user did not respond.

**WARNING** | If the ambiguity resolution Q&A session times out or stalls:

1. Note which question was being asked when the session stalled
2. Re-run `/doit.specit` — it will regenerate the spec and present clarification questions again
3. If you want to skip clarifications, the spec will use reasonable defaults (documented in the Assumptions section)
4. Verify: the generated spec.md has no more than 3 `[NEEDS CLARIFICATION]` markers

If the above steps don't resolve the issue: manually edit the spec.md to resolve any remaining `[NEEDS CLARIFICATION]` markers.

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
