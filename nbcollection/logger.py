"""Custom logger for nbcollection."""

# Standard library
import logging

__all__ = ["logger"]


class CustomHandler(logging.StreamHandler):
    """A custom handler that prepends the logger name to the message."""

    def emit(self, record):
        """Emit a formatted log record."""
        record.msg = f"[nbcollection ({record.levelname})]: {record.msg}"
        super().emit(record)


class CustomLogger(logging.getLoggerClass()):
    """A custom logger that sets up the custom handler."""

    def _set_defaults(self):
        """Reset logger to its initial state"""
        # Remove all previous handlers
        for handler in self.handlers[:]:
            self.removeHandler(handler)

        # Set default level
        self.setLevel(logging.INFO)

        # Set up the stdout handler
        sh = CustomHandler()
        self.addHandler(sh)


logging.setLoggerClass(CustomLogger)
logger = logging.getLogger("nbcollection")
logger._set_defaults()
