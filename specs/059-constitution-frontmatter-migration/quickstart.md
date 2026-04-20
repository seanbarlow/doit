# Quickstart: Constitution Frontmatter Migration

**Feature**: `059-constitution-frontmatter-migration`

This quickstart walks through exercising the migration end-to-end against a
throwaway fixture project. It doubles as the manual smoke test for
`/doit.reviewit` later.

## Prerequisites

- doit 0.3.0+ built from the feature branch and installed:
  ```bash
  uv build && uv tool install . --force
  ```
- A shell with `~/.local/bin/doit` on PATH.

## Scenario 1: Legacy project (no frontmatter) — the P1 path

```bash
# 1. Create a throwaway project mimicking a 0.1.x-era constitution
TMP=$(mktemp -d)
mkdir -p "$TMP/.doit/memory"
cat > "$TMP/.doit/memory/constitution.md" <<'EOF'
# Acme Widgets Constitution

## Purpose & Goals

### Project Purpose

Ship widgets to happy customers.

### Success Criteria

- 99.9% on-time delivery
EOF

# 2. Capture body hash BEFORE migration
PRE_HASH=$(shasum -a 256 "$TMP/.doit/memory/constitution.md" | cut -d' ' -f1)

# 3. Run update
doit update --here --force --ai claude,copilot
# (or: doit init --here --update --ai claude,copilot)

# 4. Inspect result
head -12 "$TMP/.doit/memory/constitution.md"
# Expected: --- YAML frontmatter block with 7 placeholder fields --- followed
#           by original body byte-for-byte.

# 5. Validate
doit verify-memory "$TMP"
# Expected: exit 0, 7 WARNINGs for placeholder fields, 0 ERRORs.

# 6. Verify body preservation via post-frontmatter hash
POST_BODY_HASH=$(awk '/^---$/{c++; next} c==2' "$TMP/.doit/memory/constitution.md" | shasum -a 256 | cut -d' ' -f1)
# POST_BODY_HASH must equal the SHA-256 of the original body text.
```

**Pass criteria**:

- Step 4 output begins with `---` and contains `id: "[PROJECT_ID]"` etc.
- Step 5 exits 0 with warnings only.
- Step 6 confirms body bytes unchanged.

## Scenario 2: AI enrichment — the P2 path

```bash
# Continuing from Scenario 1 fixture (constitution now has placeholders).

# 1. Open an AI assistant (Claude Code or Copilot) in the fixture project.
cd "$TMP"
claude  # or whatever launches your assistant

# 2. Invoke the skill
/doit.constitution
```

**Pass criteria**:

- Skill reports it detected placeholders and entered enrichment mode.
- After the skill completes, `doit verify-memory .` reports 0 warnings
  and 0 errors.
- `diff <(awk '/^---$/{c++; next} c==2' constitution.md.before) \
         <(awk '/^---$/{c++; next} c==2' constitution.md.after)` is empty.
- Every required field now contains a non-placeholder value inferred from
  the body ("Acme Widgets", "Ship widgets to happy customers", etc.).

## Scenario 3: Partial frontmatter — the P3 path

```bash
# 1. Fixture with only 'id' and 'name' already set
cat > "$TMP/.doit/memory/constitution.md" <<'EOF'
---
id: app-acme-widgets
name: Acme Widgets
---

# Acme Widgets Constitution

## Purpose & Goals

### Project Purpose

Ship widgets to happy customers.
EOF

# 2. Run update
doit update --here --force

# 3. Inspect
head -12 "$TMP/.doit/memory/constitution.md"
```

**Pass criteria**:

- `id: app-acme-widgets` and `name: Acme Widgets` are unchanged.
- Five new lines appear (`kind`, `phase`, `icon`, `tagline`, `dependencies`)
  each containing the placeholder token.
- Body is untouched.

## Scenario 4: Malformed YAML — the error path

```bash
# 1. Fixture with broken YAML
cat > "$TMP/.doit/memory/constitution.md" <<'EOF'
---
id: app-broken
name: "Broken: quotes inside: quoted
---
body content
EOF

# 2. Capture pre-run bytes
PRE_BYTES=$(cat "$TMP/.doit/memory/constitution.md")

# 3. Run update
doit update --here --force
EXIT=$?
```

**Pass criteria**:

- `$EXIT` equals `ExitCode.VALIDATION_ERROR` (2).
- `cat "$TMP/.doit/memory/constitution.md"` equals `$PRE_BYTES`
  byte-for-byte.
- The CLI printed an error message naming the line/column of the YAML
  problem.

## Scenario 5: Idempotency

```bash
# Starting from Scenario 1 post-migration.
HASH1=$(shasum -a 256 "$TMP/.doit/memory/constitution.md" | cut -d' ' -f1)
doit update --here --force
HASH2=$(shasum -a 256 "$TMP/.doit/memory/constitution.md" | cut -d' ' -f1)
[[ "$HASH1" == "$HASH2" ]] && echo "IDEMPOTENT" || echo "CHANGED"
```

**Pass criteria**: prints `IDEMPOTENT`.

## What this exercises

| Scenario | FRs | SCs |
|:---------|:----|:----|
| 1. Legacy | 1, 2, 3, 4, 8, 15 | 1, 2, 4, 6 |
| 2. AI enrich | 11, 12, 13 | 3 |
| 3. Partial | 5, 7, 8 | 6 |
| 4. Malformed | 9 | 7 |
| 5. Idempotent | 6, 10 | 5 |

All functional requirements (FR-001..FR-015) and all success criteria
(SC-001..SC-007) are covered by at least one scenario.
