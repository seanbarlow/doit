"""Unit tests for persona-aware user story generation templates (057).

Automates manual tests MT-001 through MT-012 from the test report.
Verifies template content for persona matching rules, traceability,
fallback behavior, and sync integrity.
"""

from pathlib import Path

# Paths to source templates (single source of truth)
TEMPLATES_DIR = Path(__file__).parent.parent.parent / "src" / "doit_cli" / "templates"
SPEC_TEMPLATE = TEMPLATES_DIR / "spec-template.md"
USER_STORIES_TEMPLATE = TEMPLATES_DIR / "user-stories-template.md"
SPECIT_COMMAND = TEMPLATES_DIR / "commands" / "doit.specit.md"

# Local project templates (.doit/templates/)
DOIT_SPEC_TEMPLATE = (
    Path(__file__).parent.parent.parent / ".doit" / "templates" / "spec-template.md"
)
DOIT_US_TEMPLATE = (
    Path(__file__).parent.parent.parent / ".doit" / "templates" / "user-stories-template.md"
)
DOIT_SPECIT_COMMAND = (
    Path(__file__).parent.parent.parent / ".doit" / "templates" / "commands" / "doit.specit.md"
)

# Sync targets (agent-specific copies)
CLAUDE_SPECIT = Path(__file__).parent.parent.parent / ".claude" / "commands" / "doit.specit.md"
GITHUB_SPECIT = (
    Path(__file__).parent.parent.parent / ".github" / "prompts" / "doit.specit.prompt.md"
)


class TestSpecTemplatePersonaHeaders:
    """MT-001: Verify spec-template.md story headers include | Persona: P-NNN."""

    def test_p1_story_header_has_persona_suffix(self):
        content = SPEC_TEMPLATE.read_text()
        assert "### User Story 1 - [Brief Title] (Priority: P1) | Persona: P-NNN" in content

    def test_p2_story_header_has_persona_suffix(self):
        content = SPEC_TEMPLATE.read_text()
        assert "### User Story 2 - [Brief Title] (Priority: P2) | Persona: P-NNN" in content

    def test_p3_story_header_has_persona_suffix(self):
        content = SPEC_TEMPLATE.read_text()
        assert "### User Story 3 - [Brief Title] (Priority: P3) | Persona: P-NNN" in content

    def test_persona_suffix_is_documented_as_optional(self):
        content = SPEC_TEMPLATE.read_text()
        assert "optional" in content.lower()
        assert "personas are loaded" in content.lower() or "personas loaded" in content.lower()


class TestUserStoriesTemplatePersonaFormat:
    """MT-002: Verify user-stories-template.md includes persona ID and archetype."""

    def test_us001_header_has_persona_id(self):
        content = USER_STORIES_TEMPLATE.read_text()
        assert "### US-001: {Story Title} (P1) | Persona: P-NNN" in content

    def test_us002_header_has_persona_id(self):
        content = USER_STORIES_TEMPLATE.read_text()
        assert "### US-002: {Story Title} (P1) | Persona: P-NNN" in content

    def test_us003_header_has_persona_id(self):
        content = USER_STORIES_TEMPLATE.read_text()
        assert "### US-003: {Story Title} (P2) | Persona: P-NNN" in content

    def test_persona_field_includes_id_and_archetype(self):
        content = USER_STORIES_TEMPLATE.read_text()
        assert "**Persona**: {Persona Name} (P-NNN) — {Archetype}" in content


class TestSpecitMatchingRules:
    """MT-003: Verify doit.specit.md contains Persona Matching Rules section."""

    def test_matching_rules_section_exists(self):
        content = SPECIT_COMMAND.read_text()
        assert "## Persona Matching Rules (when personas loaded)" in content

    def test_direct_goal_match_rule(self):
        content = SPECIT_COMMAND.read_text()
        assert "Direct goal match" in content
        assert "High" in content

    def test_pain_point_match_rule(self):
        content = SPECIT_COMMAND.read_text()
        assert "Pain point match" in content

    def test_usage_context_match_rule(self):
        content = SPECIT_COMMAND.read_text()
        assert "Usage context match" in content
        assert "Medium" in content

    def test_role_archetype_match_rule(self):
        content = SPECIT_COMMAND.read_text()
        assert "Role/archetype match" in content

    def test_no_match_rule(self):
        content = SPECIT_COMMAND.read_text()
        assert "No match" in content
        assert "without a Persona tag" in content

    def test_six_matching_rules_present(self):
        """Verify all 6 matching rules are present in order."""
        content = SPECIT_COMMAND.read_text()
        rules_section_start = content.find("## Persona Matching Rules")
        assert rules_section_start != -1
        rules_section = content[rules_section_start : rules_section_start + 2000]
        assert "1." in rules_section
        assert "2." in rules_section
        assert "3." in rules_section
        assert "4." in rules_section
        assert "5." in rules_section
        assert "6." in rules_section


