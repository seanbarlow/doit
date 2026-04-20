"""Deterministic enrichment of placeholder constitution frontmatter.

After :mod:`doit_cli.services.constitution_migrator` has prepended or
patched a placeholder skeleton to ``.doit/memory/constitution.md``, the
:func:`enrich_constitution` function here replaces those placeholder
values with concrete values inferred from the constitution body and
project context. No LLM is involved — the inference rules are pure
string parsing against the ``PLACEHOLDER_REGISTRY`` tokens.

This lives in the CLI so the ``/doit.constitution`` skill can invoke it
as a deterministic first pass via ``doit constitution enrich`` and then,
if anything remains unresolved, the skill can follow up with its own
LLM-driven inference.

Public surface:

- :class:`EnrichmentAction` — enum of enrichment outcomes.
- :class:`EnrichmentResult` — report returned by :func:`enrich_constitution`.
- :func:`enrich_constitution` — one-function public API.

Body preservation guarantee: every byte after the closing ``---\\n`` of
the frontmatter is byte-identical before and after. Only the YAML block
changes.
"""

from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any

from ..errors import DoitError
from ..models.memory_contract import (
    ICON_PATTERN,
    ID_PATTERN,
    REQUIRED_FRONTMATTER_FIELDS,
    is_placeholder_value,
)
from ..utils.atomic_write import write_text_atomic

__all__ = (
    "EnrichmentAction",
    "EnrichmentResult",
    "enrich_constitution",
)


# Fallback tagline when the body has nothing usable; explicitly left as a
# placeholder equivalent so the validator still warns.
_TAGLINE_CAP = 140

# Word boundary tokens we look at when inferring `kind`.
_SERVICE_KEYWORDS = (
    "service",
    "microservice",
    "library",
    "sdk",
    "api gateway",
    "api layer",
    "queue",
    "broker",
    "platform component",
)


_FRONTMATTER_RE = re.compile(r"^---\n(.*?\n)---\n", re.DOTALL)
_CONSTITUTION_HEADING_RE = re.compile(
    r"^#\s+(?P<name>.+?)\s+Constitution\s*$",
    re.MULTILINE,
)
_H1_HEADING_RE = re.compile(r"^#\s+(?P<name>.+?)\s*$", re.MULTILINE)
_PROJECT_PURPOSE_SECTION_RE = re.compile(
    r"###\s+Project Purpose\s*\n+(?P<body>.*?)(?=\n#{1,3}\s|\Z)",
    re.DOTALL,
)
_PURPOSE_GOALS_SECTION_RE = re.compile(
    r"##\s+Purpose\s*(?:&|and)\s*Goals\s*\n+(?P<body>.*?)(?=\n##\s|\Z)",
    re.DOTALL,
)
_COMPONENT_ID_RE = re.compile(r"\b((?:app|platform)-[a-z][a-z0-9-]+)\b")
_SLUG_RE = re.compile(r"[^a-z0-9]+")


class EnrichmentAction(str, Enum):
    """Outcome categories for :func:`enrich_constitution`."""

    NO_OP = "no_op"
    """File does not exist, has no frontmatter, or has no placeholder values."""

    ENRICHED = "enriched"
    """At least one placeholder field was replaced with an inferred value."""

    PARTIAL = "partial"
    """Some placeholders were enriched; others had insufficient context
    and remain as placeholders."""

    ERROR = "error"
    """File could not be read/parsed."""


@dataclass(frozen=True)
class EnrichmentResult:
    """Report returned by :func:`enrich_constitution`."""

    path: Path
    action: EnrichmentAction
    enriched_fields: tuple[str, ...] = ()
    """Fields whose placeholder value was replaced with a concrete value."""

    unresolved_fields: tuple[str, ...] = ()
    """Fields still containing a placeholder (low-confidence inference)."""

    preserved_body_hash: bytes | None = None
    """SHA-256 of the body bytes; unchanged for NO_OP / ENRICHED / PARTIAL."""

    error: DoitError | None = None


