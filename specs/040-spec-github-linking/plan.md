# Implementation Plan: GitHub Issue Auto-linking in Spec Creation

**Branch**: `040-spec-github-linking` | **Date**: 2026-01-22 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/040-spec-github-linking/spec.md`

**Note**: This template is filled in by the `/doit.planit` command. See `.claude/commands/doit.planit.md` for the execution workflow.

## Summary

Automatically link specification files to GitHub epics during spec creation by integrating with the roadmap system and GitHub CLI. When developers run `/doit.specit`, the system searches the roadmap for matching items, retrieves the GitHub epic number, and creates bidirectional links: spec frontmatter includes the epic reference, and the GitHub epic description is updated with the spec file path. This provides seamless traceability between specifications and GitHub project tracking without manual effort.

## Technical Context

**Language/Version**: Python 3.11+ (per constitution)
**Primary Dependencies**: Typer (CLI framework), Rich (terminal output), httpx (GitHub API client)
**Storage**: File-based (`.doit/memory/roadmap.md` for roadmap data, spec frontmatter for link metadata)
**Testing**: pytest (per constitution)
**Target Platform**: Cross-platform CLI (Linux, macOS, Windows)
**Project Type**: Single (CLI tool with Python package structure)
**Performance Goals**: <3s for spec linking operation (including GitHub API round-trip)
**Constraints**: Must be non-blocking (spec creation succeeds even if GitHub linking fails), must handle offline scenarios gracefully
**Scale/Scope**: Support repositories with 100+ roadmap items and 1000+ GitHub issues, fuzzy matching must complete in <500ms

## Architecture Overview

<!--
  AUTO-GENERATED: This section is populated by /doit.planit based on Technical Context above.
  Shows the high-level system architecture with component layers.
  Regenerate by running /doit.planit again.
-->

<!-- BEGIN:AUTO-GENERATED section="architecture" -->
```mermaid
flowchart TD
    subgraph "CLI Layer"
        CMD[specit Command]
        FLAGS[--skip-github, --update-links]
    end
    subgraph "Service Layer"
        MATCHER[Roadmap Matcher Service]
        LINKER[Spec-Epic Linker Service]
        UPDATER[GitHub Epic Updater Service]
        FUZZY[Fuzzy Match Algorithm]
    end
    subgraph "Storage Layer"
        ROADMAP[(.doit/memory/roadmap.md)]
        SPEC[(specs/###-feature/spec.md)]
    end
    subgraph "External APIs"
        GH[GitHub CLI (gh)]
        GHAPI[GitHub REST API]
    end

    CMD --> MATCHER
    CMD --> LINKER
    FLAGS --> CMD
    MATCHER --> ROADMAP
    MATCHER --> FUZZY
    LINKER --> SPEC
    LINKER --> UPDATER
    UPDATER --> GH
    GH --> GHAPI
```
<!-- END:AUTO-GENERATED -->

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

**Principle I: Specification-First** ✅

- Feature has complete specification in `specs/040-spec-github-linking/spec.md` with user stories, acceptance scenarios, and requirements

**Principle II: Persistent Memory** ✅

- Uses file-based storage in `.doit/memory/roadmap.md` for roadmap data
- Spec metadata stored in YAML frontmatter (version-controlled markdown)
- No external database dependencies

**Principle III: Auto-Generated Diagrams** ✅

- Spec includes auto-generated user journey flowchart and ER diagram
- Plan will include architecture overview and data model diagrams

**Principle IV: Opinionated Workflow** ✅

- Feature extends the standard `/doit.specit` command
- Integrates with existing workflow: constitution → specit → planit → taskit → implementit

**Principle V: AI-Native Design** ✅

- Implemented as slash command extensions to `/doit.specit`
- All logic operates on markdown files for AI assistant compatibility

**Tech Stack Alignment** ✅

- Python 3.11+ (constitution primary language)
- Typer (constitution CLI framework)
- Rich (constitution terminal formatting)
- httpx (constitution HTTP client - already used for GitHub API in 039-github-roadmap-sync)
- pytest (constitution testing framework)

**Quality Standards** ⚠️

- Tests required for: roadmap matching logic, fuzzy matching algorithm, GitHub API interactions, error handling
- Will use pytest fixtures for mocking GitHub CLI responses

**Result**: PASS - No constitution violations. All technology choices align with established tech stack.

## Project Structure

### Documentation (this feature)

```text
specs/[###-feature]/
├── plan.md              # This file (/doit.planit command output)
├── research.md          # Phase 0 output (/doit.planit command)
├── data-model.md        # Phase 1 output (/doit.planit command)
├── quickstart.md        # Phase 1 output (/doit.planit command)
├── contracts/           # Phase 1 output (/doit.planit command)
└── tasks.md             # Phase 2 output (/doit.taskit command - NOT created by /doit.planit)
```

### Source Code (repository root)

```text
src/doit_toolkit/
├── commands/
│   └── specit.py              # Modified: Add GitHub linking logic
├── services/
│   ├── roadmap_matcher.py     # New: Match feature names to roadmap items
│   ├── github_linker.py       # New: Manage spec-epic linking
│   └── github_client.py       # Existing: Reuse from 039-github-roadmap-sync
├── utils/
│   ├── fuzzy_match.py         # New: Fuzzy string matching algorithm
│   └── spec_parser.py         # New: Parse and update spec frontmatter
└── templates/
    └── spec_template.md       # Modified: Add Epic fields to frontmatter

tests/
├── unit/
│   ├── test_roadmap_matcher.py    # New: Test roadmap matching logic
│   ├── test_fuzzy_match.py        # New: Test fuzzy matching algorithm
│   ├── test_github_linker.py      # New: Test linking operations
│   └── test_spec_parser.py        # New: Test frontmatter updates
├── integration/
│   └── test_specit_github.py      # New: End-to-end spec creation with linking
└── fixtures/
    ├── sample_roadmap.md          # New: Mock roadmap data
    └── sample_spec.md             # New: Mock spec file
```

**Structure Decision**: Single project structure. This feature extends the existing `doit-toolkit` CLI by modifying the `specit` command and adding new service modules for roadmap matching and GitHub linking. The implementation reuses the existing `github_client.py` module from feature 039-github-roadmap-sync to interact with GitHub API.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
| --------- | ---------- | ------------------------------------ |
| N/A       | N/A        | N/A                                  |

**No violations detected** - All design decisions align with constitution principles.

---

## Planning Summary

### Phase 0: Research (Complete)

**Artifact**: [research.md](research.md)

Key findings:

- GitHub API integration approach: Reuse existing `github_client.py` from feature 039
- Roadmap matching: Fuzzy string matching with 80% similarity threshold using `difflib.SequenceMatcher`
- Spec frontmatter format: YAML with markdown links for IDE compatibility
- Epic description update: Append spec reference to dedicated "## Specification" section
- Error handling: Non-blocking, spec creation always succeeds even if GitHub linking fails
- Performance: In-memory caching for roadmap data and 5-minute TTL for GitHub API responses

### Phase 1: Design & Contracts (Complete)

**Artifacts**:

1. [data-model.md](data-model.md) - Entity definitions with ER diagram and state machines
2. [contracts/roadmap_matcher_service.py](contracts/roadmap_matcher_service.py) - Roadmap matching service interface
3. [contracts/github_linker_service.py](contracts/github_linker_service.py) - GitHub linking service interface
4. [contracts/spec_parser_service.py](contracts/spec_parser_service.py) - Spec frontmatter parser interface
5. [quickstart.md](quickstart.md) - Developer usage guide with examples

**Architecture decisions**:

- **CLI Layer**: Extend existing `specit` command with `--skip-github` and `--update-links` flags
- **Service Layer**: Three new services (RoadmapMatcher, GitHubLinker, SpecParser) with clear interfaces
- **Storage Layer**: File-based (roadmap.md, spec frontmatter) - no database changes
- **External APIs**: GitHub CLI (`gh`) for authentication and API operations

**Data model**:

- **Entities**: Spec File, GitHub Epic, Roadmap Item, Link Metadata
- **Relationships**: Many-to-one (spec→epic), one-to-many (roadmap→specs)
- **State Machines**: Spec states (Draft → In Progress → Complete), Epic states (Open → Closed)

### Phase 2: Task Breakdown (Pending)

Next step: Run `/doit.taskit` to generate implementation tasks from this plan.

### Agent Context Update

✓ Updated CLAUDE.md with new technologies:

- Python 3.11+ (per constitution)
- Typer, Rich, httpx (GitHub API client)
- File-based storage (roadmap.md, spec frontmatter)

### Constitution Compliance

✅ **All principles satisfied**:

- Specification-First: Complete spec with user stories and acceptance criteria
- Persistent Memory: File-based storage in `.doit/memory/` and spec frontmatter
- Auto-Generated Diagrams: Architecture overview, ER diagram, state machines
- Opinionated Workflow: Integrates with existing `/doit.specit` command
- AI-Native Design: All operations on markdown files, slash command integration

✅ **Tech stack alignment**: 100% aligned with constitution (Python 3.11+, Typer, Rich, httpx, pytest)

### Estimated Complexity

**Lines of Code**: ~800-1000 LOC

- RoadmapMatcher service: ~200 LOC
- GitHubLinker service: ~300 LOC
- SpecParser service: ~150 LOC
- Fuzzy matching utility: ~100 LOC
- Tests: ~250 LOC

**Testing**: ~15 unit tests + 5 integration tests

**Risk Level**: Low-Medium

- **Low risk**: Reusing proven GitHub client from feature 039
- **Medium risk**: Fuzzy matching accuracy, handling edge cases (closed epics, multiple matches)
