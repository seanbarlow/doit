# Quickstart Guide: Doit Command Refactoring

**Branch**: `001-doit-command-refactor` | **Date**: 2026-01-09
**Purpose**: Development setup and implementation guide

## Prerequisites

### Required Tools

| Tool | Version | Purpose |
|------|---------|---------|
| Git | 2.x+ | Version control |
| Python | 3.11+ | CLI tool |
| Claude Code | Latest | Slash command execution |
| gh CLI | 2.x+ | GitHub PR creation (optional) |

### Optional Tools

| Tool | Purpose |
|------|---------|
| Node.js | For testing JavaScript/TypeScript stacks |
| .NET SDK | For testing .NET stack scaffolding |

## Setup

### 1. Clone and Branch

```bash
# Clone repository
git clone https://github.com/seanbarlow/doit.git
cd doit

# Checkout feature branch (if not already)
git checkout 001-doit-command-refactor
```

### 2. Python Environment

```bash
# Create virtual environment
python -m venv .venv

# Activate
source .venv/bin/activate  # macOS/Linux
.venv\Scripts\activate     # Windows

# Install dependencies
pip install -e .
```

### 3. Verify Setup

```bash
# Check Python CLI
specify --version

# Check gh CLI (optional)
gh --version

# Check Claude Code access
# Run any slash command to verify
```

## Project Structure

```text
doit/
├── .claude/
│   └── commands/           # 📍 PRIMARY: Command definitions
│       ├── speckit.*.md    # Current commands (to be renamed)
│       └── doit.*.md       # New commands (to be created)
├── .specify/
│   ├── memory/
│   │   └── constitution.md # Constitution template
│   ├── scripts/
│   │   └── bash/           # Shell scripts
│   └── templates/          # Document templates
├── .github/
│   └── ISSUE_TEMPLATE/     # 📍 NEW: Issue templates
│       ├── epic.yml
│       ├── feature.yml
│       └── task.yml
├── src/
│   └── specify_cli/        # Python CLI source
├── specs/
│   └── 001-doit-command-refactor/  # This feature
│       ├── spec.md
│       ├── plan.md
│       ├── research.md
│       ├── data-model.md
│       ├── quickstart.md   # This file
│       └── contracts/
└── pyproject.toml          # Python project config
```

## Implementation Phases

### Phase 1: Foundation (Command Renaming)

**Goal**: Rename all speckit commands to doit

**Tasks**:
1. Copy each `speckit.*.md` to `doit.*.md`
2. Update all internal `speckit` references to `doit`
3. Update handoff agent references
4. Update script references
5. Delete old speckit files

**Files to modify**:
- `.claude/commands/*.md` (all 9 files)
- `.specify/scripts/bash/*.sh` (all 5 scripts)
- `.specify/templates/*.md` (update references)
- `pyproject.toml` (update project name)

**Verification**:
```bash
# Run renamed command
/doit.specify "test feature"
# Should execute without speckit references
```

### Phase 2: Constitution Enhancement

**Goal**: Add tech stack and infrastructure sections

**Tasks**:
1. Update constitution.md template with new sections
2. Add prompts for tech stack in doit.constitution.md
3. Add prompts for infrastructure in doit.constitution.md
4. Add section update capability

**New Sections in Constitution**:
```markdown
## Purpose & Goals
[Project purpose]

## Tech Stack
- Languages: [list]
- Frameworks: [list]
- Libraries: [list]

## Infrastructure
- Hosting: [environment]
- Cloud Provider: [provider]
- Deployment: [strategy]
```

### Phase 3: Scaffold Command

**Goal**: Create new scaffold command

**Tasks**:
1. Create `doit.scaffold.md` command file
2. Implement constitution reading logic
3. Define structure templates for each tech stack
4. Implement folder/file generation
5. Implement .gitignore generation
6. Implement analysis mode for existing projects

**Key Logic**:
```markdown
1. Read constitution.md
2. Extract tech_stack section
3. Match to structure template:
   - React → react-structure.md
   - .NET → dotnet-structure.md
   - etc.
4. Create folders and files
5. Generate appropriate .gitignore
```

### Phase 4: Specify Enhancement

**Goal**: Integrate clarify and add GitHub issues

**Tasks**:
1. Merge clarify logic into specify command
2. Add 8-category ambiguity scan
3. Add GitHub MCP integration for Epic creation
4. Add GitHub MCP integration for Feature creation
5. Remove standalone clarify command

**Clarification Categories** (from clarify.md):
1. Functional Scope & Behavior
2. Domain & Data Model
3. Interaction & UX Flow
4. Non-Functional Quality Attributes
5. Integration & External Dependencies
6. Edge Cases & Failure Handling
7. Constraints & Tradeoffs
8. Terminology & Consistency

### Phase 5: New Commands

**Goal**: Implement review, test, checkin commands

**doit.review**:
- Load spec, plan, tasks
- Analyze implemented code
- Generate findings report
- Walk through manual tests
- Collect sign-off

**doit.test**:
- Detect test framework
- Execute tests
- Map results to requirements
- Present manual checklist
- Generate test report

**doit.checkin**:
- Close GitHub issues
- Update roadmaps
- Generate documentation
- Commit changes
- Create PR

### Phase 6: Issue Templates

**Goal**: Create GitHub issue templates

**Tasks**:
1. Create `.github/ISSUE_TEMPLATE/` directory
2. Create `epic.yml` template
3. Create `feature.yml` template
4. Create `task.yml` template
5. Test template rendering in GitHub

## Testing Strategy

### Manual Testing

Each command should be tested with:
1. **Happy path**: Normal execution with valid inputs
2. **Edge cases**: Missing prerequisites, empty inputs
3. **Error handling**: API failures, file not found
4. **Integration**: Full workflow from constitution to checkin

### Test Scenarios

| Scenario | Commands | Expected Outcome |
|----------|----------|------------------|
| New project setup | constitution → scaffold | Project structure created |
| Feature creation | specify | Spec + Epic + Features created |
| Full workflow | All commands | PR created with closed issues |
| Existing project | scaffold --analyze | Report generated, no changes |
| No GitHub remote | specify, tasks | Local files only, no issues |

## Common Commands

### Development

```bash
# Edit command file
code .claude/commands/doit.specify.md

# Test command
/doit.specify "test feature"

# Check git status
git status

# View diff
git diff .claude/commands/
```

### Debugging

```bash
# Check script output
.specify/scripts/bash/setup-plan.sh --json

# Verify prerequisites
.specify/scripts/bash/check-prerequisites.sh

# Check GitHub CLI auth
gh auth status
```

## Resources

- [spec.md](spec.md) - Feature specification
- [plan.md](plan.md) - Implementation plan
- [research.md](research.md) - Research findings
- [data-model.md](data-model.md) - Entity definitions
- [contracts/commands.md](contracts/commands.md) - Command interfaces
- [contracts/issue-templates.md](contracts/issue-templates.md) - Issue template specs
- [current-functionality.md](current-functionality.md) - Existing command analysis
