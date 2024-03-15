from __future__ import annotations

import platform

APPNAME = "autotable"
APPAUTHOR = "gouzil"
if platform.system() == "Windows":
    CONSOLE_SUCCESSFUL = "√"
    CONSOLE_ERROR = "X"
else:
    CONSOLE_SUCCESSFUL = "✓"
    CONSOLE_ERROR = "✗"
