# JSON Schemas

**Available in**: doit 0.2.0+.

doit ships JSON Schemas for the contracts that AI assistants, CI, and the
doit-docs portal share. Schemas live at
[`src/doit_cli/schemas/`](../../src/doit_cli/schemas/) and are bundled with
the package so validators can resolve them by path.

## Constitution frontmatter

**Schema**: [`frontmatter.schema.json`](../../src/doit_cli/schemas/frontmatter.schema.json)

**Contract for**: the YAML frontmatter block at the top of a project's
`.doit/memory/constitution.md`.

**Canonical source**: this repo. The copy at
`platform-docs-site/tools/gen-data/schema/frontmatter.schema.json` is kept
in sync manually; drift between the two is a release-blocker.

### Required fields

| Field | Type | Constraint |
|:------|:-----|:-----------|
| `id` | string | Must match `^(app\|platform)-[a-z][a-z0-9-]+$` and equal the component's directory name. |
| `name` | string | Non-empty display name. |
| `kind` | string | One of `application`, `service`. |
| `phase` | integer | `1`–`4`. |
| `icon` | string | Matches `^[A-Z0-9]{2,4}$`. Rendered on the component card. |
| `tagline` | string | Non-empty one-line description. |
| `dependencies` | array of strings | Component IDs matching `^(app\|platform)-...` are linked on the site; other strings render as plain text. |

### Optional fields

| Field | Type | Purpose |
|:------|:-----|:--------|
| `competitor` | string or null | Named competitor (optional positioning metadata). |
| `consumers` | string or null | Free-text list of consuming components. |
| `status` | string | Free-text status label (e.g. "alpha", "shipped"). |

No other properties are allowed (`additionalProperties: false`).

### Example

```yaml
---
id: app-doit
name: doit
kind: application
phase: 3
icon: DT
tagline: Spec-Driven Development CLI for AI-assisted workflows.
dependencies:
  - platform-github
  - platform-azure-devops
status: shipped
---
```

### Validating locally

Pair the schema with any JSON Schema validator — for example,
[`check-jsonschema`](https://pypi.org/project/check-jsonschema/):

```bash
check-jsonschema \
  --schemafile src/doit_cli/schemas/frontmatter.schema.json \
  <(python -c "import yaml, sys; print(__import__('json').dumps(yaml.safe_load(open('.doit/memory/constitution.md').read().split('---')[1])))")
```

(doit itself validates the frontmatter during `doit validate`; the
command above is for external tooling that needs the raw schema.)
