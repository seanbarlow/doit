# Interview Notes: Error Recovery Patterns in All Commands

**Feature Branch**: `feature/058-error-recovery-patterns`
**Created**: 2026-03-26
**Derived From**: [research.md](research.md)

## Purpose

This document provides interview templates and captures notes from stakeholder interviews to deepen understanding of error recovery needs beyond the initial research session.

---

## Interview Schedule

| Interviewee | Role/Persona | Date | Status |
|-------------|--------------|------|--------|
| Developer (SDD power user) | P-001: Dev Dana | TBD | Pending |
| Product Owner (non-technical) | P-002: PO Pat | TBD | Pending |
| AI workflow tester | P-003: Agent Alex (proxy) | TBD | Pending |

---

## Interview Template: Developer (P-001: Dev Dana)

Use these questions when interviewing developers who use the doit SDD workflow regularly.

### Opening (2 min)

- Introduce yourself and the purpose of the interview
- Explain we're improving error handling documentation across all doit commands
- Confirm they're comfortable and get permission to take notes

### Context Questions (5 min)

1. How often do you use the doit SDD workflow? Which commands do you use most frequently?
2. How long have you been using the workflow?
3. Walk me through a typical workflow session — which commands do you run and in what order?

### Problem Exploration (10 min)

4. Tell me about a time when a doit command failed mid-workflow. What happened? What did you do?
5. Which commands have given you the most trouble with errors? Can you remember specific error messages?
6. When you encounter an error, what's your first instinct — check docs, check state files, restart, or ask for help?
7. Have you ever lost significant progress due to a workflow error? What was the impact?

### Goals and Needs (10 min)

8. If every command had perfect error recovery documentation, what would that look like for you?
9. What information do you need most when an error occurs — what happened, why, how to fix, or whether progress is saved?
10. What's the minimum you'd need to feel confident recovering from any workflow error?
11. Have you seen good error recovery documentation in other tools? What made it effective?

### Constraints and Concerns (5 min)

12. Would you prefer self-contained error recovery per command, or a shared reference you can look up?
13. Are there any errors where you think recovery shouldn't be attempted — just restart?
14. Do you trust AI assistants to handle error recovery autonomously, or do you want to be asked first?

### Closing (3 min)

15. Is there anything else about error handling in the workflow that we should know?
16. Can we follow up if we have additional questions?
17. Would you be interested in reviewing draft error recovery sections?

---

## Interview Template: Product Owner (P-002: PO Pat)

Use these questions when interviewing product owners or non-technical stakeholders who use researchit and specit.

### Opening (2 min)

- Introduce yourself and the purpose of the interview
- Explain we're making the workflow more resilient for non-technical users
- Confirm they're comfortable and get permission to take notes

### Context Questions (5 min)

1. Which doit commands do you typically use? (Likely researchit, specit, roadmapit)
2. How do you typically interact with the workflow — through an AI assistant, directly in terminal, or both?
3. How comfortable are you with command-line tools in general?

### Problem Exploration (10 min)

4. Have you ever encountered an error during a research or specification session? What happened?
5. When something goes wrong in the terminal, how does it make you feel? What do you usually do?
6. Have you ever had to ask a developer for help with a workflow error? How often?
7. What's the most frustrating part about encountering errors during interactive sessions (like researchit Q&A)?

### Goals and Needs (10 min)

8. When an error occurs, what would help you most — a simple explanation of what happened, reassurance that your work is saved, or step-by-step recovery instructions?
9. Would you prefer the AI assistant to handle errors silently and continue, or explain what happened and ask what you'd like to do?
10. What would make you feel confident enough to use the workflow without developer backup?

### Constraints and Concerns (5 min)

11. Is there anything about error recovery that would make you nervous? (e.g., running commands you don't understand)
12. Would you ever want to "undo" a recovery action if it didn't work?

### Closing (3 min)

13. Anything else we should consider about making the workflow more approachable?
14. Can we follow up with you later?

---

## Interview Template: AI Workflow Testing (P-003: Agent Alex proxy)

Use these questions when conducting structured testing of AI assistant behavior during errors. These should be observed through actual command execution rather than traditional interviews.

### Test Scenarios (30 min)

1. Execute each command with a missing prerequisite file — observe how the AI handles the error
2. Execute `implementit` and simulate a task failure mid-workflow — does the AI find recovery guidance?
3. Execute `specit` with an expired GitHub token — how does the AI diagnose and report?
4. Execute `researchit` and interrupt mid-session — does the AI attempt to save draft state?
5. Compare AI behavior on `fixit` (has error recovery) vs. `planit` (no error recovery) — what's the quality difference?

### Observation Criteria

- Does the AI find and follow documented recovery steps?
- Does the AI improvise when no recovery documentation exists? Is the improvisation correct?
- Does the AI clearly communicate error status to the user?
- Does the AI know when to escalate vs. attempt autonomous recovery?
- Is the AI's error handling consistent across commands?

---

## Interview Notes

*No interviews conducted yet. This section will be populated as interviews are completed.*

---

## Consolidated Insights

### Validated Assumptions

From research.md that need interview confirmation:

- [ ] Users lose significant progress when errors occur mid-workflow — Needs confirmation from developers
- [ ] Product owners find technical error messages intimidating — Needs confirmation from POs
- [ ] AI assistants produce inconsistent error handling without template guidance — Needs confirmation via structured testing
- [ ] The fixit error recovery pattern is the right model to replicate — Needs confirmation from all personas

### Challenged Assumptions

*To be populated after interviews.*

### New Discoveries

*To be populated after interviews.*

### Priority Adjustments

*To be populated after interviews.*

---

## Next Steps

- [ ] Schedule developer interview (P-001)
- [ ] Schedule product owner interview (P-002)
- [ ] Conduct AI behavior testing (P-003 proxy)
- [ ] Update research.md with new insights
- [ ] Revise user stories based on interview findings
- [ ] Proceed to `/doit.specit` when research is complete
