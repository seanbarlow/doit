# GitHub Copilot Prompt Files

**Available in**: doit 0.2.0+ (native VS Code `.prompt.md` schema).

doit generates GitHub Copilot slash-command prompts at
`<project>/.github/prompts/doit.*.prompt.md`. Each is a semantic rewrite
of the matching `src/doit_cli/templates/commands/doit.*.md` source file,
not a byte-for-byte copy — doit translates between Claude's and VS Code
Copilot's competing frontmatter schemas.

## Frontmatter contract

Per the [VS Code prompt files spec](https://code.visualstudio.com/docs/copilot/customization/prompt-files) (April 2026), each shipped
`.prompt.md` emits:

```yaml
---
description: <from source>
agent: agent
tools: [editFiles, search, codebase, runCommands, githubRepo?]
model: <from source, if set>
---
```

Fields emitted:

| Field | Purpose |
|:------|:--------|
| `description` | Short summary shown in the `/` menu. Copied verbatim from the source Claude frontmatter. |
| `agent` | Always `agent` — tells Copilot it may auto-select tools. Without this Copilot uses instructions only. |
| `tools` | List of VS Code tool identifiers (see mapping below). Copilot restricts tool access to this set during the prompt. |
| `model` | Passed through only if the source template set it; otherwise Copilot uses the picker default. |

Fields deliberately **not** emitted (they'd trigger "unknown key" warnings
in VS Code):

- `allowed-tools` — Claude's field name; replaced by the mapped `tools:` list.
- `handoffs` — doit-only invention.
- `effort` — Claude session/skill level; no VS Code equivalent.
- `argument-hint`, `when_to_use` — Claude skill-listing helpers.

The contract test at `tests/contract/test_copilot_prompt_format.py`
asserts these rules per-prompt on every CI build.

## Tool mapping

The transformer maps Claude's coarse-grained verbs to VS Code's
per-feature tool identifiers:

| Claude `allowed-tools` token | Copilot `tools` entry |
|:-----------------------------|:----------------------|
| `Read`, `Write`, `Edit` | `editFiles` |
| `Glob`, `Grep` | `search`, `codebase` |
| `Bash` | `runCommands` |
| body text contains `gh pr`, `gh issue`, `gh api`, `gh auth` | **plus** `githubRepo` |

`Bash(pattern)` constraints are stripped — Copilot tools are named per
feature (`runCommands`) rather than per command, so per-pattern
restriction doesn't translate. If tighter control is ever needed,
VS Code's `chat.tools.autoApprove` setting is the escape hatch.

## Placeholder rewrite

Claude's SKILL.md placeholder syntax is rewritten to Copilot's
`${input:…}` variables so Copilot prompts the user at invocation:

| Source | Copilot |
|:-------|:--------|
| <code>\`\`\`text\n$ARGUMENTS\n\`\`\`</code> | `${input:args:Describe what you want to do for this command.}` |
| Inline `$ARGUMENTS` | `${input:args}` |
| `$0` / `$1` / `$N` | `${input:arg0}` / `${input:arg1}` / `${input:argN}` |

## Where this lives in the package

- Transformer: [`doit_cli.services.prompt_transformer.PromptTransformer`](../../src/doit_cli/services/prompt_transformer.py)
- Writer: [`doit_cli.services.prompt_writer.PromptWriter`](../../src/doit_cli/services/prompt_writer.py)
- CLI: `doit sync-prompts --agent copilot` regenerates every prompt from
  the source commands.
- Contract tests: [`tests/contract/test_copilot_prompt_format.py`](../../tests/contract/test_copilot_prompt_format.py)

## Regenerating the prompts

After editing any source template at
`src/doit_cli/templates/commands/doit.*.md`, re-run:

```bash
doit sync-prompts --agent copilot
```

Commit the changes under `.github/prompts/` alongside the source edit.
The contract test will fail CI if the two diverge — the failure message
tells you to re-run sync.
