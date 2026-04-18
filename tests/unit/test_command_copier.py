"""Tests for the extracted CommandCopier and safe_copy utility."""

from __future__ import annotations

from pathlib import Path

import pytest

from doit_cli.models.agent import Agent
from doit_cli.services.templates import CommandCopier, CopyResult, safe_copy


@pytest.fixture
def source_dir(tmp_path: Path) -> Path:
    """Create a source dir with a couple of minimal command templates."""
    src = tmp_path / "commands"
    src.mkdir()
    (src / "doit.alpha.md").write_text(
        "---\ndescription: Alpha command\nallowed-tools: Read\n---\n\n# Alpha\n"
    )
    (src / "doit.beta.md").write_text(
        "---\ndescription: Beta command\nallowed-tools: Bash\n---\n\n# Beta\n"
    )
    (src / "not-a-command.txt").write_text("ignored\n")
    return src


class TestCommandCopier:
    def test_read_templates_returns_md_files_only(self, source_dir: Path) -> None:
        copier = CommandCopier(source_dir)
        templates = copier.read_templates()
        names = {t.name for t in templates}
        assert names == {"alpha", "beta"}

    def test_read_templates_skips_missing_dir(self, tmp_path: Path) -> None:
        copier = CommandCopier(tmp_path / "does-not-exist")
        assert copier.read_templates() == []

    def test_copy_for_claude_is_verbatim(self, source_dir: Path, tmp_path: Path) -> None:
        target = tmp_path / "commands_out"
        target.mkdir()

        result = CommandCopier(source_dir).copy_for_agent(Agent.CLAUDE, target)

        assert isinstance(result, CopyResult)
        assert len(result.created) == 2
        alpha = target / "doit.alpha.md"
        assert alpha.read_text().startswith("---")
        assert "allowed-tools: Read" in alpha.read_text()

    def test_copy_for_copilot_applies_transform(
        self, source_dir: Path, tmp_path: Path
    ) -> None:
        """Copilot path must route through PromptTransformer.transform.

        The exact output shape depends on the transformer revision that's
        live on this branch (strip-and-title pre-Phase-6, native Copilot
        frontmatter post-Phase-6). We only check that the file name and
        content both differ from a straight copy.
        """
        target = tmp_path / "prompts_out"
        target.mkdir()

        result = CommandCopier(source_dir).copy_for_agent(Agent.COPILOT, target)

        assert len(result.created) == 2
        prompt = target / "doit.alpha.prompt.md"
        assert prompt.exists()
        content = prompt.read_text()
        # Source has these; transformed output drops one of them depending
        # on which transformer revision is live. Either way, the Claude
        # allowed-tools form must not appear verbatim before the body.
        source_content = (source_dir / "doit.alpha.md").read_text()
        assert content != source_content

    def test_overwrite_false_skips_existing(
        self, source_dir: Path, tmp_path: Path
    ) -> None:
        target = tmp_path / "out"
        target.mkdir()
        (target / "doit.alpha.md").write_text("stale\n")

        result = CommandCopier(source_dir).copy_for_agent(
            Agent.CLAUDE, target, overwrite=False
        )

        assert any(p.name == "doit.alpha.md" for p in result.skipped)
        assert (target / "doit.alpha.md").read_text() == "stale\n"

    def test_overwrite_true_replaces_existing(
        self, source_dir: Path, tmp_path: Path
    ) -> None:
        target = tmp_path / "out"
        target.mkdir()
        (target / "doit.alpha.md").write_text("stale\n")

        result = CommandCopier(source_dir).copy_for_agent(
            Agent.CLAUDE, target, overwrite=True
        )

        assert any(p.name == "doit.alpha.md" for p in result.updated)
        assert "stale" not in (target / "doit.alpha.md").read_text()

    def test_result_as_dict_matches_legacy_shape(
        self, source_dir: Path, tmp_path: Path
    ) -> None:
        target = tmp_path / "out"
        target.mkdir()
        out = CommandCopier(source_dir).copy_for_agent(Agent.CLAUDE, target).as_dict()
        assert set(out.keys()) == {"created", "updated", "skipped"}


class TestSafeCopy:
    def test_returns_true_on_different_files(self, tmp_path: Path) -> None:
        src = tmp_path / "a.txt"
        dst = tmp_path / "b.txt"
        src.write_text("hello")
        assert safe_copy(src, dst) is True
        assert dst.read_text() == "hello"

    def test_returns_false_when_source_equals_target(self, tmp_path: Path) -> None:
        p = tmp_path / "same.txt"
        p.write_text("x")
        assert safe_copy(p, p) is False
