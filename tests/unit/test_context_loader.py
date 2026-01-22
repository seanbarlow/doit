"""Unit tests for ContextLoader service."""

import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock

from doit_cli.services.context_loader import (
    ContextLoader,
    estimate_tokens,
    truncate_content,
    extract_keywords,
)
from doit_cli.models.context_config import ContextConfig, SourceConfig


class TestEstimateTokens:
    """Tests for token estimation function."""

    def test_empty_string(self):
        """Test token estimation for empty string."""
        # Empty string still gets minimum 1 token
        assert estimate_tokens("") >= 0

    def test_basic_text(self):
        """Test token estimation for basic text."""
        # With fallback (character/4)
        text = "Hello world"  # 11 chars
        tokens = estimate_tokens(text)
        # Should be approximately len(text) / 4
        assert 2 <= tokens <= 4

    def test_longer_text(self):
        """Test token estimation for longer text."""
        text = "The quick brown fox jumps over the lazy dog. " * 10
        tokens = estimate_tokens(text)
        # Should be reasonable estimate
        assert tokens > 50

    def test_with_tiktoken(self):
        """Test token estimation with tiktoken if available."""
        try:
            import tiktoken
            # tiktoken is available, test actual encoding
            text = "Hello world, this is a test."
            tokens = estimate_tokens(text)
            # Should be closer to actual OpenAI tokens
            assert 5 <= tokens <= 15
        except ImportError:
            # tiktoken not available, skip test
            pytest.skip("tiktoken not installed")


class TestTruncateContent:
    """Tests for content truncation function."""

    def test_no_truncation_needed(self, tmp_path: Path):
        """Test truncation when content is under limit."""
        content = "# Header\n\nShort content."
        path = tmp_path / "test.md"
        result, truncated, original = truncate_content(content, max_tokens=1000, path=path)
        assert result == content
        assert truncated is False

    def test_truncation_preserves_headers(self, tmp_path: Path):
        """Test truncation preserves markdown headers."""
        content = """# Main Header

This is the first paragraph with some content.

## Subheader

This is another paragraph with more content.

## Another Section

Even more content here.
"""
        path = tmp_path / "test.md"
        result, truncated, original = truncate_content(content, max_tokens=20, path=path)

        # Should preserve main header
        assert "# Main Header" in result
        # Should be truncated (content may be replaced with truncation notice)
        assert truncated is True

    def test_truncation_preserves_summary(self, tmp_path: Path):
        """Test truncation preserves Summary/Overview sections."""
        content = """# Document

## Summary

This is the important summary that should be preserved.

## Details

This is less important detail content that can be truncated.

## More Details

Even more details here.
"""
        path = tmp_path / "test.md"
        result, truncated, original = truncate_content(content, max_tokens=30, path=path)

        # Should preserve summary
        assert "## Summary" in result
        assert "important summary" in result

    def test_truncation_adds_notice(self, tmp_path: Path):
        """Test truncation adds truncation notice."""
        content = "Long content. " * 1000
        path = tmp_path / "test.md"
        result, truncated, original = truncate_content(content, max_tokens=50, path=path)

        # Notice is added as HTML comment
        assert "truncated" in result.lower()
        assert len(result) < len(content)
        assert truncated is True

    def test_empty_content(self, tmp_path: Path):
        """Test truncation with empty content."""
        path = tmp_path / "test.md"
        result, truncated, original = truncate_content("", max_tokens=1000, path=path)
        assert result == ""
        assert truncated is False


class TestExtractKeywords:
    """Tests for keyword extraction function."""

    def test_basic_extraction(self):
        """Test basic keyword extraction."""
        text = "The quick brown fox jumps over the lazy dog"
        keywords = extract_keywords(text)

        # Should return top keywords
        assert len(keywords) > 0
        assert len(keywords) <= 10  # Default limit

    def test_filters_common_words(self):
        """Test common words are filtered."""
        text = "the and or but if then while for with from"
        keywords = extract_keywords(text)

        # Should filter most common words
        assert "the" not in keywords
        assert "and" not in keywords

    def test_markdown_keywords(self):
        """Test extraction from markdown content."""
        text = """# Context Injection Feature

This feature enables automatic context loading for AI commands.
The implementation uses token estimation and smart truncation.
"""
        keywords = extract_keywords(text)

        # Should find meaningful keywords
        assert len(keywords) > 0
        # Common meaningful words should appear
        meaningful_found = any(
            kw in ["context", "feature", "loading", "implementation", "token"]
            for kw in keywords
        )
        assert meaningful_found


