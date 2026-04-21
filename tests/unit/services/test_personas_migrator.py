"""Unit tests for :mod:`doit_cli.services.personas_migrator`."""

from __future__ import annotations

from doit_cli.services.personas_migrator import REQUIRED_PERSONAS_H2


def test_required_personas_h2_constant_is_two_h2s() -> None:
    """Spec 062 locks the required H2 set to exactly these two headings.

    The contract test in ``tests/contract/test_memory_files_migration_contract.py``
    enforces that ``_validate_personas`` uses the same set. This unit test
    guards the constant itself against accidental edits.
    """

    assert REQUIRED_PERSONAS_H2 == ("Persona Summary", "Detailed Profiles")
