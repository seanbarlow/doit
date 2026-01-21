# Research & Decision Log: GitHub Epic Integration

**Feature**: GitHub Epic and Issue Integration for Roadmap Command
**Date**: 2026-01-21
**Status**: Completed

## Research Questions & Decisions

### 1. GitHub CLI (`gh`) vs Direct API Access

**Question**: Should we use `gh` CLI via subprocess or httpx for direct API calls?

**Research Findings**:

**Option A: GitHub CLI (`gh`)**
- ✅ Pros:
  - Authentication handled automatically (uses existing gh auth)
  - Simpler error messages
  - JSON output with `--json` flag
  - Respects user's GitHub token and permissions
- ❌ Cons:
  - External dependency (user must install gh CLI)
  - Subprocess overhead
  - Harder to mock in tests (requires subprocess mocking)
  - Less control over request/response

**Option B: httpx Direct API**
- ✅ Pros:
  - Already in constitution's tech stack (httpx)
  - Better test mocking (pytest-httpx)
  - More control over requests
  - No external dependency beyond Python packages
- ❌ Cons:
  - Must handle GitHub token manually
  - More complex error handling
  - Need to respect rate limits explicitly

**Decision**: **Use GitHub CLI (`gh`) for production, with fallback detection**

**Rationale**:
1. User experience: Most GitHub users already have `gh` CLI installed
2. Authentication: Simpler to use existing `gh auth` than manage tokens
3. Testing: We can mock subprocess calls and use integration tests with real gh CLI
4. Alignment: The existing `/doit.specit` command already creates GitHub issues using `gh`, so this maintains consistency

**Implementation**:
```python
# Detect gh CLI availability
def has_gh_cli() -> bool:
    return shutil.which("gh") is not None

# Use gh for API calls
def fetch_epics() -> list[dict]:
    result = subprocess.run(
        ["gh", "issue", "list", "--label", "epic", "--json", "number,title,labels,body,url"],
        capture_output=True,
        text=True
    )
    if result.returncode != 0:
        raise GitHubError(result.stderr)
    return json.loads(result.stdout)
```

---

### 2. GitHub Issue Query Strategy

**Question**: How to efficiently query epics and linked features?

**Research Findings**:

**GitHub CLI Commands Available**:
- `gh issue list --label epic` - Get all epics
- `gh issue list --search "part of epic #123"` - Search for linked features
- `gh issue view 123 --json` - Get issue details

**Query Strategies**:

**Option A: Two-pass query (epics, then features per epic)**
- Query all epics with `gh issue list --label epic`
- For each epic, search for features with `gh issue list --search "part of epic #N"`
- Complexity: O(n) API calls where n = number of epics

**Option B: Single query with parsing**
- Query all issues (epics + features) with `gh issue list --label epic,feature`
- Parse "Part of Epic #XXX" pattern from issue bodies
- Build relationship graph in memory
- Complexity: O(1) API calls, but more memory

**Decision**: **Option A: Two-pass query with rate limit awareness**

**Rationale**:
1. Accuracy: GitHub search may not catch all linking patterns
2. Simplicity: Easier to understand and maintain
3. Performance: For typical repos with <50 epics, this is fast enough (<5 seconds target)
4. Caching: First pass (epics) can be cached aggressively

**Implementation**:
```python
def fetch_epics_with_features() -> list[Epic]:
    # Pass 1: Fetch all epics
    epics = fetch_epics()

    # Pass 2: For each epic, fetch linked features
    for epic in epics:
        features = fetch_features_for_epic(epic.number)
        epic.features = features

    return epics

def fetch_features_for_epic(epic_number: int) -> list[Feature]:
    # Search for issues referencing this epic
    result = subprocess.run([
        "gh", "issue", "list",
        "--search", f"is:open part of epic #{epic_number}",
        "--json", "number,title,labels,state"
    ], capture_output=True, text=True)
    return json.loads(result.stdout)
```

---

### 3. Cache Strategy & Invalidation

**Question**: When to cache, when to invalidate, cache format?

**Research Findings**:

**Cache Storage Options**:
- JSON file in `.doit/cache/github_epics.json`
- SQLite database
- Python pickle

**Invalidation Strategies**:
- TTL-based: Cache expires after N minutes
- Explicit: User runs `--refresh` flag to invalidate
- Hybrid: TTL + explicit refresh option

**Decision**: **JSON file with TTL + explicit refresh**

**Cache Structure**:
```json
{
  "version": "1.0",
  "repo": "owner/repo",
  "last_sync": "2026-01-21T10:30:00Z",
  "ttl_minutes": 30,
  "epics": [...]
}
```

**Rationale**:
1. JSON is human-readable and debuggable
2. TTL ensures reasonable freshness (30 minutes default)
3. Explicit refresh gives users control
4. Aligns with constitution's file-based storage principle

