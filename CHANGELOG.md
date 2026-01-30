# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- **Research Command for Product Owners** (#052)
  - New `/doit.researchit` slash command for pre-specification business requirements capture
  - Interactive Q&A workflow: 12 guided questions across 4 phases (Problem, Users, Requirements, Metrics)
  - No technology questions - focused purely on business value and user needs
  - Generates 4 research artifacts:
    - `research.md` - Problem statement, target users, business goals, success metrics
    - `user-stories.md` - User stories in Given/When/Then format with persona references
    - `interview-notes.md` - Stakeholder interview templates with suggested questions
    - `competitive-analysis.md` - Competitor comparison framework
  - Session resume support: Save progress mid-session and continue later
  - Gap-aware feature numbering: Correctly handles directory number gaps
  - Draft cleanup: Automatic removal of draft files after completion
  - Integration with `/doit.specit`: Research artifacts auto-loaded for specification

- **Specit Research Integration**
  - `/doit.specit` now automatically loads research artifacts from prior `/doit.researchit` sessions
  - Seamless handoff from Product Owner research to technical specification

## [0.1.14] - 2026-01-22

### Fixed

- **doit init missing templates** - Fixed `doit init` and `doit init --update` not copying all bundled templates. The following templates were missing:
  - Config files: `hooks.yaml` and `validation-rules.yaml` (only `context.yaml` was copied)
  - Hook templates: `pre-commit.sh`, `pre-push.sh`, `post-commit.sh`, `post-merge.sh` (entire `hooks/` directory was skipped)
  - Workflow document template: `agent-file-template.md`
- Added `copy_hook_templates()` method to TemplateManager for git hook scripts
- Added `copy_workflow_document_templates()` method for workflow document templates
- `doit init` now correctly copies 36 template files (was 28)

## [0.1.13] - 2026-01-22

### Added

