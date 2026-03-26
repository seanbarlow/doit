# Completed Roadmap Items

**Project**: Do-It
**Created**: 2026-01-15
**Purpose**: Historical record of completed roadmap items for AI context and project history

---

## Recently Completed

<!-- Last 20 completed items - older items are archived below -->

| Item | Original Priority | Completed Date | Feature Branch | Notes |
|------|-------------------|----------------|----------------|-------|
| Persona-aware user story generation | P2 | 2026-03-26 | `057-persona-aware-user-story-generation` | Auto-map stories to personas using P-NNN IDs during `/doit.specit`. 6-level matching rules (goal, pain point, context, role, multi-persona, no match). Traceability table auto-update in personas.md. Coverage report. Graceful fallback when no personas. Template-only: specit.md, spec-template.md, user-stories-template.md. 54 tests, 13 FR requirements, 8 user stories |
| Project-level personas with context injection | P2 | 2026-03-26 | `056-persona-context-injection` | Personas as first-class context source (priority 3). `load_personas()` in ContextLoader with feature-level precedence. Roadmapit generates `.doit/memory/personas.md`. Persona context injected into researchit, specit, planit. Per-command overrides disable for non-target commands. Fixed `_from_dict` command merge bug. 127 tests (16 new personas + 2 merge tests), 12 FR requirements, 6 user stories |
| MCP Server for doit Operations | P2 | 2026-03-26 | `055-mcp-server` | Exposes 6 MCP tools (validate, status, tasks, context, scaffold, verify) + 3 resources via FastMCP with stdio transport. Optional dependency `mcp`. 30 tests (15 unit + 4 integration + 11 automated manual), 13 FR requirements covered. |
| Research-to-Spec Auto-Pipeline | P3 | 2026-01-30 | `054-research-spec-pipeline` | Seamless handoff from `/doit.researchit` to `/doit.specit` with context preservation. Handoff prompt with Continue/Later options, `--auto-continue` flag for batch workflows, artifact validation (Step 5), progress indicator, resume instructions. Template-only feature: doit.researchit.md, doit.specit.md. 11 tasks (100% complete), 4 user stories, 12 requirements |
| Stakeholder Persona Templates | P3 | 2026-01-30 | `053-stakeholder-persona-templates` | Comprehensive persona template (17 fields vs 4), persona relationship mapping, unique IDs (P-NNN) for traceability, `/doit.researchit` Q&A integration, `/doit.specit` persona-story linking. Template-only feature: persona-template.md, personas-output-template.md. 10 tasks (100% complete), 4 user stories, 10 requirements |
| Research command for Product Owners (`/doit.researchit`) | P2 | 2026-01-29 | `052-researchit-command` | Pre-specification Q&A workflow for capturing business requirements without technology decisions. 12-question interactive session across 4 phases (Problem, Users, Requirements, Metrics). Generates research.md, user-stories.md, interview-notes.md, competitive-analysis.md. Integrated with `/doit.specit` for automatic artifact loading. 15 tasks (100% complete), 5 user stories, 18 requirements covered |
| macOS E2E testing infrastructure | P2 | 2026-01-28 | `050-macos-e2e-tests` | Comprehensive macOS testing: 112 automated tests across 20 test files, APFS/case-sensitivity, Unicode NFD/NFC normalization, BSD utilities validation, bash/zsh compatibility, extended attributes (xattr), symbolic links, GitHub Actions CI/CD with macOS runners (14, 15), 34 tasks (100% complete), 4 user stories |
| Windows E2E testing infrastructure | P1 | 2026-01-27 | `049-e2e-windows-tests` | Comprehensive Windows testing: 146 automated tests (99.3% pass), PowerShell 7.x validation, cross-platform parity, CI/CD integration, 31 tasks (100% complete), 4 user stories, path handling, CRLF line endings |
| GitLab git provider support | P3 | 2026-01-22 | `048-gitlab-provider` | Full GitLab REST API v4 implementation, PAT authentication, issue/MR/milestone management, self-hosted support, 26 tasks (100% complete), 45 unit tests pass |
| Git provider configuration wizard | P3 | 2026-01-22 | `047-provider-config-wizard` | Interactive wizard for GitHub/ADO/GitLab auth setup, gh CLI integration, PAT validation, config backup/restore, 28 tasks (100% complete), 1432 tests pass |
| Constitution and tech stack separation | P2 | 2026-01-22 | `046-constitution-tech-stack-split` | Separated constitution.md from tech-stack.md, cleanup command for migration, context loading optimization, command overrides, 24 tasks (100% complete), 1377 tests pass |
| Azure DevOps git provider support | P2 | 2026-01-22 | `044-git-provider-abstraction` | *Delivered as part of 044* - Full Azure DevOps REST API implementation, issue/PR/milestone management, PAT authentication, 745 lines |
| Git provider abstraction layer | P2 | 2026-01-22 | `044-git-provider-abstraction` | Unified interface for GitHub/Azure DevOps/GitLab, provider auto-detection from git remote, 31 tasks (100% complete), full GitHub+ADO implementation, GitLab stub |
| Unified CLI package consolidation | P2 | 2026-01-22 | `043-unified-cli` | Merged doit_toolkit_cli into doit_cli, single package structure, 17 files migrated, github_service.py merged, 1345 tests pass, cleaner imports |
| Team collaboration features (shared memory, notifications) | P4 | 2026-01-22 | `042-team-collaboration` | Git-based sync for constitution/roadmap, change notifications via watchdog, conflict resolution UI, access control (read-only/read-write), 28 tasks (100% complete), 18 integration tests passed |
| GitHub Milestone Generation from Priorities | P3 | 2026-01-22 | `041-milestone-generation` | Auto-create GitHub milestones for priority levels (P1-P4), assign epics to milestones, close completed milestones, --dry-run support, 21 tasks (100% complete), 1,327 tests passed |
| GitHub Issue Auto-linking in Spec Creation | P2 | 2026-01-21 | `040-spec-github-linking` | Auto-link specs to GitHub epics via `/doit.specit`, fuzzy roadmap matching (80% threshold), bidirectional linking, epic creation workflow, 124 tests (100% pass) |
| Roadmap Status Sync from GitHub | P3 | 2026-01-21 | `039-github-roadmap-sync` | GitHub epic state display (open/closed), synced with roadmap items, part of GitHub integration |
| Auto-create GitHub Epics from Roadmap Items | P3 | 2026-01-21 | `039-github-roadmap-sync` | `doit roadmapit add` creates GitHub epics with priority labels, descriptions, and custom labels |
---

