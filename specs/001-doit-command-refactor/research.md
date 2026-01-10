# Research: Doit Command Refactoring

**Branch**: `001-doit-command-refactor` | **Date**: 2026-01-09
**Purpose**: Resolve unknowns and document best practices for implementation

## Research Tasks

### RT-001: GitHub Issue Template Best Practices

**Question**: What is the optimal structure for Epic, Feature, and Task issue templates?

**Decision**: Use GitHub's native issue template format with YAML frontmatter.

**Rationale**: GitHub issue templates support:
- YAML frontmatter for metadata (labels, assignees, title prefixes)
- Markdown body for structured sections
- Form-based templates for guided input (optional)

**Implementation**:

```yaml
# .github/ISSUE_TEMPLATE/epic.yml
name: Epic
description: Create an Epic issue for a feature specification
labels: ["epic"]
body:
  - type: markdown
    attributes:
      value: "## Epic Details"
  - type: textarea
    id: summary
    attributes:
      label: Summary
      description: Brief description of the epic
    validations:
      required: true
  - type: textarea
    id: success-criteria
    attributes:
      label: Success Criteria
      description: Measurable outcomes for this epic
  - type: textarea
    id: user-stories
    attributes:
      label: User Stories
      description: Links to related Feature issues
```

**Alternatives Considered**:
- Plain markdown templates: Less structured, no automatic labeling
- External issue trackers: Out of scope per spec

---

### RT-002: GitHub Issue Linking Strategy

**Question**: How to maintain Epic → Feature → Task hierarchy links?

**Decision**: Use GitHub's native issue references with a standardized "Part of" section.

**Rationale**: GitHub automatically creates backlinks when issues reference each other using `#<issue-number>`.

**Implementation**:
- Epic template includes placeholder for Feature issue links
- Feature template includes "Part of Epic: #XX" field
- Task template includes "Part of Feature: #XX" field
- Use labels to reinforce hierarchy: `epic`, `feature`, `task`

**Pattern**:
```markdown
## Hierarchy
- **Part of**: #<parent-issue-number>
- **Child Issues**: <!-- Auto-populated by doit commands -->
```

---

### RT-003: Claude Code Slash Command Structure

**Question**: What is the optimal structure for doit command files?

**Decision**: Maintain existing structure with YAML frontmatter + markdown body.

**Rationale**: Existing speckit commands use a proven pattern:
- YAML frontmatter: description, handoffs (label, agent, prompt, send)
- Markdown body: User Input section, Outline, Key rules

**Implementation**: Keep existing pattern, update:
- All `speckit.*` references → `doit.*`
- Handoff agent references
- Internal cross-command references

**Existing Pattern** (from speckit.specify.md):
```yaml
---
description: Create or update the feature specification...
handoffs:
  - label: Build Technical Plan
    agent: speckit.plan  # → Change to doit.plan
    prompt: Create a plan for the spec...
---
```

---

### RT-004: Project Scaffolding Patterns by Tech Stack

**Question**: What folder structures and config files are standard for supported tech stacks?

**Decision**: Define canonical structures for each supported stack.

**Findings**:

#### React/TypeScript
```
src/
├── components/
├── hooks/
├── pages/ (or views/)
├── services/
├── types/
├── utils/
└── App.tsx

Config files: package.json, tsconfig.json, vite.config.ts (or next.config.js)
```

#### .NET Core
```
src/
├── Controllers/
├── Models/
├── Services/
├── Data/
└── Program.cs

Config files: *.csproj, appsettings.json, appsettings.Development.json
```

#### Node.js/Express
```
src/
├── routes/
├── controllers/
├── models/
├── middleware/
├── services/
└── index.js

Config files: package.json, .env.example, nodemon.json
```

#### Python/FastAPI
```
src/
├── api/
│   └── routes/
├── models/
├── services/
├── core/
└── main.py

Config files: pyproject.toml, requirements.txt, .env.example
```

#### Go
```
cmd/
├── app/
│   └── main.go
internal/
├── handlers/
├── models/
├── services/
pkg/
└── shared utilities

Config files: go.mod, go.sum, Makefile
```

**Gitignore Patterns**: Each stack has standard patterns:
- Node: node_modules/, dist/, .env
- Python: __pycache__/, .venv/, *.pyc
- .NET: bin/, obj/, *.user
- Go: vendor/, *.exe

