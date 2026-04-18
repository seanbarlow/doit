"""Tests for the shared --format option helper."""

from __future__ import annotations

import pytest
import typer

from doit_cli.cli.output import OutputFormat, format_option, resolve_format


class TestOutputFormat:
    """Basic enum hygiene."""

    def test_enum_values_are_lowercase_strings(self):
        for fmt in OutputFormat:
            assert fmt.value == fmt.value.lower()

    def test_all_expected_formats_present(self):
        names = {f.name for f in OutputFormat}
        assert names >= {"RICH", "JSON", "MARKDOWN", "TABLE", "YAML", "CSV"}


class TestFormatOption:
    """format_option returns a usable Typer Option."""

    def test_returns_typer_option(self):
        opt = format_option()
        assert isinstance(opt, typer.models.OptionInfo)

    def test_default_is_rich(self):
        opt = format_option()
        assert opt.default == OutputFormat.RICH.value

    def test_override_default(self):
        opt = format_option(default=OutputFormat.JSON)
        assert opt.default == OutputFormat.JSON.value


class TestResolveFormat:
    """resolve_format validates input against a command's allowed set."""

    ALLOWED = (OutputFormat.RICH, OutputFormat.JSON)

    def test_accepts_allowed_value(self):
        assert resolve_format("rich", self.ALLOWED) is OutputFormat.RICH
        assert resolve_format("json", self.ALLOWED) is OutputFormat.JSON

    def test_case_insensitive(self):
        assert resolve_format("Rich", self.ALLOWED) is OutputFormat.RICH
        assert resolve_format("JSON", self.ALLOWED) is OutputFormat.JSON

    def test_rejects_unknown_value(self):
        with pytest.raises(typer.BadParameter) as exc_info:
            resolve_format("xml", self.ALLOWED)
        assert "xml" in str(exc_info.value)
        assert "rich" in str(exc_info.value)  # mentions accepted list

    def test_rejects_valid_but_unsupported_value(self):
        # yaml is a valid OutputFormat but this command doesn't allow it
        with pytest.raises(typer.BadParameter) as exc_info:
            resolve_format("yaml", self.ALLOWED)
        assert "yaml" in str(exc_info.value)
        assert "not supported" in str(exc_info.value).lower()
