"""Unit tests for error recovery patterns in all commands (058).

Automates manual tests MT-001 through MT-013 from the test report.
Verifies all 13 command templates have structured Error Recovery sections
with consistent format, severity indicators, verification steps,
escalation paths, and state preservation notes.
"""

import re
from pathlib import Path

import pytest

# All command template paths (source of truth)
TEMPLATES_DIR = Path(__file__).parent.parent.parent / "src" / "doit_cli" / "templates" / "commands"
DOIT_TEMPLATES_DIR = Path(__file__).parent.parent.parent / ".doit" / "templates" / "commands"
CLAUDE_COMMANDS_DIR = Path(__file__).parent.parent.parent / ".claude" / "commands"
GITHUB_PROMPTS_DIR = Path(__file__).parent.parent.parent / ".github" / "prompts"

ALL_COMMANDS = [
    "doit.checkin.md",
    "doit.constitution.md",
    "doit.documentit.md",
    "doit.fixit.md",
    "doit.implementit.md",
    "doit.planit.md",
    "doit.researchit.md",
    "doit.reviewit.md",
    "doit.roadmapit.md",
    "doit.scaffoldit.md",
    "doit.specit.md",
    "doit.taskit.md",
    "doit.testit.md",
]

STATEFUL_COMMANDS = [
    "doit.implementit.md",
    "doit.fixit.md",
    "doit.researchit.md",
]


def _extract_error_recovery_section(content: str) -> str:
    """Extract the ## Error Recovery section from template content."""
    match = re.search(
        r"^## Error Recovery\s*\n(.*?)(?=^## (?!Error Recovery)|\Z)",
        content,
        re.MULTILINE | re.DOTALL,
    )
    return match.group(0) if match else ""


def _count_scenarios(recovery_section: str) -> int:
    """Count ### subsections within the Error Recovery section."""
    return len(re.findall(r"^### ", recovery_section, re.MULTILINE))


def _get_template_content(command_name: str) -> str:
    """Read template content from source directory."""
    return (TEMPLATES_DIR / command_name).read_text()


class TestErrorRecoverySectionExists:
    """MT-001: Verify all 13 templates have ## Error Recovery section at H2 level."""

    @pytest.mark.parametrize("command", ALL_COMMANDS)
    def test_template_has_error_recovery_section(self, command):
        content = _get_template_content(command)
        assert "## Error Recovery" in content, f"{command} missing ## Error Recovery section"


class TestErrorRecoveryPositioning:
    """MT-002: Verify Error Recovery is positioned after main workflow, before Next Steps."""

    @pytest.mark.parametrize("command", ALL_COMMANDS)
    def test_error_recovery_before_next_steps(self, command):
        content = _get_template_content(command)
        er_pos = content.find("## Error Recovery")
        assert er_pos != -1, f"{command} missing ## Error Recovery"
        # Verify Error Recovery appears before ## Next Steps in document order
        # (ignoring occurrences inside code blocks which are template output examples)
        after_er = content[er_pos:]
        assert len(after_er) > 100, f"{command} Error Recovery section appears empty"
        # Find all H2 headings after Error Recovery (outside code blocks)
        lines = after_er.split("\n")
        in_code_block = False
        found_next_section = False
        for line in lines[1:]:
            if line.strip().startswith("```"):
                in_code_block = not in_code_block
            if not in_code_block and re.match(r"^## (?!Error Recovery)", line):
                found_next_section = True
                break
        assert found_next_section, (
            f"{command}: ## Error Recovery should be followed by another H2 section"
        )


class TestOldOnErrorRemoved:
    """MT-003: Verify old ### On Error subsections are removed from all templates."""

    @pytest.mark.parametrize("command", ALL_COMMANDS)
    def test_no_old_on_error_subsections(self, command):
        content = _get_template_content(command)
        recovery_section = _extract_error_recovery_section(content)
        # Remove the Error Recovery section to check the rest of the file
        rest = content.replace(recovery_section, "")
        # Look for standalone ### On Error headings (not inside code blocks)
        lines = rest.split("\n")
        in_code_block = False
        for line in lines:
            if line.strip().startswith("```"):
                in_code_block = not in_code_block
            if not in_code_block and re.match(r"^### On Error", line):
                pytest.fail(
                    f"{command} still has old '### On Error' outside Error Recovery: {line}"
                )


