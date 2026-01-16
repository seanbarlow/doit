# Research: Spec Validation and Linting

**Feature**: 029-spec-validation-linting
**Date**: 2026-01-15
**Status**: Complete

## Research Questions

### 1. Markdown Parsing Approach

**Question**: How should we parse markdown spec files to extract sections and validate structure?

**Decision**: Use regex-based section extraction with Python's built-in `re` module

**Rationale**:
- Spec files have predictable structure with `## Section` headers
- Full markdown AST parsing (via markdown-it or mistune) is overkill for section detection
- Regex is fast, has no external dependencies, and is sufficient for our needs
- Pattern: `^##\s+(.+?)(?=\n##|\Z)` captures section headers and content

**Alternatives Considered**:
- mistune (markdown parser): Rejected - adds dependency, slower for simple section extraction
- markdown-it-py: Rejected - heavier weight, designed for rendering not validation
- Custom line-by-line parser: Rejected - regex is cleaner and more maintainable

### 2. Quality Score Calculation

**Question**: How should we calculate a deterministic quality score (0-100)?

**Decision**: Weighted category scoring with normalization

**Rationale**:
- Scores should be reproducible (same spec = same score always)
- Different rule categories have different importance weights
- Formula: `score = 100 - sum(issue_weight * issue_count) for each category`

**Scoring Algorithm**:
```python
WEIGHTS = {
    "structure": 20,      # Missing required sections
    "requirements": 15,   # Missing FR-XXX patterns
    "acceptance": 10,     # User stories without scenarios
    "naming": 5,          # Convention violations
    "clarity": 5,         # [NEEDS CLARIFICATION] markers
}

# Each issue deducts its category weight from 100
# Minimum score is 0 (no negative scores)
# Example: Missing "Requirements" section = -20 points
```

**Alternatives Considered**:
- Percentage-based (issues/total checks): Rejected - not intuitive, varies with spec size
- Letter grades (A-F): Rejected - less granular, harder to track improvement
- Pass/fail only: Rejected - doesn't show incremental improvement

### 3. Pre-commit Hook Integration

**Question**: How should validation integrate with the existing git hooks system?

**Decision**: Extend existing hook infrastructure in `doit hooks` command

**Rationale**:
- Feature 025-git-hooks-workflow already established hook patterns
- Validation becomes a hook type like `pre-commit` or `pre-push`
- Configuration via existing `.doit/config/hooks.yaml`
- Leverage existing bypass logging infrastructure

**Integration Points**:
- Add `spec-validation` as a recognized hook type
- Auto-detect changed `.md` files in `specs/` directory
- Run validation only on changed specs (performance optimization)
- Exit non-zero to block commit on errors

**Alternatives Considered**:
- Standalone pre-commit config: Rejected - duplicates existing hook system
- Husky integration: Rejected - Node.js dependency, not aligned with Python stack
- Manual hook scripts: Rejected - existing doit hooks is more maintainable

### 4. Custom Rules Configuration Schema

**Question**: What YAML schema should we use for custom validation rules?

**Decision**: Simple declarative schema with pattern matching

**Rationale**:
- Keep configuration simple and readable
- Support common customization needs without complexity
- Allow severity overrides for built-in rules

**Schema**:
```yaml
# .doit/validation-rules.yaml
version: "1.0"

# Override built-in rule severity
overrides:
  - rule: "missing-acceptance-scenarios"
    severity: error  # upgrade from warning to error

# Disable specific rules
disabled:
  - "check-todo-markers"

# Custom rules
custom:
  - name: "require-security-section"
    description: "Specs must include Security Considerations"
    pattern: "^## Security Considerations"
    severity: warning
    category: "organization"

  - name: "max-user-stories"
    description: "Limit user stories to 5 per spec"
    check: "count"
    pattern: "^### User Story"
    max: 5
    severity: info
```

**Alternatives Considered**:
- JSON configuration: Rejected - YAML is more readable for humans
- Python rule files: Rejected - security concerns, complexity overkill
- No custom rules: Rejected - organizations have legitimate customization needs

### 5. Built-in Rule Categories

**Question**: What rules should be included by default?

**Decision**: 5 rule categories with 10 built-in rules

**Categories and Rules**:

| Category | Rule | Severity | Description |
|----------|------|----------|-------------|
| Structure | missing-user-scenarios | error | No "## User Scenarios" section |
| Structure | missing-requirements | error | No "## Requirements" section |
| Structure | missing-success-criteria | error | No "## Success Criteria" section |
| Requirements | fr-naming-convention | warning | FR-XXX pattern not followed |
| Requirements | sc-naming-convention | warning | SC-XXX pattern not followed |
| Acceptance | missing-acceptance-scenarios | warning | User story lacks scenarios |
| Acceptance | incomplete-given-when-then | info | Scenario missing Given/When/Then |
| Clarity | unresolved-clarification | warning | [NEEDS CLARIFICATION] present |
| Clarity | todo-in-approved-spec | warning | TODO/FIXME in non-draft spec |
| Naming | feature-branch-format | info | Branch doesn't match NNN-name |

**Alternatives Considered**:
- Fewer rules (just errors): Rejected - warnings help improve quality
- More rules (20+): Rejected - start simple, add based on feedback
- No categories: Rejected - categories help organize output and filtering

## Resolved Clarifications

All technical decisions from the spec have been resolved:

| Item | Resolution |
|------|------------|
| Markdown parsing | Regex-based, no external parser |
| Score calculation | Weighted category deduction |
| Hook integration | Extend existing doit hooks |
| Custom rules | YAML configuration file |
| Default rules | 10 rules in 5 categories |

## Dependencies to Add

Based on research, the following dependencies are needed:

| Dependency | Purpose | Already in Constitution |
|------------|---------|------------------------|
| PyYAML | Parse custom rules config | No - add |
| re (stdlib) | Pattern matching | Yes (stdlib) |
| pathlib (stdlib) | File path handling | Yes (stdlib) |

**Note**: PyYAML is a standard, well-maintained library commonly used in Python CLIs. Adding it aligns with the pattern of using established libraries (like Rich, httpx).

## Next Steps

Research complete. Ready for Phase 1:
1. Generate data-model.md with entity definitions
2. Create contracts/ with internal API interfaces
3. Generate quickstart.md with usage examples
