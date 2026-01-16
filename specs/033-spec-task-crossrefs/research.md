# Research: Cross-Reference Support Between Specs and Tasks

**Feature**: 033-spec-task-crossrefs
**Date**: 2026-01-16

## Research Summary

### 1. Cross-Reference Syntax Decision

**Decision**: Use inline markdown pattern `[FR-XXX]` for task-to-requirement references

**Rationale**:
- Consistent with existing FR-XXX naming convention validated by `fr-naming-convention` rule
- Human-readable in plain markdown without rendering
- Parseable with simple regex: `\[FR-\d{3}(?:,\s*FR-\d{3})*\]`
- Supports multiple references: `[FR-001, FR-003]`

**Alternatives Considered**:
- YAML frontmatter in tasks.md - Rejected: adds complexity, not human-readable
- HTML comments - Rejected: hidden from users, harder to maintain
- Link syntax `[FR-001](spec.md#FR-001)` - Rejected: too verbose for frequent use

### 2. Requirement Extraction Patterns

**Decision**: Extend existing `rule_engine.py` pattern matching for FR-XXX extraction

**Rationale**:
- Existing regex in `_check_pattern_compliance()` already parses `- **FR-XXX**:` format
- Pattern: `r"^\s*-\s*\*\*FR-(\d{3})\*\*:"` captures requirement IDs
- Consistent with validation infrastructure from feature 029

**Implementation Notes**:
- Create `requirement_parser.py` utility module for shared extraction logic
- Parse both spec.md (source) and tasks.md (references)

### 3. Tasks.md Format Analysis

**Decision**: Add requirement references inline with task descriptions

**Current tasks.md format**:
```markdown
## Tasks

- [ ] Task description here
- [x] Completed task description
```

**New format with cross-references**:
```markdown
## Tasks

- [ ] Task description here [FR-001]
- [ ] Another task [FR-002, FR-003]
- [x] Completed task description [FR-001]
```

**Rationale**:
- Minimal disruption to existing format
- References at end of line are scannable
- Checkbox state preserved

### 4. Coverage Report Output

**Decision**: Rich table output with JSON/Markdown export options

**Rationale**:
- Consistent with `doit status` command output patterns
- Rich tables used throughout codebase (status_reporter.py, report_generator.py)
- JSON export enables CI/CD integration
- Markdown export enables documentation inclusion

**Output Format**:
```
Requirement Coverage Report: 033-spec-task-crossrefs
═══════════════════════════════════════════════════

Requirement │ Task Count │ Status
────────────┼────────────┼────────
FR-001      │ 2          │ ✓ Covered
FR-002      │ 1          │ ✓ Covered
FR-003      │ 0          │ ⚠ Uncovered
────────────┼────────────┼────────
Coverage: 67% (2/3 requirements)
```

### 5. Validation Integration Point

**Decision**: Add new validation rules to existing RuleEngine infrastructure

**New Rules**:
- `orphaned-task-reference`: Error when task references non-existent FR-XXX
- `uncovered-requirement`: Warning (strict mode: error) when FR-XXX has no tasks

**Rationale**:
- Leverages existing ValidationService orchestration
- Consistent severity/issue reporting
- Hooks into pre-commit validation via feature 029

**Implementation**:
- Add rules to `builtin_rules.py`
- Rules need cross-file analysis (spec.md + tasks.md)
- New rule category: "traceability"

### 6. Navigation Implementation

**Decision**: CLI command with line number output; IDE navigation deferred

**Rationale**:
- Constitution notes "IDE plugins" as out of scope
- CLI can output `spec.md:42` format for IDE integration
- Users can use grep/IDE "go to line" functionality

**Command Interface**:
```bash
# From task, find requirement
doit xref locate FR-001

# From requirement, list tasks
doit xref tasks FR-001

# Full coverage report
doit xref coverage
```

### 7. File Discovery Pattern

**Decision**: Spec-relative path resolution with feature directory context

**Discovery Logic**:
```
feature_dir/
├── spec.md      # Source of FR-XXX definitions
├── tasks.md     # Contains [FR-XXX] references
└── plan.md      # May also contain references
```

**Rationale**:
- Keep cross-references scoped to feature directory
- Support future expansion to plan.md references
- Use existing `SpecScanner` pattern for discovery

### 8. Preservation During Regeneration

**Decision**: Parse and preserve references when taskit regenerates

**Rationale**:
- FR-009 requires: "preserve existing cross-references when files regenerated"
- taskit template should merge new tasks with existing references
- Similar to how git merge preserves local changes

**Implementation Strategy**:
- Before regeneration: Extract task→FR mappings from existing tasks.md
- After regeneration: Apply saved mappings to matching tasks by description similarity
- Flag unmatched preserved references for user review

## Dependencies Confirmed

| Dependency | Status | Notes |
|------------|--------|-------|
| Feature 029 (Validation) | ✓ Merged | RuleEngine, ValidationService available |
| spec.md template | ✓ Available | FR-XXX format standardized |
| tasks.md format | ✓ Available | Checkbox format standardized |
| Rich library | ✓ Available | Table output support |
| pytest | ✓ Available | Test infrastructure ready |

## Risks and Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Performance on large specs (50+ FRs) | Low | Medium | Lazy loading, caching parsed results |
| Users forget to add references | Medium | Low | Warning on uncovered requirements (not error) |
| Task description changes break mapping | Medium | Medium | Fuzzy matching with user confirmation |
| Multi-spec features complexity | Low | Low | Path prefix syntax: `[sub/spec.md#FR-001]` |

## Resolved Clarifications

All requirements from spec.md are clear and implementable with the decisions above. No outstanding [NEEDS CLARIFICATION] items.
