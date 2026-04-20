"""Contract tests for the constitution-frontmatter migration registry.

These tests assert invariants that cross the boundary between the
migrator, the shipped JSON Schema, and the memory validator. If any of
them fail, the three layers have drifted and downstream tools
(platform-docs-site, ``verify-memory``, the ``/doit.constitution``
skill) will observe inconsistent behavior.
"""

from __future__ import annotations

import json
from pathlib import Path

from doit_cli.services.constitution_migrator import (
    PLACEHOLDER_REGISTRY,
    REQUIRED_FIELDS,
)

SCHEMA_PATH = (
    Path(__file__).resolve().parents[2]
    / "src"
    / "doit_cli"
    / "schemas"
    / "frontmatter.schema.json"
)


def _load_schema() -> dict:
    return json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))


def test_required_fields_match_schema_order() -> None:
    """REQUIRED_FIELDS is index-by-index identical to the schema's required array."""

    schema = _load_schema()
    assert tuple(schema["required"]) == REQUIRED_FIELDS, (
        "REQUIRED_FIELDS must mirror frontmatter.schema.json's required array "
        "in index order so migrated output matches downstream expectations."
    )


def test_placeholder_registry_covers_required_fields() -> None:
    """Every required field has exactly one placeholder; no extras."""

    assert set(PLACEHOLDER_REGISTRY.keys()) == set(REQUIRED_FIELDS), (
        "PLACEHOLDER_REGISTRY keys must equal REQUIRED_FIELDS as a set."
    )


def test_placeholder_registry_values_are_distinct_sentinels() -> None:
    """Each placeholder is an exact-match sentinel, distinct from the others.

    The migrator and validator detect placeholders with ``==``, so
    reusing the same token across fields would make detection
    ambiguous.
    """

    seen: list[object] = []
    for key, value in PLACEHOLDER_REGISTRY.items():
        # Lists are unhashable; compare by repr for duplicate detection.
        token_repr = repr(value)
        assert token_repr not in seen, (
            f"Placeholder for '{key}' collides with another field's placeholder."
        )
        seen.append(token_repr)


def test_placeholder_tokens_use_square_bracket_convention() -> None:
    """Scalar placeholders look like ``[PROJECT_XXX]`` so they stand out."""

    for key, value in PLACEHOLDER_REGISTRY.items():
        if key == "dependencies":
            # Handled by the list assertion below.
            continue
        assert isinstance(value, str), (
            f"Placeholder for '{key}' should be a string scalar, got {type(value)}."
        )
        assert value.startswith("[PROJECT_") and value.endswith("]"), (
            f"Placeholder for '{key}' ({value!r}) doesn't follow the "
            "[PROJECT_XXX] convention."
        )


def test_dependencies_placeholder_is_single_item_list() -> None:
    """The dependencies placeholder is a list so YAML parses it as an array."""

    deps = PLACEHOLDER_REGISTRY["dependencies"]
    assert isinstance(deps, list)
    assert len(deps) == 1
    assert deps[0] == "[PROJECT_DEPENDENCIES]"


def test_schema_additional_properties_is_false() -> None:
    """The schema must forbid extra fields so the migrator's preserve-verbatim
    behavior for unknown keys is surfaced by the validator (not silently
    accepted)."""

    schema = _load_schema()
    assert schema.get("additionalProperties") is False
