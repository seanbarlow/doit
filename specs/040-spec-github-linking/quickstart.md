# Quickstart: GitHub Issue Auto-linking

**Feature**: 040-spec-github-linking
**Audience**: Developers using the doit CLI

## Overview

This feature automatically links specification files to GitHub epics during spec creation. When you run `/doit.specit`, the system searches the roadmap for matching items, retrieves the GitHub epic, and creates bidirectional links.

## Prerequisites

1. **GitHub CLI installed and authenticated**:

   ```bash
   gh auth status
   ```

   If not authenticated, run:

   ```bash
   gh auth login
   ```

2. **Repository with GitHub remote configured**:

   ```bash
   git remote get-url origin
   # Should return: git@github.com:owner/repo.git
   ```

3. **Roadmap with GitHub epics** (created via `doit roadmapit add`):

   ```bash
   cat .doit/memory/roadmap.md
   # Should contain entries with GitHub issue numbers
   ```

## Basic Usage

### 1. Create Spec with Auto-linking

```bash
/doit.specit "GitHub Issue Auto-linking"
```

**What happens**:

1. System searches `.doit/memory/roadmap.md` for matching item
2. Finds roadmap item with GitHub epic #123
3. Creates spec file at `specs/040-spec-github-linking/spec.md`
4. Adds epic reference to spec frontmatter:
   ```yaml
   Epic: "[#123](https://github.com/owner/repo/issues/123)"
   Epic URL: "https://github.com/owner/repo/issues/123"
   Priority: P1
   ```
5. Updates GitHub epic #123 description:
   ```markdown
   ## Specification
   - `specs/040-spec-github-linking/spec.md`
   ```

**Expected output**:

```
✓ Matched roadmap item: "GitHub Issue Auto-linking in Spec Creation" (100% match)
✓ Found GitHub epic: #123
✓ Created spec: specs/040-spec-github-linking/spec.md
✓ Updated epic #123 with spec reference
```

### 2. Create Spec Without GitHub Linking

If you want to skip GitHub integration:

```bash
/doit.specit "My Feature" --skip-github
```

This creates the spec file without attempting any GitHub operations.

### 3. Handle Multiple Matches

If your feature name matches multiple roadmap items:

```bash
/doit.specit "Issue Linking"
```

**System response**:

```
Multiple roadmap items found:

1. GitHub Issue Auto-linking in Spec Creation (95% match)
2. Issue Template Management (87% match)
3. Cross-repository Issue Linking (82% match)

Select an item (1-3) or 0 to skip:
```

Enter the number of the correct item or 0 to create spec without linking.

### 4. Create Epic When Missing (P3 Feature)

If your roadmap item doesn't have a GitHub epic yet:

```bash
$ /doit.specit "New Feature Without Epic"

✓ Matched roadmap item: "New Feature Without Epic" (100% match)
⚠ No GitHub epic found for this roadmap item

Would you like to create a GitHub epic for tracking? (Y/n):
```

Press Enter (or type 'Y') to create the epic:

```bash
✓ GitHub epic created and linked successfully!
  - Created epic: [#999](https://github.com/owner/repo/issues/999)
  - Roadmap match: "New Feature Without Epic" (100% similarity)
  - Priority: P2
  - Roadmap.md updated with epic reference
  - Spec frontmatter updated with epic reference
  - GitHub epic updated with spec file path

Next: Run /doit.planit to create implementation plan
```

Or type 'n' to skip epic creation:

```bash
ℹ Roadmap match found without GitHub epic
  - Matched: "New Feature Without Epic" (100% similarity)
  - Epic creation skipped by user
  - You can manually create an epic later and link with: `doit spec link`
```

## Advanced Usage

### Link Existing Spec to Epic

To manually link an existing spec:

```bash
doit spec link specs/040-spec-github-linking
```

This updates both the spec frontmatter and GitHub epic description.

### Unlink Spec from Epic

To remove the epic reference:

```bash
doit spec unlink specs/040-spec-github-linking
```

This removes the epic fields from spec frontmatter and removes the spec path from the GitHub epic.

## Integration with Workflow

This feature integrates seamlessly with the standard doit workflow:

```bash
# 1. Add feature to roadmap with GitHub epic
doit roadmapit add "My Feature" --priority P1 --github

# 2. Create spec (auto-links to epic created in step 1)
/doit.specit "My Feature"

# 3. Continue with planning
/doit.planit

# 4. Create tasks
/doit.taskit

# 5. Implement
/doit.implementit

# 6. Check in (epic is automatically updated with PR link)
/doit.checkin
```

## Troubleshooting

### Error: "GitHub CLI not found"

**Cause**: `gh` CLI is not installed

**Solution**:

```bash
# macOS
brew install gh

# Linux
sudo apt install gh

# Windows
winget install GitHub.cli
```

