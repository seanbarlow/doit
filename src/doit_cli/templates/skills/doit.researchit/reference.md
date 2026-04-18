# doit.researchit — detailed reference

This file continues the playbook in [SKILL.md](SKILL.md) for sections that don't need to sit in the main context at all times.

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

## Error Recovery

### Session Interrupted

The research Q&A session was interrupted before all questions were answered.

**WARNING** | Your answers ARE preserved in the draft file. If the session is interrupted:

1. Check for a saved draft: `ls specs/{feature}/.research-draft.md`
2. If found, re-run `/doit.researchit {feature}` — it will offer to resume from where you left off
3. Choose "Resume" to continue from the last unanswered question
4. Verify: the session continues from the correct question

> Prevention: Save your work frequently by answering one question at a time

If the above steps don't resolve the issue: start a fresh session — your previous answers will be offered as a starting point.

### Draft File Corruption

The saved research draft has become unreadable or contains invalid data.

**ERROR** | Your draft answers may be partially lost. If the draft file is corrupted:

1. Check the draft file: `cat specs/{feature}/.research-draft.md`
2. If unreadable, back it up: `cp specs/{feature}/.research-draft.md specs/{feature}/.research-draft.md.bak`
3. Delete the corrupted draft: `rm specs/{feature}/.research-draft.md`
4. Re-run `/doit.researchit {feature}` to start a fresh session
5. Verify: the new session starts cleanly without errors

If the above steps don't resolve the issue: manually create research.md by answering the research template questions directly.

### Feature Directory Creation Failure

The directory for research artifacts could not be created.

**ERROR** | If the feature directory cannot be created:

1. Check directory permissions: `ls -la specs/`
2. Create the directory manually: `mkdir -p specs/{NNN-feature-name}/`
3. Verify write access: `touch specs/{NNN-feature-name}/test && rm specs/{NNN-feature-name}/test`
4. Re-run `/doit.researchit {feature}`
5. Verify: `ls specs/{NNN-feature-name}/` shows the directory exists

If the above steps don't resolve the issue: check filesystem permissions or disk space with `df -h .`

### Resume vs Fresh Start Conflict

Existing research artifacts were found but you're unsure whether to continue or start over.

**WARNING** | If existing research is found and you're unsure how to proceed:

1. Review the existing research: `cat specs/{feature}/research.md | head -20`
2. If the existing research is still relevant, choose "Resume" to add to it
3. If the research is outdated, choose "Start Fresh" — the old files will be backed up with `.bak` extension
4. Verify: after your choice, the session proceeds without errors

If the above steps don't resolve the issue: manually back up existing files and delete them, then start fresh.

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