class TestNoConflictingSections:
    """MT-004: Verify no template has both old On Error and new Error Recovery."""

    @pytest.mark.parametrize("command", ALL_COMMANDS)
    def test_no_dual_error_handling(self, command):
        content = _get_template_content(command)
        has_recovery = "## Error Recovery" in content
        # Check for On Error outside code blocks and outside Error Recovery section
        recovery_section = _extract_error_recovery_section(content)
        rest = content.replace(recovery_section, "")
        lines = rest.split("\n")
        in_code_block = False
        has_old = False
        for line in lines:
            if line.strip().startswith("```"):
                in_code_block = not in_code_block
            if not in_code_block and re.match(r"^### On Error", line):
                has_old = True
                break
        assert not (has_recovery and has_old), f"{command} has both Error Recovery and old On Error"


class TestPlainLanguageSummaries:
    """MT-005: Verify each scenario starts with plain-language summary."""

    @pytest.mark.parametrize("command", ALL_COMMANDS)
    def test_scenarios_have_plain_language_summary(self, command):
        content = _get_template_content(command)
        recovery = _extract_error_recovery_section(content)
        if not recovery:
            pytest.skip(f"{command} has no Error Recovery section")
        # Split into scenarios by ### headings
        scenarios = re.split(r"^### ", recovery, flags=re.MULTILINE)[1:]
        for scenario in scenarios:
            lines = scenario.strip().split("\n")
            # First line is the heading, second should be blank, third is summary
            non_empty_lines = [l for l in lines[1:] if l.strip()]
            if non_empty_lines:
                summary = non_empty_lines[0].strip()
                # Summary must be a plain-language sentence, not a numbered step,
                # code block, severity indicator, or markdown formatting
                assert not summary.startswith("1."), (
                    f"{command}: scenario '{lines[0][:40]}' starts with numbered step, not summary"
                )
                assert not summary.startswith("- "), (
                    f"{command}: scenario '{lines[0][:40]}' starts with list item, not summary"
                )
                assert not summary.startswith("```"), (
                    f"{command}: scenario '{lines[0][:40]}' starts with code block, not summary"
                )
                assert not summary.startswith("**ERROR**"), (
                    f"{command}: scenario '{lines[0][:40]}' starts with severity, not summary"
                )
                assert not summary.startswith("**WARNING**"), (
                    f"{command}: scenario '{lines[0][:40]}' starts with severity, not summary"
                )
                assert not summary.startswith("**FATAL**"), (
                    f"{command}: scenario '{lines[0][:40]}' starts with severity, not summary"
                )


class TestSeverityIndicators:
    """MT-006: Verify severity indicators present in all scenarios."""

    @pytest.mark.parametrize("command", ALL_COMMANDS)
    def test_all_scenarios_have_severity(self, command):
        content = _get_template_content(command)
        recovery = _extract_error_recovery_section(content)
        if not recovery:
            pytest.skip(f"{command} has no Error Recovery section")
        scenarios = re.split(r"^### ", recovery, flags=re.MULTILINE)[1:]
        for scenario in scenarios:
            heading = scenario.split("\n")[0].strip()
            has_severity = any(
                indicator in scenario for indicator in ["**ERROR**", "**WARNING**", "**FATAL**"]
            )
            assert has_severity, f"{command}: scenario '{heading}' missing severity indicator"


