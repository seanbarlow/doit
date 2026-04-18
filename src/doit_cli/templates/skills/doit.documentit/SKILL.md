---
name: doit.documentit
description: Organize, index, audit, and enhance project documentation aligned with scaffoldit conventions.
when_to_use: Use when the user wants to organize project docs, generate the documentation index, audit coverage, cleanup duplicates,
  or enhance command templates.
allowed-tools: Read Write Edit Glob Grep Bash
argument-hint: '[organize | index | audit | cleanup | enhance]'
---

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty).

## Load Project Context

Before proceeding, load the project context to inform your responses:

```bash
doit context show
```

**If the command fails or doit is not installed**: Continue without context, but note that alignment with project principles cannot be verified.

**Use loaded context to**:

- Reference constitution principles when making decisions
- Consider roadmap priorities
- Identify connections to related specifications

## Code Quality Guidelines

Before generating or modifying code:

1. **Search for existing implementations** - Use Glob/Grep to find similar functionality before creating new code
2. **Follow established patterns** - Match existing code style, naming conventions, and architecture
3. **Avoid duplication** - Reference or extend existing utilities rather than recreating them
4. **Check imports** - Verify required dependencies already exist in the project

**Context already loaded** (DO NOT read these files again):

- Constitution principles and tech stack
- Roadmap priorities
- Current specification
- Related specifications

## Artifact Storage

- **Temporary scripts**: Save to `.doit/temp/{purpose}-{timestamp}.sh` (or .py/.ps1)
- **Status reports**: Save to `specs/{feature}/reports/{command}-report-{timestamp}.md`
- **Create directories if needed**: Use `mkdir -p` before writing files
- Note: `.doit/temp/` is gitignored - temporary files will not be committed

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

Create a report showing proposed changes:

```markdown
# Documentation Migration Plan

**Generated**: [DATE]

## Proposed Changes

| Current Location | New Location | Reason |
| ---------------- | ------------ | ------ |
| path/to/file.md | docs/guides/file.md | Tutorial content detected |

## Directories to Create

- docs/features/
- docs/guides/
- docs/api/
- docs/templates/
- docs/assets/

## Confirmation Required

Proceed with migration? (y/n)
```

### 2.4 Execute Migration

**IMPORTANT**: Only proceed after user confirmation.

For each file to move:
1. Check if git is available: `git rev-parse --git-dir 2>/dev/null`
2. If git available: Use `git mv [source] [destination]` to preserve history
3. If git not available: Use standard file move
4. Create target directories if they don't exist
5. Report each move as it completes

### 2.5 Report Results

```text
Migration Complete:
- Files moved: X
- Directories created: Y
- Files unchanged: Z

Next steps:
- Run `/doit.documentit index` to update documentation index
```

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
4. Assign to category based on directory:
   - docs/features/ → Features
   - docs/guides/ → Guides
   - docs/api/ → API Reference
   - docs/templates/ → Templates
   - docs/ (root) → Other
```

### 3.3 Generate Index Content

Create categorized tables:

```markdown
<!-- BEGIN:AUTO-GENERATED section="documentation-index" -->

## Features

| Document | Description | Last Modified |
| -------- | ----------- | ------------- |
| [Feature Name](./features/feature.md) | First paragraph summary... | 2026-01-10 |

## Guides

| Document | Description | Last Modified |
| -------- | ----------- | ------------- |
| [Guide Name](./guides/guide.md) | First paragraph summary... | 2026-01-10 |

[... other categories ...]

<!-- END:AUTO-GENERATED -->
```

### 3.4 Update or Create Index

1. If `docs/index.md` exists:
   - Read existing file
   - Find content between `<!-- BEGIN:AUTO-GENERATED -->` and `<!-- END:AUTO-GENERATED -->`
   - Replace only that section, preserving all other content
2. If `docs/index.md` doesn't exist:
   - Create new file using template structure
   - Fill in auto-generated sections

### 3.5 Report Results

```text
Index Updated:
- Total files indexed: X
- Categories: Features (X), Guides (X), API (X), Templates (X), Other (X)
- Location: docs/index.md
```

---

## Step 4: Audit Documentation Health (FR-020 to FR-024)

### 4.1 Check for Broken Links

Parse all markdown files in docs/ for internal links:

```text
Link patterns to check:
- [text](relative/path.md)
- [text](./relative/path.md)
- [text](/absolute/path.md)
- ![alt](path/to/image.png)
```

For each link, verify the target file exists.

### 4.2 Check for Missing Headers

For each markdown file:
- Check if file starts with `# ` heading
- Flag files without proper title headers

### 4.3 Check Documentation Coverage

Cross-reference completed features with documentation:

```text
1. Scan specs/ for completed features (check for tasks.md with all [x])
2. For each completed feature, check if docs/features/[feature-name].md exists
3. Report features missing user documentation
```

### 4.4 Generate Audit Report (FR-023, FR-024)

```markdown
# Documentation Audit Report

**Generated**: [DATE]

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

| File | Issue | Suggestion |
| ---- | ----- | ---------- |
| docs/guide.md | Broken link to ./missing.md | Update or remove link |

### Warnings (Should Fix)

| File | Issue | Suggestion |
| ---- | ----- | ---------- |
| docs/api/endpoint.md | Missing # header | Add title heading |

### Info (Consider)

| File | Issue | Suggestion |
| ---- | ----- | ---------- |
| docs/old-doc.md | No internal links | Consider linking to related docs |

## Coverage Analysis

| Feature | Spec Status | User Docs | Status |
| ------- | ----------- | --------- | ------ |
| 008-roadmapit | Complete | Exists | ✅ |
| 007-cli-rename | Complete | Missing | ⚠️ |
```

---

## Step 5: Cleanup Redundant Documentation (FR-025 to FR-028)

### 5.1 Find Potential Duplicates

Compare files for similarity:

```text
Duplicate detection methods:
1. Exact title match (# heading)
2. Near-identical titles (fuzzy match)
3. First 500 characters identical
4. Same filename in different directories
```

### 5.2 Find Orphaned Files

Track all internal links across documentation:

```text
1. Build link graph: file → [files it links to]
2. Find files not linked from any other file
3. Exclude index.md and README.md from orphan check
4. Flag truly orphaned files
```

### 5.3 Generate Cleanup Suggestions (FR-027, FR-028)

```markdown
# Documentation Cleanup Suggestions

## Potential Duplicates

| File 1 | File 2 | Similarity | Suggestion |
| ------ | ------ | ---------- | ---------- |
| docs/setup.md | docs/guides/setup.md | 95% | Consolidate into guides/ |

## Orphaned Files

| File | Last Modified | Action |
| ---- | ------------- | ------ |
| docs/old-notes.md | 2025-06-01 | Review for deletion |

## Actions

For each suggestion, choose:
- [A]ccept - Apply the suggestion
- [R]eject - Keep files as-is
- [S]kip - Decide later

Enter choices (e.g., "A1 R2 S3"):
```

### 5.4 Apply Accepted Changes

Only make changes for accepted suggestions:
- For duplicates: Merge content, remove duplicate
- For orphans: Delete or move to archive based on user choice

---

## Additional Reference

For the full set of sections that follow this playbook, see [reference.md](reference.md). Claude loads it on demand when the content is needed.
