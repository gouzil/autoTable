from __future__ import annotations

from autotable.processor.analysis import content2Table
from autotable.processor.file import to_markdown
from autotable.utils.migrate import migrate_pr_url_02to03


def test_migrate_pr_url_02to03():
    repo_fall_name = "gouzil/autotable"
    doc_table_content = f"""| 序号     | Python API   | 所在文件                  | 优先级    | 单测覆盖率 |                认领人                | PR  |
| ------ | ------------ | --------------------- | ------ | :---: | :-------------------------------: | --- |
| 🙋1     | wait         | ***/group.py          | p1     |       | 🙋@undefined1452<br/>🙋@gouzil<br/> | https://github.com/{repo_fall_name}/pull/1    |
| 🙋2     | wait         | ***/group.py          | p1     |       | 🙋@undefined1452<br/>🙋@gouzil<br/> | #1    |
| 🙋3     | barrier      | ***/group.py          | p1     |       | 🙋@undefined1452<br/>🙋@gouzil<br/> |  #1<br/>#2<br/>   |
| 🙋4     | all_gather   | ***/all_gather.py     | p1     |       |             🙋@gouzil              |  https://github.com/{repo_fall_name}/pull/1<br/>https://github.com/{repo_fall_name}/pull/1<br/>   |
| 🙋5     | all_reduce   | ***/all_reduce.py     | p1     |       |             🙋@gouzil              |  https://github.com/{repo_fall_name}/pull/1<br/>#2<br/>   |
| 🔵6     | alltoall     | ***/all_to_all.py     | p1     |       |                                   |     |
| 🔵7     | alltoall     | ***/all_to_all.py     | p1     |       |                                   |   https://github.com/gouzil/test/pull/1<br/>#2<br/>  |
| ~~🔵8~~ | ~~alltoall~~ | ~~***/all_to_all.py~~ | ~~p1~~ |       |                                   |  ~~#1~~   |
"""  # noqa: E501
    res_table_content = to_markdown(migrate_pr_url_02to03(content2Table(doc_table_content), repo_fall_name))

    res = f"""| 序号     | Python API   | 所在文件                  | 优先级    | 单测覆盖率 |                认领人                | PR                                             |
| ------ | ------------ | --------------------- | ------ | :---: | :-------------------------------: | ---------------------------------------------- |
| 🙋1     | wait         | ***/group.py          | p1     |       | 🙋@undefined1452<br/>🙋@gouzil<br/> | {repo_fall_name}#1                             |
| 🙋2     | wait         | ***/group.py          | p1     |       | 🙋@undefined1452<br/>🙋@gouzil<br/> | {repo_fall_name}#1                             |
| 🙋3     | barrier      | ***/group.py          | p1     |       | 🙋@undefined1452<br/>🙋@gouzil<br/> | {repo_fall_name}#1<br/>{repo_fall_name}#2<br/> |
| 🙋4     | all_gather   | ***/all_gather.py     | p1     |       |             🙋@gouzil              | {repo_fall_name}#1<br/>{repo_fall_name}#1<br/> |
| 🙋5     | all_reduce   | ***/all_reduce.py     | p1     |       |             🙋@gouzil              | {repo_fall_name}#1<br/>{repo_fall_name}#2<br/> |
| 🔵6     | alltoall     | ***/all_to_all.py     | p1     |       |                                   |                                                |
| 🔵7     | alltoall     | ***/all_to_all.py     | p1     |       |                                   | gouzil/test#1<br/>{repo_fall_name}#2<br/>      |
| ~~🔵8~~ | ~~alltoall~~ | ~~***/all_to_all.py~~ | ~~p1~~ |       |                                   | ~~{repo_fall_name}#1~~                         |
"""  # noqa: E501

    assert res_table_content == res
