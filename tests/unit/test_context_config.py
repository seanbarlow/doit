"""Unit tests for ContextConfig model."""

import pytest
from pathlib import Path

from doit_cli.models.context_config import (
    SourceConfig,
    CommandOverride,
    ContextConfig,
    ContextSource,
    LoadedContext,
)


class TestSourceConfig:
    """Tests for SourceConfig dataclass."""

    def test_default_values(self):
        """Test default SourceConfig values."""
        config = SourceConfig()
        assert config.source_type == ""
        assert config.enabled is True
        assert config.priority == 99
        assert config.max_count == 1

    def test_custom_values(self):
        """Test SourceConfig with custom values."""
        config = SourceConfig(
            source_type="constitution",
            enabled=False,
            priority=1,
            max_count=5,
        )
        assert config.source_type == "constitution"
        assert config.enabled is False
        assert config.priority == 1
        assert config.max_count == 5

    def test_default_sources(self):
        """Test default source configurations."""
        sources = SourceConfig.default_sources()

        assert "constitution" in sources
        assert "tech_stack" in sources
        assert "roadmap" in sources
        assert "current_spec" in sources
        assert "related_specs" in sources
        assert "completed_roadmap" in sources

        assert sources["constitution"].priority == 1
        assert sources["tech_stack"].priority == 2
        assert sources["roadmap"].priority == 3
        assert sources["completed_roadmap"].priority == 4
        assert sources["current_spec"].priority == 5
        assert sources["related_specs"].priority == 6
        assert sources["related_specs"].max_count == 3
        assert sources["completed_roadmap"].max_count == 5


class TestCommandOverride:
    """Tests for CommandOverride dataclass."""

    def test_default_values(self):
        """Test default CommandOverride values."""
        override = CommandOverride()
        assert override.command_name == ""
        assert override.sources == {}

    def test_custom_values(self):
        """Test CommandOverride with custom values."""
        override = CommandOverride(
            command_name="specit",
            sources={
                "related_specs": SourceConfig(
                    source_type="related_specs",
                    enabled=False,
                )
            },
        )
        assert override.command_name == "specit"
        assert "related_specs" in override.sources
        assert override.sources["related_specs"].enabled is False


class TestContextConfig:
    """Tests for ContextConfig dataclass."""

    def test_default_values(self):
        """Test default ContextConfig values."""
        config = ContextConfig()
        assert config.version == 1
        assert config.enabled is True
        assert config.max_tokens_per_source == 4000
        assert config.total_max_tokens == 16000
        assert "constitution" in config.sources
        # Default command overrides for specit, constitution, roadmapit
        assert "specit" in config.commands
        assert "constitution" in config.commands
        assert "roadmapit" in config.commands

    def test_post_init_fixes_invalid_values(self):
        """Test __post_init__ fixes invalid token values."""
        config = ContextConfig(
            max_tokens_per_source=-100,
            total_max_tokens=100,  # Less than default max_tokens_per_source
        )
        assert config.max_tokens_per_source == 4000
        assert config.total_max_tokens >= config.max_tokens_per_source

    def test_get_source_config_basic(self):
        """Test getting basic source config."""
        config = ContextConfig()
        source = config.get_source_config("constitution")
        assert source.source_type == "constitution"
        assert source.enabled is True
        assert source.priority == 1

    def test_get_source_config_with_command_override(self):
        """Test getting source config with command override."""
        config = ContextConfig(
            commands={
                "specit": CommandOverride(
                    command_name="specit",
                    sources={
                        "related_specs": SourceConfig(
                            source_type="related_specs",
                            enabled=False,
                        )
                    },
                )
            }
        )

        # Without command, should be enabled
        source = config.get_source_config("related_specs")
        assert source.enabled is True

        # With command, should be disabled
        source = config.get_source_config("related_specs", command="specit")
        assert source.enabled is False

    def test_get_source_config_unknown_source(self):
        """Test getting unknown source returns default SourceConfig."""
        config = ContextConfig()
        source = config.get_source_config("custom_unknown")
        assert source.source_type == "custom_unknown"
        assert source.priority == 99


