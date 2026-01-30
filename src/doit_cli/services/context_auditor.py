"""Context auditor service for analyzing AI context injection patterns.

This module provides the ContextAuditor service that scans command templates
for double-injection patterns and generates optimization recommendations.
"""

import logging
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


# Context sources provided by `doit context show`
CONTEXT_SHOW_SOURCES = {
    "constitution": ".doit/memory/constitution.md",
    "tech_stack": ".doit/memory/tech-stack.md",
    "roadmap": ".doit/memory/roadmap.md",
    "completed_roadmap": ".doit/memory/completed_roadmap.md",
    "current_spec": "specs/{feature}/spec.md",
    "related_specs": "specs/*/spec.md",
}

# Patterns that indicate explicit file reads for context sources
DOUBLE_INJECTION_PATTERNS = [
    r'Read\s+[`"]?\.doit/memory/constitution\.md[`"]?',
    r'Read\s+[`"]?\.doit/memory/tech-stack\.md[`"]?',
    r'Read\s+[`"]?\.doit/memory/roadmap\.md[`"]?',
    r'Read\s+[`"]?\.doit/memory/completed_roadmap\.md[`"]?',
    r'Check\s+if\s+[`"]?\.doit/memory/',
    r'Load\s+context:.*\.doit/memory/',
    r'Extract\s+.*from\s+constitution\.md',
    r'Read\s+Tech\s+Stack\s+section\s+from\s+constitution',
]


@dataclass
class AuditFinding:
    """Represents a single finding from a context audit."""

    template_name: str
    finding_type: str  # "double_injection", "excessive_context", "missing_instruction"
    severity: str  # "critical", "major", "minor"
    line_number: int
    description: str
    recommendation: str
    pattern_matched: str = ""


@dataclass
class TemplateAuditResult:
    """Audit results for a single template."""

    template_name: str
    file_path: Path
    has_context_show: bool = False
    has_explicit_reads: bool = False
    is_double_injection: bool = False
    estimated_tokens: int = 0
    findings: list[AuditFinding] = field(default_factory=list)
    explicit_read_patterns: list[str] = field(default_factory=list)


@dataclass
class AuditReport:
    """Complete audit report for all templates."""

    templates_analyzed: int = 0
    total_findings: int = 0
    double_injection_count: int = 0
    token_waste_estimate: int = 0
    template_results: list[TemplateAuditResult] = field(default_factory=list)
    findings: list[AuditFinding] = field(default_factory=list)


def estimate_tokens(text: str) -> int:
    """Estimate token count for text (approximate: words * 1.3)."""
    words = len(text.split())
    return int(words * 1.3)


