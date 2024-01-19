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
    替换表格
    """
    return content.replace(
        # 起始位置+起始字符串长度+换行符 : 结束位置
        content[content.find(start_str) + len(start_str) + 1 : content.find(end_str)],
        new_table,
    )
