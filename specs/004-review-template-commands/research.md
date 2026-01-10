# Research: Review Template Commands

**Feature**: 004-review-template-commands
**Date**: 2026-01-10
**Status**: Complete

## Research Questions

### RQ-001: What legacy templates exist in templates/commands/?

**Question**: Identify all legacy speckit templates that need to be removed.

**Findings**:

| File | Size | Contains "speckit" |
|------|------|-------------------|
| analyze.md | 7,250 bytes | Yes |
| checklist.md | 16,870 bytes | Yes |
| clarify.md | 11,408 bytes | Yes |
| constitution.md | 5,180 bytes | Yes |
| implement.md | 7,601 bytes | Yes |
| plan.md | 3,274 bytes | Yes |
| specify.md | 12,786 bytes | Yes |
| tasks.md | 6,388 bytes | Yes |
| taskstoissues.md | 1,187 bytes | No |

**Decision**: All 9 files will be removed. 8 of 9 contain "speckit" references.

---

### RQ-002: What doit templates exist as replacements?

**Question**: Confirm all 9 doit templates are available in `.doit/templates/commands/`.

**Findings**:

| File | Size | Purpose |
|------|------|---------|
| doit.checkin.md | 6,347 bytes | Finalize feature, create PR |
| doit.constitution.md | 8,131 bytes | Create/update project constitution |
| doit.implement.md | 8,664 bytes | Execute implementation tasks |
| doit.plan.md | 3,577 bytes | Generate implementation plan |
| doit.review.md | 5,535 bytes | Review code and run manual tests |
| doit.scaffold.md | 8,764 bytes | Generate project structure |
| doit.specify.md | 16,505 bytes | Create feature specification |
| doit.tasks.md | 7,079 bytes | Generate task breakdown |
| doit.test.md | 5,713 bytes | Execute automated tests |

**Decision**: All 9 doit templates are present and ready to copy.

---

### RQ-003: Are there any path reference issues in doit templates?

**Question**: Do any doit templates still reference `.specify/` instead of `.doit/`?

**Findings**: Verified via grep search - zero `.specify/` references found in `.doit/templates/commands/`.

**Decision**: Templates are clean and ready for distribution.

---

### RQ-004: Template naming convention mapping

**Question**: How do legacy names map to new doit names?

**Findings**:

| Legacy Template | Doit Equivalent | Notes |
|-----------------|-----------------|-------|
| analyze.md | (removed) | No direct equivalent |
| checklist.md | (removed) | Functionality in doit.review.md |
| clarify.md | (removed) | Functionality in doit.specify.md |
| constitution.md | doit.constitution.md | Direct replacement |
| implement.md | doit.implement.md | Direct replacement |
| plan.md | doit.plan.md | Direct replacement |
| specify.md | doit.specify.md | Direct replacement |
| tasks.md | doit.tasks.md | Direct replacement |
| taskstoissues.md | (removed) | No direct equivalent |

**Decision**: Not a 1:1 mapping. The doit suite has 9 commands with different organization. Replace entire directory contents.

---

## Alternatives Considered

### Alternative 1: In-place editing of legacy templates

**Rejected because**: The legacy templates have fundamentally different structure and references. Full replacement is cleaner than trying to modify each file.

### Alternative 2: Keep both template sets

**Rejected because**: Creates confusion about which templates to use. Single authoritative source is better for maintainability.

## Risks and Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| External projects depend on legacy template names | Low | Medium | Out of scope per spec - no external dependencies assumed |
| Incomplete file copy | Low | High | Verify file count and content match after copy |

## Conclusion

This is a straightforward file replacement operation:

1. Remove all 9 files from `templates/commands/`
2. Copy all 9 files from `.doit/templates/commands/` to `templates/commands/`
3. Verify content matches between directories

No clarifications needed. Ready for Phase 1.
