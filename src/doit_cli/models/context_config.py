"""Context configuration models for AI context injection.

This module provides dataclasses for configuring and managing context loading
for doit commands. Context includes constitution, roadmap, current spec,
and related specifications.
"""

from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Optional

import yaml


@dataclass
class SourceConfig:
    """Configuration for an individual context source type.

    Attributes:
        source_type: Type identifier (constitution, roadmap, current_spec, related_specs, custom)
        enabled: Whether this source should be loaded
        priority: Loading priority (lower = higher priority, loaded first)
        max_count: Maximum items for multi-item sources (e.g., related_specs)
    """

    source_type: str = ""
    enabled: bool = True
    priority: int = 99
    max_count: int = 1

    @classmethod
    def default_sources(cls) -> dict[str, "SourceConfig"]:
        """Get default source configurations."""
        return {
            "constitution": cls(source_type="constitution", enabled=True, priority=1),
            "roadmap": cls(source_type="roadmap", enabled=True, priority=2),
            "current_spec": cls(source_type="current_spec", enabled=True, priority=3),
            "related_specs": cls(source_type="related_specs", enabled=True, priority=4, max_count=3),
        }


@dataclass
class CommandOverride:
    """Per-command configuration overrides.

    Attributes:
        command_name: Command to override (specit, planit, etc.)
        sources: Source configuration overrides for this command
    """

    command_name: str = ""
    sources: dict[str, SourceConfig] = field(default_factory=dict)


@dataclass
class ContextConfig:
    """Configuration for context loading behavior.

    Loaded from `.doit/config/context.yaml`.

    Attributes:
        version: Config schema version (must be 1)
        enabled: Master toggle for context loading
        max_tokens_per_source: Token limit per individual source
        total_max_tokens: Token limit for all context combined
        sources: Per-source configuration
        commands: Per-command overrides
    """

    version: int = 1
    enabled: bool = True
    max_tokens_per_source: int = 4000
    total_max_tokens: int = 16000
    sources: dict[str, SourceConfig] = field(default_factory=SourceConfig.default_sources)
    commands: dict[str, CommandOverride] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """Validate configuration after initialization."""
        if self.max_tokens_per_source <= 0:
            self.max_tokens_per_source = 4000
        if self.total_max_tokens < self.max_tokens_per_source:
            self.total_max_tokens = self.max_tokens_per_source

    @classmethod
    def default(cls) -> "ContextConfig":
        """Create default configuration."""
        return cls()

    @classmethod
    def from_yaml(cls, path: Path) -> "ContextConfig":
        """Load configuration from YAML file.

        Args:
            path: Path to the context.yaml configuration file.

        Returns:
            ContextConfig instance with values from file or defaults.
        """
        if not path.exists():
            return cls.default()

        try:
            with open(path, encoding="utf-8") as f:
                data = yaml.safe_load(f) or {}
        except (yaml.YAMLError, OSError):
            # Return default config on parse error
            return cls.default()

        return cls._from_dict(data)

    @classmethod
    def _from_dict(cls, data: dict) -> "ContextConfig":
        """Create ContextConfig from dictionary."""
        # Parse sources
        sources_data = data.get("sources", {})
        sources = SourceConfig.default_sources()

        for source_type, source_config in sources_data.items():
            if isinstance(source_config, dict):
                if source_type in sources:
                    # Update existing source config
                    for key, value in source_config.items():
                        if hasattr(sources[source_type], key):
                            setattr(sources[source_type], key, value)
                else:
                    # Create new custom source
                    sources[source_type] = SourceConfig(
                        source_type=source_type,
                        **{k: v for k, v in source_config.items()
                           if k in SourceConfig.__dataclass_fields__}
                    )

        # Parse command overrides
        commands_data = data.get("commands", {})
        commands: dict[str, CommandOverride] = {}

        for cmd_name, cmd_config in commands_data.items():
            if isinstance(cmd_config, dict):
                cmd_sources: dict[str, SourceConfig] = {}
                cmd_sources_data = cmd_config.get("sources", {})

                for source_type, source_config in cmd_sources_data.items():
                    if isinstance(source_config, dict):
                        cmd_sources[source_type] = SourceConfig(
                            source_type=source_type,
                            **{k: v for k, v in source_config.items()
                               if k in SourceConfig.__dataclass_fields__}
                        )

                commands[cmd_name] = CommandOverride(
                    command_name=cmd_name,
                    sources=cmd_sources
                )

        return cls(
            version=data.get("version", 1),
            enabled=data.get("enabled", True),
            max_tokens_per_source=data.get("max_tokens_per_source", 4000),
            total_max_tokens=data.get("total_max_tokens", 16000),
            sources=sources,
            commands=commands,
        )

    @classmethod
    def get_default_config_path(cls) -> Path:
        """Get the default configuration file path."""
        return Path(".doit/config/context.yaml")

    @classmethod
    def load_default(cls) -> "ContextConfig":
        """Load configuration from default location."""
        return cls.from_yaml(cls.get_default_config_path())

    @classmethod
    def load_from_project(cls, project_root: Path) -> "ContextConfig":
        """Load configuration from a project directory.

        Args:
            project_root: Root directory of the project.

        Returns:
            ContextConfig loaded from the project or defaults.
        """
        config_path = project_root / ".doit" / "config" / "context.yaml"
        return cls.from_yaml(config_path)

    def get_source_config(
        self, source_type: str, command: Optional[str] = None
    ) -> SourceConfig:
        """Get effective source configuration, considering command overrides.

        Args:
            source_type: Type of source (constitution, roadmap, etc.)
            command: Current command name for per-command overrides

        Returns:
            Effective SourceConfig for the given source and command.
        """
        # Start with base source config
        base_config = self.sources.get(
            source_type,
            SourceConfig(source_type=source_type)
        )

        # Check for command-specific override
        if command and command in self.commands:
            cmd_override = self.commands[command]
            if source_type in cmd_override.sources:
                override = cmd_override.sources[source_type]
                # Merge override with base (override takes precedence)
                return SourceConfig(
                    source_type=source_type,
                    enabled=override.enabled,
                    priority=override.priority if override.priority != 99 else base_config.priority,
                    max_count=override.max_count if override.max_count != 1 else base_config.max_count,
                )

        return base_config


