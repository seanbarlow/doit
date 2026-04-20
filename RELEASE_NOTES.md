# Release Notes - v0.2.0

**Release Date**: 2026-04-20

## Highlights

This release completes the **April 2026 modernization sweep**: Claude Code
templates now ship as [Agent Skills](https://agentskills.io), GitHub Copilot
prompts adopt the native VS Code `.prompt.md` schema, and a new
`DoitError` / `ExitCode` / `format_option` foundation gives every CLI
command a uniform contract. A new JSON Schema contract for the
constitution frontmatter lands alongside.

**Coming next in 0.3.0** (on `develop`): auto-migration of legacy
`.doit/memory/constitution.md` files via `doit update`, paired with an
enrichment step in the `/doit.constitution` skill that fills in
placeholder values by reading the constitution body. See
[Unreleased](CHANGELOG.md#unreleased) in the changelog.

No breaking changes. Legacy `.claude/commands/` templates continue to work
during Anthropic's back-compat window — upgrade at your own pace.

## What's New

### Agent Skills layout for Claude Code

All 13 workflow commands now ship as skill directories under
`.claude/skills/doit.<name>/SKILL.md`, generated alongside the legacy flat
command files. Oversized templates (`specit`, `researchit`, `scaffoldit`,
`documentit`) split into `SKILL.md` + supporting reference files to stay
under Anthropic's 500-line skill budget. See
[docs/templates/agent-skills.md](docs/templates/agent-skills.md).

### Native GitHub Copilot `.prompt.md` frontmatter

`.github/prompts/doit.*.prompt.md` now use the April 2026 VS Code schema:
`description`, `agent: agent`, `tools: [...]`, optional `model`. The
`PromptTransformer` translates Claude's coarse verbs
(`Read`, `Write`, `Bash`) to VS Code tool identifiers
(`editFiles`, `search`, `runCommands`) and rewrites `$ARGUMENTS`
placeholders to `${input:args}`. A contract test fails CI if shipped
prompts drift from the transformer output. See
[docs/templates/copilot-prompts.md](docs/templates/copilot-prompts.md).

### CLI conventions foundation

- **`DoitError` hierarchy** at
  [src/doit_cli/errors.py](src/doit_cli/errors.py) — subclass at
  boundaries, chain with `raise X(...) from e`.
- **`ExitCode` constants** at
  [src/doit_cli/exit_codes.py](src/doit_cli/exit_codes.py) — no more
  numeric literals in `typer.Exit`.
- **`format_option()` + `OutputFormat`** at
  [src/doit_cli/cli/output.py](src/doit_cli/cli/output.py) — one
  `--format / -f` flag with per-command `allowed` subsets.

See [docs/guides/cli-conventions.md](docs/guides/cli-conventions.md).

### Constitution frontmatter JSON Schema

A canonical contract for `.doit/memory/constitution.md` YAML frontmatter
ships at
[src/doit_cli/schemas/frontmatter.schema.json](src/doit_cli/schemas/frontmatter.schema.json).
Required fields: `id`, `name`, `kind`, `phase`, `icon`, `tagline`,
`dependencies`. See
[docs/templates/schemas.md](docs/templates/schemas.md).

### Quality foundation

- mypy now runs as a pre-commit hook and blocks commits on type errors.
- `context_loader` service refactored into a package.
- GitHub provider gains branch-creation, issue-close, and issue-comment
  helpers used by `doit.checkin` and `doit.fixit`.

## Breaking Changes

None.

## Deprecations

- Flat `.claude/commands/doit.<name>.md` templates continue to work in
  0.2.0 but are deprecated in favor of the Skills layout. A future minor
  release will remove the flat-command generator.

## Upgrade Instructions

1. Upgrade the CLI:

   ```bash
   uv tool install doit-toolkit-cli --force
   ```

2. Refresh project files to get the Skills layout and new Copilot
   frontmatter:

   ```bash
   doit init --here --force --ai claude,copilot
   ```

3. Verify the new layout:

   ```bash
   ls .claude/skills/           # doit.* skill directories
   ls .github/prompts/          # native-schema .prompt.md files
   ```

See the [Upgrade Guide](docs/upgrade.md) for detailed scenarios and the
"0.1.x → 0.2.0" section.

## Contributors

- Claude Code implementation assistance

## Full Changelog

See [CHANGELOG.md](./CHANGELOG.md) for complete release history.
