# Research: GitHub Issue Auto-linking in Spec Creation

**Feature**: 040-spec-github-linking
**Date**: 2026-01-22
**Status**: Complete

## Overview

This document captures research findings for implementing automatic GitHub epic linking during spec creation. The feature integrates with the existing roadmap system and GitHub CLI to create bidirectional links between specification files and GitHub issues.

## Key Technical Decisions

### 1. GitHub API Integration Approach

**Decision**: Reuse existing `github_client.py` module from feature 039-github-roadmap-sync, leverage `gh` CLI for authentication

**Rationale**:
- Feature 039 already established patterns for GitHub API integration using httpx
- `gh` CLI handles authentication complexity (OAuth tokens, SSH keys, etc.)
- Avoids duplicating GitHub API client code
- Consistent error handling across GitHub-related features

**Alternatives Considered**:
- Direct GitHub API integration using PyGithub library
  - Rejected: Adds new dependency not in constitution
  - Rejected: Requires separate authentication management
- Using only `gh` CLI for all operations (no httpx)
  - Rejected: Less flexibility for complex API operations
  - Rejected: Harder to mock/test compared to HTTP client

**Implementation Notes**:
- Use `gh api` commands for read operations (get issue details)
- Use `gh issue edit` for write operations (update epic description)
- Cache GitHub API responses for 5 minutes to avoid rate limits (FR-024)

### 2. Roadmap Matching Algorithm

**Decision**: Implement fuzzy string matching using Levenshtein distance with 80% similarity threshold

**Rationale**:
- Users may provide feature names that don't exactly match roadmap titles
- Example: "GitHub Issue Auto-linking" vs "GitHub Issue Auto-linking in Spec Creation"
- 80% threshold balances precision (avoid false matches) with recall (find correct matches)
- Industry standard for text similarity matching

**Alternatives Considered**:
- Exact string matching only
  - Rejected: Too rigid, requires users to know exact roadmap titles
  - Rejected: Fails when roadmap items have longer descriptive titles
- TF-IDF + cosine similarity
  - Rejected: Overkill for simple title matching
  - Rejected: Would require scikit-learn dependency (not in constitution)
- Regular expression pattern matching
  - Rejected: Not robust to typos or word order variations

**Implementation Notes**:
- Use Python's `difflib.SequenceMatcher` (stdlib, no new dependency)
- Return top 3 matches if similarity > 80%
- Prompt user to select if multiple matches found (FR-010)
- If no matches, offer to search GitHub issues directly

### 3. Spec Frontmatter Format

**Decision**: Add `Epic` and `Epic URL` fields to YAML frontmatter, format epic as markdown link

**Rationale**:
- YAML frontmatter is established pattern in doit spec files
- Markdown link format `[#123](https://github.com/...)` is clickable in VS Code, GitHub web UI
- Separate `Epic URL` field allows full GitHub URL for scripts/automation
- Consistent with existing frontmatter fields (Feature Branch, Created, Status)

**Alternatives Considered**:
- Single `Epic` field with just issue number
  - Rejected: Requires users to manually construct GitHub URL
  - Rejected: Not clickable in IDEs without URL
- Embedded in spec body instead of frontmatter
  - Rejected: Harder to parse programmatically
  - Rejected: Breaks separation of metadata vs. content
- Custom `<!-- EPIC: #123 -->` comment syntax
  - Rejected: Not standard markdown, harder for users to edit manually
  - Rejected: Not visible in file preview/outline views

**Implementation Notes**:
- Frontmatter format:
  ```yaml
  Epic: "[#123](https://github.com/owner/repo/issues/123)"
  Epic URL: "https://github.com/owner/repo/issues/123"
  Priority: P1
  ```
- Parse frontmatter using PyYAML (already in tech stack per 025-git-hooks-workflow)
- Preserve all existing frontmatter fields when updating

### 4. GitHub Epic Description Update Strategy

**Decision**: Append spec reference to epic description in a dedicated "## Specification" section

**Rationale**:
- Preserves existing epic content (user-written descriptions, checklists)
- Clear visual separation between epic content and spec reference
- Markdown heading allows easy navigation on GitHub web UI
- Supports multiple specs per epic (list all spec paths)

**Alternatives Considered**:
- Add spec reference at top of epic description
  - Rejected: Disrupts reading flow for epic description
  - Rejected: Important epic summary gets pushed down
- Use GitHub issue comments for spec reference
  - Rejected: Comments can be overwhelming, spec link might get lost
  - Rejected: No clear "single source of truth" for spec location
- Store spec reference in GitHub issue metadata/custom fields
  - Rejected: GitHub custom fields require organization-level config
  - Rejected: Not visible in standard issue view

**Implementation Notes**:
- Format in epic description:
  ```markdown
  [... existing epic content ...]

  ## Specification

  - `specs/040-spec-github-linking/spec.md`
  ```
- Use regex to detect existing "## Specification" section and update it
- If section exists with other specs, append new spec path to the list
- Preserve markdown formatting in the rest of the epic body

### 5. Error Handling and Graceful Degradation

**Decision**: Spec creation always succeeds; GitHub linking failures are logged as warnings, not errors

