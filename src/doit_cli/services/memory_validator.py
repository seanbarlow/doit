"""Validate a project's ``.doit/memory/*.md`` files against the contract.

The contract is authored by :mod:`doit_cli.models.memory_contract` and the
canonical JSON Schema at
``src/doit_cli/schemas/frontmatter.schema.json``. This service walks the
three memory files a doit project cares about — ``constitution.md``,
``tech-stack.md``, ``roadmap.md`` — and returns a flat list of
:class:`~doit_cli.models.memory_contract.MemoryContractIssue` records that
can be rendered by the CLI or consumed by the MCP tool.

No heavyweight markdown parser is used. All checks are heading- and
table-shape aware but operate on the raw text of each file, keeping this
service dependency-free beyond the stdlib + pyyaml (already a base dep).
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

from ..models.memory_contract import (
    ConstitutionFrontmatter,
    MemoryContractIssue,
    MemoryIssueSeverity,
    OpenQuestion,
    split_frontmatter,
)


# Tokens a freshly-scaffolded file contains. When three or more distinct
# tokens are present we treat the file as unfilled; fewer tokens are
# tolerated because the platform-event-bus / app-cc-in-a-box constitutions
# mention these tokens in "X -> real value" comments.
PLACEHOLDER_TOKENS = (
    "[PROJECT_NAME]",
    "[PROJECT_PURPOSE]",
    "[SUCCESS_CRITERIA]",
    "[PRINCIPLE_1_NAME]",
    "[PRINCIPLE_1_DESCRIPTION]",
    "[QUALITY_STANDARDS]",
)
PLACEHOLDER_THRESHOLD = 3


@dataclass
class MemoryValidationReport:
    """Flat list of issues plus per-file placeholder flags."""

    issues: list[MemoryContractIssue]
    placeholder_files: list[str]

    @property
    def errors(self) -> list[MemoryContractIssue]:
        return [i for i in self.issues if i.severity is MemoryIssueSeverity.ERROR]

    @property
    def warnings(self) -> list[MemoryContractIssue]:
        return [i for i in self.issues if i.severity is MemoryIssueSeverity.WARNING]

    def has_errors(self) -> bool:
        return any(i.severity is MemoryIssueSeverity.ERROR for i in self.issues)

    def to_dict(self) -> dict:
        return {
            "issues": [i.to_dict() for i in self.issues],
            "placeholder_files": list(self.placeholder_files),
            "error_count": len(self.errors),
            "warning_count": len(self.warnings),
        }


# Heading regexes. Anchored at start-of-line so ``##`` inside code fences
# doesn't accidentally count. Compiled once.
_H2_HEADING = re.compile(r"^(##)\s+(.+?)\s*$", re.MULTILINE)
_H3_HEADING = re.compile(r"^(###)\s+(.+?)\s*$", re.MULTILINE)


def validate_project(project_root: Path | str) -> MemoryValidationReport:
    """Validate a project's memory files.

    Args:
        project_root: Path to the project root (directory containing
            ``.doit/memory/``).

    Returns:
        A :class:`MemoryValidationReport`. Callers check ``has_errors()``
        to decide exit codes.
    """

    root = Path(project_root)
    memory_dir = root / ".doit" / "memory"

    issues: list[MemoryContractIssue] = []
    placeholder_files: list[str] = []

    if not memory_dir.exists():
        issues.append(
            MemoryContractIssue(
                file=str(memory_dir.relative_to(root))
                if root in memory_dir.parents or memory_dir.is_relative_to(root)
                else str(memory_dir),
                severity=MemoryIssueSeverity.ERROR,
                message=".doit/memory directory does not exist — run /doit.scaffoldit first",
            )
        )
        return MemoryValidationReport(issues=issues, placeholder_files=placeholder_files)

    issues.extend(_validate_constitution(memory_dir, placeholder_files))
    issues.extend(_validate_tech_stack(memory_dir, placeholder_files))
    issues.extend(_validate_roadmap(memory_dir, placeholder_files))

    return MemoryValidationReport(issues=issues, placeholder_files=placeholder_files)


# ---------------------------------------------------------------------------
# Per-file validators


def _validate_constitution(
    memory_dir: Path, placeholder_files: list[str]
) -> list[MemoryContractIssue]:
    path = memory_dir / "constitution.md"
    rel = str(path.relative_to(memory_dir.parent.parent))

    if not path.exists():
        return [
            MemoryContractIssue(
                file=rel,
                severity=MemoryIssueSeverity.ERROR,
                message="constitution.md does not exist",
            )
        ]

    source = path.read_text(encoding="utf-8")
    issues: list[MemoryContractIssue] = []

    # Frontmatter: every project that ships to the docs generator needs it.
    fm_data, body, _body_line = split_frontmatter(source)
    if not fm_data:
        issues.append(
            MemoryContractIssue(
                file=rel,
                severity=MemoryIssueSeverity.ERROR,
                message="constitution.md has no YAML frontmatter block",
                line=1,
            )
        )
    else:
        fm = ConstitutionFrontmatter.from_dict(fm_data)
        for issue in fm.validate(file=rel):
            issues.append(issue)

    # Placeholder detection on the body (not the frontmatter).
    if _is_placeholder(body):
        placeholder_files.append(rel)
        issues.append(
            MemoryContractIssue(
                file=rel,
                severity=MemoryIssueSeverity.WARNING,
                message=(
                    "constitution.md body still contains template placeholders "
                    f"(≥ {PLACEHOLDER_THRESHOLD} distinct [TOKEN] names); "
                    "run /doit.constitution to fill it in"
                ),
            )
        )
        # If the file is a placeholder, structural checks below are noise.
        return issues

    # Structural: require ## Purpose & Goals and ### Project Purpose below it.
    if not _has_heading(body, 2, "Purpose & Goals"):
        issues.append(
            MemoryContractIssue(
                file=rel,
                severity=MemoryIssueSeverity.ERROR,
                message="missing required `## Purpose & Goals` section",
            )
        )
    elif not _has_heading(body, 3, "Project Purpose"):
        issues.append(
            MemoryContractIssue(
                file=rel,
                severity=MemoryIssueSeverity.WARNING,
                message="`## Purpose & Goals` is missing a `### Project Purpose` subsection",
            )
        )

    return issues


def _validate_tech_stack(
    memory_dir: Path, placeholder_files: list[str]
) -> list[MemoryContractIssue]:
    path = memory_dir / "tech-stack.md"
    rel = str(path.relative_to(memory_dir.parent.parent))

    if not path.exists():
        return [
            MemoryContractIssue(
                file=rel,
                severity=MemoryIssueSeverity.WARNING,
                message="tech-stack.md does not exist — the docs generator expects one",
            )
        ]

    source = path.read_text(encoding="utf-8")

    if _is_placeholder(source):
        placeholder_files.append(rel)
        return [
            MemoryContractIssue(
                file=rel,
                severity=MemoryIssueSeverity.WARNING,
                message="tech-stack.md still contains template placeholders",
            )
        ]

    issues: list[MemoryContractIssue] = []

    if not _has_heading(source, 2, "Tech Stack"):
        issues.append(
            MemoryContractIssue(
                file=rel,
                severity=MemoryIssueSeverity.ERROR,
                message="missing required `## Tech Stack` section",
            )
        )
        return issues

    # At least one ### sub-heading under ## Tech Stack (Languages, Frameworks, …).
    sub = _subheadings_under(source, "Tech Stack")
    if not sub:
        issues.append(
            MemoryContractIssue(
                file=rel,
                severity=MemoryIssueSeverity.WARNING,
                message=(
                    "`## Tech Stack` has no `### <Group>` subsections — "
                    "the docs generator expects at least one (e.g. Languages, Frameworks, Libraries)"
                ),
            )
        )

    return issues


def _validate_roadmap(
    memory_dir: Path, placeholder_files: list[str]
) -> list[MemoryContractIssue]:
    path = memory_dir / "roadmap.md"
    rel = str(path.relative_to(memory_dir.parent.parent))

    if not path.exists():
        return [
            MemoryContractIssue(
                file=rel,
                severity=MemoryIssueSeverity.WARNING,
                message="roadmap.md does not exist",
            )
        ]

    source = path.read_text(encoding="utf-8")

    if _is_placeholder(source):
        placeholder_files.append(rel)
        return [
            MemoryContractIssue(
                file=rel,
                severity=MemoryIssueSeverity.WARNING,
                message="roadmap.md still contains template placeholders",
            )
        ]

    issues: list[MemoryContractIssue] = []

    if not _has_heading(source, 2, "Active Requirements"):
        issues.append(
            MemoryContractIssue(
                file=rel,
                severity=MemoryIssueSeverity.ERROR,
                message="missing required `## Active Requirements` section",
            )
        )
    else:
        priority_subs = [
            s for s in _subheadings_under(source, "Active Requirements")
            if re.match(r"^p[1-4]\b", s, re.IGNORECASE)
        ]
        if not priority_subs:
            issues.append(
                MemoryContractIssue(
                    file=rel,
                    severity=MemoryIssueSeverity.WARNING,
                    message=(
                        "`## Active Requirements` has no `### P1` / `### P2` / …"
                        " subsections — nothing for the docs generator to pick up"
                    ),
                )
            )

    # ## Open Questions is optional (empty list is a valid state) but when
    # present its table must obey the fixed column order.
    if _has_heading(source, 2, "Open Questions"):
        issues.extend(_validate_open_questions_table(rel, source))

    return issues


# ---------------------------------------------------------------------------
# Helpers


def _is_placeholder(source: str) -> bool:
    hits = sum(1 for t in PLACEHOLDER_TOKENS if t in source)
    return hits >= PLACEHOLDER_THRESHOLD


def _has_heading(source: str, depth: int, title: str) -> bool:
    target = title.strip().lower()
    pattern = _H2_HEADING if depth == 2 else _H3_HEADING
    for match in pattern.finditer(source):
        if match.group(2).strip().lower() == target:
            return True
    return False


def _subheadings_under(source: str, h2_title: str) -> list[str]:
    """Return the text of every `### sub-heading` found between the given
    ``## <h2_title>`` heading and the next H2 (or end of file)."""

    target = h2_title.strip().lower()
    lines = source.splitlines()
    depth2 = 0
    in_section = False
    out: list[str] = []
    for line in lines:
        m2 = re.match(r"^(##)\s+(.+?)\s*$", line)
        if m2:
            if in_section:
                # Reached the next H2 — stop.
                break
            if m2.group(2).strip().lower() == target:
                in_section = True
                depth2 = 1
            continue
        if in_section:
            m3 = re.match(r"^(###)\s+(.+?)\s*$", line)
            if m3:
                out.append(m3.group(2).strip())
    _ = depth2  # kept for clarity even though the flag suffices
    return out


