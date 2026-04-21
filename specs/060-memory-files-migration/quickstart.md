# Quickstart: Memory Files Migration

**Feature**: `060-memory-files-migration`

End-to-end walkthrough against a throwaway fixture project. Doubles as
the manual smoke-test plan for `/doit.reviewit`.

## Prerequisites

- doit 0.4.0+ built from the feature branch and installed:
  ```bash
  uv build && uv tool install . --force
  ```
- `~/.local/bin/doit` on PATH.

## Scenario 1: Legacy roadmap.md missing Active Requirements (US1)

```bash
TMP=$(mktemp -d)
mkdir -p "$TMP/.doit/memory"

# Legacy roadmap: has a title and a few stray sections, no Active Requirements
cat > "$TMP/.doit/memory/roadmap.md" <<'EOF'
# Acme Widgets Roadmap

## Vision

Ship widgets that customers love.

## Notes

Some legacy notes.
EOF

# Minimal tech-stack and constitution so the validator has something to read
cat > "$TMP/.doit/memory/constitution.md" <<'EOF'
---
id: app-acme
name: Acme
kind: application
phase: 2
icon: AC
tagline: Ship widgets.
dependencies: []
---
# Acme Constitution
## Purpose & Goals
### Project Purpose
Ship widgets.
EOF

cat > "$TMP/.doit/memory/tech-stack.md" <<'EOF'
# Tech
## Tech Stack
### Languages
Python
EOF

PRE_HASH=$(shasum -a 256 "$TMP/.doit/memory/roadmap.md" | cut -d' ' -f1)

cd "$TMP" && doit update . --agent claude 2>&1 | grep -Ei "roadmap|section" | head -3

echo "=== after update ==="
cat "$TMP/.doit/memory/roadmap.md"

echo "=== verify ==="
doit verify-memory "$TMP" 2>&1 | grep -Ei "error|warning|summary"
```

**Pass criteria**:

- `## Active Requirements` section was appended with `### P1..P4` stubs.
- Pre-existing `## Vision` and `## Notes` sections survive byte-for-byte.
- `doit verify-memory` exits 0 with WARNINGs only (placeholder detection).

## Scenario 2: Tech-stack enrichment from constitution (US2)

```bash
# Continue from Scenario 1 fixture; expand constitution with legacy tech stack
cat > "$TMP/.doit/memory/constitution.md" <<'EOF'
---
id: app-acme
name: Acme
kind: application
phase: 2
icon: AC
tagline: Ship widgets.
dependencies: []
---
# Acme Constitution

## Purpose & Goals
### Project Purpose
Ship widgets.

## Tech Stack

### Languages

- Python 3.11+
- TypeScript

### Frameworks

- Typer
- FastAPI

### Libraries

- Rich
- httpx

## Infrastructure

- AWS us-east-1
- Fargate

## Deployment

- GitHub Actions
- Manual promotion to prod
EOF

# Re-stub tech-stack.md so enricher has placeholders to fill
cat > "$TMP/.doit/memory/tech-stack.md" <<'EOF'
# Tech Stack

## Tech Stack

### Languages

<!-- Add [PROJECT_NAME]'s Languages here -->

### Frameworks

<!-- Add [PROJECT_NAME]'s Frameworks here -->

### Libraries

<!-- Add [PROJECT_NAME]'s Libraries here -->
EOF

doit memory enrich tech-stack "$TMP" --json

echo "=== after enrich ==="
cat "$TMP/.doit/memory/tech-stack.md"

echo "=== verify ==="
doit verify-memory "$TMP" 2>&1 | grep -Ei "tech-stack|warning|summary"
```

**Pass criteria**:

- All three subsections (Languages, Frameworks, Libraries) now contain
  the same bullet lists as the constitution — verbatim.
- New `### Infrastructure` and `### Deployment` subsections were added
  with the constitution's content.
- `doit verify-memory` reports no warnings on `tech-stack.md`.

## Scenario 3: Roadmap Vision + completed-items seeding (US3)