---

### RT-005: GitHub MCP Server Integration

**Question**: How to integrate GitHub issue creation via MCP server?

**Decision**: Use existing MCP server pattern with graceful fallback.

**Rationale**: The speckit.taskstoissues command already demonstrates the pattern.

**Implementation** (from existing code):
```markdown
**Tools Required**: GitHub MCP server (`github/github-mcp-server/issue_write`)

**Safety Mechanisms**:
- Check remote URL is GitHub before proceeding
- Never create issues in repositories that don't match remote URL
```

**Graceful Fallback**:
- If MCP server unavailable: Log warning, skip issue creation, continue workflow
- If GitHub remote not configured: Inform user, proceed with local-only mode
- Store issue references locally for retry

---

### RT-006: Roadmap File Format

**Question**: What format should roadmap.md and roadmap_completed.md use?

**Decision**: Use structured markdown with feature entries.

**Rationale**: Human-readable, easily parseable, consistent with other artifacts.

**Implementation**:

```markdown
# Roadmap

## Planned Features

| Feature | Branch | Status | Priority |
|---------|--------|--------|----------|
| User Authentication | 002-user-auth | In Progress | P1 |
| Dashboard Analytics | 003-dashboard | Planned | P2 |

## Backlog

- Feature idea 1
- Feature idea 2
```

```markdown
# Completed Features

| Feature | Branch | Completed | PR |
|---------|--------|-----------|-----|
| Doit Command Refactor | 001-doit-command-refactor | 2026-01-15 | #42 |
```

---

### RT-007: Review Command Code Analysis

**Question**: How should the review command perform code review?

**Decision**: Compare implementation against spec requirements and plan architecture.

**Rationale**: Claude can analyze code against documented requirements.

**Implementation**:
1. Load spec.md, plan.md, tasks.md
2. Identify implemented files from tasks.md completion markers
3. Read implemented code
4. Check each functional requirement is addressed
5. Verify architecture matches plan decisions
6. Generate findings report with severity levels

**Finding Categories**:
- CRITICAL: Requirement not implemented
- HIGH: Implementation deviates from plan
- MEDIUM: Code quality issues
- LOW: Style/formatting suggestions

---

### RT-008: Test Command Detection

**Question**: How should the test command detect and run the project's test suite?

**Decision**: Auto-detect test framework from project files, execute via standard commands.

**Rationale**: Each framework has discoverable markers and standard run commands.

**Detection Matrix**:

| Framework | Detection File | Run Command |
|-----------|---------------|-------------|
| pytest | pyproject.toml (pytest), pytest.ini | `pytest` |
| jest | package.json (jest), jest.config.* | `npm test` or `jest` |
| mocha | package.json (mocha) | `npm test` |
| XCTest | *.xcodeproj | `xcodebuild test` |
| cargo test | Cargo.toml | `cargo test` |
| go test | go.mod | `go test ./...` |
| dotnet test | *.csproj | `dotnet test` |

---

### RT-009: Checkin Command PR Creation

**Question**: How should the checkin command create pull requests?

**Decision**: Use `gh` CLI tool for PR creation.

**Rationale**: Standard GitHub CLI tool, widely available, handles authentication.

**Implementation**:
```bash
# Check gh is available
gh --version

# Create PR
gh pr create \
  --title "feat(001): Doit Command Refactoring" \
  --body "## Summary\n\n<generated from spec>\n\n## Changes\n\n<from commit history>" \
  --base develop \
  --head 001-doit-command-refactor
```

**Fallback**: If `gh` unavailable, provide manual PR URL and instructions.

---

## Resolved Clarifications

| Item | Resolution |
|------|------------|
| Issue template format | GitHub YAML form templates with markdown body |
| Issue hierarchy linking | Native GitHub issue references + "Part of" section |
| Command file structure | Keep existing YAML frontmatter + markdown pattern |
| Scaffold tech stacks | React, .NET, Node, Python, Go with canonical structures |
| MCP integration | Existing pattern with graceful fallback |
| Roadmap format | Structured markdown tables |
| Code review approach | Spec/plan comparison analysis |
| Test detection | Auto-detect from project files |
| PR creation | `gh` CLI with manual fallback |

## Next Steps

1. Create data-model.md with entity definitions
2. Create contracts/ with command interface specifications
3. Create quickstart.md with development setup
