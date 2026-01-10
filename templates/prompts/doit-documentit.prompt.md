---
mode: agent
description: Organize, index, audit, and enhance project documentation
---

# Doit Documentit - Documentation Manager

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty).

## Outline

You are managing project documentation. This command supports multiple operations:

- `organize` - Reorganize documentation into standard structure
- `index` - Generate or update docs/index.md
- `audit` - Check documentation health (links, headers, coverage)
- `cleanup` - Identify duplicates and orphaned files
- `enhance-templates` - Suggest improvements to command templates

If no subcommand is provided, show an interactive menu.

## Subcommand Detection

Parse $ARGUMENTS to detect the operation:

1. **If empty**: Show interactive menu (step 1)
2. **If starts with "organize"**: Execute organize workflow (step 2)
3. **If starts with "index"**: Execute index workflow (step 3)
4. **If starts with "audit"**: Execute audit workflow (step 4)
5. **If starts with "cleanup"**: Execute cleanup workflow (step 5)
6. **If starts with "enhance-templates"**: Execute enhance workflow (step 6)

---

## Step 1: Interactive Menu (Default)

If no subcommand provided, present this menu:

```text
Documentation Management

Choose an operation:

1. organize         - Reorganize documentation into standard structure
2. index            - Generate or update docs/index.md
3. audit            - Check documentation health
4. cleanup          - Find duplicates and orphaned files
5. enhance-templates - Suggest template improvements

Enter choice (1-5) or operation name:
```

Wait for user selection, then execute the corresponding workflow.

---

## Step 2: Organize Documentation (FR-005 to FR-009)

### 2.1 Scan for Documentation Files

Search for markdown files in non-standard locations:

```text
Scanning locations:
- Root directory (*.md except README.md, CHANGELOG.md, LICENSE.md)
- Any folder not in docs/, specs/, .doit/, .claude/, node_modules/
- Look for: *.md, *.mdx files
```

### 2.2 Categorize Files

Assign each file to a category based on content analysis:

| Pattern | Category | Target Directory |
| ------- | -------- | ---------------- |
| Contains "# Feature:" or feature-like content | Features | docs/features/ |
| Contains "## Steps", "How to", tutorial content | Guides | docs/guides/ |
| Contains API endpoints, method signatures | API | docs/api/ |
| Contains template placeholders, scaffolding | Templates | docs/templates/ |
| Binary files (images, PDFs) | Assets | docs/assets/ |
| Other markdown | Other | docs/ |

### 2.3 Generate Migration Report

Create a report showing proposed changes and ask for confirmation.

### 2.4 Execute Migration (FR-008)

**IMPORTANT**: Only proceed after user confirmation.

For each file to move:
1. Check if git is available
2. If git available: Use `git mv` to preserve history
3. If git not available: Use standard file move
4. Create target directories if they don't exist

---

## Step 3: Generate Documentation Index (FR-010 to FR-014)

### 3.1 Read Template

Load `.doit/templates/docs-index-template.md` for structure reference.

### 3.2 Scan Documentation

Scan `docs/` directory and subdirectories:

```text
For each .md file found:
1. Extract title from first # heading (or use filename)
2. Extract description from first non-heading paragraph (max 80 chars)
3. Get file modification date
4. Assign to category based on directory
```

### 3.3 Generate Index Content

Create categorized tables with auto-generated markers.

### 3.4 Update or Create Index

Update only auto-generated sections, preserving all other content.

---

## Step 4: Audit Documentation Health (FR-020 to FR-024)

### 4.1 Check for Broken Links (FR-020)

Parse all markdown files in docs/ for internal links and verify targets exist.

### 4.2 Check for Missing Headers (FR-021)

Flag files without proper title headers.

### 4.3 Check Documentation Coverage (FR-022)

Cross-reference completed features with documentation.

### 4.4 Generate Audit Report (FR-023, FR-024)

```markdown
# Documentation Audit Report

## Summary

| Metric | Count |
| ------ | ----- |
| Total Documentation Files | X |
| Files with Issues | X |
| Broken Links | X |
| Missing Headers | X |
| Coverage Score | X% |

## Issues by Severity

### Errors (Must Fix)
[list of critical issues]

### Warnings (Should Fix)
[list of warnings]

### Info (Consider)
[list of suggestions]
```

---

## Step 5: Cleanup Redundant Documentation (FR-025 to FR-028)

### 5.1 Find Potential Duplicates (FR-025)

Compare files for similarity using title matching, content comparison, and filename analysis.

### 5.2 Find Orphaned Files (FR-026)

Track all internal links and find files not linked from any other file.

### 5.3 Generate Cleanup Suggestions (FR-027, FR-028)

Present suggestions for duplicates and orphans with accept/reject options.

### 5.4 Apply Accepted Changes

Only make changes for accepted suggestions.

---

## Step 6: Enhance Command Templates (FR-029 to FR-032)

### 6.1 Scan Command Templates

Read all files in `.claude/commands/` or `.github/prompts/` and check for required elements.

### 6.2 Identify Missing Elements (FR-029, FR-030)

Generate report showing which templates are missing frontmatter, examples, user input sections, or outlines.

### 6.3 Generate Improvement Suggestions (FR-031)

For each file with missing elements, suggest specific additions.

### 6.4 Apply Enhancements (FR-032)

For accepted suggestions, update the template files while preserving existing content.

---

## Validation Rules

Before any file modification:
1. **Always confirm** with user before moving, deleting, or modifying files
2. **Backup first** when modifying existing files
3. **Preserve markers** - never modify content outside auto-generated markers
4. **Check git status** before bulk operations

## Notes

- This command never modifies files in specs/ or .doit/templates/
- Binary files (images, PDFs) are cataloged but content is not analyzed
- Symlinks are followed for reading but flagged in audit
- Large files (>1MB markdown) are skipped with warning
