from __future__ import annotations

import os
import re
from pathlib import Path

from mcp.server.fastmcp import FastMCP

from autotable.api import get_issues
from autotable.command import backup, init_issue_table, update_content
from autotable.settings import AutoTableSettings, init_setting, select_setting
from autotable.storage_model import TrackerIssuesData, reset_stats
from autotable.utils.fetcher import Fetcher

# Create an MCP server
mcp = FastMCP("mcp-server-autoTable")
config_path = os.getenv("CONFIG_PATH", None)
default_token = os.getenv("DEFAULT_TOKEN", None)

# 预编译正则表达式模式
GITHUB_URL_PATTERN = re.compile(r"(?:https://github\.com/)?([\w-]+/[\w-]+)(?:/.*)?")


def get_config() -> AutoTableSettings:
    if setting := init_setting(file_path=config_path, enable_log=False):
        return setting
    raise FileNotFoundError("not found config file")


@mcp.resource("config://app")
def get_config_resource() -> AutoTableSettings | str:
    """get autotable setting config"""
    return get_config()


@mcp.tool()
def get_config_tool() -> AutoTableSettings | str:
    """get autotable setting config"""
    return get_config()


@mcp.tool()
def get_config_path() -> str:
    """get user setting config path"""
    if config_path:
        return config_path
    raise FileNotFoundError("not found config path")


@mcp.tool()
def github_url_convert_owner_repo(url: str) -> str:
    """Convert GitHub URL to owner/repo format"""

    match = GITHUB_URL_PATTERN.search(url)

    if match:
        return match.group(1)
    raise ValueError("Invalid GitHub URL format")


@mcp.tool()
def init_issue_table_tool(input_file_path: str, output_file_path: str) -> str:
    """
    Initialize issue table, the file path must be a markdown file, and the content of the file must be a markdown table
    And save to the specified path

    :param input_file_path: user input need to parse file path
    :param output_file_path: The output path of the file after initialization
    :return: The path of the file after initialization
    """
    reset_stats()

    # 检查输入文件路径是否存在
    input_file = Path(input_file_path)
    match input_file:
        case _ if not input_file.exists():
            raise FileNotFoundError("file not exists")
        case _ if not input_file.is_file():
            raise ValueError("file is not a file")
        case _ if not input_file_path.endswith(".md"):
            raise ValueError("file is not a markdown file")

    output_file = Path(output_file_path)

    tracker_issues_data = TrackerIssuesData(
        "local",
        input_file.read_text(encoding="utf-8"),
        None,
        None,
        "",
    )

    new_issue = init_issue_table(tracker_issues_data)

    # 复写文件
    if output_file.exists():
        output_file.unlink()

    # 创建目录
    output_file.parent.mkdir(parents=True, exist_ok=True)

    # 创建新文件
    output_file.write_text(new_issue, encoding="utf-8")

    return f"file created: {output_file.resolve()}"


@mcp.tool()
def backup_issue(owner_repo: str, issue_id: int) -> str:
    """
    Backup issue content to file, the file path must be a markdown file, and the content of the file must be a markdown
    a conversation only one call is allowed

    :param owner_repo: user input need to parse file path
    :param issue_id: The issue ID to be backed up
    :return: The path of the file after initialization
    """
    setting = init_setting(file_path=config_path, enable_log=False)
    if default_token is None and setting is None:
        raise ValueError("Failed to initialize settings")

    owner_repo = github_url_convert_owner_repo(owner_repo)
    Fetcher.set_github(select_setting(setting, f"{owner_repo}/{issue_id}", "token", default_token))
    Fetcher.set_owner_repo(owner_repo)
    # 获取issue内容
    tracker_issues_data = get_issues(issue_id)
    path = backup(tracker_issues_data.issue_title, tracker_issues_data.issue_content)
    return f"Backup for issue {issue_id} saved to {path.resolve()}"


@mcp.tool()
def update_issue(owner_repo: str, issue_id: int, dry_run: bool, output_file_path: str, reset_table: bool = True) -> str:
    """
    Synchronize/update issue content, including updating table information, counting PR status,
    updating existing PR status, updating issue registration status,
    and updating issue completion status. A conversation only allows one call.

    :param owner_repo: Repository address
    :param issue_id: Issue ID
    :param dry_run: Dry run mode, this mode will not write to the remote issue but will generate an updated file
    :param output_file_path: File output path. if dry_run mode is used, you need to specify the file output path
    :param reset_table: Whether to reset the table, if true, the table will be re-initialized
    :return: Success or failure
    """
    reset_stats()

    # 检查如果是 dry_run 模式, output_file_path 不能为空
    if dry_run and output_file_path == "":
        raise ValueError("Dry run mode requires output file path")

    # 配置
    setting = init_setting(file_path=config_path, enable_log=False)
    if default_token is None and setting is None:
        raise ValueError("Failed to initialize settings")
    owner_repo = github_url_convert_owner_repo(owner_repo)
    Fetcher.set_github(select_setting(setting, f"{owner_repo}/{issue_id}", "token", default_token))
    Fetcher.set_owner_repo(owner_repo)

    # 更新
    tracker_issues_data = get_issues(issue_id)
    new_issue = update_content(
        tracker_issues_data,
        False,  # 这里不处理, 在外部处理这个 dry_run
        reset_table,
    )
    if not dry_run:
        # 备份
        backup(tracker_issues_data.issue_title, tracker_issues_data.issue_content)
        # 写入远程
        Fetcher.set_issue(issue_id, new_issue)
    else:
        assert output_file_path is not None
        # 检查输出路径是否存在
        output_file = Path(output_file_path)
        if output_file.exists():
            output_file.unlink()

        # 创建目录
        output_file.parent.mkdir(parents=True, exist_ok=True)

        # 创建新文件
        output_file.write_text(new_issue, encoding="utf-8")

    return "update issue success"


if __name__ == "__main__":
    mcp.run()
