# Requirements Checklist: Constitution and Tech Stack Separation

**Feature**: 046-constitution-tech-stack-split
**Created**: 2026-01-22
**Status**: Pending Implementation

## User Story Coverage

### US1 - New Project Setup (P1)
- [ ] `doit init` creates `constitution.md` with only principles, governance, and quality standards
- [ ] `doit init` creates `tech-stack.md` with languages, frameworks, infrastructure, deployment
- [ ] Both files include cross-references to each other

### US2 - Migrate Existing Constitution (P1)
- [ ] `/doit.constitution cleanup` command extracts tech content to tech-stack.md
- [ ] Cleanup retains only principles, governance, and standards in constitution.md
- [ ] Backup created before modification
- [ ] User prompted when tech-stack.md already exists

### US3 - AI Agent Research Phase (P2)
- [ ] `/doit.planit` loads tech-stack.md for technical context
- [ ] `/doit.taskit` references tech-stack.md for implementation details
- [ ] Graceful fallback to constitution.md with warning for legacy projects

### US4 - Context Loading Optimization (P3)
- [ ] `/doit.specit` only loads constitution.md (no tech details needed)
- [ ] `/doit.planit` loads both constitution.md and tech-stack.md
- [ ] `doit context show` displays tech-stack.md as separate loadable source

## Functional Requirements

### File Structure (FR-001 to FR-003)
- [ ] FR-001: constitution.md contains only Purpose & Goals, Core Principles, Quality Standards, Development Workflow, Governance
- [ ] FR-002: tech-stack.md contains only Languages, Frameworks, Libraries, Infrastructure, Deployment, Environments
- [ ] FR-003: Both files include cross-reference navigation links

### Init Command Updates (FR-004 to FR-006)
- [ ] FR-004: `doit init` creates separate constitution.md and tech-stack.md files
- [ ] FR-005: Init workflow asks tech stack questions separately from principles questions
- [ ] FR-006: Templates exist in `.doit/templates/` for both files

### Cleanup Command (FR-007 to FR-010)
- [ ] FR-007: `/doit.constitution cleanup` command implemented
- [ ] FR-008: Cleanup creates backup before modification
- [ ] FR-009: Cleanup identifies tech sections via content analysis (headers + keywords)
- [ ] FR-010: Cleanup preserves custom sections that don't fit either category

### Script Updates (FR-011 to FR-013)
- [ ] FR-011: `/doit.planit` template references tech-stack.md
- [ ] FR-012: `/doit.taskit` template references tech-stack.md
- [ ] FR-013: Research scripts check for tech-stack.md with constitution.md fallback

### Context Integration (FR-014 to FR-016)
- [ ] FR-014: Context loading system recognizes tech-stack.md as loadable source
- [ ] FR-015: Context loading configurable to include/exclude tech-stack.md by command
- [ ] FR-016: `doit context show` displays tech-stack.md status separately

## Success Criteria

- [ ] SC-001: New projects have separated files 100% of the time
- [ ] SC-002: Cleanup correctly separates 95%+ of content
- [ ] SC-003: `/doit.planit` accesses tech-stack.md for all projects with separated files
- [ ] SC-004: Constitution.md size reduced by at least 30% after separation
- [ ] SC-005: Migration completes in under 2 minutes for typical projects
- [ ] SC-006: Zero data loss during migration (backup + content preserved)

## Edge Cases

- [ ] Constitution.md with no tech sections: Cleanup reports "no changes needed"
- [ ] User declines tech-stack.md during init: Tech stack stored in constitution.md (backward compatible)
- [ ] Partial migrations with unclear content: Unclear content stays with comment marker for review

## Quality Gates

- [ ] All unit tests pass
- [ ] Integration tests cover all user stories
- [ ] Templates validated with sample projects
- [ ] Documentation updated (tutorials, reference)
- [ ] Pre-commit hooks pass
