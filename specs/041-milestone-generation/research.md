# Research: GitHub Milestone Generation from Priorities

**Feature**: 041-milestone-generation
**Date**: 2026-01-22
**Phase**: Phase 0 - Research & Decisions

## Overview

This document captures research findings and technical decisions for implementing automatic GitHub milestone generation from roadmap priorities.

## Research Questions

### Q1: How to create and manage milestones via GitHub CLI?

**Research Findings**:

The GitHub CLI (`gh`) provides milestone operations through the API command:

```bash
# List milestones
gh api repos/{owner}/{repo}/milestones

# Create milestone
gh api repos/{owner}/{repo}/milestones \
  --method POST \
  --field title="P1 - Critical" \
  --field description="Auto-managed by doit" \
  --field state="open"

# Update milestone
gh api repos/{owner}/{repo}/milestones/{number} \
  --method PATCH \
  --field state="closed"

# Assign issue to milestone
gh issue edit {issue_number} --milestone "P1 - Critical"
```

**Decision**: Use `gh api` for milestone CRUD operations and `gh issue edit` for epic assignment. This maintains consistency with features 039/040 which use `gh` CLI for all GitHub operations.

**Rationale**: The `gh` CLI provides:
- Authentication handling (uses existing GitHub credentials)
- Error handling and retries
- Consistent API across all GitHub operations in doit
- No additional dependencies (httpx already used for other features)

**Alternatives Considered**:
- PyGithub library: Rejected - adds new dependency, inconsistent with existing GitHub integration
- Direct REST API via httpx: Rejected - reinvents auth and error handling that gh CLI provides

---

### Q2: How to detect priority sections in roadmap.md?

**Research Findings**:

Current roadmap.md structure (from feature 039):

```markdown
### P1 - Critical (Must Have for MVP)

- [x] Completed item
  - **Feature**: `[034-fixit-workflow]` ✅ COMPLETED

- [ ] Active item
  - **Rationale**: Description

### P2 - High Priority (Significant Business Value)
...
```

Priority sections are marked with `### P[1-4]` headers followed by title.

**Decision**: Use regex pattern `^### (P[1-4])` to detect priority section headers. Parse roadmap line-by-line to extract items under each priority.

**Implementation**:
```python
import re

PRIORITY_HEADER_RE = re.compile(r"^### (P[1-4])")
EPIC_REFERENCE_RE = re.compile(r"GitHub: #(\d+)")
CHECKBOX_RE = re.compile(r"^- \[([ x])\]")
```

**Rationale**:
- Regex is efficient for line-by-line parsing
- Matches existing roadmap structure from features 039/040
- Reuses RoadmapParser patterns from feature 039

**Alternatives Considered**:
- Markdown AST parsing: Rejected - overkill for simple structure, adds complexity
- String splitting on headers: Rejected - fragile to formatting variations

---

### Q3: How to determine when all items in a priority are completed?

**Research Findings**:

Items can be completed in two ways:
1. Marked with `[x]` checkbox in roadmap.md
2. Moved to completed_roadmap.md (via `/doit.checkin`)

A priority section is complete when:
- All items under the priority header have `[x]` checkboxes, OR
- The priority section in roadmap.md is empty/has only completed items AND items exist in completed_roadmap.md with matching priority

**Decision**: Check both conditions:
1. Parse roadmap.md for priority section - count uncompleted items `- [ ]`
2. If zero uncompleted items in roadmap, verify items exist in completed_roadmap.md for that priority
3. Only prompt to close milestone if both conditions true

**Rationale**:
- Handles both completion workflows (in-place checkbox vs checkin)
- Prevents premature closure (priority might just be empty, not completed)
- Aligns with existing roadmap management patterns

**Alternatives Considered**:
- Only check roadmap.md: Rejected - doesn't account for items moved to completed_roadmap.md
- Only check completed_roadmap.md: Rejected - doesn't handle in-place checkbox completion
- Automatically close milestones: Rejected - user might want milestone open for future planning

---

### Q4: How to handle milestone naming conflicts?

**Research Findings**:

Potential conflicts:
- User creates manual milestone "P1 - Critical" before running sync
- Milestone exists but with different description
- Milestone exists but is closed

GitHub milestone API:
- Titles must be unique within a repository
- API returns 422 Unprocessable Entity if title exists

**Decision**: Before creating milestone, list all milestones and check if title exists:

```python
def get_milestone_by_title(title: str) -> Optional[int]:
    """Get milestone number by exact title match."""
    result = subprocess.run(
        ["gh", "api", f"repos/{repo}/milestones"],
        capture_output=True, text=True
    )
    milestones = json.loads(result.stdout)
    for ms in milestones:
        if ms["title"] == title:
            return ms["number"]
    return None
```

