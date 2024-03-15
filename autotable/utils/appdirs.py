from __future__ import annotations

from appdirs import user_data_dir, user_log_dir

from autotable.constant import APPAUTHOR, APPNAME


def log_dir():
    return user_log_dir(APPNAME, APPAUTHOR)


def data_dir():
    return user_data_dir(APPNAME, APPAUTHOR)