class TestSpecitTraceabilityUpdate:
    """MT-006: Verify traceability update instructions exist."""

    def test_traceability_section_exists(self):
        content = SPECIT_COMMAND.read_text()
        assert "### Update Persona Traceability" in content

    def test_traceability_reads_personas_md(self):
        content = SPECIT_COMMAND.read_text()
        traceability_start = content.find("### Update Persona Traceability")
        assert traceability_start != -1
        section = content[traceability_start : traceability_start + 1000]
        assert "personas.md" in section

    def test_traceability_is_full_replacement(self):
        content = SPECIT_COMMAND.read_text()
        traceability_start = content.find("### Update Persona Traceability")
        section = content[traceability_start : traceability_start + 1000]
        assert "full replacement" in section.lower() or "Replace the table content" in section

    def test_traceability_includes_zero_coverage_personas(self):
        content = SPECIT_COMMAND.read_text()
        traceability_start = content.find("### Update Persona Traceability")
        section = content[traceability_start : traceability_start + 1000]
        assert "zero mapped stories" in section.lower() or "zero stories" in section.lower()


class TestSpecitCoverageReport:
    """MT-007: Verify persona coverage report section."""

    def test_coverage_report_section_exists(self):
        content = SPECIT_COMMAND.read_text()
        assert "### Persona Coverage Report" in content

    def test_coverage_table_format(self):
        content = SPECIT_COMMAND.read_text()
        coverage_start = content.find("### Persona Coverage Report")
        assert coverage_start != -1
        section = content[coverage_start : coverage_start + 1000]
        assert "| Persona | Stories | Coverage |" in section

    def test_covered_indicator(self):
        content = SPECIT_COMMAND.read_text()
        assert "Covered" in content

    def test_underserved_indicator(self):
        content = SPECIT_COMMAND.read_text()
        assert "Underserved" in content

    def test_coverage_only_when_personas_available(self):
        content = SPECIT_COMMAND.read_text()
        coverage_start = content.find("### Persona Coverage Report")
        section = content[coverage_start : coverage_start + 1000]
        assert (
            "skip when no personas loaded" in section.lower()
            or "Only display this section when personas are available" in section
        )


class TestSpecitFallbackBehavior:
    """MT-005, MT-008, MT-011: Verify fallback when no personas exist."""

    def test_no_personas_found_section_exists(self):
        content = SPECIT_COMMAND.read_text()
        assert "**If NO personas.md found**:" in content

    def test_no_personas_available_section_exists(self):
        content = SPECIT_COMMAND.read_text()
        assert "**When No Personas Are Available**:" in content

    def test_fallback_skips_matching_rules(self):
        content = SPECIT_COMMAND.read_text()
        fallback_start = content.find("**When No Personas Are Available**:")
        assert fallback_start != -1
        section = content[fallback_start : fallback_start + 500]
        assert "Skip all persona matching rules" in section

    def test_fallback_skips_traceability(self):
        content = SPECIT_COMMAND.read_text()
        fallback_start = content.find("**When No Personas Are Available**:")
        section = content[fallback_start : fallback_start + 500]
        assert "Skip the traceability table update" in section

    def test_fallback_skips_coverage_report(self):
        content = SPECIT_COMMAND.read_text()
        fallback_start = content.find("**When No Personas Are Available**:")
        section = content[fallback_start : fallback_start + 500]
        assert "Skip the persona coverage report" in section

    def test_fallback_no_errors(self):
        content = SPECIT_COMMAND.read_text()
        fallback_start = content.find("**When No Personas Are Available**:")
        section = content[fallback_start : fallback_start + 500]
        assert "Do NOT raise errors" in section

    def test_empty_personas_treated_as_no_personas(self):
        """MT-008: personas.md with no valid P-NNN entries treated as empty."""
        content = SPECIT_COMMAND.read_text()
        assert "no valid persona entries" in content.lower() or "no P-NNN IDs found" in content

    def test_standard_format_without_persona_suffix(self):
        content = SPECIT_COMMAND.read_text()
        fallback_start = content.find("**When No Personas Are Available**:")
        section = content[fallback_start : fallback_start + 500]
        assert "without" in section and "Persona" in section


