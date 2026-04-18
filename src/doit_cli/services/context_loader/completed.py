"""Completed-roadmap parsing and formatting.

`completed_roadmap.md` uses a markdown table. These helpers parse it into
`CompletedItem` dataclasses and render the list back as an AI-friendly
markdown section.
"""

from __future__ import annotations

from datetime import date as date_type

from ...models.context_config import CompletedItem


def parse_completed_roadmap(content: str) -> list[CompletedItem]:
    """Parse completed_roadmap.md markdown table into CompletedItem list."""
    items: list[CompletedItem] = []
    lines = content.split("\n")

    in_table = False
    for raw_line in lines:
        line = raw_line.strip()

        # Skip header separator row (|---|---|...)
        if line.startswith("|") and "---" in line:
            in_table = True
            continue

        # Skip header row before separator
        if line.startswith("|") and not in_table:
            continue

        # Parse table data rows
        if line.startswith("|") and in_table:
            cells = [c.strip() for c in line.split("|") if c.strip()]
            if len(cells) >= 2:
                text = cells[0]
                priority = cells[1] if len(cells) > 1 else ""
                date_str = cells[2] if len(cells) > 2 else ""
                branch = cells[3] if len(cells) > 3 else ""

                completion_date = None
                if date_str:
                    for _fmt in ["%Y-%m-%d", "%m/%d/%Y", "%d-%m-%Y"]:
                        try:
                            completion_date = (
                                date_type.fromisoformat(date_str)
                                if "-" in date_str and len(date_str) == 10
                                else None
                            )
                            break
                        except ValueError:
                            continue

                items.append(
                    CompletedItem(
                        text=text,
                        priority=priority,
                        completion_date=completion_date,
                        feature_branch=branch,
                        relevance_score=0.0,
                    )
                )

    return items


def format_completed_for_context(items: list[CompletedItem]) -> str:
    """Render completed items as an AI-friendly markdown section."""
    if not items:
        return ""

    sections = [
        "## Completed Roadmap Items",
        "",
        "*Related completed features for context:*",
        "",
    ]

    for item in items:
        line = f"- **{item.text}**"
        if item.priority:
            line += f" ({item.priority})"
        sections.append(line)

        if item.completion_date:
            sections.append(f"  - Completed: {item.completion_date}")
        if item.feature_branch:
            sections.append(f"  - Branch: `{item.feature_branch}`")

    sections.append("")
    return "\n".join(sections)
