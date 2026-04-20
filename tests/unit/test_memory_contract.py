"""Unit tests for the .doit/memory contract models."""

from __future__ import annotations

import textwrap

from doit_cli.models.memory_contract import (
    ConstitutionFrontmatter,
    MemoryIssueSeverity,
    OpenQuestion,
    split_frontmatter,
)


def valid_frontmatter_dict() -> dict:
    """Return a dict representing a well-formed constitution frontmatter."""

    return {
        "id": "app-example",
        "name": "Example App",
        "kind": "application",
        "phase": 2,
        "icon": "EX",
        "tagline": "An example app used only for unit tests.",
        "competitor": None,
        "dependencies": ["platform-identity-service"],
        "consumers": None,
    }


class TestConstitutionFrontmatter:
    """Tests for :class:`ConstitutionFrontmatter`."""

    def test_from_dict_roundtrip(self):
        fm = ConstitutionFrontmatter.from_dict(valid_frontmatter_dict())
        assert fm.id == "app-example"
        assert fm.kind == "application"
        assert fm.phase == 2
        assert fm.icon == "EX"
        assert fm.dependencies == ["platform-identity-service"]

    def test_validate_happy_path_returns_no_issues(self):
        fm = ConstitutionFrontmatter.from_dict(valid_frontmatter_dict())
        assert fm.validate() == []

    def test_validate_rejects_bad_id_pattern(self):
        data = valid_frontmatter_dict()
        data["id"] = "something-weird"
        fm = ConstitutionFrontmatter.from_dict(data)
        issues = fm.validate()
        assert len(issues) == 1
        assert issues[0].severity is MemoryIssueSeverity.ERROR
        assert issues[0].field_name == "id"
        assert "(app|platform)-" in issues[0].message

    def test_validate_rejects_invalid_kind(self):
        data = valid_frontmatter_dict()
        data["kind"] = "widget"
        fm = ConstitutionFrontmatter.from_dict(data)
        issues = fm.validate()
        assert any(i.field_name == "kind" for i in issues)

    def test_validate_rejects_out_of_range_phase(self):
        data = valid_frontmatter_dict()
        data["phase"] = 7
        fm = ConstitutionFrontmatter.from_dict(data)
        issues = fm.validate()
        assert any(i.field_name == "phase" for i in issues)

    def test_validate_rejects_non_uppercase_icon(self):
        data = valid_frontmatter_dict()
        data["icon"] = "ex"
        fm = ConstitutionFrontmatter.from_dict(data)
        issues = fm.validate()
        assert any(i.field_name == "icon" for i in issues)

    def test_validate_missing_required_fields_lists_them_all(self):
        fm = ConstitutionFrontmatter.from_dict({})
        issues = fm.validate()
        fields = {i.field_name for i in issues}
        # Every required field except dependencies (which defaults to [] and
        # is valid-but-empty) should report an issue.
        assert {"id", "name", "kind", "phase", "icon", "tagline"} <= fields

    def test_competitor_and_consumers_accept_null(self):
        data = valid_frontmatter_dict()
        data["competitor"] = None
        data["consumers"] = None
        assert ConstitutionFrontmatter.from_dict(data).validate() == []

    def test_status_field_is_preserved(self):
        data = valid_frontmatter_dict()
        data["status"] = "Draft — placeholder content"
        fm = ConstitutionFrontmatter.from_dict(data)
        assert fm.status == "Draft — placeholder content"
        assert fm.validate() == []


class TestOpenQuestion:
    """Tests for :class:`OpenQuestion.normalise`."""

    def test_happy_path_preserves_priority_casing(self):
        q, issue = OpenQuestion.normalise("high", "Should we?", "Product")
        assert issue is None
        assert q is not None
        assert q.priority == "High"
        assert q.owner == "Product"

    def test_em_dash_owner_normalises_to_na(self):
        q, issue = OpenQuestion.normalise("Medium", "Pending?", "\u2014")
        assert issue is None
        assert q is not None
        assert q.owner == "N/A"

    def test_blank_owner_normalises_to_na(self):
        q, issue = OpenQuestion.normalise("Low", "?", "")
        assert issue is None
        assert q is not None
        assert q.owner == "N/A"

    def test_invalid_priority_returns_warning(self):
        q, issue = OpenQuestion.normalise("Urgent", "?", "Product")
        assert q is None
        assert issue is not None
        assert issue.severity is MemoryIssueSeverity.WARNING
        assert "Urgent" in issue.message


class TestSplitFrontmatter:
    """Tests for :func:`split_frontmatter`."""

    def test_parses_frontmatter_and_returns_body(self):
        source = textwrap.dedent(
            """\
            ---
            id: app-demo
            name: Demo
            ---

            # Demo
            Hello.
            """
        )
        data, body, _ = split_frontmatter(source)
        assert data == {"id": "app-demo", "name": "Demo"}
        assert body.startswith("\n# Demo")

    def test_returns_empty_when_no_frontmatter(self):
        source = "# Demo\nHello.\n"
        data, body, line = split_frontmatter(source)
        assert data == {}
        assert body == source
        assert line == 1

    def test_ignores_malformed_yaml(self):
        source = "---\nnot: [valid yaml\n---\n# Demo\n"
        data, body, _ = split_frontmatter(source)
        assert data == {}
        assert "# Demo" in body

    def test_body_start_line_reports_correct_offset(self):
        source = textwrap.dedent(
            """\
            ---
            id: app-demo
            name: Demo
            ---

            # Demo
            """
        )
        _, _, line = split_frontmatter(source)
        # "---\nid:\nname:\n---\n" = 4 lines; body starts on line 5.
        assert line == 5