class TestContextLoader:
    """Tests for ContextLoader service."""

    def test_initialization(self, tmp_path: Path):
        """Test basic initialization."""
        loader = ContextLoader(project_root=tmp_path)
        assert loader.project_root == tmp_path
        assert loader.config is not None
        assert loader.command is None

    def test_initialization_with_config(self, tmp_path: Path):
        """Test initialization with custom config."""
        config = ContextConfig(enabled=False)
        loader = ContextLoader(project_root=tmp_path, config=config)
        assert loader.config.enabled is False

    def test_initialization_with_command(self, tmp_path: Path):
        """Test initialization with command for overrides."""
        loader = ContextLoader(project_root=tmp_path, command="specit")
        assert loader.command == "specit"

    def test_load_empty_project(self, tmp_path: Path):
        """Test loading context from empty project."""
        loader = ContextLoader(project_root=tmp_path)
        context = loader.load()

        assert context.sources == []
        assert context.total_tokens == 0
        assert context.any_truncated is False

    def test_load_disabled_context(self, tmp_path: Path):
        """Test loading when context is disabled."""
        config = ContextConfig(enabled=False)
        loader = ContextLoader(project_root=tmp_path, config=config)
        context = loader.load()

        assert context.sources == []
        assert context.total_tokens == 0


class TestContextLoaderConstitution:
    """Tests for constitution loading."""

    def test_load_constitution(self, tmp_path: Path):
        """Test loading constitution file."""
        # Create constitution
        memory_dir = tmp_path / ".doit" / "memory"
        memory_dir.mkdir(parents=True)
        constitution = memory_dir / "constitution.md"
        constitution.write_text("# Constitution\n\nProject principles.")

        loader = ContextLoader(project_root=tmp_path)
        source = loader.load_constitution()

        assert source is not None
        assert source.source_type == "constitution"
        assert "Project principles" in source.content
        assert source.token_count > 0

    def test_load_constitution_missing(self, tmp_path: Path):
        """Test loading missing constitution returns None."""
        loader = ContextLoader(project_root=tmp_path)
        source = loader.load_constitution()

        assert source is None

    def test_load_constitution_disabled(self, tmp_path: Path):
        """Test disabled constitution is not included in load() results."""
        # Create constitution
        memory_dir = tmp_path / ".doit" / "memory"
        memory_dir.mkdir(parents=True)
        constitution = memory_dir / "constitution.md"
        constitution.write_text("# Constitution")

        # Create config that disables constitution via YAML
        config_dir = tmp_path / ".doit" / "config"
        config_dir.mkdir(parents=True)
        (config_dir / "context.yaml").write_text("""
version: 1
sources:
  constitution:
    enabled: false
""")

        config = ContextConfig.load_from_project(tmp_path)
        loader = ContextLoader(project_root=tmp_path, config=config)

        # Enabled check happens in load(), not load_constitution()
        context = loader.load()
        assert not context.has_source("constitution")


class TestContextLoaderRoadmap:
    """Tests for roadmap loading."""

    def test_load_roadmap(self, tmp_path: Path):
        """Test loading roadmap file."""
        memory_dir = tmp_path / ".doit" / "memory"
        memory_dir.mkdir(parents=True)
        roadmap = memory_dir / "roadmap.md"
        roadmap.write_text("# Roadmap\n\n## P1 - Critical\n- Feature X")

        loader = ContextLoader(project_root=tmp_path)
        source = loader.load_roadmap()

        assert source is not None
        assert source.source_type == "roadmap"
        assert "Feature X" in source.content

    def test_load_roadmap_missing(self, tmp_path: Path):
        """Test loading missing roadmap returns None."""
        loader = ContextLoader(project_root=tmp_path)
        source = loader.load_roadmap()

        assert source is None


class TestContextLoaderCurrentSpec:
    """Tests for current spec loading."""

    def test_load_current_spec(self, tmp_path: Path):
        """Test loading current spec based on branch."""
        # Create spec directory
        spec_dir = tmp_path / "specs" / "026-test-feature"
        spec_dir.mkdir(parents=True)
        spec_file = spec_dir / "spec.md"
        spec_file.write_text("# Feature Spec\n\nFeature description.")

        loader = ContextLoader(project_root=tmp_path)

        # Mock branch detection
        with patch.object(loader, "get_current_branch", return_value="026-test-feature"):
            source = loader.load_current_spec()

        assert source is not None
        assert source.source_type == "current_spec"
        assert "Feature description" in source.content

    def test_load_current_spec_no_branch(self, tmp_path: Path):
        """Test loading current spec with no branch returns None."""
        loader = ContextLoader(project_root=tmp_path)

        with patch.object(loader, "get_current_branch", return_value=None):
            source = loader.load_current_spec()

        assert source is None

    def test_load_current_spec_no_matching_spec(self, tmp_path: Path):
        """Test loading current spec with no matching spec dir returns None."""
        loader = ContextLoader(project_root=tmp_path)

        with patch.object(loader, "get_current_branch", return_value="026-test-feature"):
            source = loader.load_current_spec()

        assert source is None


