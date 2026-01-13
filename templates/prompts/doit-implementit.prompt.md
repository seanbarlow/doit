---
agent: true
description: Execute implementation tasks from tasks.md
---

# Doit Implementit - Task Executor

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty).

## Instructions

Execute implementation tasks from tasks.md. Follow these steps:

1. **Run prerequisites check** `.doit/scripts/bash/check-prerequisites.sh --json --require-tasks --include-tasks`
2. **Check checklists** in `specs/<branch>/checklists/` - verify all pass before proceeding
3. **Load tasks.md** and parse task phases, dependencies, and execution order
4. **Verify project setup**:
   - Check/create .gitignore with appropriate patterns
   - Verify directory structure matches plan.md

5. **Execute tasks phase by phase**:
   - Complete each phase before moving to next
   - Respect dependencies (sequential vs parallel)
   - Mark completed tasks with `[x]` in tasks.md

6. **Progress tracking**:
   - Report progress after each task
   - Halt on non-parallel task failure
   - Provide clear error messages

7. **Generate completion summary**:
   ```
   ## Implementation Summary
   **Feature**: [name]
   **Branch**: [branch]

   ### Task Completion
   | Phase | Total | Completed | Status |

   ### Files Modified
   - [list of files]

   ### Next Steps
   - Run `#doit-reviewit` for code review
   - Run `#doit-testit` for testing
   ```
