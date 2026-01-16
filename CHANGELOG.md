# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

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
