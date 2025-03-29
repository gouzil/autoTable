from __future__ import annotations

import shutil
from pathlib import Path

import typer
from loguru import logger
from rich.console import Console
from rich.highlighter import NullHighlighter
from rich.logging import RichHandler
from rich.style import Style

from autotable.api.issues import get_issues
from autotable.command import backup, init_issue_table, replacement_pr_url, update_content, update_stats
from autotable.constant import CONFIG_FILE_NAME, CONSOLE_ERROR, CONSOLE_SUCCESSFUL, CONSOLE_WARNING
from autotable.processor.file import save_file
from autotable.settings import init_setting, search_for_settings_file, select_setting
from autotable.storage_model.tracker_issues_data import TrackerIssuesData
from autotable.utils.appdirs import data_dir, log_dir
from autotable.utils.fetcher import Fetcher

app = typer.Typer()


def init_logger(log_level: str):
    r"""
    初始化日志
    """
    handler = RichHandler(console=Console(style=Style()), highlighter=NullHighlighter(), markup=True)
    logger.remove()
    logger.add(handler, format="{message}", level=log_level)
    logger.add(
        f"{log_dir()}/autotable.log",
        rotation="5MB",
        encoding="utf-8",
        enqueue=True,
        retention="10d",
    )


def init(
    owner_repo: str,
    issue_id: int,
    token: str | None,
    log_level: str | None,
    config_file: str | None = None,
) -> None:
    r"""
    初始化日志、github token、repo等信息
    """
    setting = init_setting(config_file)
    init_logger(select_setting(setting, f"{owner_repo}/{issue_id}", "log_level", log_level))
    Fetcher.set_github(select_setting(setting, f"{owner_repo}/{issue_id}", "token", token))
    Fetcher.set_owner_repo(owner_repo)


@app.command()
def init_issue(
    owner_repo: str = typer.Argument("", help="仓库地址"),
    token: str = typer.Option("", help="github token"),
    issue_id: int | None = typer.Option(None, "-i", "--issue-id", help="issue 编号"),
    file_path: str | None = typer.Option(None, "-f", "--file", help="需要初始化的文件路径"),
    log_level: str = typer.Option("INFO", help="日志等级: INFO, DEBUG"),
):
    """
    初始化 issue 任务表格, 暂不支持统计表格的初始化
    """
    assert issue_id is not None or file_path is not None
    init_logger(log_level)
    if issue_id is not None:
        assert owner_repo is not None
        Fetcher.set_github(token)
        Fetcher.set_owner_repo(owner_repo)
        tracker_issues_data = get_issues(issue_id)
    else:
        assert file_path is not None
        tracker_issues_data = TrackerIssuesData(
            "local", Path(file_path).read_text(encoding="utf-8"), None, None, owner_repo
        )
    new_issue = init_issue_table(tracker_issues_data)
    save_file(
        new_issue,
        f"{tracker_issues_data.issue_title}_init_issue.md",
        dry_run=True,
    )


@app.command()
def issue_update(
    owner_repo: str = typer.Argument(..., help="仓库地址"),
    issue_id: int = typer.Argument(..., help="issue 编号"),
    token: str = typer.Argument(..., help="github token"),
    overwrite_remote: bool = typer.Option(True, "-o", "--overwrite-remote", help="写入远程 issue"),
    dry_run: bool = typer.Option(False, help="试运行模式, 此模式将不会写入远程 issue, 但会生成更新后的文件"),
    reset_table: bool = typer.Option(
        True, help="重置表格数据, 次模式会删除表格内所有任务状态, 并重新统计. NOTE: 手动修改表格数据将会丢失"
    ),
    log_level: str = typer.Option("INFO", help="日志等级: INFO, DEBUG"),
    config_file: str | None = typer.Option(None, "-c", "--config", help="配置文件"),
):
    """
    更新 issue 内容
    """
    init(owner_repo, issue_id, token, log_level, config_file)
    # 获取issue内容
    tracker_issues_data = get_issues(issue_id)
    new_issue: str = update_content(
        tracker_issues_data,
        dry_run,
        reset_table,
    )
    if overwrite_remote and not dry_run:
        backup(tracker_issues_data.issue_title, tracker_issues_data.issue_content)
        Fetcher.set_issue(issue_id, new_issue)


@app.command()
def issue_update_stats(
    owner_repo: str = typer.Argument(..., help="仓库地址"),
    issue_id: int = typer.Argument(..., help="issue 编号"),
    token: str = typer.Argument(..., help="github token"),
    overwrite_remote: bool = typer.Option(True, "-o", "--overwrite-remote", help="写入远程 issue"),
    dry_run: bool = typer.Option(False, help="试运行模式, 此模式将不会写入远程 issue, 但会生成更新后的文件"),
    log_level: str = typer.Option("INFO", help="日志等级: INFO, DEBUG"),
    config_file: str | None = typer.Option(None, "-c", "--config", help="配置文件"),
):
    """
    仅更新 issue 任务统计
    """
    init(owner_repo, issue_id, token, log_level, config_file)
    tracker_issues_data = get_issues(issue_id)
    new_issue: str = update_stats(tracker_issues_data.issue_title, tracker_issues_data.issue_content, dry_run)
    if overwrite_remote and not dry_run:
        backup(tracker_issues_data.issue_title, tracker_issues_data.issue_content)
        Fetcher.set_issue(issue_id, new_issue)