# ---------------------------------------------------------------------------
# Internal helpers


def _body_hash(body: str) -> bytes:
    return hashlib.sha256(body.encode("utf-8")).digest()


def _slugify(text: str) -> str:
    """Return a kebab-case slug from ``text``.

    Returns an empty string when ``text`` contains no slug-able characters —
    callers use that to decide whether to skip an inference that requires a
    valid slug source.
    """

    lowered = text.strip().lower()
    slug = _SLUG_RE.sub("-", lowered).strip("-")
    return slug


def _initials(name: str) -> str:
    """Produce 2-4 uppercase initials from ``name``.

    - "Cloud Control" → "CC"
    - "Doit Toolkit CLI" → "DTC"
    - "API" → "API"
    - "My" → "MY" (pads single-initial names to length 2)
    """

    words = [w for w in re.split(r"[\s_-]+", name.strip()) if w]
    initials = "".join(w[0].upper() for w in words if w[0].isalpha())
    if not initials:
        return ""
    # If there are no spaces and all-caps already, use the word itself
    # capped at 4 chars (e.g. "API" → "API").
    if len(words) == 1 and words[0].isalpha() and words[0].isupper():
        return words[0][:4]
    if len(initials) == 1:
        # Pad to 2 by using first two chars of the single word.
        w = words[0]
        if len(w) >= 2 and w[1].isalnum():
            return (w[0] + w[1]).upper()
        return initials  # give up — validator will flag
    return initials[:4]


def _first_sentence(paragraph: str, *, cap: int = _TAGLINE_CAP) -> str:
    """Extract the first sentence from ``paragraph``, capped at ``cap`` chars."""

    text = paragraph.strip()
    # Consider the first non-empty paragraph (newlines separate paragraphs).
    for chunk in re.split(r"\n\s*\n", text, maxsplit=1):
        chunk = chunk.strip()
        if chunk:
            text = chunk
            break
    # Stop at first terminator (. ! ?) followed by space/end.
    match = re.search(r".+?[.!?](?=\s|$)", text, re.DOTALL)
    sentence = match.group(0) if match else text
    sentence = re.sub(r"\s+", " ", sentence).strip()
    if len(sentence) > cap:
        sentence = sentence[: cap - 1].rstrip() + "…"
    return sentence


def _parse_frontmatter(source: str) -> tuple[dict[str, Any] | None, str, bool, int]:
    """Return ``(parsed_or_None, body, has_block, frontmatter_end_pos)``.

    ``parsed_or_None`` is ``None`` for malformed YAML, ``{}`` when no block
    is present, else the loaded YAML dict. ``frontmatter_end_pos`` is the
    source offset of the first byte of the body (``0`` when no block).
    """

    match = _FRONTMATTER_RE.match(source)
    if not match:
        return {}, source, False, 0

    try:
        import yaml
    except ImportError:  # pragma: no cover - pyyaml is a base dep
        return {}, source, True, match.end()

    raw = match.group(1)
    try:
        data = yaml.safe_load(raw)
    except yaml.YAMLError:
        return None, source[match.end():], True, match.end()

    if data is None:
        data = {}
    if not isinstance(data, dict):
        return None, source[match.end():], True, match.end()

    return data, source[match.end():], True, match.end()


def _format_frontmatter(data: dict[str, Any]) -> str:
    try:
        import yaml
    except ImportError as e:  # pragma: no cover
        raise DoitError(
            "PyYAML is required to render constitution frontmatter"
        ) from e

    ordered: dict[str, Any] = {}
    for key in REQUIRED_FRONTMATTER_FIELDS:
        if key in data:
            ordered[key] = data[key]
    for key, value in data.items():
        if key not in ordered:
            ordered[key] = value

    rendered = yaml.safe_dump(
        ordered,
        sort_keys=False,
        default_flow_style=False,
        allow_unicode=True,
    )
    return f"---\n{rendered}---\n"


