"""Tests for the ContextAuditor service."""

from pathlib import Path

from doit_cli.services.context_auditor import (
    AuditFinding,
    AuditReport,
    ContextAuditor,
    TemplateAuditResult,
    estimate_tokens,
)


class TestEstimateTokens:
    """Tests for the estimate_tokens helper function."""

    def test_empty_string(self):
        assert estimate_tokens("") == 0

    def test_single_word(self):
        assert estimate_tokens("hello") == 1  # int(1 * 1.3) = 1

    def test_multiple_words(self):
        result = estimate_tokens("hello world foo bar")
        assert result == int(4 * 1.3)  # 5

    def test_long_text(self):
        text = " ".join(["word"] * 100)
        assert estimate_tokens(text) == int(100 * 1.3)


class TestAuditFinding:
    """Tests for the AuditFinding dataclass."""

    def test_creation(self):
        finding = AuditFinding(
            template_name="doit.specit.md",
            finding_type="double_injection",
            severity="critical",
            line_number=42,
            description="Test description",
            recommendation="Test recommendation",
        )
        assert finding.template_name == "doit.specit.md"
        assert finding.finding_type == "double_injection"
        assert finding.severity == "critical"
        assert finding.line_number == 42
        assert finding.pattern_matched == ""

    def test_with_pattern(self):
        finding = AuditFinding(
            template_name="test.md",
            finding_type="double_injection",
            severity="major",
            line_number=10,
            description="desc",
            recommendation="rec",
            pattern_matched=r"Read\s+constitution",
        )
        assert finding.pattern_matched == r"Read\s+constitution"


class TestTemplateAuditResult:
    """Tests for the TemplateAuditResult dataclass."""

    def test_defaults(self):
        result = TemplateAuditResult(
            template_name="test.md",
            file_path=Path("test.md"),
        )
        assert result.has_context_show is False
        assert result.has_explicit_reads is False
        assert result.is_double_injection is False
        assert result.estimated_tokens == 0
        assert result.findings == []
        assert result.explicit_read_patterns == []


class TestAuditReport:
    """Tests for the AuditReport dataclass."""

    def test_defaults(self):
        report = AuditReport()
        assert report.templates_analyzed == 0
        assert report.total_findings == 0
        assert report.double_injection_count == 0
        assert report.token_waste_estimate == 0
        assert report.template_results == []
        assert report.findings == []