class TestContextConfigFileLoading:
    """Tests for configuration file loading."""

    def test_load_from_nonexistent_file(self, tmp_path: Path):
        """Test loading from nonexistent file returns defaults."""
        config_path = tmp_path / "nonexistent.yaml"
        config = ContextConfig.from_yaml(config_path)

        assert config.version == 1
        assert config.enabled is True
        assert config.max_tokens_per_source == 4000

    def test_load_from_valid_yaml(self, tmp_path: Path):
        """Test loading from valid YAML file."""
        config_path = tmp_path / "context.yaml"
        config_path.write_text("""
version: 1
enabled: false
max_tokens_per_source: 8000
total_max_tokens: 32000
sources:
  constitution:
    enabled: true
    priority: 1
  roadmap:
    enabled: false
    priority: 2
commands:
  specit:
    sources:
      related_specs:
        enabled: false
""")
        config = ContextConfig.from_yaml(config_path)

        assert config.version == 1
        assert config.enabled is False
        assert config.max_tokens_per_source == 8000
        assert config.total_max_tokens == 32000
        assert config.sources["roadmap"].enabled is False
        assert "specit" in config.commands

    def test_load_from_invalid_yaml(self, tmp_path: Path):
        """Test loading from invalid YAML returns defaults."""
        config_path = tmp_path / "context.yaml"
        config_path.write_text("invalid: yaml: content:")

        config = ContextConfig.from_yaml(config_path)

        # Should return defaults on parse error
        assert config.version == 1
        assert config.enabled is True

    def test_load_from_empty_file(self, tmp_path: Path):
        """Test loading from empty file returns defaults."""
        config_path = tmp_path / "context.yaml"
        config_path.write_text("")

        config = ContextConfig.from_yaml(config_path)

        assert config.version == 1
        assert config.enabled is True

    def test_load_from_project(self, tmp_path: Path):
        """Test loading from project directory."""
        config_dir = tmp_path / ".doit" / "config"
        config_dir.mkdir(parents=True)
        config_path = config_dir / "context.yaml"
        config_path.write_text("""
version: 1
enabled: false
""")

        config = ContextConfig.load_from_project(tmp_path)
        assert config.enabled is False

    def test_get_default_config_path(self):
        """Test default config path."""
        path = ContextConfig.get_default_config_path()
        assert path == Path(".doit/config/context.yaml")


class TestContextSource:
    """Tests for ContextSource dataclass."""

    def test_basic_creation(self, tmp_path: Path):
        """Test basic ContextSource creation."""
        source = ContextSource(
            source_type="constitution",
            path=tmp_path / "constitution.md",
            content="# Constitution\nTest content.",
            token_count=10,
        )
        assert source.source_type == "constitution"
        assert source.token_count == 10
        assert source.truncated is False
        assert source.original_tokens is None

    def test_truncated_source(self, tmp_path: Path):
        """Test ContextSource with truncation."""
        source = ContextSource(
            source_type="roadmap",
            path=tmp_path / "roadmap.md",
            content="# Roadmap\nTruncated...",
            token_count=100,
            truncated=True,
            original_tokens=500,
        )
        assert source.truncated is True
        assert source.original_tokens == 500

    def test_comparison(self, tmp_path: Path):
        """Test ContextSource comparison for sorting."""
        source1 = ContextSource(
            source_type="constitution",
            path=tmp_path / "a.md",
            content="",
            token_count=0,
        )
        source2 = ContextSource(
            source_type="roadmap",
            path=tmp_path / "b.md",
            content="",
            token_count=0,
        )
        assert source1 < source2


class TestLoadedContext:
    """Tests for LoadedContext dataclass."""

    def test_default_values(self):
        """Test default LoadedContext values."""
        context = LoadedContext()
        assert context.sources == []
        assert context.total_tokens == 0
        assert context.any_truncated is False
        assert context.loaded_at is not None

    def test_has_source(self, tmp_path: Path):
        """Test has_source method."""
        context = LoadedContext(
            sources=[
                ContextSource(
                    source_type="constitution",
                    path=tmp_path / "constitution.md",
                    content="test",
                    token_count=10,
                )
            ],
            total_tokens=10,
        )
        assert context.has_source("constitution") is True
        assert context.has_source("roadmap") is False

    def test_get_source(self, tmp_path: Path):
        """Test get_source method."""
        source = ContextSource(
            source_type="constitution",
            path=tmp_path / "constitution.md",
            content="test",
            token_count=10,
        )
        context = LoadedContext(sources=[source], total_tokens=10)

        result = context.get_source("constitution")
        assert result is source

        result = context.get_source("roadmap")
        assert result is None

    def test_to_markdown_empty(self):
        """Test to_markdown with no sources."""
        context = LoadedContext()
        assert context.to_markdown() == ""

    def test_to_markdown_with_sources(self, tmp_path: Path):
        """Test to_markdown with sources."""
        context = LoadedContext(
            sources=[
                ContextSource(
                    source_type="constitution",
                    path=tmp_path / "constitution.md",
                    content="# Constitution\nProject principles here.",
                    token_count=10,
                ),
                ContextSource(
                    source_type="roadmap",
                    path=tmp_path / "roadmap.md",
                    content="# Roadmap\nProject roadmap here.",
                    token_count=10,
                ),
            ],
            total_tokens=20,
        )

        markdown = context.to_markdown()

        assert "<!-- PROJECT CONTEXT - Auto-loaded by doit -->" in markdown
        assert "## Constitution" in markdown
        assert "## Roadmap" in markdown
        assert "Project principles here." in markdown
        assert "Project roadmap here." in markdown
        assert "<!-- End of project context -->" in markdown

    def test_to_markdown_with_truncation_notice(self, tmp_path: Path):
        """Test to_markdown includes truncation notice."""
        context = LoadedContext(
            sources=[
                ContextSource(
                    source_type="constitution",
                    path=tmp_path / "constitution.md",
                    content="Truncated content...",
                    token_count=100,
                    truncated=True,
                    original_tokens=500,
                ),
            ],
            total_tokens=100,
            any_truncated=True,
        )

        markdown = context.to_markdown()

        assert "truncated from 500 to 100 tokens" in markdown
