---
agent: true
description: Generate implementation plan from feature specification
---

# Doit Planit - Implementation Plan Generator

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty).

## Instructions

Generate an implementation plan from the feature specification. Follow these steps:

1. **Load the specification** from the current feature branch's `specs/<branch>/spec.md`
2. **Run setup script** `.doit/scripts/bash/setup-plan.sh --json` to create plan structure
3. **Generate plan.md** with:
   - Technical context (language, dependencies, storage, testing)
   - Architecture overview (Mermaid diagram)
   - Project structure
   - Constitution check (pass/fail gates)
   - Design artifacts list

4. **Generate supporting documents**:
   - `research.md` - Technical decisions and clarifications
   - `data-model.md` - Entity definitions and relationships
   - `quickstart.md` - Usage guide for the feature
   - `contracts/` - API/interface specifications

## Plan Template Structure

```markdown
# Implementation Plan: [FEATURE NAME]

**Branch**: `<branch>` | **Date**: YYYY-MM-DD | **Spec**: [spec.md](./spec.md)

## Summary
[Brief description of what will be implemented]

## Technical Context
**Language/Version**: [e.g., Python 3.11+]
**Primary Dependencies**: [libraries]
**Storage**: [database/file-based]
**Testing**: [framework]

## Architecture Overview
[Mermaid flowchart showing components]

## Project Structure
[Directory tree showing file locations]

## Next Steps
1. Run `#doit-taskit` to generate implementation tasks
```
