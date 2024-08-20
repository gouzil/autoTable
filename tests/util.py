from __future__ import annotations

import io
import logging


# copy for https://github.com/Delgan/loguru/issues/616#issue-1168421879
class CaptureLogger:
    """Context manager to capture log streams

    Args:
        logger: logger object

    Results:
        The captured output is available via `self.out`

    """

    def __init__(self, logger):
        self.logger = logger
        self.io = io.StringIO()
        self.sh = logging.StreamHandler(self.io)
        self.out = ""

    def __enter__(self):
        try:
            # try standard logging
            self.logger.add(self.sh)
        except AttributeError:
            # try loguru logging
            self.logger.add(self.sh)
        return self

    def __exit__(self, *exc):
        try:
            # try standard logging
            self.logger.removeHandler(self.sh)
        except AttributeError:
            # try loguru
            self.logger.remove()

        self.out = self.io.getvalue()

    def __repr__(self):
        return f"captured: {self.out}\n"
