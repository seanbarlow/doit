# doit.documentit — detailed reference

This file continues the playbook in [SKILL.md](SKILL.md) for sections that don't need to sit in the main context at all times.

## Step 6: Enhance Command Templates (FR-029 to FR-032)

### 6.1 Scan Command Templates

Read all files in `.claude/commands/`:

```text
For each command file, check:
1. YAML frontmatter present and valid
2. Description field exists
3. ## Examples section exists
4. ## User Input section exists
5. ## Outline section exists
6. Consistent heading structure
```

### 6.2 Identify Missing Elements (FR-029, FR-030)

```markdown
# Template Enhancement Report

## Files Analyzed

| File | Frontmatter | Examples | User Input | Outline | Score |
| ---- | ----------- | -------- | ---------- | ------- | ----- |
| doit.specit.md | ✅ | ✅ | ✅ | ✅ | 100% |
| doit.planit.md | ✅ | ❌ | ✅ | ✅ | 75% |
```

### 6.3 Generate Improvement Suggestions

For each file with missing elements:

```markdown
## Suggested Improvements

### doit.planit.md

**Missing: ## Examples section**

Suggested addition:

## Examples

```text
# Create implementation plan with tech stack
/doit.planit Use React with TypeScript for frontend, FastAPI for backend

# Plan with specific architecture
/doit.planit Microservices architecture with message queue
```

**Accept this suggestion? (y/n)**
```

### 6.4 Apply Enhancements

For accepted suggestions:
1. Read current file content
2. Insert suggested section at appropriate location
3. Preserve all existing content and functionality
4. Write updated file

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

---

## Error Recovery

### Missing Documentation Sources

The documentation generator could not find expected source files.

**ERROR** | If source files referenced by the documentation are not found:

1. Check that all source directories exist: `ls src/ docs/ specs/`
2. Verify the project structure matches what documentit expects
3. If files were recently moved or renamed, update the documentation configuration
4. Re-run `/doit.documentit` after fixing the source paths
5. Verify: `ls src/ docs/ specs/` confirms all expected source directories exist

> Prevention: Run `doit verify` before documentation generation to confirm project structure

If the above steps don't resolve the issue: manually specify source directories when running the documentation command.

### Index Generation Failure

The documentation index could not be generated from the available content.

**ERROR** | If the documentation index fails to generate:

1. Check if the documentation directory exists and has content: `ls docs/`
2. Verify no files have syntax errors that prevent parsing
3. Try generating documentation for a single file to isolate the issue
4. Re-run `/doit.documentit` after fixing any issues
5. Verify: `ls docs/index.md` confirms the index file was generated

> Prevention: Ensure all documentation files have valid markdown syntax before generating the index

If the above steps don't resolve the issue: manually create the index file based on the available documentation structure.

### Stale Cross-References

The documentation contains links to files or sections that no longer exist.

**WARNING** | If stale cross-references are detected:

1. Review the list of broken references in the documentation output
2. Update or remove references to files that have been moved or deleted
3. Check for renamed files that need their references updated
4. Re-run `/doit.documentit` to verify all references are valid
5. Verify: no broken reference warnings appear in the output

> Prevention: Update documentation references whenever you rename or move files

If the above steps don't resolve the issue: use `grep -r "](.*\.md)" docs/` to find all markdown links and manually verify each one.

---

## Next Steps

After completing this command, display a recommendation section based on the outcome:

### On Success (documentation organized or indexed)

Display the following at the end of your output:

```markdown
---

## Next Steps

**Documentation operation complete!**

**Recommended**: Continue with your development workflow:
- Run `/doit.specit [feature]` to create a new feature specification
- Run `/doit.implementit` to continue implementation work

**Alternative**: Run `/doit.documentit` again with a different operation (organize, index, audit, cleanup, enhance-templates).
```

### On Audit Issues Found

If the audit found documentation issues:

```markdown
---

## Next Steps

**Documentation audit found issues.**

**Recommended**: Address the issues listed above, then run `/doit.documentit audit` again to verify.
```
