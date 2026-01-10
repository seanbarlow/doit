# Quickstart: Doit Documentit Command & Scaffoldit Enhancement

**Feature**: 009-doit-documentit-command
**Date**: 2026-01-10

## Prerequisites

- Claude Code or compatible AI coding agent installed
- Project initialized with Spec Kit (`specify init`)
- Existing doit commands in `.claude/commands/`

## Quick Usage

### Organize Documentation

```bash
# Analyze and reorganize docs/ structure
/doit.documentit organize
```

The command will:
1. Scan for documentation files across the project
2. Identify files outside standard locations
3. Propose moves to proper directories
4. Ask for confirmation before making changes

### Generate Documentation Index

```bash
# Create or update docs/index.md
/doit.documentit index
```

The command will:
1. Scan all markdown files in docs/
2. Extract titles and descriptions
3. Generate categorized navigation links
4. Preserve any manual content in existing index

### Audit Documentation Health

```bash
# Check for issues in documentation
/doit.documentit audit
```

The command will:
1. Validate all internal links
2. Check for missing headers
3. Identify undocumented features
4. Generate a report with severity levels

### Clean Up Redundant Docs

```bash
# Find duplicates and orphans
/doit.documentit cleanup
```

The command will:
1. Identify potential duplicate files
2. Find orphaned documentation
3. Suggest consolidation strategies
4. Allow selective cleanup

### Enhance Command Templates

```bash
# Review and improve templates
/doit.documentit enhance-templates
```

The command will:
1. Analyze command template clarity
2. Suggest missing examples
3. Check formatting consistency
4. Propose improvements

### Interactive Mode

```bash
# Show menu of all operations
/doit.documentit
```

## Tech Stack Documentation (via Scaffoldit)

When scaffolding a new project:

```bash
/doit.scaffoldit
```

After answering tech stack questions, the command now:
1. Creates `.doit/memory/tech-stack.md`
2. Documents chosen languages and versions
3. Records key libraries with rationale
4. Captures architecture decisions

## File Locations

| File | Purpose |
| ---- | ------- |
| `.claude/commands/doit.documentit.md` | Command definition |
| `.doit/memory/tech-stack.md` | Tech stack documentation |
| `docs/index.md` | Generated documentation index |
| `docs/features/` | Feature documentation |
| `docs/guides/` | User guides |
| `docs/api/` | API reference |
| `docs/templates/` | Template documentation |
| `docs/assets/` | Binary files (images, etc.) |

## Common Workflows

### New Project Setup

1. Run `/doit.scaffoldit` to scaffold project
2. Tech stack is captured in `.doit/memory/tech-stack.md`
3. Run `/doit.documentit organize` to create docs structure
4. Run `/doit.documentit index` to generate navigation

### Documentation Maintenance

1. Run `/doit.documentit audit` to check health
2. Fix any reported issues
3. Run `/doit.documentit cleanup` to remove redundancy
4. Run `/doit.documentit index` to update navigation

### Template Improvements

1. Run `/doit.documentit enhance-templates` to analyze
2. Review suggestions
3. Accept or modify proposed changes