- **GitLab Git Provider Support** (#637)
  - Full GitLab REST API v4 implementation (1035 lines)
  - Personal Access Token (PAT) authentication with token validation
  - Issue management: create, read, update, list with label filtering
  - Merge request management: create, read, list with branch filtering
  - Milestone management: create, read, update, list with state filtering
  - Label auto-creation with scoped priority labels (`priority::1` through `priority::4`)
  - Self-hosted GitLab instance support with configurable host
  - Comprehensive error handling (401/403/404/429/5xx)
  - 45 unit tests with 97% requirement coverage
  - Integration test scaffolding for live API testing

- **GitLab Provider Tutorial**
  - Step-by-step guide for GitLab configuration (`docs/tutorials/04-gitlab-provider-tutorial.md`)
  - Personal Access Token creation walkthrough
  - Provider wizard and manual configuration options
  - Self-hosted GitLab setup instructions
  - Troubleshooting guide for common issues

### Changed

- **Documentation Updates**
  - Added Git Provider Configuration section to quickstart.md
  - Updated tutorials index with GitLab provider tutorial
  - Provider comparison table (GitHub, GitLab, Azure DevOps)

## [0.1.12] - 2026-01-22

### Added

- **Git Provider Configuration Wizard** (#636)
  - Interactive `doit provider wizard` command for setting up git providers
  - Auto-detection of provider from git remote URL
  - Support for GitHub, GitLab, and Azure DevOps
  - Token validation against provider APIs
  - `gh` CLI integration for GitHub token retrieval
  - Configuration backup and restore functionality
  - Provider status command: `doit provider status`

- **Constitution and Tech Stack Separation** (#606)
  - Separated `tech-stack.md` from `constitution.md` for cleaner organization
  - `doit constitution cleanup` command for migrating existing projects
  - Context loading optimization with dedicated tech stack source
  - Command overrides support in constitution
  - 24 implementation tasks, 1377 tests pass

## [0.1.11] - 2026-01-22

### Added

- **Unified CLI Package** (#603)
  - Consolidated `doit_cli` and `doit_toolkit_cli` into single unified package
  - Merged 17 files (7 models, 4 utils, 5 services, 1 command) into `doit_cli`
  - Combined two `github_service.py` files into unified service with issue, epic, milestone, and branch operations
  - Cleaner import structure using `doit_cli.*` paths throughout
  - All 1345 tests pass with no test logic modifications

- **Team Collaboration Features** (#602)
  - Git-based sync for constitution and roadmap files across team members
  - Change notifications via watchdog file monitoring
  - Conflict resolution UI for handling merge conflicts
  - Access control with read-only and read-write modes
  - 28 implementation tasks, 18 integration tests

### Fixed

- **Agent Detection** (#596)
  - Improved agent detection before updating instruction files
  - Scripts now correctly detect configured AI agents (Claude, Copilot)
  - Prevents errors when only one agent is configured

### Changed

- **Package Structure**
  - `pyproject.toml` now references only `doit_cli` package
  - Removed `doit_toolkit_cli` directory entirely
  - Import paths standardized across codebase

## [0.1.10] - 2026-01-22

### Added

- **GitHub Milestone Generation from Priorities** (#594)
  - `doit roadmapit sync-milestones` command to create GitHub milestones for priority levels (P1-P4)
  - Automatic assignment of roadmap epics to corresponding priority milestones
  - Detection and prompt to close completed priority milestones
  - `--dry-run` flag to preview milestone sync changes
  - Milestone titles: "P1 - Critical", "P2 - High Priority", "P3 - Medium Priority", "P4 - Low Priority"
  - Seamless integration with GitHub via `gh` CLI

- **GitHub Epic Auto-linking in Spec Creation** (#591)
  - Automatic linking of specs to GitHub epics during `/doit.specit`
  - Fuzzy matching of spec names to roadmap items (80% threshold)
  - Bidirectional linking: spec→epic and epic→spec
  - Interactive epic creation workflow when no epic exists
  - Priority label propagation from roadmap to GitHub issues

- **GitHub Epic and Issue Integration for Roadmap** (#586)
  - Display GitHub epic state (open/closed) in roadmap items
  - `doit roadmapit add` creates GitHub epics with priority labels
  - Smart epic description generation with rationale
  - 30-minute cache for GitHub API responses
  - Custom label support for epics

### Fixed

- **Agent Detection in update-agent-context.sh** (#596)
  - Fixed errors when only one AI agent (Claude or Copilot) is configured
  - Added `detect_configured_agents()` function matching Python's AgentDetector logic
  - Script now only updates instruction files for detected agents
  - Prevents attempts to create/update CLAUDE.md when only Copilot configured (and vice versa)

- **Context Roadmap Summarization** (#593)
  - Fixed roadmap being summarized even when under token limit
  - Summarization now only triggers when roadmap exceeds soft threshold
  - Improved context efficiency and preservation of roadmap details

## [0.1.9] - 2026-01-20

### Added

- **Context Roadmap Summary** (#576)
  - Intelligent roadmap summarization for AI context injection
  - Priority-based summaries: P1/P2 items with full content and rationale, P3/P4 titles only
  - Current feature branch highlighting with `[CURRENT]` marker
  - Completed roadmap items formatted for AI semantic matching
  - Two-tier context condensation: guidance prompt at soft threshold, truncation fallback
  - New `SummarizationConfig` for customizing summarization behavior
  - `doit context show` now displays summarization status (summarized/formatted/complete)

### Changed

- **AI Context Injection**
  - Context loader now uses RoadmapSummarizer for intelligent roadmap condensation
  - Added ContextCondenser for threshold-based condensation with AI guidance prompts
  - Completed roadmap items parsed and formatted for AI semantic understanding

## [0.1.8] - 2026-01-17

### Added

- **Spec-Task Cross References** (#389)
  - `doit xref` command for bidirectional traceability between specs and tasks
  - Coverage reports showing which requirements are implemented
  - Validation rules for orphan tasks and uncovered requirements
  - JSON and line output formats for CI/IDE integration

- **Bug-Fix Workflow** (#440)
  - `/doit.fixit` slash command for structured bug-fix workflow
  - GitHub issue integration for bug tracking
  - AI-assisted investigation and root cause analysis
  - Fix planning with test scenarios
  - Reuses existing reviewit/testit commands

- **Automatic Mermaid Diagram Generation** (#472)
  - `doit diagram` command for auto-generating diagrams from specs
  - User journey flowcharts from user stories
  - Entity relationship diagrams from data models
  - Architecture diagrams from component descriptions
  - Syntax validation before insertion
  - Preview mode and strict validation options

### Changed

- **Documentation Updates**
  - Updated README.md, quickstart.md, tutorials with new commands
  - Added `/doit.fixit` to all command reference tables
  - Added `doit validate`, `doit status`, `doit xref`, `doit diagram` CLI commands
  - Fixed 2 broken documentation links
  - Audited and verified all 43 documentation files

- **Roadmap Milestone**
  - All P1 and P2 items completed - MVP achieved
  - 13 total items shipped (4 P1, 8 P2)

## [0.1.7] - 2026-01-16

### Fixed

- **Pre-push hook fails with extra arguments** (#374) - Fixed pre-push and pre-commit hook templates incorrectly passing `"$@"` to `doit hooks validate`, which only expects a single `hook_type` argument. Git passes remote name and URL as CLI arguments to pre-push hooks, causing validation to fail with "Got unexpected extra arguments".

## [0.1.6] - 2026-01-15

### Fixed

- **sync-prompts command not finding templates** - Fixed `doit sync-prompts` failing with "command not found in templates folder" when used in end-user projects. The command now correctly falls back to bundled package templates when project templates don't exist.

## [0.1.5] - 2026-01-15

### Changed

- **Unified Template Management** (#171)
  - Single source of truth: All doit command templates now live in `templates/commands/`
  - Copilot prompts are generated dynamically via transformation during `doit init`
  - Removed duplicate `templates/prompts/` directory (11 files)
  - Maintainers edit one file; changes apply to both Claude Code and GitHub Copilot

### Added

- **GitHub Copilot Prompts Synchronization** (#023)
  - `doit sync-prompts` command to generate Copilot prompt files from command templates
  - `doit sync-prompts --check` to detect drift between templates and prompts
  - Automatic YAML frontmatter stripping and $ARGUMENTS placeholder handling
  - Selective synchronization support for individual commands

- **Git Hooks Workflow Enforcement** (#025)
  - `doit hooks install` and `doit hooks uninstall` commands for managing Git hooks
  - Pre-commit hook validates feature branches have spec.md
  - Pre-push hook validates required artifacts (spec.md, plan.md, tasks.md)
  - Configurable via `.doit/config/hooks.yaml`
  - Bypass with `--no-verify` for emergency fixes

- **AI Context Injection** (#026)
  - Automatic loading of constitution.md and roadmap.md for all commands
  - `doit context show` command to display loaded context
  - `doit context status` command to show configuration and file availability
  - Feature branch detection loads current spec automatically
  - Related spec discovery based on keyword matching
  - Configurable via `.doit/config/context.yaml`

- **Template Context Injection** (#027)
  - All 11 doit command templates now include context loading step
  - AI assistants automatically receive project context before executing commands
  - Context loading positioned before main logic in all templates
  - Graceful handling of missing context files

- **Documentation and Tutorial Refresh** (#028)
  - Updated quickstart.md with CLI commands table and context injection documentation
  - Updated README.md with separate CLI and slash command sections
  - Regenerated feature index with all 19+ features
  - Added workflow enforcement documentation
  - Updated tutorials with context injection and sync-prompts mentions

- `Agent.needs_transformation` property for determining which agents require template transformation
- `TemplateManager._transform_and_write_templates()` for on-demand prompt generation
- 15 integration tests for context injection
- 29 new unit tests for unified template functionality

## [0.1.4] - 2026-01-13

### Fixed

- **GitHub Copilot prompt files**: Replaced deprecated `mode: agent` with `agent: true` (#139)
  - Updated all 11 prompt files in `/templates/prompts/`
  - Ensures compatibility with VS Code 1.106+ and current GitHub Copilot specification
  - Eliminates deprecation warnings when using Do-It prompts

### Added

- **Constitution command improvements** (#131)
  - Dotfile exclusion: Excludes dotfiles and dotfolders when scanning for context
  - Greenfield detection: Detects empty/new projects and provides interactive questioning

- **Comprehensive tutorials** (#111, #112, #113)
  - Added Do-It workflow tutorials with step-by-step guides
  - Updated quickstart and upgrade guides with correct commands

## [0.1.3] - 2026-01-13

### Added

- Implemented Gitflow-inspired branching strategy with `develop` as default branch (#75)
  - `develop` is now the default branch for feature integration
  - `main` reserved for production-ready releases
  - Updated CONTRIBUTING.md with new branching workflow
  - Added release process documentation for maintainers

### Fixed

- Roadmap templates now contain placeholder syntax instead of sample data (#56)
  - `templates/memory/roadmap.md` - clean template for new projects
  - `templates/memory/roadmap_completed.md` - clean template for tracking completed items
