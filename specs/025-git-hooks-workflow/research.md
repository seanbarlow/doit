# Research: Git Hook Integration for Workflow Enforcement

**Feature**: 025-git-hooks-workflow
**Date**: 2026-01-15

## Research Summary

This document captures technical decisions and research findings for the Git hooks workflow enforcement feature.

---

## R-001: Git Hook Script Architecture

**Question**: How should hook scripts invoke doit validation?

**Decision**: Shell wrapper scripts that call `doit hooks validate <hook-type>`

**Rationale**:
- Git hooks must be executable shell scripts (or have shebang)
- Keeping logic in Python allows for rich error messages and configuration
- Shell wrapper is minimal and portable
- Allows hook scripts to work even if doit isn't in PATH (uses absolute path)

**Alternatives Considered**:
1. **Pure shell validation** - Rejected: Would duplicate logic, harder to maintain
2. **Python script directly** - Rejected: Requires Python shebang handling across platforms
3. **Symlink to Python** - Rejected: Complex installation, permission issues

**Implementation**:
```bash
#!/usr/bin/env bash
# pre-commit hook installed by doit
exec doit hooks validate pre-commit "$@"
```

---

## R-002: Cross-Platform Compatibility

**Question**: How to ensure hooks work on macOS, Linux, and Windows?

**Decision**: Use `#!/usr/bin/env bash` shebang and POSIX-compatible shell

**Rationale**:
- `/usr/bin/env bash` works on macOS and Linux
- Windows Git Bash provides bash compatibility
- Avoiding bashisms ensures broader compatibility
- Git for Windows includes bash by default

**Constraints**:
- No GNU-specific options (use POSIX equivalents)
- No process substitution `<()` (not portable)
- Use `$()` instead of backticks for command substitution

**Testing Strategy**:
- Unit tests with mock subprocess
- Integration tests in CI on Ubuntu and macOS
- Manual verification on Windows Git Bash

---

## R-003: Hook Bypass Detection

**Question**: How to detect and log when `--no-verify` is used?

**Decision**: Use post-commit hook to detect bypassed commits

**Rationale**:
- `--no-verify` skips pre-commit AND pre-push hooks entirely
- Cannot detect bypass from within the skipped hook (it doesn't run)
- Post-commit hook always runs, can check if pre-commit was skipped
- Environment variable `GIT_SKIP_HOOKS` is not standard

**Implementation Approach**:
1. Pre-commit hook writes a marker file `.doit/.hook-ran` on success
2. Post-commit hook checks for marker file
3. If marker missing but commit succeeded → bypass detected
4. Log bypass event with timestamp, branch, commit hash
5. Clean up marker file

**Alternative**: Git's `core.hooksPath` with wrapper - Rejected (too invasive)

---

## R-004: Configuration File Format

**Question**: What format and structure for `.doit/config/hooks.yaml`?

**Decision**: YAML with explicit defaults and validation

**Rationale**:
- YAML is human-readable and supports comments
- PyYAML is well-maintained and already used in Python ecosystem
- Explicit defaults prevent confusion about behavior
- Schema validation catches configuration errors early

**Configuration Schema**:
```yaml
# .doit/config/hooks.yaml
version: 1

pre_commit:
  enabled: true
  require_spec: true
  require_spec_status: ["In Progress", "Complete"]  # Block "Draft"
  exempt_branches:
    - main
    - develop
    - "hotfix/*"
    - "bugfix/*"
  exempt_paths:
    - "docs/**"
    - "*.md"
    - ".github/**"

pre_push:
  enabled: true
  require_spec: true
  require_plan: true
  require_tasks: false  # Optional for initial adoption
  exempt_branches:
    - main
    - develop

logging:
  enabled: true
  log_bypasses: true
  log_path: .doit/logs/hook-bypasses.log
```

---

## R-005: Branch Name to Spec Directory Mapping

**Question**: How to map branch names to spec directories?

**Decision**: Direct mapping with pattern extraction

**Rationale**:
- Branch naming convention: `###-feature-name` (e.g., `025-git-hooks-workflow`)
- Spec directory: `specs/###-feature-name/spec.md`
- Simple regex extraction handles most cases
- Warning (not error) for non-standard branch names

**Pattern**: `^(\d{3}-[a-z0-9-]+)$` or `^feature/(\d{3}-[a-z0-9-]+)$`

**Edge Cases**:
- `main`, `develop` → Exempt (protected branches)
- `hotfix/urgent-fix` → Exempt (matches exempt pattern)
- `my-random-branch` → Warning, allow commit
- Detached HEAD → Skip validation with warning

---

## R-006: Spec Status Validation

**Question**: How to determine spec status from spec.md file?

**Decision**: Parse YAML-like header for `**Status**:` field

**Rationale**:
- Spec files have consistent header format with `**Status**: Draft|In Progress|Complete`
- Simple regex parsing is sufficient
- No need for full YAML parser (frontmatter is markdown-style)

**Implementation**:
```python
import re

def get_spec_status(spec_path: Path) -> str | None:
    content = spec_path.read_text()
    match = re.search(r'\*\*Status\*\*:\s*(\w+(?:\s+\w+)?)', content)
    return match.group(1) if match else None
```

**Valid Statuses**: `Draft`, `In Progress`, `Complete`, `Approved`

---

## R-007: Existing Hook Backup Strategy

**Question**: How to handle existing hooks without losing user customizations?

**Decision**: Backup to `.doit/backups/hooks/` with timestamp

**Rationale**:
- Users may have custom hooks (linters, formatters)
- Never silently overwrite user work
- Timestamped backups allow multiple install attempts
- Restore command provides easy recovery

**Implementation**:
```
.doit/backups/hooks/
├── pre-commit.2026-01-15T10-30-00.bak
├── pre-push.2026-01-15T10-30-00.bak
└── manifest.json  # Track which backup set is latest
```

**Manifest Format**:
```json
{
  "latest_backup": "2026-01-15T10-30-00",
  "backups": [
    {
      "timestamp": "2026-01-15T10-30-00",
      "hooks": ["pre-commit", "pre-push"]
    }
  ]
}
```

---

## Dependencies

| Dependency | Version | Purpose | Already in Project |
|------------|---------|---------|-------------------|
| PyYAML | >=6.0 | Configuration parsing | No (new) |
| pathlib | stdlib | Path handling | Yes |
| subprocess | stdlib | Git operations | Yes |
| re | stdlib | Pattern matching | Yes |
| json | stdlib | Manifest handling | Yes |
| datetime | stdlib | Timestamps | Yes |

**New Dependency Justification**: PyYAML is the standard Python YAML library, well-maintained, and minimal footprint. It's already an indirect dependency through many Python tools.

---

## Open Questions (Resolved)

All questions resolved - no NEEDS CLARIFICATION items remain.