**Invalidation Logic**:
```python
def is_cache_valid(cache: dict) -> bool:
    if not cache:
        return False

    last_sync = datetime.fromisoformat(cache["last_sync"])
    ttl = timedelta(minutes=cache.get("ttl_minutes", 30))

    return datetime.now() - last_sync < ttl

def get_epics(refresh: bool = False) -> list[Epic]:
    cache = load_cache()

    if not refresh and is_cache_valid(cache):
        return cache["epics"]

    # Fetch from GitHub
    epics = fetch_epics_from_github()
    save_cache(epics)
    return epics
```

---

### 4. Priority Label Mapping

**Question**: How to handle non-standard priority labels?

**Research Findings**:

**Common GitHub Label Patterns**:
- `priority:P1`, `priority:P2`, etc. (standard)
- `P1`, `P2`, etc. (short form)
- `critical`, `high`, `medium`, `low` (semantic)
- `priority/high`, `priority/critical` (with slash)

**Mapping Strategies**:
- Exact match only (strict)
- Fuzzy matching with string similarity
- Configurable mapping table

**Decision**: **Exact match with common aliases + configurable fallback**

**Priority Mapping Table**:
```python
PRIORITY_MAP = {
    # Standard format
    "priority:P1": "P1", "priority:p1": "P1",
    "priority:P2": "P2", "priority:p2": "P2",
    "priority:P3": "P3", "priority:p3": "P3",
    "priority:P4": "P4", "priority:p4": "P4",

    # Short form
    "P1": "P1", "p1": "P1",
    "P2": "P2", "p2": "P2",
    "P3": "P3", "p3": "P3",
    "P4": "P4", "p4": "P4",

    # Semantic (common aliases)
    "critical": "P1",
    "high": "P2",
    "medium": "P3",
    "low": "P4",

    # Slash format
    "priority/critical": "P1",
    "priority/high": "P2",
    "priority/medium": "P3",
    "priority/low": "P4",
}

DEFAULT_PRIORITY = "P3"
```

**Rationale**:
1. Covers 90% of common label patterns
2. Case-insensitive matching
3. Sensible default (P3) for unrecognized labels
4. Can be extended via config file in future

**Implementation**:
```python
def map_labels_to_priority(labels: list[str]) -> str:
    """Map GitHub issue labels to roadmap priority."""
    for label in labels:
        priority = PRIORITY_MAP.get(label.lower())
        if priority:
            return priority
    return DEFAULT_PRIORITY
```

---

### 5. Conflict Resolution Strategy

**Question**: When local and GitHub have same-named items, which wins?

**Research Findings**:

**Conflict Scenarios**:
1. Same title, different priority
2. Same title, one has feature branch reference
3. Same title, different descriptions
4. GitHub epic exists but not in local roadmap

**Resolution Strategies**:
- GitHub wins (sync from source of truth)
- Local wins (preserve user edits)
- Merge (combine data from both)
- Show both (no automatic resolution)

**Decision**: **Smart merge based on feature branch reference**

**Merge Rules**:
1. **If feature branch reference matches**: Merge data
   - Use local priority and description (user may have edited)
   - Add GitHub URL and issue number
   - Preserve local rationale

2. **If no feature branch reference**: Treat as separate items
   - Display both with source indicator
   - Suggest creating GitHub epic for local item

3. **GitHub-only items**: Add to roadmap
   - Mark with `[GitHub #XXX]` indicator
   - Use GitHub priority and description

4. **Never delete local items**: Always preserve

**Implementation**:
```python
def merge_roadmap_items(local: list[Item], github: list[Epic]) -> list[Item]:
    merged = []
    matched_github = set()

    # Match by feature branch reference
    for local_item in local:
        if local_item.feature_branch:
            # Look for matching GitHub epic
            github_epic = find_epic_by_branch(github, local_item.feature_branch)
            if github_epic:
                # Merge: local data + GitHub URL
                merged_item = local_item.copy()
                merged_item.github_url = github_epic.url
                merged_item.github_number = github_epic.number
                merged.append(merged_item)
                matched_github.add(github_epic.number)
                continue

        # No match: preserve local item
        merged.append(local_item)

    # Add unmatched GitHub epics
    for epic in github:
        if epic.number not in matched_github:
            merged.append(RoadmapItem.from_github_epic(epic))

    return sorted(merged, key=lambda x: x.priority)
```

**Rationale**:
1. Respects user edits (local always preserved)
2. Enriches local data with GitHub metadata
3. Minimizes data loss
4. Provides clear source attribution

---

## Summary of Decisions

| Question | Decision | Rationale |
|----------|----------|-----------|
| API Access | GitHub CLI (`gh`) | Better UX, existing auth, consistency with specit |
| Query Strategy | Two-pass (epics, then features) | Simple, accurate, fast enough for target scale |
| Cache Strategy | JSON file with 30min TTL | File-based storage, human-readable, explicit refresh |
| Priority Mapping | Exact match with common aliases | Covers 90% of patterns, sensible default |
| Conflict Resolution | Smart merge by feature branch ref | Preserves local edits, enriches with GitHub data |

---

## Open Questions

None remaining. All research questions resolved and ready for Phase 1 design.
