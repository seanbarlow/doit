"""ContextLoader orchestrator — loads and aggregates project context sources.

This module holds the `ContextLoader` class that stitches together constitution,
tech-stack, personas, roadmap, and spec content for injection into AI command
prompts. The supporting pieces (token/similarity helpers, condenser, completed-
roadmap parser) live in sibling modules in this package.
"""

from __future__ import annotations

import logging
import os
import re
import subprocess
from datetime import datetime
from pathlib import Path

from ...models.context_config import (
    ContextConfig,
    ContextSource,
    LoadedContext,
)
from ..roadmap_summarizer import RoadmapSummarizer
from .completed import format_completed_for_context, parse_completed_roadmap
from .condenser import ContextCondenser
from .utils import compute_similarity_scores, estimate_tokens, truncate_content

logger = logging.getLogger(__name__)


class ContextLoader:
    """Service for loading and aggregating project context.

    Loads context from various sources (constitution, roadmap, specs) and
    formats them for injection into AI command prompts.
    """

    def __init__(
        self,
        project_root: Path,
        config: ContextConfig | None = None,
        command: str | None = None,
    ):
        """Initialize context loader.

        Args:
            project_root: Root directory of the project.
            config: Context configuration (loads default if None).
            command: Current command name for per-command overrides.
        """
        self.project_root = project_root
        self.command = command

        if config is None:
            config_path = project_root / ".doit" / "config" / "context.yaml"
            self.config = ContextConfig.from_yaml(config_path)
        else:
            self.config = config

        self._cache: dict[Path, str] = {}

    def _is_debug_enabled(self) -> bool:
        return os.environ.get("DOIT_DEBUG", "").lower() in ("1", "true", "yes")

    def _log_debug(self, message: str) -> None:
        if self._is_debug_enabled():
            print(f"[context] {message}")

    def _read_file(self, path: Path) -> str | None:
        """Read file content with caching."""
        if path in self._cache:
            return self._cache[path]

        if not path.exists():
            return None

        try:
            content = path.read_text(encoding="utf-8")
            self._cache[path] = content
            return content
        except (OSError, UnicodeDecodeError) as e:
            self._log_debug(f"Warning: Could not read {path}: {e}")
            return None

    def load(self) -> LoadedContext:
        """Load all configured context sources."""
        if not self.config.enabled:
            return LoadedContext(loaded_at=datetime.now())

        sources: list[ContextSource] = []
        total_tokens = 0

        source_configs = [
            (name, self.config.get_source_config(name, self.command))
            for name in [
                "constitution",
                "tech_stack",
                "personas",
                "roadmap",
                "completed_roadmap",
                "current_spec",
                "related_specs",
            ]
        ]
        source_configs.sort(key=lambda x: x[1].priority)

        for source_name, source_config in source_configs:
            if not source_config.enabled:
                continue

            if total_tokens >= self.config.total_max_tokens:
                self._log_debug(f"Skipping {source_name}: total token limit reached")
                break

            remaining_tokens = self.config.total_max_tokens - total_tokens
            max_for_source = min(self.config.max_tokens_per_source, remaining_tokens)

            if source_name == "constitution":
                source = self.load_constitution(max_tokens=max_for_source)
                if source:
                    sources.append(source)
                    total_tokens += source.token_count
            elif source_name == "tech_stack":
                source = self.load_tech_stack(max_tokens=max_for_source)
                if source:
                    sources.append(source)
                    total_tokens += source.token_count
            elif source_name == "personas":
                source = self.load_personas(max_tokens=max_for_source)
                if source:
                    sources.append(source)
                    total_tokens += source.token_count
            elif source_name == "roadmap":
                source = self.load_roadmap(max_tokens=max_for_source)
                if source:
                    sources.append(source)
                    total_tokens += source.token_count
            elif source_name == "completed_roadmap":
                source = self.load_completed_roadmap(max_tokens=max_for_source)
                if source:
                    sources.append(source)
                    total_tokens += source.token_count
            elif source_name == "current_spec":
                source = self.load_current_spec(max_tokens=max_for_source)
                if source:
                    sources.append(source)
                    total_tokens += source.token_count
            elif source_name == "related_specs":
                related = self.find_related_specs(
                    max_count=source_config.max_count,
                    max_tokens_per_spec=max_for_source // max(source_config.max_count, 1),
                )
                for spec in related:
                    if total_tokens + spec.token_count <= self.config.total_max_tokens:
                        sources.append(spec)
                        total_tokens += spec.token_count

        any_truncated = any(s.truncated for s in sources)

        self._log_debug(f"Total context: {total_tokens} tokens from {len(sources)} sources")

        context = LoadedContext(
            sources=sources,
            total_tokens=total_tokens,
            any_truncated=any_truncated,
            loaded_at=datetime.now(),
        )

        return self._check_and_apply_condensation(context)

    def _check_and_apply_condensation(self, context: LoadedContext) -> LoadedContext:
        """Apply soft-threshold guidance and hard-limit truncation."""
        if not self.config.summarization.enabled:
            return context

        condenser = ContextCondenser(self.config.summarization)

        exceeds_soft, exceeds_hard = condenser.check_threshold(
            context.total_tokens, self.config.total_max_tokens
        )

        if exceeds_hard:
            self._log_debug(
                f"Context exceeds hard limit ({context.total_tokens} >= "
                f"{self.config.total_max_tokens}), truncating sources"
            )
            new_sources, new_total = condenser.truncate_if_needed(
                context.sources,
                self.config.total_max_tokens,
                self.config.summarization.source_priorities,
            )
            context = LoadedContext(
                sources=new_sources,
                total_tokens=new_total,
                any_truncated=True,
                loaded_at=context.loaded_at,
            )
            exceeds_soft, _ = condenser.check_threshold(
                context.total_tokens, self.config.total_max_tokens
            )

        if exceeds_soft:
            soft_threshold = int(
                self.config.total_max_tokens
                * (self.config.summarization.threshold_percentage / 100.0)
            )
            self._log_debug(
                f"Context exceeds soft threshold ({context.total_tokens} >= "
                f"{soft_threshold}), adding guidance prompt"
            )

            current_feature = None
            branch = self.get_current_branch()
            if branch:
                current_feature = self.extract_feature_name(branch)

            context._guidance_prompt = condenser.add_guidance_prompt("", current_feature).rstrip()

        return context

    def load_constitution(self, max_tokens: int | None = None) -> ContextSource | None:
        """Load `.doit/memory/constitution.md` if enabled and exists."""
        max_tokens = max_tokens or self.config.max_tokens_per_source
        path = self.project_root / ".doit" / "memory" / "constitution.md"

        content = self._read_file(path)
        if content is None:
            self._log_debug("Constitution not found")
            return None

        truncated_content, was_truncated, original_tokens = truncate_content(
            content, max_tokens, path
        )
        token_count = estimate_tokens(truncated_content)

        self._log_debug(f"Loaded constitution: {token_count} tokens")

        return ContextSource(
            source_type="constitution",
            path=path,
            content=truncated_content,
            token_count=token_count,
            truncated=was_truncated,
            original_tokens=original_tokens if was_truncated else None,
        )

    def load_tech_stack(self, max_tokens: int | None = None) -> ContextSource | None:
        """Load `.doit/memory/tech-stack.md` if enabled and exists."""
        max_tokens = max_tokens or self.config.max_tokens_per_source
        path = self.project_root / ".doit" / "memory" / "tech-stack.md"

        content = self._read_file(path)
        if content is None:
            self._log_debug("Tech stack not found")
            return None

        truncated_content, was_truncated, original_tokens = truncate_content(
            content, max_tokens, path
        )
        token_count = estimate_tokens(truncated_content)

        self._log_debug(f"Loaded tech stack: {token_count} tokens")

        return ContextSource(
            source_type="tech_stack",
            path=path,
            content=truncated_content,
            token_count=token_count,
            truncated=was_truncated,
            original_tokens=original_tokens if was_truncated else None,
        )

    def load_personas(self, max_tokens: int | None = None) -> ContextSource | None:
        """Load personas.md if present.

        Feature-level (`specs/{feature}/personas.md`) takes precedence over
        project-level (`.doit/memory/personas.md`). Content is always loaded
        in full without truncation. The `max_tokens` argument is accepted for
        interface consistency but ignored.
        """
        branch = self.get_current_branch()
        feature_name = self.extract_feature_name(branch) if branch else None
        path = None

        if feature_name:
            feature_personas = self.project_root / "specs" / feature_name / "personas.md"
            if feature_personas.exists():
                path = feature_personas
                self._log_debug(f"Using feature-level personas: {path}")

        if path is None:
            path = self.project_root / ".doit" / "memory" / "personas.md"

        content = self._read_file(path)
        if content is None:
            self._log_debug("Personas not found")
            return None

        if not content.strip():
            self._log_debug("Personas file is empty, skipping")
            return None

        token_count = estimate_tokens(content)

        self._log_debug(f"Loaded personas: {token_count} tokens")

        return ContextSource(
            source_type="personas",
            path=path,
            content=content,
            token_count=token_count,
            truncated=False,
            original_tokens=None,
        )

    def load_roadmap(self, max_tokens: int | None = None) -> ContextSource | None:
        """Load `.doit/memory/roadmap.md`, summarizing if it exceeds budget."""
        max_tokens = max_tokens or self.config.max_tokens_per_source
        path = self.project_root / ".doit" / "memory" / "roadmap.md"

        content = self._read_file(path)
        if content is None:
            self._log_debug("Roadmap not found")
            return None

        original_tokens = estimate_tokens(content)
        if self.config.summarization.enabled and original_tokens > max_tokens:
            return self._summarize_roadmap(path, content, max_tokens)

        truncated_content, was_truncated, original_tokens = truncate_content(
            content, max_tokens, path
        )
        token_count = estimate_tokens(truncated_content)

        self._log_debug(f"Loaded roadmap: {token_count} tokens")

        return ContextSource(
            source_type="roadmap",
            path=path,
            content=truncated_content,
            token_count=token_count,
            truncated=was_truncated,
            original_tokens=original_tokens if was_truncated else None,
        )

    def _summarize_roadmap(self, path: Path, content: str, max_tokens: int) -> ContextSource:
        """Summarize roadmap by priority, highlighting the current feature."""
        original_tokens = estimate_tokens(content)

        branch = self.get_current_branch()
        current_feature = self.extract_feature_name(branch) if branch else None

        summarizer = RoadmapSummarizer(self.config.summarization)
        items = summarizer.parse_roadmap(content)
        summary = summarizer.summarize(items, max_tokens, current_feature)

        token_count = estimate_tokens(summary.condensed_text)
        was_summarized = token_count < original_tokens

        self._log_debug(
            f"Loaded roadmap (summarized): {token_count} tokens "
            f"({summary.item_count} items, priorities: {summary.priorities_included})"
        )

        return ContextSource(
            source_type="roadmap",
            path=path,
            content=summary.condensed_text,
            token_count=token_count,
            truncated=was_summarized,
            original_tokens=original_tokens if was_summarized else None,
        )

    def load_completed_roadmap(self, max_tokens: int | None = None) -> ContextSource | None:
        """Parse and format `.doit/memory/completed_roadmap.md`."""
        max_tokens = max_tokens or self.config.max_tokens_per_source
        path = self.project_root / ".doit" / "memory" / "completed_roadmap.md"

        content = self._read_file(path)
        if content is None:
            self._log_debug("Completed roadmap not found")
            return None

        items = parse_completed_roadmap(content)
        if not items:
            self._log_debug("No completed items found in completed_roadmap.md")
            return None

        max_count = self.config.summarization.completed_items_max_count
        items = items[:max_count]

        formatted_content = format_completed_for_context(items)
        token_count = estimate_tokens(formatted_content)

        if token_count > max_tokens:
            truncated_content, was_truncated, original_tokens = truncate_content(
                formatted_content, max_tokens, path
            )
            token_count = estimate_tokens(truncated_content)
        else:
            truncated_content = formatted_content
            was_truncated = False
            original_tokens = token_count

        self._log_debug(f"Loaded completed_roadmap: {token_count} tokens ({len(items)} items)")

        return ContextSource(
            source_type="completed_roadmap",
            path=path,
            content=truncated_content,
            token_count=token_count,
            truncated=was_truncated,
            original_tokens=original_tokens if was_truncated else None,
        )

    def get_current_branch(self) -> str | None:
        """Return current git branch name, or None if unavailable."""
        try:
            result = subprocess.run(
                ["git", "rev-parse", "--abbrev-ref", "HEAD"],
                capture_output=True,
                text=True,
                cwd=self.project_root,
                timeout=5,
            )
            if result.returncode == 0:
                return result.stdout.strip()
        except (subprocess.SubprocessError, FileNotFoundError, OSError):
            pass
        return None

    def extract_feature_name(self, branch: str) -> str | None:
        """Extract `NNN-feature-name` from a branch like `026-ai-context` or `feature/026-name`."""
        patterns = [
            r"^(\d{3}-[\w-]+)",  # 026-feature-name
            r"^feature/(\d{3}-[\w-]+)",  # feature/026-name
            r"^feat/(\d{3}-[\w-]+)",  # feat/026-name
        ]

        for pattern in patterns:
            match = re.match(pattern, branch)
            if match:
                return match.group(1)

        return None

    def load_current_spec(self, max_tokens: int | None = None) -> ContextSource | None:
        """Load `specs/<feature>/spec.md` for the current branch."""
        max_tokens = max_tokens or self.config.max_tokens_per_source

        branch = self.get_current_branch()
        if not branch:
            self._log_debug("Not in a git repository or git unavailable")
            return None

        feature_name = self.extract_feature_name(branch)
        if not feature_name:
            self._log_debug(f"Branch '{branch}' does not match feature pattern")
            return None

        spec_path = self.project_root / "specs" / feature_name / "spec.md"
        if not spec_path.exists():
            self._log_debug(f"Spec not found at {spec_path}")
            return None

        content = self._read_file(spec_path)
        if content is None:
            return None

        truncated_content, was_truncated, original_tokens = truncate_content(
            content, max_tokens, spec_path
        )
        token_count = estimate_tokens(truncated_content)

        self._log_debug(f"Loaded current_spec ({feature_name}): {token_count} tokens")

        return ContextSource(
            source_type="current_spec",
            path=spec_path,
            content=truncated_content,
            token_count=token_count,
            truncated=was_truncated,
            original_tokens=original_tokens if was_truncated else None,
        )

    def get_memory_files(self) -> list[Path]:
        """Return paths to governance memory files that exist."""
        memory_dir = self.project_root / ".doit" / "memory"
        files = []

        governance_files = [
            "constitution.md",
            "tech-stack.md",
            "personas.md",
            "roadmap.md",
            "completed_roadmap.md",
        ]

        for filename in governance_files:
            path = memory_dir / filename
            if path.exists():
                files.append(path)

        return files

    def get_spec_files(self) -> list[Path]:
        """Return all `specs/*/spec.md` paths that exist, sorted."""
        specs_dir = self.project_root / "specs"
        files: list[Path] = []

        if not specs_dir.exists():
            return files

        for spec_dir in specs_dir.iterdir():
            if not spec_dir.is_dir():
                continue
            spec_path = spec_dir / "spec.md"
            if spec_path.exists():
                files.append(spec_path)

        return sorted(files)

    def get_all_searchable_files(self) -> list[Path]:
        """Return the union of memory files and spec files."""
        return self.get_memory_files() + self.get_spec_files()

    def find_related_specs(
        self,
        max_count: int = 3,
        max_tokens_per_spec: int | None = None,
        similarity_threshold: float = 0.3,
    ) -> list[ContextSource]:
        """Find specs related to the current feature by similarity score."""
        max_tokens = max_tokens_per_spec or self.config.max_tokens_per_source

        current_spec = self.load_current_spec(max_tokens=max_tokens)
        if not current_spec:
            return []

        current_feature = self.extract_feature_name(self.get_current_branch() or "")
        if not current_feature:
            return []

        specs_dir = self.project_root / "specs"
        if not specs_dir.exists():
            return []

        candidate_specs: list[tuple[Path, str]] = []
        for spec_dir in specs_dir.iterdir():
            if not spec_dir.is_dir():
                continue
            if spec_dir.name == current_feature:
                continue  # Skip current spec

            spec_path = spec_dir / "spec.md"
            if spec_path.exists():
                content = self._read_file(spec_path)
                if content:
                    candidate_specs.append((spec_path, content[:1000]))

        if not candidate_specs:
            return []

        candidate_texts = [text for _, text in candidate_specs]
        scores = compute_similarity_scores(current_spec.content[:1000], candidate_texts)

        scored_specs = [
            (score, path, text)
            for score, (path, text) in zip(scores, candidate_specs, strict=False)
            if score >= similarity_threshold
        ]
        scored_specs.sort(key=lambda x: x[0], reverse=True)

        related: list[ContextSource] = []
        for score, path, _ in scored_specs[:max_count]:
            content = self._read_file(path)
            if content is None:
                continue

            truncated_content, was_truncated, original_tokens = truncate_content(
                content, max_tokens, path
            )
            token_count = estimate_tokens(truncated_content)

            self._log_debug(
                f"Loaded related_spec ({path.parent.name}): "
                f"{token_count} tokens (similarity: {score:.2f})"
            )

            related.append(
                ContextSource(
                    source_type="related_specs",
                    path=path,
                    content=truncated_content,
                    token_count=token_count,
                    truncated=was_truncated,
                    original_tokens=original_tokens if was_truncated else None,
                )
            )

        return related