class ContextAuditor:
    """Service for auditing templates for context injection patterns."""

    def __init__(self, templates_dir: Optional[Path] = None):
        """Initialize the context auditor.

        Args:
            templates_dir: Directory containing command templates.
                          Defaults to templates/commands/ from repo root.
        """
        if templates_dir is None:
            # Try to find templates directory from current working directory
            cwd = Path.cwd()
            self.templates_dir = cwd / "templates" / "commands"
        else:
            self.templates_dir = templates_dir

    def audit_template(self, template_path: Path) -> TemplateAuditResult:
        """Audit a single template for context injection patterns.

        Args:
            template_path: Path to the template file.

        Returns:
            TemplateAuditResult with findings and recommendations.
        """
        result = TemplateAuditResult(
            template_name=template_path.name,
            file_path=template_path,
        )

        if not template_path.exists():
            result.findings.append(
                AuditFinding(
                    template_name=template_path.name,
                    finding_type="missing_file",
                    severity="critical",
                    line_number=0,
                    description=f"Template file not found: {template_path}",
                    recommendation="Verify template exists in templates/commands/",
                )
            )
            return result

        content = template_path.read_text(encoding="utf-8")
        lines = content.split("\n")
        result.estimated_tokens = estimate_tokens(content)

        # Check for `doit context show` instruction
        context_show_pattern = r"doit\s+context\s+show"
        for i, line in enumerate(lines, 1):
            if re.search(context_show_pattern, line, re.IGNORECASE):
                result.has_context_show = True
                break

        # Check for explicit file read patterns
        for i, line in enumerate(lines, 1):
            for pattern in DOUBLE_INJECTION_PATTERNS:
                if re.search(pattern, line, re.IGNORECASE):
                    result.has_explicit_reads = True
                    result.explicit_read_patterns.append(pattern)

                    # If we have both context show and explicit reads, it's double-injection
                    if result.has_context_show:
                        result.is_double_injection = True
                        result.findings.append(
                            AuditFinding(
                                template_name=template_path.name,
                                finding_type="double_injection",
                                severity="critical",
                                line_number=i,
                                description=f"Double-injection: explicit read after doit context show",
                                recommendation="Remove explicit file read - content already in context",
                                pattern_matched=pattern,
                            )
                        )

        # Check for missing best practices block
        if "Code Quality Guidelines" not in content:
            result.findings.append(
                AuditFinding(
                    template_name=template_path.name,
                    finding_type="missing_instruction",
                    severity="major",
                    line_number=0,
                    description="Missing 'Code Quality Guidelines' section",
                    recommendation="Add standardized best practices instruction block",
                )
            )

        # Check for missing artifact storage block
        if "Artifact Storage" not in content:
            result.findings.append(
                AuditFinding(
                    template_name=template_path.name,
                    finding_type="missing_instruction",
                    severity="major",
                    line_number=0,
                    description="Missing 'Artifact Storage' section",
                    recommendation="Add artifact storage instructions for temp scripts and reports",
                )
            )

        return result

    def audit_all_templates(self) -> AuditReport:
        """Audit all templates in the templates directory.

        Returns:
            AuditReport with all findings and recommendations.
        """
        report = AuditReport()

        if not self.templates_dir.exists():
            logger.warning(f"Templates directory not found: {self.templates_dir}")
            return report

        template_files = list(self.templates_dir.glob("doit.*.md"))
        report.templates_analyzed = len(template_files)

        for template_path in template_files:
            result = self.audit_template(template_path)
            report.template_results.append(result)
            report.findings.extend(result.findings)

            if result.is_double_injection:
                report.double_injection_count += 1
                # Estimate token waste (roughly half the template is duplicated)
                report.token_waste_estimate += result.estimated_tokens // 3

        report.total_findings = len(report.findings)

        return report

    def format_report(self, report: AuditReport, output_format: str = "table") -> str:
        """Format the audit report for display.

        Args:
            report: The audit report to format.
            output_format: Output format (table, json, markdown).

        Returns:
            Formatted report string.
        """
        if output_format == "json":
            import json

            return json.dumps(
                {
                    "templates_analyzed": report.templates_analyzed,
                    "total_findings": report.total_findings,
                    "double_injection_count": report.double_injection_count,
                    "token_waste_estimate": report.token_waste_estimate,
                    "findings": [
                        {
                            "template": f.template_name,
                            "type": f.finding_type,
                            "severity": f.severity,
                            "line": f.line_number,
                            "description": f.description,
                            "recommendation": f.recommendation,
                        }
                        for f in report.findings
                    ],
                },
                indent=2,
            )

        # Default: table format
        lines = [
            "╭─────────────────────────────────────────────────────────╮",
            "│ Context Audit Report                                    │",
            "├─────────────────────────────────────────────────────────┤",
            f"│ Templates analyzed: {report.templates_analyzed:<36} │",
            f"│ Total findings: {report.total_findings:<40} │",
            f"│ Double-injection patterns: {report.double_injection_count:<29} │",
            f"│ Estimated token waste: {report.token_waste_estimate:<33} │",
            "╰─────────────────────────────────────────────────────────╯",
            "",
        ]

        # Group findings by severity
        critical = [f for f in report.findings if f.severity == "critical"]
        major = [f for f in report.findings if f.severity == "major"]
        minor = [f for f in report.findings if f.severity == "minor"]

        for severity, findings in [
            ("CRITICAL", critical),
            ("MAJOR", major),
            ("MINOR", minor),
        ]:
            if findings:
                lines.append(f"\n{severity}:")
                for f in findings:
                    lines.append(f"  {f.template_name}:{f.line_number}")
                    lines.append(f"    {f.description}")
                    lines.append(f"    → {f.recommendation}")

        return "\n".join(lines)