# ---------------------------------------------------------------------------
# Inference rules


def _infer_name(body: str, project_dir: str | None) -> str | None:
    """Return an inferred display name, or ``None`` if nothing matches."""

    match = _CONSTITUTION_HEADING_RE.search(body)
    if match:
        name = match.group("name").strip()
        if name:
            return name

    match = _H1_HEADING_RE.search(body)
    if match:
        name = match.group("name").strip()
        # Strip a trailing " Constitution" just in case.
        name = re.sub(r"\s+constitution\s*$", "", name, flags=re.IGNORECASE)
        if name:
            return name

    if project_dir:
        words = re.split(r"[\s_-]+", project_dir.strip())
        titled = " ".join(w.capitalize() for w in words if w)
        return titled or None

    return None


def _infer_tagline(body: str) -> str | None:
    """Return an inferred tagline (≤ 140 chars) or ``None``."""

    m = _PROJECT_PURPOSE_SECTION_RE.search(body)
    if m and m.group("body").strip():
        sentence = _first_sentence(m.group("body"))
        if sentence:
            return sentence

    m = _PURPOSE_GOALS_SECTION_RE.search(body)
    if m and m.group("body").strip():
        # Skip nested `### Project Purpose` heading text if it's there.
        candidate = re.sub(
            r"^###\s+Project Purpose\s*\n+",
            "",
            m.group("body").strip(),
            count=1,
        )
        sentence = _first_sentence(candidate)
        if sentence:
            return sentence

    return None


def _infer_kind(body: str) -> str:
    """Return ``"service"`` when the body reads like a service/library, else ``"application"``."""

    lower = body.lower()
    for keyword in _SERVICE_KEYWORDS:
        if keyword in lower:
            return "service"
    return "application"


def _infer_id(name: str | None, kind: str, project_dir: str | None) -> str | None:
    """Build an id matching ``ID_PATTERN`` from the most reliable slug source."""

    slug_source = project_dir or name
    if not slug_source:
        return None
    slug = _slugify(slug_source)
    if not slug or not slug[0].isalpha():
        return None
    prefix = "app" if kind == "application" else "platform"
    candidate = f"{prefix}-{slug}"
    return candidate if ID_PATTERN.match(candidate) else None


def _infer_icon(name: str | None) -> str | None:
    if not name:
        return None
    icon = _initials(name)
    if icon and ICON_PATTERN.match(icon):
        return icon
    return None


def _infer_phase() -> int:
    """Default to phase 1 (pre-spec/prototype) — conservative when we can't tell."""

    return 1


def _infer_dependencies(body: str, self_id: str | None) -> list[str]:
    """Return unique component ids referenced in the body, excluding ``self_id``."""

    seen: list[str] = []
    for match in _COMPONENT_ID_RE.finditer(body):
        dep = match.group(1)
        if dep == self_id:
            continue
        if dep not in seen:
            seen.append(dep)
    return seen


# ---------------------------------------------------------------------------
# Public API


