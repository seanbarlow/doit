"""Tests for the canonical ExitCode enum."""

from __future__ import annotations

from doit_cli.exit_codes import ExitCode


class TestExitCode:
    """The enum doubles as an int so `typer.Exit(code=ExitCode.X)` works."""

    def test_values_are_ints(self):
        for code in ExitCode:
            assert isinstance(code.value, int)

    def test_standard_codes_match_convention(self):
        assert ExitCode.SUCCESS == 0
        assert ExitCode.FAILURE == 1
        assert ExitCode.VALIDATION_ERROR == 2

    def test_user_cancel_matches_sigint_convention(self):
        # SIGINT exit = 128 + 2
        assert ExitCode.USER_CANCEL == 130

    def test_all_codes_unique(self):
        values = [code.value for code in ExitCode]
        assert len(values) == len(set(values))

    def test_intenum_arithmetic(self):
        # ExitCode must work in arithmetic / comparison contexts
        assert ExitCode.SUCCESS < ExitCode.FAILURE
        assert int(ExitCode.VALIDATION_ERROR) + 1 == int(ExitCode.PROVIDER_ERROR)