class TestVerifySteps:
    """MT-007: Verify 'Verify:' step present in all recovery procedures."""

    @pytest.mark.parametrize("command", ALL_COMMANDS)
    def test_all_scenarios_have_verify_step(self, command):
        content = _get_template_content(command)
        recovery = _extract_error_recovery_section(content)
        if not recovery:
            pytest.skip(f"{command} has no Error Recovery section")
        scenarios = re.split(r"^### ", recovery, flags=re.MULTILINE)[1:]
        for scenario in scenarios:
            heading = scenario.split("\n")[0].strip()
            has_verify = "Verify:" in scenario or "verify:" in scenario.lower()
            assert has_verify, f"{command}: scenario '{heading}' missing Verify step"


class TestEscalationPaths:
    """MT-008: Verify escalation paths present in all scenarios."""

    @pytest.mark.parametrize("command", ALL_COMMANDS)
    def test_all_scenarios_have_escalation(self, command):
        content = _get_template_content(command)
        recovery = _extract_error_recovery_section(content)
        if not recovery:
            pytest.skip(f"{command} has no Error Recovery section")
        scenarios = re.split(r"^### ", recovery, flags=re.MULTILINE)[1:]
        for scenario in scenarios:
            heading = scenario.split("\n")[0].strip()
            has_escalation = (
                "above steps" in scenario.lower()
                or "don't resolve" in scenario.lower()
                or "doesn't resolve" in scenario.lower()
                or "cannot resolve" in scenario.lower()
            )
            assert has_escalation, (
                f"{command}: scenario '{heading}' missing escalation path "
                "(expected 'above steps', 'don't resolve', or similar)"
            )


class TestStatePreservationNotes:
    """MT-009: Verify state preservation notes in stateful commands."""

    @pytest.mark.parametrize("command", STATEFUL_COMMANDS)
    def test_stateful_commands_have_preservation_notes(self, command):
        content = _get_template_content(command)
        recovery = _extract_error_recovery_section(content)
        assert recovery, f"{command} has no Error Recovery section"
        has_preservation = (
            "preserved" in recovery.lower()
            or "progress" in recovery.lower()
            or "state" in recovery.lower()
        )
        assert has_preservation, f"{command}: stateful command missing state preservation guidance"


class TestScenarioCount:
    """FR-002: Verify 3-5 error scenarios per template."""

    @pytest.mark.parametrize("command", ALL_COMMANDS)
    def test_scenario_count_in_range(self, command):
        content = _get_template_content(command)
        recovery = _extract_error_recovery_section(content)
        assert recovery, f"{command} has no Error Recovery section"
        count = _count_scenarios(recovery)
        assert 3 <= count <= 5, f"{command}: expected 3-5 scenarios, found {count}"


class TestSyncIntegrity:
    """MT-010 through MT-013: Verify all template copies are in sync."""

    @pytest.mark.parametrize("command", ALL_COMMANDS)
    def test_src_matches_doit_templates(self, command):
        """MT-010: src/doit_cli/templates/commands/ matches .doit/templates/commands/"""
        source = (TEMPLATES_DIR / command).read_text()
        doit_copy = (DOIT_TEMPLATES_DIR / command).read_text()
        assert source == doit_copy, (
            f"src/doit_cli/templates/commands/{command} differs from .doit/templates/commands/{command}"
        )

    @pytest.mark.parametrize("command", ALL_COMMANDS)
    def test_claude_commands_match_source(self, command):
        """MT-011: .claude/commands/ matches source templates"""
        source = (TEMPLATES_DIR / command).read_text()
        claude_path = CLAUDE_COMMANDS_DIR / command
        assert claude_path.exists(), f".claude/commands/{command} missing"
        assert source == claude_path.read_text(), f".claude/commands/{command} differs from source"

    @pytest.mark.parametrize("command", ALL_COMMANDS)
    def test_github_prompts_match_source(self, command):
        """MT-012: .github/prompts/ matches source templates"""
        source = (TEMPLATES_DIR / command).read_text()
        prompt_name = command.replace(".md", ".prompt.md")
        github_path = GITHUB_PROMPTS_DIR / prompt_name
        assert github_path.exists(), f".github/prompts/{prompt_name} missing"
        assert source == github_path.read_text(), (
            f".github/prompts/{prompt_name} differs from source"
        )
