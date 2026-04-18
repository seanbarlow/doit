"""Per-target copier package for bundled doit templates.

The monolithic `TemplateManager` had a handful of `copy_X` methods that
each encapsulated a different "where does this go on disk" policy. This
package pulls the most complex one out — command-template copying, with
its Copilot transform branch — into a small focused class so:

- The same logic can be reused by `SkillWriter` (`.claude/skills/`)
  without dragging the whole TemplateManager along.
- The validator/copilot-instructions/simple-list copies in
  TemplateManager aren't coupled to the command-copy path.

Further copiers (workflow/memory/config/hooks/scripts/github-issues) can
be extracted later if needed. For now those are simple flat-list copies
and stay inside TemplateManager itself.
"""

from __future__ import annotations

from .command_copier import CommandCopier, CopyResult
from .safe_copy import safe_copy

__all__ = ["CommandCopier", "CopyResult", "safe_copy"]
