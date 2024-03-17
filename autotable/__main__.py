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
from autotable.command import backup, update_content, update_stats
from autotable.constant import CONSOLE_ERROR, CONSOLE_SUCCESSFUL
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
    repo: str,
    token: str,
    log_level: str = "INFO",
):
    r"""
    初始化日志、github token、repo等信息
    """
    init_logger(log_level)
    Fetcher.set_github(token)
    Fetcher.set_repo(repo)


@app.command()
def issue_update(
    repo: str = typer.Argument(..., help="仓库地址"),
    issue_id: int = typer.Argument(..., help="issue 编号"),
    token: str = typer.Argument(..., help="github token"),
    overwrite_remote: bool = typer.Option(True, "-o", "--overwrite-remote", help="写入远程 issue"),
    dry_run: bool = typer.Option(False, help="试运行模式, 此模式将不会写入远程 issue, 但会生成更新后的文件"),
    log_level: str = typer.Option("INFO", help="日志等级: INFO, DEBUG"),
):
    """
    更新 issue 内容
    """
    init(repo, token, log_level)
    # 获取issue内容
    issue_title, issue_content, issue_create_time, issue_comments = get_issues(issue_id)
    new_issue: str = update_content(issue_title, issue_content, issue_create_time, issue_comments, dry_run)
    if overwrite_remote and not dry_run:
        backup(issue_title, issue_content)
        Fetcher.set_issue(issue_id, new_issue)


@app.command()
def issue_update_stats(
    repo: str = typer.Argument(..., help="仓库地址"),
    issue_id: int = typer.Argument(..., help="issue 编号"),
    token: str = typer.Argument(..., help="github token"),
    overwrite_remote: bool = typer.Option(True, "-o", "--overwrite-remote", help="写入远程 issue"),
    dry_run: bool = typer.Option(False, help="试运行模式, 此模式将不会写入远程 issue, 但会生成更新后的文件"),
    log_level: str = typer.Option("INFO", help="日志等级: INFO, DEBUG"),
):
    """
    仅更新 issue 任务统计
    """
    init(repo, token, log_level)
    issue_title, issue_content, _, _ = get_issues(issue_id)
    new_issue: str = update_stats(issue_title, issue_content, dry_run)
    if overwrite_remote and not dry_run:
        backup(issue_title, issue_content)
        Fetcher.set_issue(issue_id, new_issue)


@app.command()
def issue_backup(
    repo: str = typer.Argument(..., help="仓库地址"),
    issue_id: int = typer.Argument(..., help="issue 编号"),
    token: str = typer.Argument(..., help="github token"),
    log_level: str = typer.Option("INFO", help="日志等级: INFO, DEBUG"),
):
    """
    备份 issue
    """
    init(repo, token, log_level)
    issue_title, issue_content, _, _ = get_issues(issue_id)
    backup(issue_title, issue_content)


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
def doctor():
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
            rf"[green]\[{CONSOLE_SUCCESSFUL}][/green] Data dir path: {data_dir()}, size: {data_size/1024/1024:.3f}M"
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
            rf"[green]\[{CONSOLE_SUCCESSFUL}][/green] Log dir path: {log_dir()}, size: {log_size/1024/1024:.3f}M"
        )
    except Exception as error_msg:
        Console().print(rf"[red]\[{CONSOLE_ERROR}][/red] Log dir path: {log_dir()}, fail to write to file")
        Console().print(f"log store error message: {error_msg}")

    # check github
    try:
        Fetcher.set_github("")
        Fetcher.set_repo("gouzil/autoTable")
        Fetcher.get_issue(10).body  # noqa: B018
        Console().print(rf"[green]\[{CONSOLE_SUCCESSFUL}][/green] Github resources")
    except Exception as error_msg:
        Console().print(rf"[red]\[{CONSOLE_ERROR}][/red] Github resources")
        Console().print(f"Github error message: {error_msg}")


if __name__ == "__main__":  # pragma: no cover
    app()