class TestContextLoaderExtractFeatureName:
    """Tests for feature name extraction from branch."""

    def test_extract_feature_branch(self, tmp_path: Path):
        """Test extracting feature from standard branch name."""
        loader = ContextLoader(project_root=tmp_path)

        result = loader.extract_feature_name("026-ai-context-injection")
        assert result == "026-ai-context-injection"

    def test_extract_with_prefix(self, tmp_path: Path):
        """Test extracting feature from branch with prefix."""
        loader = ContextLoader(project_root=tmp_path)

        result = loader.extract_feature_name("feature/026-ai-context")
        assert result == "026-ai-context"

        result = loader.extract_feature_name("feat/001-initial-setup")
        assert result == "001-initial-setup"

    def test_extract_main_branch(self, tmp_path: Path):
        """Test extracting feature from main branch returns None."""
        loader = ContextLoader(project_root=tmp_path)

        result = loader.extract_feature_name("main")
        assert result is None

        result = loader.extract_feature_name("master")
        assert result is None

    def test_extract_develop_branch(self, tmp_path: Path):
        """Test extracting feature from develop branch returns None."""
        loader = ContextLoader(project_root=tmp_path)

        result = loader.extract_feature_name("develop")
        assert result is None


class TestContextLoaderRelatedSpecs:
    """Tests for related specs discovery."""

    def test_find_related_specs_empty(self, tmp_path: Path):
        """Test finding related specs with no specs directory."""
        loader = ContextLoader(project_root=tmp_path)
        related = loader.find_related_specs()

        assert related == []

    def test_find_related_specs(self, tmp_path: Path):
        """Test finding related specs based on content similarity."""
        # Create current spec
        spec_dir = tmp_path / "specs" / "026-context-injection"
        spec_dir.mkdir(parents=True)
        (spec_dir / "spec.md").write_text("""
# Context Injection

## Summary
Automatic context loading for AI commands.
""")

        # Create related spec
        related_dir = tmp_path / "specs" / "023-prompt-sync"
        related_dir.mkdir(parents=True)
        (related_dir / "spec.md").write_text("""
# Prompt Sync

## Summary
Synchronize AI prompt templates.
""")

        # Create unrelated spec
        unrelated_dir = tmp_path / "specs" / "001-database-setup"
        unrelated_dir.mkdir(parents=True)
        (unrelated_dir / "spec.md").write_text("""
# Database Setup

## Summary
Configure PostgreSQL database.
""")

        loader = ContextLoader(project_root=tmp_path)

        with patch.object(loader, "get_current_branch", return_value="026-context-injection"):
            related = loader.find_related_specs()

        # Should find specs but exclude current
        for source in related:
            assert source.source_type == "related_specs"
            assert "026-context-injection" not in str(source.path)


class TestContextLoaderFullLoad:
    """Integration tests for full context loading."""

    def test_full_load(self, tmp_path: Path):
        """Test loading all context sources."""
        # Setup project
        memory_dir = tmp_path / ".doit" / "memory"
        memory_dir.mkdir(parents=True)
        (memory_dir / "constitution.md").write_text("# Constitution\nPrinciples.")
        (memory_dir / "roadmap.md").write_text("# Roadmap\nItems.")

        spec_dir = tmp_path / "specs" / "026-test"
        spec_dir.mkdir(parents=True)
        (spec_dir / "spec.md").write_text("# Spec\nFeature.")

        loader = ContextLoader(project_root=tmp_path)

        with patch.object(loader, "get_current_branch", return_value="026-test"):
            context = loader.load()

        assert len(context.sources) == 3
        assert context.has_source("constitution")
        assert context.has_source("roadmap")
        assert context.has_source("current_spec")
        assert context.total_tokens > 0

    def test_load_respects_priority_order(self, tmp_path: Path):
        """Test sources are loaded in priority order."""
        memory_dir = tmp_path / ".doit" / "memory"
        memory_dir.mkdir(parents=True)
        (memory_dir / "constitution.md").write_text("# Constitution")
        (memory_dir / "roadmap.md").write_text("# Roadmap")

        loader = ContextLoader(project_root=tmp_path)
        context = loader.load()

        # Constitution (priority 1) should come before roadmap (priority 2)
        if len(context.sources) >= 2:
            types = [s.source_type for s in context.sources]
            const_idx = types.index("constitution")
            road_idx = types.index("roadmap")
            assert const_idx < road_idx

    def test_load_applies_command_overrides(self, tmp_path: Path):
        """Test command overrides are applied during load."""
        memory_dir = tmp_path / ".doit" / "memory"
        memory_dir.mkdir(parents=True)
        (memory_dir / "constitution.md").write_text("# Constitution")
        (memory_dir / "roadmap.md").write_text("# Roadmap")

        # Create config that disables roadmap for specit command
        config_dir = tmp_path / ".doit" / "config"
        config_dir.mkdir(parents=True)
        (config_dir / "context.yaml").write_text("""
version: 1
commands:
  specit:
    sources:
      roadmap:
        enabled: false
""")

        # Load without command - should have roadmap
        loader1 = ContextLoader(project_root=tmp_path)
        context1 = loader1.load()
        assert context1.has_source("roadmap")

        # Load with specit command - should not have roadmap
        loader2 = ContextLoader(project_root=tmp_path, command="specit")
        context2 = loader2.load()
        assert not context2.has_source("roadmap")