If milestone exists:
- Verify description matches expected format
- If description differs, log warning but continue (don't overwrite user content)
- If state is closed, skip (don't reopen automatically)

**Rationale**:
- Preserves user-created milestones
- Prevents duplicate milestone errors
- Respects manual milestone management

**Alternatives Considered**:
- Always try to create, catch 422 error: Rejected - inefficient, requires error parsing
- Overwrite existing milestones: Rejected - loses user customizations
- Rename conflicts to "P1 - Critical (doit)": Rejected - confusing, breaks convention

---

### Q5: How to handle epic assignment when epic is already assigned to different milestone?

**Research Findings**:

GitHub API behavior:
- `gh issue edit --milestone "New"` updates milestone assignment
- Previous milestone assignment is replaced (not additive)
- No warning if milestone changes

Scenarios:
- Epic #123 assigned to "Sprint 5" milestone
- Roadmap shows epic under P1 priority
- Sync should assign to "P1 - Critical" milestone

**Decision**: Always update epic milestone to match roadmap priority. Roadmap is source of truth for priority-based milestone assignment.

Log warning when overwriting existing milestone:
```
⚠️  Epic #123 reassigned from "Sprint 5" to "P1 - Critical" (roadmap priority)
```

**Rationale**:
- Roadmap priority is canonical source of truth for doit workflows
- Feature is explicitly for priority-based milestone organization
- User can disable sync if they want manual milestone control
- Warning provides visibility into changes

**Alternatives Considered**:
- Skip assignment if milestone exists: Rejected - defeats purpose of sync
- Prompt user for each conflict: Rejected - not scalable for 100+ epics
- Only assign if milestone is empty: Rejected - doesn't handle reprioritization

---

### Q6: How to implement dry-run mode?

**Research Findings**:

Dry-run should:
- Parse roadmap and detect changes
- Show what would be created/updated/closed
- NOT make any GitHub API calls

**Decision**: Add `--dry-run` flag to command. In dry-run mode:

1. Detect missing milestones (would create)
2. Detect epic assignment changes (would update)
3. Detect completed priorities (would prompt to close)
4. Print summary table without executing

```bash
$ doit roadmapit sync-milestones --dry-run

🔍 Dry Run - No changes will be made

Milestones to Create:
  ✓ P3 - Medium Priority
  ✓ P4 - Low Priority

Epic Assignments to Update:
  #587 → P2 - High Priority (currently: unassigned)
  #590 → P2 - High Priority (currently: Sprint 5)

Milestones to Close:
  P1 - Critical (all items completed)

Run without --dry-run to apply changes.
```

**Implementation**:
```python
@click.option("--dry-run", is_flag=True, help="Preview changes without executing")
def sync_milestones(dry_run: bool):
    service = MilestoneService(dry_run=dry_run)
    service.sync_all()
```

**Rationale**:
- Standard pattern for commands with side effects
- Provides confidence before making bulk changes
- Useful for CI/CD validation (verify sync is up-to-date)

**Alternatives Considered**:
- Interactive confirmation prompts: Rejected - not scriptable, annoying for CI
- Separate `preview` command: Rejected - duplicates logic, confusing UX

---

## Technical Decisions Summary

| Decision | Choice | Rationale |
|----------|--------|-----------|
| **Milestone Creation** | `gh api repos/{repo}/milestones --method POST` | Consistent with features 039/040 |
| **Epic Assignment** | `gh issue edit --milestone` | Simple, handles updates automatically |
| **Priority Detection** | Regex `^### (P[1-4])` on roadmap.md | Matches existing structure |
| **Completion Detection** | Check roadmap.md + completed_roadmap.md | Handles both workflows |
| **Naming Conflicts** | Check existing, skip if found | Preserves user milestones |
| **Assignment Conflicts** | Always update to match roadmap | Roadmap is source of truth |
| **Dry Run** | `--dry-run` flag with preview output | Standard pattern, scriptable |

## Implementation Patterns

### From Feature 039 (GitHub Roadmap Sync)

Reuse patterns:
- `RoadmapParser.parse_priority_sections()` - Priority detection
- `GitHubService._get_repo_slug()` - Repository detection
- `GitHubService._run_gh_command()` - GitHub CLI wrapper

### From Feature 040 (GitHub Issue Auto-linking)

Reuse patterns:
- Error handling with graceful degradation
- Rich console formatting for status output
- Integration test structure (mock GitHub API)

### New Patterns

Introduce:
- `MilestoneService` - Core sync orchestration
- `SyncResult` dataclass - Track created/updated/skipped counts
- `--dry-run` flag pattern - Useful for other commands

## API Contract

See [contracts/github-api.md](contracts/github-api.md) for detailed GitHub API endpoints and request/response formats.

## Performance Considerations

**GitHub API Rate Limits**:
- Primary: 5,000 requests/hour (authenticated)
- Secondary: 60 requests/hour (unauthenticated)

**Optimization Strategy**:
- Batch milestone list query (1 API call)
- Only update epics that changed (skip if already assigned)
- Collect errors, don't fail-fast (complete as much as possible)

**Expected API Calls** (for roadmap with 50 items, 4 priorities):
- 1 call: List milestones
- 4 calls: Create missing milestones (worst case)
- ~25 calls: Assign epics to milestones (assuming 50% need updates)
- **Total**: ~30 calls per sync (well within rate limits)

## Error Handling Strategy

| Error Type | Handling |
|------------|----------|
| **No GitHub remote** | Error message, exit gracefully |
| **gh CLI not installed** | Error with installation instructions |
| **Network failure** | Retry with exponential backoff (3 attempts) |
| **API rate limit** | Log warning, continue with remaining operations |
| **Invalid epic number** | Skip epic, log warning, continue |
| **Milestone create fails** | Log error, skip epic assignments for that priority |

## Testing Strategy

**Unit Tests** (test_milestone_service.py):
- Milestone creation logic
- Epic assignment logic
- Completion detection logic
- Dry-run mode behavior
- Error handling paths

**Integration Tests** (test_roadmapit_sync.py):
- End-to-end sync workflow with mocked GitHub API
- Roadmap parsing → milestone creation → epic assignment
- Completion detection → close prompt
- Dry-run output verification

**Manual Tests**:
- Real GitHub repository sync
- Large roadmap (100+ items) performance
- Network failure recovery
- Rate limit handling

## Open Questions

None - all research questions resolved.

## References

- [GitHub API - Milestones](https://docs.github.com/en/rest/issues/milestones)
- [GitHub CLI Manual](https://cli.github.com/manual/gh_api)
- Feature 039: GitHub Roadmap Sync implementation patterns
- Feature 040: GitHub Issue Auto-linking error handling patterns