Then authenticate:

```bash
gh auth login
```

### Error: "No GitHub remote configured"

**Cause**: Repository doesn't have a GitHub remote

**Solution**:

```bash
git remote add origin git@github.com:owner/repo.git
```

### Warning: "GitHub linking failed: API rate limit exceeded"

**Cause**: You've made too many GitHub API requests (5,000/hour limit)

**Solution**: Wait an hour or create spec without linking:

```bash
/doit.specit "My Feature" --skip-github
```

Then retry linking later:

```bash
doit spec link specs/###-my-feature
```

### Error: "Epic #123 is closed"

**Cause**: The roadmap references a closed GitHub epic

**Solution**: Choose one of:

1. Create a new epic: Confirm when prompted "Create a new epic?"
2. Skip linking: Answer "No" to epic creation prompt
3. Reopen the epic on GitHub if it was closed incorrectly

### Spec Not Found in Epic Description

**Cause**: Spec file was renamed/moved after linking

**Solution**:

```bash
/doit.specit --update-links
```

This refreshes all spec-epic links with current file paths.

## Configuration

### Change Fuzzy Match Threshold

Edit `.doit/config/linking.yaml`:

```yaml
fuzzy_match:
  threshold: 0.8  # Default: 80% similarity
  max_candidates: 3  # Max items to show in selection prompt
```

### Disable Auto-linking by Default

Edit `.doit/config/linking.yaml`:

```yaml
auto_link:
  enabled: false  # Require --link flag to enable
```

Then use `--link` flag to explicitly enable:

```bash
/doit.specit "My Feature" --link
```

## Examples

### Example 1: Happy Path

```bash
$ /doit.specit "User Authentication"

✓ Matched roadmap item: "User Authentication System" (95% match)
✓ Found GitHub epic: #456
✓ Created spec: specs/045-user-auth/spec.md
✓ Updated epic #456 with spec reference

Next: Run /doit.planit to create implementation plan
```

**Spec frontmatter**:

```yaml
Feature: "User Authentication System"
Branch: "[045-user-auth]"
Created: "2026-01-22"
Status: "Draft"
Epic: "[#456](https://github.com/owner/repo/issues/456)"
Epic URL: "https://github.com/owner/repo/issues/456"
Priority: P1
```

**Epic #456 description**:

```markdown
# User Authentication System

Implement secure user authentication with OAuth 2.0 and JWT tokens.

## Specification

- `specs/045-user-auth/spec.md`
```

### Example 2: Multiple Specs per Epic

```bash
$ /doit.specit "User Authentication V2"

✓ Matched roadmap item: "User Authentication System V2" (100% match)
✓ Found GitHub epic: #456 (also used by specs/045-user-auth/spec.md)
✓ Created spec: specs/047-user-auth-v2/spec.md
✓ Updated epic #456 with spec reference
```

**Epic #456 description** (updated):

```markdown
# User Authentication System

Implement secure user authentication with OAuth 2.0 and JWT tokens.

## Specification

- `specs/045-user-auth/spec.md`
- `specs/047-user-auth-v2/spec.md`
```

### Example 3: Offline Development

```bash
$ /doit.specit "Offline Feature"

✓ Matched roadmap item: "Offline Feature"
✗ GitHub API unreachable (network error)
✓ Created spec: specs/048-offline-feature/spec.md
⚠ Spec created successfully, but GitHub linking failed

Retry linking later: doit spec link specs/048-offline-feature
```

Spec is created without epic reference. You can add it later when online.

## Tips

1. **Use Descriptive Feature Names**: Match your feature names closely to roadmap titles for better auto-matching

2. **Create Roadmap Items First**: Run `doit roadmapit add` before `/doit.specit` for seamless linking

3. **Review Links in IDE**: Epic links in spec frontmatter are clickable in VS Code - verify them after creation

4. **Batch Update Links**: After reorganizing specs, run `/doit.specit --update-links` to refresh all links

5. **Check Epic Status**: If a spec isn't auto-linking, check if the epic is closed on GitHub

## Next Steps

After creating a linked spec:

1. **Plan Implementation**: Run `/doit.planit` to create technical design
2. **View Epic on GitHub**: Click the epic link in spec frontmatter
3. **Track Progress**: GitHub epic automatically shows linked specs and related PRs
4. **Create Tasks**: Run `/doit.taskit` to break down implementation

## Related Features

- **039-github-roadmap-sync**: Creates GitHub epics from roadmap items
- **026-ai-context-injection**: Includes epic references in AI context
- **034-fixit-workflow**: Links bug fix specs to GitHub issues

## Support

For issues or questions:

1. Check troubleshooting section above
2. Run `doit spec validate-links` to check for broken references
3. View logs: `.doit/logs/spec-linking.log`
4. Report bugs: Create GitHub issue with "spec-linking" label
