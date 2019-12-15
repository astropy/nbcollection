# Standard library
import logging

__all__ = ['logger']


class CustomHandler(logging.StreamHandler):
    def emit(self, record):
        record.msg = f'[nbstatic ({record.levelname})]: {record.msg}'
        super().emit(record)


class CustomLogger(logging.getLoggerClass()):
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
logger = logging.getLogger('nbstatic')
logger._set_defaults()
