from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from autotable.storage_model import PullRequestData

APPNAME = "autotable"

CONSOLE_SUCCESSFUL = "✓"
CONSOLE_ERROR = "✗"
CONSOLE_WARNING = "⚠"

CONFIG_FILE_NAME = f"{APPNAME}.toml"


# processor/github_prs cache
_REPO_FULL_NAME = str
global_error_prs: dict[_REPO_FULL_NAME, set[PullRequestData]] = {}
global_pr_title_index_cache: dict[_REPO_FULL_NAME, dict[int, list[str]]] = {}
global_request_pull_list_cache: dict[_REPO_FULL_NAME, list[PullRequestData]] = {}
global_table_index_set: set[str] = set()