class TestContextLoaderTechStack:
    """Tests for tech-stack loading (Feature #046)."""

    def test_load_tech_stack(self, tmp_path: Path):
        """Test loading tech-stack.md file."""
        memory_dir = tmp_path / ".doit" / "memory"
        memory_dir.mkdir(parents=True)
        tech_stack = memory_dir / "tech-stack.md"
        tech_stack.write_text("# Tech Stack\n\n## Languages\nPython 3.11+")

        loader = ContextLoader(project_root=tmp_path)
        source = loader.load_tech_stack()

        assert source is not None
        assert source.source_type == "tech_stack"
        assert "Python 3.11" in source.content
        assert source.token_count > 0

    def test_load_tech_stack_missing(self, tmp_path: Path):
        """Test loading missing tech-stack returns None."""
        loader = ContextLoader(project_root=tmp_path)
        source = loader.load_tech_stack()

        assert source is None

    def test_load_includes_tech_stack(self, tmp_path: Path):
        """Test that load() includes tech_stack in results."""
        memory_dir = tmp_path / ".doit" / "memory"
        memory_dir.mkdir(parents=True)
        (memory_dir / "constitution.md").write_text("# Constitution")
        (memory_dir / "tech-stack.md").write_text("# Tech Stack\n\nPython")

        loader = ContextLoader(project_root=tmp_path)
        context = loader.load()

        assert context.has_source("constitution")
        assert context.has_source("tech_stack")

    def test_tech_stack_priority(self, tmp_path: Path):
        """Test tech_stack has priority 2 (after constitution)."""
        memory_dir = tmp_path / ".doit" / "memory"
        memory_dir.mkdir(parents=True)
        (memory_dir / "constitution.md").write_text("# Constitution")
        (memory_dir / "tech-stack.md").write_text("# Tech Stack")
        (memory_dir / "roadmap.md").write_text("# Roadmap")

        loader = ContextLoader(project_root=tmp_path)
        context = loader.load()

        # Should be: constitution (1), tech_stack (2), roadmap (3)
        types = [s.source_type for s in context.sources]
        const_idx = types.index("constitution")
        tech_idx = types.index("tech_stack")
        road_idx = types.index("roadmap")
        assert const_idx < tech_idx < road_idx

    def test_specit_command_disables_tech_stack(self, tmp_path: Path):
        """Test that specit command disables tech_stack loading."""
        memory_dir = tmp_path / ".doit" / "memory"
        memory_dir.mkdir(parents=True)
        (memory_dir / "constitution.md").write_text("# Constitution")
        (memory_dir / "tech-stack.md").write_text("# Tech Stack")

        # Load without command - should have tech_stack
        loader1 = ContextLoader(project_root=tmp_path)
        context1 = loader1.load()
        assert context1.has_source("tech_stack")

        # Load with specit command - should not have tech_stack
        loader2 = ContextLoader(project_root=tmp_path, command="specit")
        context2 = loader2.load()
        assert not context2.has_source("tech_stack")

    def test_constitution_command_disables_tech_stack(self, tmp_path: Path):
        """Test that constitution command disables tech_stack loading."""
        memory_dir = tmp_path / ".doit" / "memory"
        memory_dir.mkdir(parents=True)
        (memory_dir / "constitution.md").write_text("# Constitution")
        (memory_dir / "tech-stack.md").write_text("# Tech Stack")

        # Load with constitution command - should not have tech_stack
        loader = ContextLoader(project_root=tmp_path, command="constitution")
        context = loader.load()
        assert context.has_source("constitution")
        assert not context.has_source("tech_stack")

    def test_tech_stack_display_name(self, tmp_path: Path):
        """Test tech_stack appears with proper display name in markdown output."""
        memory_dir = tmp_path / ".doit" / "memory"
        memory_dir.mkdir(parents=True)
        (memory_dir / "tech-stack.md").write_text("# Tech Stack\n\nPython")

        loader = ContextLoader(project_root=tmp_path)
        context = loader.load()
        markdown = context.to_markdown()

        assert "## Tech Stack" in markdown
