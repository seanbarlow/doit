# Quickstart: Tutorial Validation

**Feature**: 019-doit-tutorials
**Purpose**: Validate tutorials are complete and functional

## Tutorial 1: Greenfield Validation Checklist

Follow Tutorial 1 end-to-end and verify each checkpoint:

### Prerequisites Validation

- [ ] DoIt CLI installed and `doit --version` works
- [ ] Git installed and configured
- [ ] Claude Code or compatible AI IDE available
- [ ] GitHub account accessible (or `--skip-issues` noted)
- [ ] Python 3.11+ available

### Section-by-Section Validation

- [ ] **Installation**: Commands execute without errors
- [ ] **doit init**: Interactive prompts match documented examples
- [ ] **/doit.constitution**: Constitution file created with expected structure
- [ ] **/doit.scaffoldit**: Project structure matches documented output
- [ ] **/doit.specit**: Spec created, clarification questions appear as documented
- [ ] **/doit.planit**: Plan, research, and contracts generated
- [ ] **/doit.taskit**: Tasks.md created with proper structure
- [ ] **/doit.implementit**: At least 3 tasks complete successfully
- [ ] **/doit.reviewit**: Review feedback shown correctly
- [ ] **/doit.checkin**: PR created (or skip message if no GitHub)
- [ ] **/doit.testit**: Tests execute (or clear skip instructions)
- [ ] **/doit.roadmapit**: Roadmap updates work

### Outcome Validation

- [ ] User has a functional TaskFlow CLI project
- [ ] At least one feature is fully implemented
- [ ] GitHub issues created (or skipped with clear instructions)
- [ ] Pull request created (or skipped with clear instructions)
- [ ] User understands the complete DoIt workflow

### Time Check

- [ ] Tutorial completable in under 2 hours (SC-001)

---

## Tutorial 2: Existing Project Validation Checklist

Follow Tutorial 2 end-to-end and verify each checkpoint:

### Prerequisites Validation

- [ ] Existing project available (use Weather API sample or own project)
- [ ] DoIt CLI installed
- [ ] Git initialized in project

### Section-by-Section Validation

- [ ] **Preparation**: Backup recommendations clear
- [ ] **doit init**: Guidance for existing project answers clear
- [ ] **/doit.constitution**: Constitution reflects existing patterns
- [ ] **/doit.specit**: New feature spec created
- [ ] **/doit.planit**: Plan integrates with existing code
- [ ] **/doit.taskit**: Tasks reference existing files appropriately
- [ ] **/doit.implementit**: Implementation works with existing code
- [ ] **/doit.checkin**: Feature integrated into project

### Differences Section

- [ ] Clear explanation of what to skip (scaffoldit usually)
- [ ] Clear guidance on adapting workflow to existing structure
- [ ] Common pitfalls addressed

### Outcome Validation

- [ ] User has DoIt integrated into their existing project
- [ ] One new feature added using DoIt workflow
- [ ] User understands how to continue using DoIt

### Time Check

- [ ] Tutorial completable in under 90 minutes (SC-002)

---

## Cross-Tutorial Validation

### Content Quality

- [ ] All code blocks have syntax highlighting
- [ ] All commands are copy-paste ready
- [ ] Callout boxes (tips/warnings/notes) render correctly
- [ ] Mermaid diagrams render on GitHub
- [ ] Navigation (TOC, anchors) works

### Completeness

- [ ] Every DoIt command documented (FR-018)
- [ ] Every command shows: purpose, syntax, input, prompts, output (FR-026)
- [ ] Estimated completion times included (FR-023)
- [ ] Prerequisites checklists included (FR-024)

### Accessibility

- [ ] Alt text for any images (if used)
- [ ] Code blocks readable in screen readers
- [ ] No reliance on color alone for information

---

## Validation Sign-off

| Validator | Date | Tutorial 1 | Tutorial 2 | Notes |
| --------- | ---- | ---------- | ---------- | ----- |
|           |      | [ ] Pass   | [ ] Pass   |       |