## Archive

<!-- Older completed items (beyond 20 most recent) -->

<details>
<summary>Archived Items (click to expand)</summary>

| Item | Original Priority | Completed Date | Feature Branch |
|------|-------------------|----------------|----------------|
| GitHub epic and issue integration for roadmap command | P2 | 2026-01-21 | `039-github-roadmap-sync` |
| Context roadmap summary and AI context condensation | P2 | 2026-01-20 | `038-context-roadmap-summary` |
| Documentation audit and link fixes | — | 2026-01-17 | — |
| Memory search and query across project context | P2 | 2026-01-16 | `037-memory-search-query` |
| Spec analytics and metrics dashboard | P3 | 2026-01-16 | `036-spec-analytics-dashboard` |
| Automatic Mermaid diagram generation from specs | P2 | 2026-01-16 | `035-auto-mermaid-diagrams` |
| Bug-fix workflow command (doit.fixit) | P1 | 2026-01-16 | `034-fixit-workflow` |
| Cross-reference support between specs and tasks | P2 | 2026-01-16 | `033-spec-task-crossrefs` |
| Spec status dashboard command | P2 | 2026-01-16 | `032-status-dashboard` |
| Init command workflow integration | P2 | 2026-01-16 | `031-init-workflow-integration` |
| Interactive guided workflows with validation | P2 | 2026-01-16 | `030-guided-workflows` |
| Spec validation and linting | P2 | 2026-01-15 | `029-spec-validation-linting` |
| AI context injection for commands | P2 | 2026-01-15 | `026-ai-context-injection`, `027-template-context-injection` |
| Git hook integration for workflow enforcement | P2 | 2026-01-15 | `025-git-hooks-workflow` |
| Unified template management | P1 | 2026-01-15 | `024-unified-templates` |
| Multi-agent prompt synchronization | P1 | 2026-01-15 | `023-copilot-prompts-sync` |
| Core workflow commands | P1 | 2026-01-10 | — |

</details>

---

## Statistics

- **Total Items Completed**: 33
- **P1 Items Completed**: 5 (5 archived)
- **P2 Items Completed**: 18 (9 archived)
- **P3 Items Completed**: 8 (1 archived)
- **P4 Items Completed**: 2
- **Other**: 1 (documentation audit, archived)

---

## Notes

- This file is maintained automatically by `/doit.checkin` when features complete
- Items are matched by feature branch reference `[###-feature-name]`
- Only the 20 most recent items are kept in "Recently Completed"
- Older items are moved to the Archive section
- Use this history to understand project evolution and past decisions
