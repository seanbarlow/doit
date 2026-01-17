# Quickstart: Constitution Command Improvements

**Feature**: 020-constitution-improvements
**Date**: 2026-01-13

## Pre-Implementation Checklist

- [ ] Read current constitution command: `.claude/commands/doit.constitution.md`
- [ ] Review constitution template: `.doit/memory/constitution.md`
- [ ] Understand existing workflow and placeholders

## Implementation Checklist

### Phase 1: Dotfile Exclusion

- [ ] Add dotfile exclusion instructions to command template
- [ ] Specify exception for `.doit/memory/constitution.md`
- [ ] Document excluded patterns in command

### Phase 2: Greenfield Detection

- [ ] Add source file counting logic
- [ ] Define source extension list
- [ ] Add greenfield detection message
- [ ] Add branching logic for interactive mode

### Phase 3: Interactive Questioning

- [ ] Add Q1: Project purpose prompt
- [ ] Add Q2: Primary language prompt
- [ ] Add Q3: Frameworks prompt (with skip option)
- [ ] Add Q4: Libraries prompt (with skip option)
- [ ] Add Q5: Hosting platform prompt
- [ ] Add Q6: Database prompt (with "none" option)
- [ ] Add Q7: CI/CD prompt
- [ ] Add argument pre-fill logic
- [ ] Add constitution generation from answers

## Testing Checklist

### MT-001: Dotfile Exclusion

- [ ] Create test project with `.git`, `.vscode`, `.idea` folders
- [ ] Run `/doit.constitution`
- [ ] Verify no dotfolder content in analysis output

### MT-002: Greenfield Detection (Empty)

- [ ] Create empty project with only `.doit` initialized
- [ ] Run `/doit.constitution`
- [ ] Verify "Detected greenfield project" message appears
- [ ] Verify interactive mode starts

### MT-003: Existing Project Detection

- [ ] Use project with existing source files
- [ ] Run `/doit.constitution`
- [ ] Verify normal inference mode (no interactive prompts)

### MT-004: Argument Pre-fill

- [ ] Create greenfield project
- [ ] Run `/doit.constitution Python FastAPI PostgreSQL`
- [ ] Verify language, framework, database questions are skipped
- [ ] Verify remaining questions are asked

### MT-005: Complete Interactive Flow

- [ ] Create greenfield project
- [ ] Run `/doit.constitution`
- [ ] Answer all questions
- [ ] Verify constitution.md is created
- [ ] Verify all placeholders are filled
- [ ] Verify version is 1.0.0
- [ ] Verify date is today

## Validation Commands

```bash
# Check if constitution was created
cat .doit/memory/constitution.md

# Verify no placeholder tokens remain
grep -c "\[.*\]" .doit/memory/constitution.md
# Should return 0 for fully filled constitution

# Check version
grep "Version:" .doit/memory/constitution.md
```

## Success Criteria Verification

| SC | Criterion | How to Verify |
| -- | --------- | ------------- |
| SC-001 | Dotfolders not referenced | Check output for `.git`, `.vscode` mentions |
| SC-002 | Greenfield detection >95% | Test on 20+ empty projects |
| SC-003 | Interactive completion <5min | Time the flow |
| SC-004 | All fields populated | Grep for placeholders |
| SC-005 | No placeholder tokens | Grep returns 0 |
