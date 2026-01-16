"""Services for doit-cli project initialization and management."""

from .agent_detector import AgentDetector
from .backup_service import BackupService
from .context_loader import ContextLoader, estimate_tokens, truncate_content
from .scaffolder import Scaffolder
from .template_manager import TemplateManager
from .validator import Validator
from .spec_scanner import SpecScanner, NotADoitProjectError, SpecNotFoundError
from .status_reporter import StatusReporter

__all__ = [
    "AgentDetector",
    "BackupService",
    "ContextLoader",
    "Scaffolder",
    "TemplateManager",
    "Validator",
    "estimate_tokens",
    "truncate_content",
    "SpecScanner",
    "NotADoitProjectError",
    "SpecNotFoundError",
    "StatusReporter",
]