def enrich_constitution(
    path: Path, *, project_dir: str | None = None
) -> EnrichmentResult:
    """Replace placeholder frontmatter values with inferred real values.

    Args:
        path: Path to ``.doit/memory/constitution.md``.
        project_dir: Directory name (basename) of the project root.
            Used as a slug source when inferring ``id`` / fallback
            ``name``. Defaults to ``path.resolve().parents[2].name``
            (``.../<project>/.doit/memory/constitution.md``).

    Returns:
        :class:`EnrichmentResult` describing which fields were replaced
        and which remain as placeholders (low confidence).

    The function never raises — errors are captured in
    :attr:`EnrichmentResult.error`.
    """

    path = Path(path)

    if not path.exists():
        return EnrichmentResult(path=path, action=EnrichmentAction.NO_OP)

    if project_dir is None:
        try:
            project_dir = path.resolve().parents[2].name
        except IndexError:  # pragma: no cover - path too shallow
            project_dir = None

    try:
        original = path.read_text(encoding="utf-8")
    except OSError as e:
        return EnrichmentResult(
            path=path,
            action=EnrichmentAction.ERROR,
            error=DoitError(f"Could not read {path}: {e}"),
        )

    parsed, body, has_block, _ = _parse_frontmatter(original)
    if parsed is None or not has_block:
        return EnrichmentResult(
            path=path,
            action=EnrichmentAction.NO_OP,
            preserved_body_hash=_body_hash(body),
        )

    # Find every placeholder field — these are the enrichment candidates.
    placeholder_fields = [
        k for k in REQUIRED_FRONTMATTER_FIELDS if is_placeholder_value(k, parsed.get(k))
    ]
    if not placeholder_fields:
        return EnrichmentResult(
            path=path,
            action=EnrichmentAction.NO_OP,
            preserved_body_hash=_body_hash(body),
        )

    def _resolved_non_placeholder(field_name: str) -> Any:
        """Return the non-placeholder existing value for ``field_name``,
        or ``None`` when the value is absent or still a placeholder.

        This prevents derived-field inference (``id``, ``icon``) from
        seeding their slug/initial source with the literal placeholder
        string when the name/kind field hasn't been enriched yet.
        """

        if field_name in placeholder_fields:
            return None  # enrichment will decide
        existing = parsed.get(field_name)
        if is_placeholder_value(field_name, existing):
            return None
        return existing

    # Pre-compute name/kind first — id/icon derive from them.
    inferred_name: str | None = (
        _infer_name(body, project_dir) if "name" in placeholder_fields else None
    )
    inferred_kind: str | None = (
        _infer_kind(body) if "kind" in placeholder_fields else None
    )

    name_for_derived: str | None = (
        inferred_name if inferred_name is not None else _resolved_non_placeholder("name")
    )
    kind_for_derived: str = (
        inferred_kind
        if inferred_kind is not None
        else (_resolved_non_placeholder("kind") or "application")
    )

    enriched: dict[str, Any] = dict(parsed)
    enriched_keys: list[str] = []
    unresolved: list[str] = []

    for field in placeholder_fields:
        inferred: Any = None
        if field == "name":
            inferred = inferred_name
        elif field == "tagline":
            inferred = _infer_tagline(body)
        elif field == "kind":
            inferred = inferred_kind
        elif field == "phase":
            inferred = _infer_phase()
        elif field == "id":
            # Only infer an id when we have a real slug source — either
            # a non-placeholder name or a non-empty project_dir.
            if name_for_derived or project_dir:
                inferred = _infer_id(name_for_derived, kind_for_derived, project_dir)
        elif field == "icon":
            if name_for_derived:
                inferred = _infer_icon(name_for_derived)
        elif field == "dependencies":
            # Empty list is a valid resolution (no dependencies mentioned).
            inferred = _infer_dependencies(body, _resolved_non_placeholder("id"))

        if inferred is None or (isinstance(inferred, str) and not inferred.strip()):
            unresolved.append(field)
            continue

        enriched[field] = inferred
        enriched_keys.append(field)

    if not enriched_keys:
        return EnrichmentResult(
            path=path,
            action=EnrichmentAction.NO_OP,
            unresolved_fields=tuple(unresolved),
            preserved_body_hash=_body_hash(body),
        )

    new_frontmatter = _format_frontmatter(enriched)
    new_content = new_frontmatter + body

    try:
        write_text_atomic(path, new_content)
    except OSError as e:
        return EnrichmentResult(
            path=path,
            action=EnrichmentAction.ERROR,
            error=DoitError(f"Could not write {path}: {e}"),
        )

    action = (
        EnrichmentAction.PARTIAL if unresolved else EnrichmentAction.ENRICHED
    )
    return EnrichmentResult(
        path=path,
        action=action,
        enriched_fields=tuple(enriched_keys),
        unresolved_fields=tuple(unresolved),
        preserved_body_hash=_body_hash(body),
    )
