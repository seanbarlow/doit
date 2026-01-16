"""Base formatter for status output."""

from abc import ABC, abstractmethod

from ..models.status_models import StatusReport


class StatusFormatter(ABC):
    """Abstract base class for status output formatters.

    Subclasses implement format() to produce output in different formats
    (rich terminal, JSON, markdown, etc.).
    """

    @abstractmethod
    def format(self, report: StatusReport, verbose: bool = False) -> str:
        """Format the status report for output.

        Args:
            report: The StatusReport to format.
            verbose: Include detailed validation errors.

        Returns:
            Formatted string representation.
        """
        pass

    def format_to_console(self, report: StatusReport, verbose: bool = False) -> None:
        """Format and print directly to console.

        Default implementation calls format() and prints.
        Subclasses may override for richer output (e.g., Rich tables).

        Args:
            report: The StatusReport to format.
            verbose: Include detailed validation errors.
        """
        print(self.format(report, verbose))
