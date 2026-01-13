# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.4] - 2026-01-13

### Fixed

- **GitHub Copilot prompt files**: Replaced deprecated `mode: agent` with `agent: true` (#139)
  - Updated all 11 prompt files in `/templates/prompts/`
  - Ensures compatibility with VS Code 1.106+ and current GitHub Copilot specification
  - Eliminates deprecation warnings when using DoIt prompts

### Added

- **Constitution command improvements** (#131)
  - Dotfile exclusion: Excludes dotfiles and dotfolders when scanning for context
  - Greenfield detection: Detects empty/new projects and provides interactive questioning

- **Comprehensive tutorials** (#111, #112, #113)
  - Added DoIt workflow tutorials with step-by-step guides
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
