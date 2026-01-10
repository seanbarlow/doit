# Research: Doit CLI and Command Rename

**Date**: 2026-01-10
**Feature**: 007-doit-cli-rename

## Summary

This feature involves two major renaming efforts:
1. CLI tool branding: "Specify CLI" → "Doit CLI"
2. Slash command naming: `/doit.*` pattern → shorter action-oriented names

## Research Findings

### R-001: Command Naming Convention

**Question**: What naming pattern should the new commands follow?

**Decision**: Action-oriented verbs with "it" suffix

**Rationale**:
- Shorter names are faster to type and easier to remember
- The "it" suffix creates a consistent pattern (specit, planit, taskit)
- Names become intuitive action words: "spec it", "plan it", "task it"

**Alternatives Considered**:
- `/spec`, `/plan`, `/task` - Too generic, conflicts likely with other tools
- `/dospec`, `/doplan`, `/dotask` - Longer, less memorable
- `/s`, `/p`, `/t` - Too cryptic, hard to remember

**Command Mapping**:
| Old Command | New Command | Reasoning |
|-------------|-------------|-----------|
| /doit.specify | /doit.specit | "Spec it" - create specification |
| /doit.plan | /doit.planit | "Plan it" - create implementation plan |
| /doit.tasks | /doit.taskit | "Task it" - generate task list |
| /doit.implement | /doit.implementit | "Implement it" - execute implementation |
| /doit.test | /doit.testit | "Test it" - run tests |
| /doit.review | /doit.reviewit | "Review it" - code review |
| /doit.scaffold | /doit.scaffoldit | "Scaffold it" - generate project structure |
| /doit.constitution | UNCHANGED | Less frequent, explicit naming preferred |
| /doit.checkin | UNCHANGED | Less frequent, explicit naming preferred |

**Namespace Decision**: Keeping the `doit.` prefix ensures commands don't conflict with other spec-driven development tools or generic slash commands.

---

### R-002: Python Package Rename

**Question**: Should we rename `src/specify_cli/` to `src/doit_cli/`?

**Decision**: Yes, rename to `src/doit_cli/`

**Rationale**:
- Maintains consistency between package name and product name
- pyproject.toml already defines `name = "doit-cli"` and script `doit = ...`
- Only internal reference (`specify_cli:main`) needs updating
- Clean separation from legacy naming

**Files Affected**:
1. `src/specify_cli/__init__.py` → `src/doit_cli/__init__.py`
2. `pyproject.toml` - Update package path and entry point
3. Internal string references in the Python code (~35 occurrences)

---

### R-003: CLI Branding Updates

**Question**: What branding strings need to change in the Python CLI?

**Decision**: Update all user-facing strings

**Findings from code analysis**:

| Current | New | Location |
|---------|-----|----------|
| "Specify CLI" | "Doit CLI" | Docstring, help text |
| "Specify Project Setup" | "Doit Project Setup" | Setup banner |
| "Specify CLI Information" | "Doit CLI Information" | Info panel |
| "specify init" | "doit init" | Usage examples |
| "specify-cli" | "doit-cli" | Package references |
| "Initial commit from Specify template" | "Initial commit from Doit template" | Git commit message |
| "Initialize a new Specify project" | "Initialize a new Doit project" | Help text |

**Occurrences**: ~35 string replacements in `src/specify_cli/__init__.py`

---

### R-004: Documentation Scope

**Question**: Which documentation files need updates?

**Decision**: Update active docs, preserve historical specs

**Active Files to Update** (167 command references):
- `spec-driven.md` - Main documentation
- `.doit/templates/*.md` - All template files
- `templates/*.md` - Distribution templates
- `docs/*.md` - User documentation
- `README.md`, `CONTRIBUTING.md`, `AGENTS.md`
- `specs/007-*/` - Current feature

**Files to PRESERVE** (historical accuracy):
- `CHANGELOG.md` - Historical record
- `specs/001-*/ through specs/006-*/` - Completed features

---

### R-005: Command File Renaming

**Question**: How should command definition files be renamed?

**Decision**: Rename files to match new command names

**File Renames**:

| Current | New |
|---------|-----|
| `.doit/templates/commands/doit.specify.md` | `.doit/templates/commands/doit.specit.md` |
| `.doit/templates/commands/doit.plan.md` | `.doit/templates/commands/doit.planit.md` |
| `.doit/templates/commands/doit.tasks.md` | `.doit/templates/commands/doit.taskit.md` |
| `.doit/templates/commands/doit.implement.md` | `.doit/templates/commands/doit.implementit.md` |
| `.doit/templates/commands/doit.test.md` | `.doit/templates/commands/doit.testit.md` |
| `.doit/templates/commands/doit.review.md` | `.doit/templates/commands/doit.reviewit.md` |
| `.doit/templates/commands/doit.scaffold.md` | `.doit/templates/commands/doit.scaffoldit.md` |

**Unchanged**:
- `.doit/templates/commands/doit.checkin.md`
- `.doit/templates/commands/doit.constitution.md`

---

### R-006: Internal Command References

**Question**: What cross-references exist between commands?

**Decision**: Update all internal references to use new command names

**Patterns Found**:
- "Run `/doit.plan` next" → "Run `/planit` next"
- "Use `/doit.tasks` to generate" → "Use `/taskit` to generate"
- Workflow documentation references

**Estimated Impact**: ~50+ internal cross-references within command files

---

### R-007: Settings and Configuration

**Question**: Are there settings files that reference command names?

**Decision**: Update .claude/settings.json if present

**Findings**:
- Claude Code settings may reference skill names
- Local settings files should use new names
- No centralized config files found beyond pyproject.toml

---

## Technical Decisions Summary

| Decision | Choice | Risk Level |
|----------|--------|------------|
| Package rename | specify_cli → doit_cli | Low |
| Command naming | Action + "it" suffix | Low |
| Preserve commands | constitution, checkin | N/A |
| Historical docs | Preserve unchanged | N/A |
| File renames | Use git mv | Low |

## Open Questions

None - all clarifications resolved.

## Next Steps

1. Phase 1: Design the file structure changes
2. Generate tasks.md with ordered implementation steps
3. Execute implementation
