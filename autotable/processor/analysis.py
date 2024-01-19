from __future__ import annotations

from loguru import logger
from mistletoe import Document, ast_renderer
from mistletoe.block_token import Table


# 解析markdown表格
def analysis_table(content: str, start_str: str, end_str: str) -> Table:
    """ 解析markdown 表格"""
    # 切分一下表格, 后期可能需要调整多表策略
    # TODO(gouzi): 或许不应该在这里处理多表, 而是交给上层去处理
    content = content[content.find(start_str)+len(start_str):content.find(end_str)]

    doc = Document(content.split("\n"))
    assert isinstance(doc.children[0], Table)

    # 渲染一下ast, 方便调试
    logger.debug(ast_renderer.get_ast(doc))

    return doc.children[0]

# 解析任务列表markdown中任务的标题 暂停音乐
def analysis_title(content: str) -> str:
    """
    解析pr开头标题

    标题的最后一位是结束符
    """
    title_start = '<!--title_name="'
    title_end = '"-->'
    content = content[content.find(title_start) + len(title_start):]
    return content[:content.find(title_end)]