@app.command()
def issue_backup(
    owner_repo: str = typer.Argument(..., help="仓库地址"),
    issue_id: int = typer.Argument(..., help="issue 编号"),
    token: str = typer.Argument(..., help="github token"),
    log_level: str = typer.Option("INFO", help="日志等级: INFO, DEBUG"),
    config_file: str | None = typer.Option(None, "-c", "--config", help="配置文件"),
):
    """
    备份 issue
    """
    init(owner_repo, issue_id, token, log_level, config_file)
    tracker_issues_data = get_issues(issue_id)
    backup(tracker_issues_data.issue_title, tracker_issues_data.issue_content)


@app.command()
def clean():
    """
    清理备份文件
    """
    if Path(data_dir()).exists():
        shutil.rmtree(data_dir())
    if Path(log_dir()).exists():
        shutil.rmtree(log_dir())
    Console().print(rf"[green]\[{CONSOLE_SUCCESSFUL}][/green] Cleanup successful")


@app.command()
def doctor(
    config_file: str | None = typer.Option(None, "-c", "--config", help="配置文件"),
):
    """
    自检查
    """

    # 计算应用数据大小
    try:
        data_size = 0
        data_path = Path(data_dir())
        if not data_path.exists():
            data_path.mkdir(parents=True, exist_ok=True)
        for files in data_path.iterdir():
            if files.is_file():
                data_size += files.stat().st_size
        Console().print(
            rf"[green]\[{CONSOLE_SUCCESSFUL}][/green] Data dir path: {data_dir()}, size: {data_size / 1024 / 1024:.3f}M"
        )
    except Exception as error_msg:
        Console().print(rf"[red]\[{CONSOLE_ERROR}][/red] Data dir path: {data_dir()}, fail to write to file")
        Console().print(f"Data store error message: {error_msg}")

    try:
        log_size = 0
        log_path = Path(log_dir())
        if not log_path.exists():
            log_path.mkdir(parents=True, exist_ok=True)
        for files in log_path.iterdir():
            if files.is_file():
                log_size += files.stat().st_size
        Console().print(
            rf"[green]\[{CONSOLE_SUCCESSFUL}][/green] Log dir path: {log_dir()}, size: {log_size / 1024 / 1024:.3f}M"
        )
    except Exception as error_msg:
        Console().print(rf"[red]\[{CONSOLE_ERROR}][/red] Log dir path: {log_dir()}, fail to write to file")
        Console().print(f"Log store error message: {error_msg}")

    # check config file
    try:
        setting = init_setting(config_file, enable_log=False)
        if setting:
            if config_file:
                Console().print(rf"[green]\[{CONSOLE_SUCCESSFUL}][/green] Config file: {config_file}")
            else:
                if file := search_for_settings_file():
                    config_file = file.absolute().as_posix()
                else:
                    raise FileNotFoundError(f"config file {CONFIG_FILE_NAME} not found")
                Console().print(rf"[green]\[{CONSOLE_SUCCESSFUL}][/green] Config file: {config_file}")
        else:
            Console().print(rf"[yellow]\[{CONSOLE_WARNING}][/yellow] config {CONFIG_FILE_NAME} not found")
    except Exception as error_msg:
        Console().print(rf"[red]\[{CONSOLE_ERROR}][/red] Config file: {config_file}, fail to load")
        Console().print(f"Config file error message: {error_msg}")

    # check github
    try:
        Fetcher.set_github("")
        Fetcher.set_owner_repo("gouzil/autoTable")
        assert Fetcher.get_issue(10).body is not None
        Console().print(rf"[green]\[{CONSOLE_SUCCESSFUL}][/green] Github resources")
    except Exception as error_msg:
        Console().print(rf"[red]\[{CONSOLE_ERROR}][/red] Github resources")
        Console().print(f"Github error message: {error_msg}")


@app.command()
def migrate02to03(
    owner_repo: str = typer.Argument(..., help="仓库地址"),
    token: str = typer.Option("", help="github token"),
    issue_id: int | None = typer.Option(None, "-i", "--issue-id", help="issue 编号"),
    file_path: str | None = typer.Option(None, "-f", "--file", help="文件路径"),
    log_level: str = typer.Option("INFO", help="日志等级: INFO, DEBUG"),
):
    """
    迁移 v0.2.0->v0.3.0

    可以使用在线 issue 或者本地文件(file_path)
    """
    assert issue_id is not None or file_path is not None
    init_logger(log_level)
    if issue_id is not None:
        Fetcher.set_github(token)
        Fetcher.set_owner_repo(owner_repo)
        tracker_issues_data = get_issues(issue_id)
    else:
        assert file_path is not None
        tracker_issues_data = TrackerIssuesData(
            "local", Path(file_path).read_text(encoding="utf-8"), None, None, owner_repo
        )

    new_issue = replacement_pr_url(tracker_issues_data)

    save_file(
        new_issue,
        f"{tracker_issues_data.issue_title}_migrate.md",
        dry_run=True,
    )


# TODO: 添加初始化 autotable 的命令

if __name__ == "__main__":  # pragma: no cover
    app()
