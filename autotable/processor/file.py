from __future__ import annotations

from pathlib import Path

from loguru import logger
from mistletoe.block_token import Table
from mistletoe.markdown_renderer import MarkdownRenderer

from autotable.utils.appdirs import data_dir


def save_file(content: str, filename: str, title: str = "", dry_run: bool = False):
    """存储文件到md"""
    if title != "":
        content = f"# {title}\n\n{content}"
    if dry_run:
        path_: Path = Path(f"./{filename}")
    else:
        Path(data_dir()).mkdir(parents=True, exist_ok=True)
        path_: Path = Path(f"{data_dir()}/{filename}")
    logger.info(f"save file: {path_.resolve()}")
    path_.write_text(content, encoding="utf-8")
    return path_


def to_markdown(doc: Table) -> str:
    """
    转markdown
    """
    with MarkdownRenderer() as renderer:
        md = renderer.render(doc)

    return md


def replace_table(content: str, start_str: str, end_str: str, new_table: str) -> str:
    """
    替换表格, 后来也被用于替换一些文本信息
    """
    # 前半部分+起始字符串长度+换行符
    first_half: str = content[: content.find(start_str) + len(start_str) + 1]
    # 后半部分
    second_half: str = content[content.find(end_str) :]
    # 加新内容
    return f"{first_half}{new_table}{second_half}"
