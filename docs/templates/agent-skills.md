# Agent Skills Format (April 2026)

As of April 2026, doit's Claude Code templates follow the
[Agent Skills open standard](https://agentskills.io). This page documents
the format, where skills live, and how the legacy `.claude/commands/`
layout continues to coexist during the deprecation window.

## Two layouts, one workflow

Anthropic merged custom slash commands into the Skills standard in early
2026. Both of these produce the same `/skill-name` invocation:

**Legacy: flat command file**
```
.claude/commands/doit.constitution.md
```

**Current: skill directory**
```
.claude/skills/doit.constitution/
  SKILL.md           # required — playbook + frontmatter
  reference.md       # optional — loaded on demand
  examples/
    sample.md
```

The skill layout wins when present. Both work today; new templates should
ship as directories.

## SKILL.md frontmatter

Every skill directory has a `SKILL.md` file with YAML frontmatter. Fields
doit uses:

| Field | Required | Purpose |
|:------|:---------|:--------|
| `name` | yes | The `/skill-name` invocation and directory name (lowercase, hyphens allowed, ≤64 chars). |
| `description` | yes | One-sentence summary Claude reads to decide when to load the skill. |
| `when_to_use` | recommended | Trigger keywords / example phrases. Counts against the 1,536-char budget combined with `description`. |
| `allowed-tools` | optional | Space-separated tool list. Constraints use `Bash(pattern)` form, e.g. `Bash(git add *) Bash(git commit *)`. |
| `argument-hint` | optional | Hint shown in the `/` menu autocomplete, e.g. `[issue-number]`. |
| `model` | optional | Override the session model. |
| `disable-model-invocation` | optional | When `true`, only the user can invoke (not Claude). |
| `user-invocable` | optional | When `false`, hides from the `/` menu (Claude-only). |

Fields doit **deliberately does not emit** in the skill layout:

- `effort` — default is to inherit from the session; hard-coding `high`
  on every skill wastes tokens.
- `handoffs` — not a native Claude Code field (doit-only invention). The
  equivalent today is an inline "Next steps" section in the body that
  suggests the next `/doit.<name>` invocation, or `context: fork` with
  `agent:` for skills that truly need an isolated subagent.

## Budgets

Per [Anthropic's skill authoring guide](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices) (April 2026):

- **SKILL.md ≤ 500 lines.** Move long reference material into supporting
  files and link to them with `See [reference.md](reference.md)`. Claude
  loads referenced files on demand.
- **`description` + `when_to_use` ≤ 1,536 characters combined.** Longer
  text is truncated in Claude's skill listing, which can strip the
  keywords Claude needs to match.

`SkillTemplate.validate()` in `doit_cli.models.skill_template` enforces
both budgets; the contract tests in `tests/contract/` run it against
every shipped skill on every CI build.

## Placeholder syntax

SKILL.md still uses Claude's native placeholder syntax:

- `$ARGUMENTS` — the full argument string typed after the skill name.
- `$ARGUMENTS[N]` or `$N` — Nth positional argument, zero-indexed.
- `${CLAUDE_SESSION_ID}`, `${CLAUDE_SKILL_DIR}` — session/path substitutions.

The Copilot transformer (see [copilot-prompts.md](copilot-prompts.md))
rewrites these to `${input:args:…}` when syncing to `.github/prompts/`.

## Migration status

As of April 2026, only the constitution template has been migrated to
the skills layout. Templates still in the flat `.claude/commands/`
format:

- `doit.scaffoldit`, `doit.roadmapit`, `doit.researchit`, `doit.specit`,
  `doit.planit`, `doit.taskit`, `doit.implementit`, `doit.reviewit`,
  `doit.testit`, `doit.fixit`, `doit.documentit`, `doit.checkin`.

Follow-up PRs (labelled Phase 5b, 5c in the modernization tracker)
migrate the rest — oversized templates (specit, researchit, scaffoldit,
documentit) will split into SKILL.md + supporting files to stay under
the 500-line budget.

## Where this lives in the package

- Source: `src/doit_cli/templates/skills/<name>/SKILL.md`
- Model:  [`doit_cli.models.skill_template.SkillTemplate`](../../src/doit_cli/models/skill_template.py)
- Reader: [`doit_cli.services.skill_reader.SkillReader`](../../src/doit_cli/services/skill_reader.py)
- Writer: [`doit_cli.services.skill_writer.SkillWriter`](../../src/doit_cli/services/skill_writer.py)

The Copilot counterpart is documented in
[copilot-prompts.md](copilot-prompts.md).
