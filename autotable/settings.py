from __future__ import annotations

import sys
from pathlib import Path
from typing import Annotated, Any, Literal, Optional

from loguru import logger
from pydantic import BaseModel, Field

from autotable.constant import CONFIG_FILE_NAME
from autotable.utils.appdirs import config_dir

if sys.version_info >= (3, 11):
    import tomllib
else:
    import tomli as tomllib

LOG_LITERALS_T = Literal["TRACE", "DEBUG", "INFO", "SUCCESS", "WARNING", "ERROR", "CRITICAL"]


class RepoSettings(BaseModel):
    issue_id: Annotated[Optional[int], Field(None)]  # noqa: UP007
    token: Annotated[Optional[str], Field(None)]  # noqa: UP007
    log_level: Annotated[Optional[LOG_LITERALS_T], Field("INFO")]  # noqa: UP007


class AutoTableSettings(BaseModel):
    """
    AutoTableSettings is a class that contains settings for the AutoTable application.
    It includes the token, log level, and repository settings.
    The repository settings are a dictionary where the keys are the owner/repo names
    and the values are RepoSettings objects.
    """

    token: Annotated[Optional[str], Field(None)]  # noqa: UP007
    log_level: Annotated[LOG_LITERALS_T, Field("INFO")]
    repo_settings: Annotated[dict[str, RepoSettings], Field({})]


def search_for_settings_file() -> Path | None:
    settings_file = Path(CONFIG_FILE_NAME)
    if not settings_file.exists():
        settings_file = Path(config_dir()) / CONFIG_FILE_NAME
    if not settings_file.exists():
        return None
    return settings_file


def load_settings_file(settings_file: Path) -> AutoTableSettings:
    """
    Load settings from a TOML file.
    """
    with settings_file.open("r", encoding="utf-8") as f:
        settings_raw = tomllib.loads(f.read())

    # Convert the raw settings to a AutoTableSettings object
    settings_obj = AutoTableSettings(
        token=settings_raw.get("token", None),
        log_level=settings_raw.get("log_level", "INFO"),
        repo_settings={},
    )

    # 处理 common
    common_setting = settings_raw.get("common", None)
    if common_setting:
        settings_obj.token = common_setting.get("token", settings_obj.token)
        settings_obj.log_level = common_setting.get("log_level", settings_obj.log_level)

    # 处理 repo_settings
    for org, repos in settings_raw.get("repo_settings", {}).items():
        assert isinstance(repos, dict), f"repo_settings must be a dict, got {type(repos)}"
        # 处理 repo_settings
        for repo, issues_settings in repos.items():
            assert isinstance(issues_settings, dict), f"repo_settings must be a dict, got {type(issues_settings)}"
            # 处理 issues_settings
            for issue_id, issue_setting in issues_settings.items():
                assert isinstance(issue_setting, dict), f"repo_settings must be a dict, got {type(issue_setting)}"
                assert issue_id.isdigit(), f"issue_id must be a int, got {issue_id}"
                settings_obj.repo_settings[f"{org}/{repo}/{issue_id}"] = RepoSettings(
                    issue_id=int(issue_id),
                    token=issue_setting.get("token", settings_obj.token),
                    log_level=issue_setting.get("log_level", settings_obj.log_level),
                )

    return settings_obj


def select_setting(setting: AutoTableSettings | None, setting_key: str, key: str, default: Any) -> Any:
    """
    选择设置
    顺序是: 用户arg -> 配置文件
    """
    if setting is None or default is not None:
        return default

    return getattr(setting.repo_settings[setting_key], key)


def init_setting(file_path: str | None = None, enable_log: bool = True) -> AutoTableSettings | None:
    """
    初始化配置
    """
    setting: None | AutoTableSettings = None
    if file_path is not None:
        # 直接使用用户指定的配置文件
        file = Path(file_path)
        assert file.exists(), f"file_path {file_path} not exists"
        if enable_log:
            logger.info("发现配置文件: {}", file_path)
        setting = load_settings_file(file)
    elif config_file := search_for_settings_file():
        # 使用默认配置文件
        if enable_log:
            logger.info("发现配置文件: {}", config_file.absolute())
        setting = load_settings_file(config_file)

    return setting