def _validate_open_questions_table(
    rel: str, source: str
) -> list[MemoryContractIssue]:
    """Parse the Open Questions section and flag column-order and priority issues.

    The parser is deliberately tolerant: missing table = silent (the section
    can legitimately be empty). Rows that don't match the expected column
    order produce a warning, not an error, so legacy content can still be
    picked up by the docs generator's parser.
    """

    # Extract the slice of text between "## Open Questions" and the next H2.
    m = re.search(r"^##\s+Open Questions\s*$", source, re.MULTILINE | re.IGNORECASE)
    if not m:
        return []

    rest = source[m.end():]
    next_h2 = re.search(r"^##\s+", rest, re.MULTILINE)
    section = rest[: next_h2.start()] if next_h2 else rest

    # Find the first GFM table header row in the section.
    rows = [line for line in section.splitlines() if line.lstrip().startswith("|")]
    if len(rows) < 2:
        return []  # empty table (header + divider only, or nothing)

    header = _split_row(rows[0])
    if [c.lower() for c in header[:3]] != ["priority", "question", "owner"]:
        return [
            MemoryContractIssue(
                file=rel,
                severity=MemoryIssueSeverity.WARNING,
                message=(
                    "`## Open Questions` table columns must be "
                    "`Priority | Question | Owner`, got "
                    f"`{' | '.join(header[:3])}`"
                ),
            )
        ]

    issues: list[MemoryContractIssue] = []
    # Skip header + divider; iterate data rows.
    for row in rows[2:]:
        cells = _split_row(row)
        if len(cells) < 3 or not any(cells):
            continue
        _, issue = OpenQuestion.normalise(cells[0], cells[1], cells[2])
        if issue is not None:
            # Re-target the issue to the real file/line.
            issues.append(
                MemoryContractIssue(
                    file=rel,
                    severity=issue.severity,
                    message=issue.message,
                )
            )
    return issues


def _split_row(line: str) -> list[str]:
    """Split a GFM table row into cell strings, trimmed, unescaped pipes."""
    line = line.strip()
    if line.startswith("|"):
        line = line[1:]
    if line.endswith("|"):
        line = line[:-1]
    # Replace escaped pipes with a sentinel, split, restore.
    parts = line.replace("\\|", "\u0000").split("|")
    return [p.replace("\u0000", "|").strip() for p in parts]
