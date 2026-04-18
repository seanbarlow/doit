"""Tests for the shared DoitError hierarchy."""

from __future__ import annotations

import pytest

from doit_cli.errors import (
    DoitAuthError,
    DoitConfigError,
    DoitError,
    DoitProviderError,
    DoitStateError,
    DoitTemplateError,
    DoitValidationError,
)


class TestDoitErrorHierarchy:
    """The hierarchy must let callers catch by category."""

    def test_all_subclass_doit_error(self):
        for subclass in (
            DoitConfigError,
            DoitStateError,
            DoitTemplateError,
            DoitProviderError,
            DoitAuthError,
            DoitValidationError,
        ):
            assert issubclass(subclass, DoitError)

    def test_auth_error_is_provider_error(self):
        assert issubclass(DoitAuthError, DoitProviderError)

    def test_catching_base_catches_subclass(self):
        with pytest.raises(DoitError):
            raise DoitConfigError("missing field")

    def test_catching_provider_catches_auth(self):
        with pytest.raises(DoitProviderError):
            raise DoitAuthError("token expired")

    def test_carries_message(self):
        err = DoitValidationError("bad input")
        assert str(err) == "bad input"
