# Completed Roadmap Items

**Project**: Do-It
**Created**: 2026-01-15
**Purpose**: Historical record of completed roadmap items for AI context and project history

---

## Recently Completed

<!-- Last 20 completed items - older items are archived below -->

| Item | Original Priority | Completed Date | Feature Branch | Notes |
|------|-------------------|----------------|----------------|-------|
| Personas.md migration (extends memory-file migrator pattern) | P3 | 2026-04-21 | `062-personas-migration` | Closes the memory-file-migration pattern across all four `.doit/memory/*.md` files (constitution, roadmap, tech-stack, personas). New `personas_migrator.migrate_personas` applies the spec-060 shape-migrator pattern — opt-in semantic: absent file is a valid NO_OP, never auto-created. New `personas_enricher.enrich_personas` is linter-only (reports `{placeholder}` tokens via PARTIAL; never modifies the file; points users at `/doit.roadmapit` or `/doit.researchit` via a CLI hint). New `doit memory enrich personas` subcommand + `_validate_personas` rule enforcing required H2s and canonical `Persona: P-NNN` three-digit regex. Umbrella `doit memory migrate` now emits 4 rows (constitution → roadmap → tech-stack → personas). 47 feature tests (9 unit + 10 integration + 28 contract), 81% coverage on new files, full suite 2296/2296. |
| Fix roadmap migrator H3 matching for decorated priority headings | P1 (bug fix) | 2026-04-21 | `061-fix-roadmap-h3-matching` | Regression fix for spec 060 found by dogfooding against doit's own `.doit/memory/roadmap.md`. Migrator now mirrors `memory_validator._validate_roadmap`'s `^p[1-4]\b` prefix regex so decorated headings (`### P1 - Critical (MVP)`) are recognised as present; no more spurious duplicate stubs. Shared helper `_memory_shape.insert_section_if_missing` gained an optional per-H3 `matchers` parameter (default preserves spec 060 exact-match; tech-stack migrator unchanged). 77 feature tests + 1 repo-dogfood regression guard, 95% coverage on touched files, full suite 2257/2257. |
| Memory files migration (roadmap.md, tech-stack.md) | P2 | 2026-04-21 | `060-memory-files-migration` | Extends spec 059's migrator + enricher pattern to `.doit/memory/roadmap.md` and `tech-stack.md`. `doit update` inserts `## Active Requirements` + `### P1..P4` and `## Tech Stack` + `### Languages/Frameworks/Libraries` with placeholder stubs. New `doit memory enrich roadmap` and `doit memory enrich tech-stack` CLIs + `doit memory migrate` umbrella. Preserves CRLF line endings. 57 feature tests (8 contract, 14 unit, 20+15 integration), 91% coverage, 100% FR/SC automated. Full suite 2127/2127. |
| Constitution frontmatter migration | P2 | 2026-04-20 | `059-constitution-frontmatter-migration` | `doit update` auto-migrates legacy `.doit/memory/constitution.md` to the 0.3.0+ YAML-frontmatter shape (prepend / patch / idempotent NO_OP / atomic-write error). New `doit constitution enrich` CLI deterministically fills placeholders from the body. `ConstitutionFrontmatter.validate()` classifies placeholder values as WARNING (not ERROR). 40 feature tests, 86% coverage, 100% FR/SC automated. Full suite 2070/2070. |
| Error recovery patterns in all commands | P2 | 2026-03-26 | `058-error-recovery-patterns` | Structured `## Error Recovery` sections added to all 13 command templates. 3-5 error scenarios per template with plain-language summaries, severity indicators, numbered recovery steps, verification steps, prevention tips, and escalation paths. Migrated 9 existing On Error sections, wrote 3 from scratch, aligned fixit reference. 159 new tests, 12 FR requirements, 8 user stories. Documentation-only feature (no Python code changes). |
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

---

## Archive

<!-- Older completed items (beyond 20 most recent) -->

<details>
<summary>Archived Items (click to expand)</summary>

| Item | Original Priority | Completed Date | Feature Branch |
|------|-------------------|----------------|----------------|
| GitHub Milestone Generation from Priorities | P3 | 2026-01-22 | `041-milestone-generation` |
| GitHub Issue Auto-linking in Spec Creation | P2 | 2026-01-21 | `040-spec-github-linking` |
| Roadmap Status Sync from GitHub | P3 | 2026-01-21 | `039-github-roadmap-sync` |
| Auto-create GitHub Epics from Roadmap Items | P3 | 2026-01-21 | `039-github-roadmap-sync` |
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

- **Total Items Completed**: 35
- **P1 Items Completed**: 6 (5 archived) — includes 1 bug-fix (spec 061)
- **P2 Items Completed**: 18 (10 archived)
- **P3 Items Completed**: 9 (2 archived)
- **P4 Items Completed**: 2
- **Other**: 1 (documentation audit, archived)

---

## Notes

- This file is maintained automatically by `/doit.checkin` when features complete
- Items are matched by feature branch reference `[###-feature-name]`
- Only the 20 most recent items are kept in "Recently Completed"
- Older items are moved to the Archive section
- Use this history to understand project evolution and past decisions
