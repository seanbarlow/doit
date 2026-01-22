# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

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
