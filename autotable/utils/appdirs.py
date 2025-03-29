from __future__ import annotations

from appdirs import user_config_dir, user_data_dir, user_log_dir

from autotable.constant import APPNAME


def log_dir():
    return user_log_dir(appname=APPNAME)


def data_dir():
    return user_data_dir(appname=APPNAME)


def config_dir():
    return user_config_dir(appname=APPNAME)