**Rationale**:
- Spec creation is the primary user goal; GitHub linking is enhancement
- Network failures, API rate limits, or missing `gh` CLI shouldn't block spec creation
- Users can retry linking later with `--update-links` flag
- Follows principle of "fail gracefully" for non-critical operations

**Alternatives Considered**:
- Fail spec creation if GitHub linking fails
  - Rejected: Too strict, blocks offline development
  - Rejected: Bad UX when GitHub is temporarily down
- Silent failure (no warning message)
  - Rejected: Users won't know linking failed
  - Rejected: No indication of how to fix the issue
- Retry GitHub operations automatically
  - Rejected: Can significantly slow down spec creation
  - Rejected: May hit rate limits faster

**Implementation Notes**:
- Catch all GitHub-related exceptions in linking service
- Log warning with clear message: "Spec created. GitHub linking failed: [reason]"
- Provide recovery command: "Run `doit spec link [spec-dir]` to retry"
- Add `--skip-github` flag to explicitly disable linking (FR-013)

### 6. Performance Optimization

**Decision**: Cache roadmap data and GitHub API responses for duration of command execution

**Rationale**:
- Roadmap file (~100 items) is read multiple times during fuzzy matching
- GitHub API rate limit is 5,000 requests/hour for authenticated users
- Spec creation should complete in <3s (performance goal)
- Caching avoids redundant file I/O and API calls

**Alternatives Considered**:
- No caching (read files and call API fresh each time)
  - Rejected: Slower performance, wastes API quota
  - Rejected: May hit rate limits during batch operations
- Persistent cache across command invocations
  - Rejected: Adds complexity (cache invalidation, file locking)
  - Rejected: Stale data risk if roadmap changes
- LRU cache with expiration
  - Rejected: Overkill for single-command scope

**Implementation Notes**:
- Use Python `@lru_cache` decorator for roadmap parsing function
- Store GitHub epic data in memory dict with 5-minute TTL (FR-024)
- Clear cache on command exit

## Integration Points

### Existing Features

**039-github-roadmap-sync**:
- Reuses `github_client.py` for GitHub API interactions
- Relies on roadmap entries having `github_number` field populated
- Assumes GitHub issues created by 039 have "epic" and "priority:*" labels

**026-ai-context-injection**:
- Epic reference in spec frontmatter becomes part of AI context
- Allows AI assistants to reference GitHub issues in responses

**021-copilot-agent-fix**:
- Spec frontmatter format must remain YAML-compatible
- Markdown links in frontmatter should be valid for Copilot parsing

### External Dependencies

**GitHub CLI (`gh`)**:
- Version: 2.0+ recommended
- Required commands: `gh auth status`, `gh api`, `gh issue edit`
- Installation check: `which gh` or `gh --version`

**Git Remote**:
- Repository must have GitHub remote configured
- Remote detection: `git remote get-url origin`
- URL parsing to extract owner/repo for GitHub API

## Testing Strategy

### Unit Tests

1. **Roadmap Matching** (`test_roadmap_matcher.py`):
   - Exact match scenarios
   - Fuzzy match with 80%+ similarity
   - Multiple matches (should prompt)
   - No matches (should fallback)
   - Case sensitivity handling

2. **Fuzzy Matching Algorithm** (`test_fuzzy_match.py`):
   - Levenshtein distance calculation
   - Threshold boundary testing (79%, 80%, 81%)
   - Special characters handling
   - Empty string edge cases

3. **GitHub Linker** (`test_github_linker.py`):
   - Spec frontmatter updates
   - Epic description updates
   - Multiple specs per epic
   - Error handling (API failures, closed epics)

4. **Spec Parser** (`test_spec_parser.py`):
   - YAML frontmatter parsing
   - Preserving existing fields
   - Markdown link formatting
   - Atomic file writes

### Integration Tests

1. **End-to-End Spec Creation** (`test_specit_github.py`):
   - Mock roadmap with GitHub epic
   - Mock `gh` CLI responses
   - Verify spec file created with epic reference
   - Verify epic description updated with spec path

2. **Error Scenarios**:
   - GitHub CLI not installed
   - API rate limit exceeded
   - Network failure during epic update
   - Closed epic in roadmap

### Fixtures

- `sample_roadmap.md`: Mock roadmap with various feature entries
- `sample_spec.md`: Mock spec file with frontmatter
- `mock_gh_responses.json`: Sample GitHub API responses

## Security Considerations

1. **GitHub Token Exposure**:
   - Never log GitHub authentication tokens
   - Use `gh` CLI for auth management (handles token storage securely)
   - No tokens stored in spec files or logs

2. **Command Injection**:
   - Sanitize feature names before passing to shell commands
   - Use Python `subprocess` with list args, not shell strings
   - Validate epic numbers are integers before use

3. **Path Traversal**:
   - Validate spec file paths stay within `specs/` directory
   - Use `pathlib.Path.resolve()` to normalize paths
   - Reject paths with `..` or absolute paths

## Open Questions

None remaining - all technical decisions finalized.

## References

- Feature 039 GitHub Roadmap Sync: `specs/039-github-roadmap-sync/`
- GitHub CLI Documentation: https://cli.github.com/manual/
- Python difflib: https://docs.python.org/3/library/difflib.html
- Constitution Tech Stack: `.doit/memory/constitution.md`
