from __future__ import annotations

from pathlib import Path

from mistletoe.block_token import Table
from mistletoe.markdown_renderer import MarkdownRenderer


def save_file(content: str, path: str, title: str = ""):
    """存储文件到md"""
    if title != "":
        content = f"# {title}\n\n{content}"
    path_: Path = Path(path)
    path_.write_text(content)


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