@dataclass
class ContextSource:
    """A loaded context source ready for injection.

    Attributes:
        source_type: Type of source (constitution, roadmap, etc.)
        path: File path that was loaded
        content: Loaded content (possibly truncated)
        token_count: Estimated token count
        truncated: Whether content was truncated
        original_tokens: Original token count before truncation (if truncated)
    """

    source_type: str
    path: Path
    content: str
    token_count: int
    truncated: bool = False
    original_tokens: Optional[int] = None

    def __lt__(self, other: "ContextSource") -> bool:
        """Compare sources by their source type for sorting."""
        return self.source_type < other.source_type


@dataclass
class LoadedContext:
    """Aggregated context ready for injection into command prompt.

    Attributes:
        sources: All loaded sources, ordered by priority
        total_tokens: Sum of all source token counts
        any_truncated: True if any source was truncated
        loaded_at: Timestamp when context was loaded
    """

    sources: list[ContextSource] = field(default_factory=list)
    total_tokens: int = 0
    any_truncated: bool = False
    loaded_at: datetime = field(default_factory=datetime.now)

    def to_markdown(self) -> str:
        """Format all sources as markdown for injection.

        Returns:
            Markdown-formatted context suitable for AI consumption.
        """
        if not self.sources:
            return ""

        sections = ["<!-- PROJECT CONTEXT - Auto-loaded by doit -->", ""]

        # Map source types to display names
        display_names = {
            "constitution": "Constitution",
            "roadmap": "Roadmap",
            "current_spec": "Current Spec",
            "related_specs": "Related Specs",
        }

        for source in self.sources:
            display_name = display_names.get(source.source_type, source.source_type.title())

            # Add section header
            if source.source_type == "current_spec":
                # Extract feature name from path if possible
                feature_name = source.path.parent.name if source.path.parent.name != "." else ""
                if feature_name:
                    sections.append(f"## {display_name}: {feature_name}")
                else:
                    sections.append(f"## {display_name}")
            elif source.source_type == "related_specs":
                # For related specs, use individual headers
                feature_name = source.path.parent.name if source.path.parent.name != "." else ""
                sections.append(f"### {feature_name}")
            else:
                sections.append(f"## {display_name}")

            sections.append("")
            sections.append(source.content)

            if source.truncated and source.original_tokens:
                sections.append("")
                sections.append(f"<!-- Content truncated from {source.original_tokens} to {source.token_count} tokens. Full file at: {source.path} -->")

            sections.append("")

        sections.append("<!-- End of project context -->")

        return "\n".join(sections)

    def get_source(self, source_type: str) -> Optional[ContextSource]:
        """Get specific source by type.

        Args:
            source_type: Type of source to retrieve.

        Returns:
            ContextSource if found, None otherwise.
        """
        for source in self.sources:
            if source.source_type == source_type:
                return source
        return None

    def has_source(self, source_type: str) -> bool:
        """Check if source type is loaded.

        Args:
            source_type: Type of source to check.

        Returns:
            True if source is loaded, False otherwise.
        """
        return self.get_source(source_type) is not None