```bash
# Continuing with the fixture: seed completed_roadmap.md
cat > "$TMP/.doit/memory/completed_roadmap.md" <<'EOF'
# Completed Roadmap Items

**Project**: Acme Widgets
**Created**: 2026-01-01

## Recently Completed

| Item | Original Priority | Completed Date | Feature Branch | Notes |
|------|-------------------|----------------|----------------|-------|
| User authentication | P1 | 2026-02-10 | 001-user-auth | |
| Widget catalog | P1 | 2026-02-20 | 002-catalog | |
| Order tracking | P2 | 2026-03-05 | 003-orders | |
EOF

# Re-stub roadmap.md to clear the post-US1 placeholder content
cat > "$TMP/.doit/memory/roadmap.md" <<'EOF'
# Acme Widgets Roadmap

## Vision

<!-- [PROJECT_NAME]'s vision will go here -->

## Active Requirements

### P1

<!-- Add [PROJECT_NAME]'s P1 items here -->

### P2

<!-- Add [PROJECT_NAME]'s P2 items here -->

### P3

<!-- Add [PROJECT_NAME]'s P3 items here -->

### P4

<!-- Add [PROJECT_NAME]'s P4 items here -->
EOF

doit memory enrich roadmap "$TMP" --json

echo "=== after enrich ==="
head -30 "$TMP/.doit/memory/roadmap.md"
```

**Pass criteria**:

- `## Vision` no longer contains a placeholder — replaced with "Ship widgets." (first sentence of Project Purpose).
- Near the top of `## Active Requirements` is an HTML-comment listing the three completed items.
- P1/P2/P3/P4 subsections still contain their placeholder hints (enrichment intentionally doesn't auto-fill priorities).

## Scenario 4: Missing source → PARTIAL exit 1

```bash
# Constitution with no tech-stack content; enrich should return PARTIAL
cat > "$TMP/.doit/memory/constitution.md" <<'EOF'
---
id: app-acme
name: Acme
kind: application
phase: 2
icon: AC
tagline: Ship widgets.
dependencies: []
---
# Acme Constitution
## Purpose & Goals
### Project Purpose
Ship widgets.
EOF

# Placeholder-stubbed tech-stack
cat > "$TMP/.doit/memory/tech-stack.md" <<'EOF'
# Tech Stack

## Tech Stack

### Languages

<!-- Add [PROJECT_NAME]'s Languages here -->

### Frameworks

<!-- Add [PROJECT_NAME]'s Frameworks here -->

### Libraries

<!-- Add [PROJECT_NAME]'s Libraries here -->
EOF

doit memory enrich tech-stack "$TMP" --json
echo "exit=$?"
```

**Pass criteria**:

- Exit code `1`.
- JSON lists `unresolved_fields: ["Languages", "Frameworks", "Libraries"]`.
- `tech-stack.md` is byte-identical to its pre-run state.

## Scenario 5: Idempotent re-run (US1 + SC-005)

```bash
cd "$TMP"
HASH1=$(shasum -a 256 .doit/memory/roadmap.md | cut -d' ' -f1)
doit update . --agent claude
HASH2=$(shasum -a 256 .doit/memory/roadmap.md | cut -d' ' -f1)
[[ "$HASH1" == "$HASH2" ]] && echo "IDEMPOTENT ✓" || echo "CHANGED ✗"
```

**Pass criteria**: prints `IDEMPOTENT`.

## What these exercise

| Scenario | Requirements covered | Success criteria |
|:---------|:---------------------|:-----------------|
| 1. Legacy roadmap | FR-001..FR-003, FR-007..FR-011 | SC-001, SC-002, SC-006 |
| 2. Tech-stack enrich | FR-012..FR-014, FR-017 | SC-003 |
| 3. Roadmap enrich | FR-015, FR-016, FR-017 | SC-008 |
| 4. Missing source | FR-014, FR-017 | SC-007 |
| 5. Idempotency | FR-008, FR-009 | SC-004, SC-005 |

All 20 FRs and 8 SCs are covered by at least one scenario.
