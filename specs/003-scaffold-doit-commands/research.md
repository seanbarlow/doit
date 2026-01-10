# Research: Scaffold Doit Commands

**Feature**: 003-scaffold-doit-commands
**Date**: 2026-01-09

## Research Summary

### R-001: Files Requiring .specify → .doit Update

**Decision**: Update all 50 files referencing `.specify` to use `.doit`

**Files by Category**:

#### Doit Commands (8 files)
- `.claude/commands/doit.checkin.md`
- `.claude/commands/doit.constitution.md`
- `.claude/commands/doit.implement.md`
- `.claude/commands/doit.plan.md`
- `.claude/commands/doit.review.md`
- `.claude/commands/doit.scaffold.md`
- `.claude/commands/doit.specify.md`
- `.claude/commands/doit.tasks.md`
- `.claude/commands/doit.test.md`

#### Bash Scripts (5 files in .specify/scripts/bash/)
- `check-prerequisites.sh`
- `common.sh`
- `create-new-feature.sh`
- `setup-plan.sh`
- `update-agent-context.sh`

#### Templates (5 files in .specify/templates/)
- `agent-file-template.md` (to be deleted)
- `checklist-template.md` (to be deleted)
- `plan-template.md`
- `spec-template.md`
- `tasks-template.md`

#### Documentation (8 files)
- `README.md`
- `CHANGELOG.md`
- `CONTRIBUTING.md`
- `docs/upgrade.md`
- `docs/installation.md`
- `docs/local-development.md`
- `docs/quickstart.md`
- `spec-driven.md`

#### Root Scripts (6 files)
- `scripts/bash/setup-plan.sh`
- `scripts/bash/update-agent-context.sh`
- `scripts/bash/check-prerequisites.sh`
- `scripts/bash/create-new-feature.sh`
- `scripts/powershell/create-new-feature.ps1`
- `scripts/powershell/setup-plan.ps1`
- `scripts/powershell/update-agent-context.ps1`
- `scripts/powershell/check-prerequisites.ps1`

#### Legacy Templates (5 files in templates/)
- `templates/plan-template.md`
- `templates/vscode-settings.json`
- `templates/commands/clarify.md`
- `templates/commands/constitution.md`
- `templates/commands/specify.md`
- `templates/commands/analyze.md`

#### Source Code (1 file)
- `src/specify_cli/__init__.py`

#### Spec Files (Feature 001 - historical)
- `specs/001-doit-command-refactor/` (multiple files)

#### Spec Files (Feature 003 - current)
- `specs/003-scaffold-doit-commands/` (multiple files)

**Rationale**: Consistent naming with `doit` command convention

**Alternatives Rejected**:
- Keep `.specify` - Inconsistent with doit branding
- Use `.speckit` - Older naming convention

---

### R-002: Templates to Remove

**Decision**: Remove 2 unused templates

| Template | Reason for Removal |
|----------|-------------------|
| `agent-file-template.md` | Not referenced by any doit command |
| `checklist-template.md` | References non-existent `/doit.checklist` command |

**Rationale**: Clean up unused files to reduce confusion

---

### R-003: Templates to Keep

**Decision**: Keep 3 actively-used templates

| Template | Used By |
|----------|---------|
| `spec-template.md` | `/doit.specify` command |
| `plan-template.md` | `/doit.plan` command |
| `tasks-template.md` | `/doit.tasks` command |

---

### R-004: Command Templates to Create

**Decision**: Create 9 command templates in `.doit/templates/commands/`

| Command | Description |
|---------|-------------|
| `doit.checkin.md` | Feature completion and PR creation |
| `doit.constitution.md` | Project constitution management |
| `doit.implement.md` | Task implementation execution |
| `doit.plan.md` | Implementation planning workflow |
| `doit.review.md` | Code review workflow |
| `doit.scaffold.md` | Project scaffolding |
| `doit.specify.md` | Feature specification creation |
| `doit.tasks.md` | Task generation from plan |
| `doit.test.md` | Test execution and reporting |

**Rationale**: Enable scaffold command to generate complete doit workflow in new projects

**Alternatives Considered**:
- Copy from `.claude/commands/` directly: Rejected - templates may need placeholders
- Generate dynamically: Rejected - adds complexity, harder to maintain

---

### R-005: Scaffold Command Enhancement

**Decision**: Add command copying step to `doit.scaffold.md`

**Implementation Approach**:
1. Create `.doit/templates/commands/` directory with all 9 templates
2. Update scaffold command to:
   - Create `.claude/commands/` directory in target project
   - Copy all command templates to target
   - Preserve file permissions

**Rationale**: Ensures new projects have complete doit workflow immediately

---

### R-006: Folder Structure After Changes

**Decision**: New folder structure

```text
.doit/                           # Renamed from .specify
├── memory/
│   ├── constitution.md
│   └── roadmap_completed.md
├── scripts/
│   └── bash/
│       ├── check-prerequisites.sh
│       ├── common.sh
│       ├── create-new-feature.sh
│       ├── setup-plan.sh
│       └── update-agent-context.sh
└── templates/
    ├── commands/                # NEW - command templates
    │   ├── doit.checkin.md
    │   ├── doit.constitution.md
    │   ├── doit.implement.md
    │   ├── doit.plan.md
    │   ├── doit.review.md
    │   ├── doit.scaffold.md
    │   ├── doit.specify.md
    │   ├── doit.tasks.md
    │   └── doit.test.md
    ├── plan-template.md         # KEPT
    ├── spec-template.md         # KEPT
    └── tasks-template.md        # KEPT
    # REMOVED: agent-file-template.md
    # REMOVED: checklist-template.md
```

---

## Open Questions (Resolved)

| Question | Resolution |
|----------|------------|
| Should legacy `templates/` folder be removed? | Yes, it's redundant with `.doit/templates/` |
| Should `src/specify_cli/` be renamed? | Out of scope for this feature |
| How to handle existing projects? | Document migration in upgrade.md |