class TestContextAuditor:
    """Tests for the ContextAuditor service."""

    def test_init_with_custom_dir(self, tmp_path):
        auditor = ContextAuditor(templates_dir=tmp_path)
        assert auditor.templates_dir == tmp_path

    def test_audit_missing_template(self, tmp_path):
        auditor = ContextAuditor(templates_dir=tmp_path)
        result = auditor.audit_template(tmp_path / "nonexistent.md")
        assert len(result.findings) == 1
        assert result.findings[0].finding_type == "missing_file"
        assert result.findings[0].severity == "critical"

    def test_audit_clean_template(self, tmp_path):
        template = tmp_path / "doit.test.md"
        template.write_text(
            "# Test Template\n\n"
            "## Code Quality Guidelines\n\n"
            "Follow best practices.\n\n"
            "## Artifact Storage\n\n"
            "Store artifacts in specs/.\n",
            encoding="utf-8",
        )
        auditor = ContextAuditor(templates_dir=tmp_path)
        result = auditor.audit_template(template)
        assert result.has_context_show is False
        assert result.has_explicit_reads is False
        assert result.is_double_injection is False
        assert len(result.findings) == 0

    def test_audit_detects_double_injection(self, tmp_path):
        template = tmp_path / "doit.double.md"
        template.write_text(
            "# Template\n\n"
            "## Code Quality Guidelines\n\n"
            "## Artifact Storage\n\n"
            "Run `doit context show` first.\n"
            "Then Read `.doit/memory/constitution.md`\n",
            encoding="utf-8",
        )
        auditor = ContextAuditor(templates_dir=tmp_path)
        result = auditor.audit_template(template)
        assert result.has_context_show is True
        assert result.has_explicit_reads is True
        assert result.is_double_injection is True
        double_findings = [f for f in result.findings if f.finding_type == "double_injection"]
        assert len(double_findings) >= 1

    def test_audit_explicit_read_without_context_show(self, tmp_path):
        template = tmp_path / "doit.explicit.md"
        template.write_text(
            "# Template\n\n"
            "## Code Quality Guidelines\n\n"
            "## Artifact Storage\n\n"
            "Read `.doit/memory/constitution.md`\n",
            encoding="utf-8",
        )
        auditor = ContextAuditor(templates_dir=tmp_path)
        result = auditor.audit_template(template)
        assert result.has_explicit_reads is True
        assert result.has_context_show is False
        assert result.is_double_injection is False

    def test_audit_missing_code_quality(self, tmp_path):
        template = tmp_path / "doit.missing.md"
        template.write_text(
            "# Template\n\n## Artifact Storage\n\nStore artifacts.\n",
            encoding="utf-8",
        )
        auditor = ContextAuditor(templates_dir=tmp_path)
        result = auditor.audit_template(template)
        missing = [
            f
            for f in result.findings
            if f.finding_type == "missing_instruction" and "Code Quality" in f.description
        ]
        assert len(missing) == 1
        assert missing[0].severity == "major"

    def test_audit_missing_artifact_storage(self, tmp_path):
        template = tmp_path / "doit.noartifact.md"
        template.write_text(
            "# Template\n\n## Code Quality Guidelines\n\nFollow rules.\n",
            encoding="utf-8",
        )
        auditor = ContextAuditor(templates_dir=tmp_path)
        result = auditor.audit_template(template)
        missing = [
            f
            for f in result.findings
            if f.finding_type == "missing_instruction" and "Artifact Storage" in f.description
        ]
        assert len(missing) == 1

    def test_audit_estimates_tokens(self, tmp_path):
        template = tmp_path / "doit.tokens.md"
        content = " ".join(["word"] * 50)
        template.write_text(
            f"# Template\n\n## Code Quality Guidelines\n\n## Artifact Storage\n\n{content}\n",
            encoding="utf-8",
        )
        auditor = ContextAuditor(templates_dir=tmp_path)
        result = auditor.audit_template(template)
        assert result.estimated_tokens > 0

    def test_audit_all_templates(self, tmp_path):
        for name in ["doit.specit.md", "doit.planit.md", "doit.taskit.md"]:
            (tmp_path / name).write_text(
                "# Template\n\n## Code Quality Guidelines\n\n## Artifact Storage\n",
                encoding="utf-8",
            )
        auditor = ContextAuditor(templates_dir=tmp_path)
        report = auditor.audit_all_templates()
        assert report.templates_analyzed == 3
        assert len(report.template_results) == 3

    def test_audit_all_empty_directory(self, tmp_path):
        auditor = ContextAuditor(templates_dir=tmp_path)
        report = auditor.audit_all_templates()
        assert report.templates_analyzed == 0

    def test_audit_all_missing_directory(self, tmp_path):
        auditor = ContextAuditor(templates_dir=tmp_path / "nonexistent")
        report = auditor.audit_all_templates()
        assert report.templates_analyzed == 0

    def test_audit_all_counts_double_injections(self, tmp_path):
        (tmp_path / "doit.bad.md").write_text(
            "Run `doit context show`.\nRead `.doit/memory/constitution.md`\n",
            encoding="utf-8",
        )
        auditor = ContextAuditor(templates_dir=tmp_path)
        report = auditor.audit_all_templates()
        assert report.double_injection_count == 1
        assert report.token_waste_estimate > 0


class TestFormatReport:
    """Tests for the format_report method."""

    def test_table_format(self, tmp_path):
        auditor = ContextAuditor(templates_dir=tmp_path)
        report = AuditReport(
            templates_analyzed=3,
            total_findings=2,
            double_injection_count=1,
            token_waste_estimate=500,
            findings=[
                AuditFinding(
                    template_name="test.md",
                    finding_type="double_injection",
                    severity="critical",
                    line_number=10,
                    description="Double injection found",
                    recommendation="Remove explicit read",
                ),
            ],
        )
        output = auditor.format_report(report, "table")
        assert "Context Audit Report" in output
        assert "Templates analyzed: 3" in output
        assert "CRITICAL:" in output

    def test_json_format(self, tmp_path):
        import json

        auditor = ContextAuditor(templates_dir=tmp_path)
        report = AuditReport(templates_analyzed=1, total_findings=0)
        output = auditor.format_report(report, "json")
        data = json.loads(output)
        assert data["templates_analyzed"] == 1
        assert data["total_findings"] == 0
        assert data["findings"] == []

    def test_table_format_no_findings(self, tmp_path):
        auditor = ContextAuditor(templates_dir=tmp_path)
        report = AuditReport(templates_analyzed=5, total_findings=0)
        output = auditor.format_report(report, "table")
        assert "CRITICAL" not in output
        assert "MAJOR" not in output
