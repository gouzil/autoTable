from __future__ import annotations

from mistletoe.block_token import Table

from autotable.processor.analysis import analysis_table, analysis_title

start_str: str = "<!--task start bot-->"
end_str: str = "<!--task end bot-->"
table = f"""
{start_str}
|  序号  |  文件位置  |  认领人  |  PR  |
| :---: | :---: | :---: | :---: |
| 🔵1 | test_varname_inplace_ipu.py | @gouzil  | #123 |
| 🔵2 | test_eval_model_ipu.py | @gouzil | #456 |
| 🔵3 | test_weight_decay_ipu.py | @gouzil | #789 |
{end_str}
"""


def test_analysis_title():
    "测试解析任务标题前缀"
    title = '<!--title_name="【Cleanup No.】"-->'

    assert analysis_title(title) == "【Cleanup No.】"


def test_analysis_table():
    "解析是否为表格"
    res = analysis_table(table, start_str, end_str)
    assert isinstance(res, Table)
