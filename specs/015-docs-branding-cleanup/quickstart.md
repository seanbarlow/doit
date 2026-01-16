# Quickstart: Documentation Branding Cleanup

**Feature**: 015-docs-branding-cleanup
**Date**: 2026-01-12

## Overview

Step-by-step guide to update all documentation files, removing legacy Spec Kit/specify branding and updating AI agent support.

## Prerequisites

- Git branch `015-docs-branding-cleanup` checked out
- Access to edit files in `docs/` directory
- Grep tool for verification

## Implementation Steps

### Phase 1: Primary Documentation Files

#### Step 1.1: Update docs/upgrade.md

1. Open `docs/upgrade.md`
2. Replace all occurrences:
   - `specify-cli` → `doit-toolkit-cli`
   - `specify` (CLI command) → `doit`
   - `git+https://github.com/github/spec-kit.git` → `doit-toolkit-cli`
   - `github.com/github/spec-kit` → `github.com/seanbarlow/doit`
   - `github.github.io/spec-kit` → `seanbarlow.github.io/doit`
   - `SPECIFY_FEATURE` → `DOIT_FEATURE`
3. Update AI agent examples to show only `--ai claude` and `--ai copilot`
4. Save and verify Markdown renders correctly

#### Step 1.2: Update docs/docfx.json

1. Open `docs/docfx.json`
2. Update globalMetadata section:

```json
"globalMetadata": {
  "_appTitle": "DoIt Documentation",
  "_appName": "DoIt",
  "_appFooter": "DoIt - A specification-driven development toolkit",
  "_enableSearch": true,
  "_disableContribution": false,
  "_gitContribute": {
    "repo": "https://github.com/seanbarlow/doit",
    "branch": "main"
  }
}
```

3. Validate JSON syntax with a linter
4. Save file

#### Step 1.3: Update docs/installation.md

1. Open `docs/installation.md`
2. Update supported AI agents list to show only:
   - Claude Code
   - GitHub Copilot
3. Remove any references to:
   - Gemini / gemini
   - Codebuddy / codebuddy
4. Update any remaining spec-kit/specify references
5. Save and verify

### Phase 2: Template Documentation

#### Step 2.1: Update docs/templates/commands.md

1. Replace all legacy branding references
2. Update command examples to use `doit` CLI

#### Step 2.2: Update docs/templates/index.md

1. Replace all legacy branding references

#### Step 2.3: Update docs/templates/root-templates.md

1. Replace all legacy branding references

### Phase 3: Feature Documentation

#### Step 3.1-3.5: Update Feature Docs

For each file in `docs/features/`:
- `006-docs-doit-migration.md` (13 occurrences)
- `003-scaffold-doit-commands.md` (8 occurrences)
- `update-doit-templates.md` (4 occurrences)
- `004-review-template-commands.md` (4 occurrences)
- `005-mermaid-visualization.md` (1 occurrence)

1. Open file
2. Replace legacy branding references
3. Note: Some references in 006-docs-doit-migration.md may be intentional historical documentation - preserve context
4. Save file

#### Step 3.6: Update docs/local-development.md

1. Replace any remaining legacy references

### Phase 4: Verification

#### Step 4.1: Verify Zero Legacy References

Run these commands and verify zero results:

```bash
# Should return no results
grep -ri "spec-kit" docs/
grep -ri "Spec Kit" docs/
grep -ri "specify" docs/ | grep -v "specify\|specified\|specifies"  # Filter English word usage
grep -ri "github/spec-kit" docs/
grep -ri "gemini" docs/
grep -ri "codebuddy" docs/
```

#### Step 4.2: Verify JSON Syntax

```bash
# Validate docfx.json
python -m json.tool docs/docfx.json > /dev/null && echo "Valid JSON"
```

#### Step 4.3: Verify Links

1. Check that all GitHub URLs point to `seanbarlow/doit`
2. Check that documentation links are not broken

### Phase 5: Commit Changes

```bash
git add docs/
git status  # Review changed files
git commit -m "docs: Remove legacy Spec Kit branding, update to DoIt

- Replace all spec-kit/specify references with doit/doit-toolkit-cli
- Update GitHub URLs to seanbarlow/doit
- Update supported AI agents to Claude and GitHub Copilot only
- Update docfx.json metadata with correct branding"
```

## Verification Checklist

- [ ] Zero `spec-kit` matches in docs/
- [ ] Zero `Spec Kit` matches in docs/
- [ ] Zero `specify` CLI references in docs/
- [ ] Zero `github/spec-kit` URLs in docs/
- [ ] Zero `gemini` references in docs/
- [ ] Zero `codebuddy` references in docs/
- [ ] docfx.json validates as valid JSON
- [ ] All GitHub URLs point to seanbarlow/doit

## Troubleshooting

### "specify" appears in grep results

The English word "specify" (verb meaning "to state explicitly") may appear legitimately. Check context:
- ❌ `specify init` - CLI command, should be `doit init`
- ✅ `You must specify the path` - English usage, leave as-is

### JSON validation fails

Check for:
- Missing commas between properties
- Trailing commas (not allowed in JSON)
- Unclosed quotes or brackets