class TestSpecitMultiPersona:
    """MT-009: Verify multi-persona tagging support."""

    def test_multi_persona_rule_exists(self):
        content = SPECIT_COMMAND.read_text()
        assert "Multi-persona" in content

    def test_comma_separated_format(self):
        content = SPECIT_COMMAND.read_text()
        assert "P-001, P-002" in content

    def test_multi_persona_traceability(self):
        """Multi-persona stories should register under each persona."""
        content = SPECIT_COMMAND.read_text()
        rules_start = content.find("## Persona Matching Rules")
        section = content[rules_start : rules_start + 3000]
        assert (
            "genuinely serve multiple personas" in section.lower()
            or "genuinely serves multiple personas" in section.lower()
        )


class TestDotDoitTemplateSyncIntegrity:
    """Verify .doit/templates/ local copies match source templates."""

    def test_doit_spec_template_matches_source(self):
        source = SPEC_TEMPLATE.read_text()
        local = DOIT_SPEC_TEMPLATE.read_text()
        assert source == local, ".doit/templates/spec-template.md differs from source"

    def test_doit_user_stories_template_matches_source(self):
        source = USER_STORIES_TEMPLATE.read_text()
        local = DOIT_US_TEMPLATE.read_text()
        assert source == local, ".doit/templates/user-stories-template.md differs from source"

    def test_doit_specit_command_matches_source(self):
        source = SPECIT_COMMAND.read_text()
        local = DOIT_SPECIT_COMMAND.read_text()
        assert source == local, ".doit/templates/commands/doit.specit.md differs from source"


class TestAgentSyncIntegrity:
    """MT-010: Verify agent-synced files match source template."""

    def test_claude_commands_exists(self):
        assert CLAUDE_SPECIT.exists(), ".claude/commands/doit.specit.md missing"

    def test_github_prompts_exists(self):
        assert GITHUB_SPECIT.exists(), ".github/prompts/doit.specit.prompt.md missing"

    def test_claude_commands_has_matching_rules(self):
        content = CLAUDE_SPECIT.read_text()
        assert "## Persona Matching Rules (when personas loaded)" in content

    def test_github_prompts_has_matching_rules(self):
        content = GITHUB_SPECIT.read_text()
        assert "## Persona Matching Rules (when personas loaded)" in content

    def test_claude_commands_matches_source(self):
        source = SPECIT_COMMAND.read_text()
        synced = CLAUDE_SPECIT.read_text()
        assert source == synced, "Claude commands specit differs from source template"

    def test_github_prompts_matches_source(self):
        source = SPECIT_COMMAND.read_text()
        synced = GITHUB_SPECIT.read_text()
        assert source == synced, "GitHub prompts specit differs from source template"


class TestSpecitPersonaLoadingEnhanced:
    """Verify enhanced persona loading extracts goals and pain points."""

    def test_extract_primary_goal(self):
        content = SPECIT_COMMAND.read_text()
        load_section_start = content.find("## Load Personas")
        assert load_section_start != -1
        section = content[load_section_start : load_section_start + 1500]
        assert "primary_goal" in section

    def test_extract_pain_points(self):
        content = SPECIT_COMMAND.read_text()
        load_section_start = content.find("## Load Personas")
        section = content[load_section_start : load_section_start + 1500]
        assert "pain_points" in section

    def test_extract_usage_context(self):
        content = SPECIT_COMMAND.read_text()
        load_section_start = content.find("## Load Personas")
        section = content[load_section_start : load_section_start + 1500]
        assert "usage_context" in section

    def test_extract_archetype(self):
        content = SPECIT_COMMAND.read_text()
        load_section_start = content.find("## Load Personas")
        section = content[load_section_start : load_section_start + 1500]
        assert "archetype" in section


class TestSpecitBackwardCompatibility:
    """MT-012: Verify no existing specit behavior changed for non-persona workflows."""

    def test_original_no_personas_fallback_preserved(self):
        content = SPECIT_COMMAND.read_text()
        assert 'Use generic "As a user..." format' in content

    def test_original_research_loading_preserved(self):
        content = SPECIT_COMMAND.read_text()
        assert "## Load Research Artifacts" in content

    def test_original_outline_section_preserved(self):
        content = SPECIT_COMMAND.read_text()
        assert "## Outline" in content

    def test_original_github_issue_integration_preserved(self):
        content = SPECIT_COMMAND.read_text()
        assert "## GitHub Issue Integration" in content

    def test_original_ambiguity_scan_preserved(self):
        content = SPECIT_COMMAND.read_text()
        assert "## Integrated Ambiguity Scan" in content

    def test_persona_sections_are_conditional(self):
        """All persona sections gated on personas being available."""
        content = SPECIT_COMMAND.read_text()
        assert "If NO personas.md found" in content
        assert "When No Personas Are Available" in content
        assert "when personas loaded" in content.lower()
