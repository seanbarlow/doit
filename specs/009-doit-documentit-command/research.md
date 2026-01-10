# Research: Doit Documentit Command & Scaffoldit Enhancement

**Feature**: 009-doit-documentit-command
**Date**: 2026-01-10
**Status**: Complete

## Executive Summary

This research validates the technical approach for implementing `/doit.documentit` and enhancing `/doit.scaffoldit`. All NEEDS CLARIFICATION items have been resolved through analysis of existing patterns and best practices.

## Research Areas

### 1. Existing Command Patterns

**Finding**: Analyzed existing doit commands (roadmapit, scaffoldit, checkin) to understand established patterns.

| Pattern | Implementation | Source |
| ------- | -------------- | ------ |
| YAML Frontmatter | `description`, `handoffs` fields | All command files |
| User Input Section | `$ARGUMENTS` placeholder | doit.roadmapit.md |
| Outline Structure | Numbered steps with sub-sections | doit.scaffoldit.md |
| File Operations | Read/write to .doit/memory/ | doit.roadmapit.md |
| Template Usage | Copy from .doit/templates/ | doit.scaffoldit.md |

**Decision**: Follow same structure for doit.documentit.md command file.

### 2. Documentation Structure Best Practices

**Finding**: Research on documentation organization patterns from industry standards.

| Convention | Description | Adoption |
| ---------- | ----------- | -------- |
| docs/ root folder | Standard location for user-facing documentation | Recommended |
| features/ subfolder | Feature-specific documentation | Common in multi-feature projects |
| guides/ subfolder | How-to guides and tutorials | Standard practice |
| api/ subfolder | API reference documentation | Common for libraries/services |
| assets/ subfolder | Binary files (images, diagrams) | Universal practice |
| index.md | Main navigation/entry point | DocFX, MkDocs, GitHub Pages |

**Decision**: Adopt standard 5-folder structure: features, guides, api, templates, assets.

### 3. Auto-Generated Marker Pattern

**Finding**: Existing templates use markers to preserve manual content during regeneration.

```markdown
<!-- BEGIN:AUTO-GENERATED section="name" -->
[generated content]
<!-- END:AUTO-GENERATED -->
```

**Source**: spec-template.md, plan-template.md (user journey, entity relationships)

**Decision**: Use same marker pattern for index.md auto-generated sections.

### 4. Tech Stack Documentation Format

**Finding**: Analyzed constitution.md template for existing tech stack structure.

Existing sections in constitution.md:
- Languages
- Frameworks
- Libraries
- Infrastructure (Hosting, Cloud Provider, Database)
- Deployment (CI/CD, Strategy, Environments)

**Gap**: Constitution captures principles but not specific version numbers or implementation decisions made during scaffolding.

**Decision**: Create separate tech-stack.md that captures:
- Specific versions chosen
- Key library selections with rationale
- Architecture decisions (why framework X over Y)
- Integration patterns defined

### 5. Link Analysis Approach

**Finding**: Markdown internal link formats to detect and validate.

| Link Type | Pattern | Example |
| --------- | ------- | ------- |
| Relative file | `[text](path/file.md)` | `[Guide](./guides/setup.md)` |
| Anchor link | `[text](#heading)` | `[Section](#overview)` |
| Absolute path | `[text](/path/file.md)` | `[Home](/docs/index.md)` |
| Image reference | `![alt](path/image.png)` | `![Logo](./assets/logo.png)` |

**Decision**: Support all link types, report broken links by category.

### 6. Duplicate Detection Strategy

**Finding**: Options for identifying similar/duplicate content.

| Approach | Pros | Cons |
| -------- | ---- | ---- |
| Exact title match | Simple, fast | Misses renamed duplicates |
| Content similarity | Thorough | Complex, may false positive |
| Header structure | Good for templates | Misses content changes |
| File path pattern | Quick categorization | Misses misplaced files |

**Decision**: Use multi-factor approach:
1. Check file titles (# heading) for near-matches
2. Flag files with identical first 500 characters
3. Report files in same category covering similar topics

### 7. Scaffoldit Command Count

**Finding**: Current scaffoldit copies 10 commands. Adding documentit makes 11.

Commands after this feature:
1. doit.checkin.md
2. doit.constitution.md
3. doit.documentit.md (NEW)
4. doit.implementit.md
5. doit.planit.md
6. doit.reviewit.md
7. doit.roadmapit.md
8. doit.scaffoldit.md
9. doit.specit.md
10. doit.taskit.md
11. doit.testit.md

**Decision**: Update scaffoldit documentation from "10 commands" to "11 commands".

### 8. Subcommand Design

**Finding**: User story analysis reveals 5 distinct operations.

| Subcommand | Purpose | User Story |
| ---------- | ------- | ---------- |
| `organize` | Move files to proper locations | US1 |
| `index` | Generate/update docs/index.md | US2 |
| `audit` | Check coverage, broken links | US4 |
| `cleanup` | Find duplicates, orphans | US5 |
| `enhance-templates` | Improve command templates | US6 |

**Decision**: Support all 5 subcommands. Default (no args) shows interactive menu.

## Technical Decisions Summary

| Decision | Choice | Rationale |
| -------- | ------ | --------- |
| Command Structure | YAML frontmatter + Outline | Matches existing commands |
| Doc Structure | 5-folder hierarchy | Industry standard |
| Index Preservation | Auto-generated markers | Protects manual content |
| Tech Stack Location | `.doit/memory/tech-stack.md` | Follows memory folder pattern |
| Link Validation | Regex-based parse | Simple, reliable |
| Duplicate Detection | Multi-factor | Balances accuracy and simplicity |
| Subcommand Count | 5 operations | Maps 1:1 with user stories |
| Command Total | 11 commands | Adding documentit to 10 existing |

## Resolved Clarifications

All NEEDS CLARIFICATION items from spec have been resolved:

1. **Doc structure alignment**: Align with scaffoldit-defined conventions (FR-006) ✅
2. **Binary file handling**: Catalog but don't modify; move to docs/assets/ if misplaced ✅
3. **Index preservation**: Use auto-generated markers (FR-011) ✅
4. **Tech stack location**: `.doit/memory/tech-stack.md` (FR-015) ✅
5. **Symlink handling**: Follow for reading, flag in audit (Edge case documented) ✅

## References

- `.claude/commands/doit.roadmapit.md` - Command pattern reference
- `.claude/commands/doit.scaffoldit.md` - Template copy pattern reference
- `.doit/templates/spec-template.md` - Auto-generated marker pattern
- `docs/features/008-doit-roadmapit-command.md` - Feature doc format reference
