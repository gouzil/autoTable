from __future__ import annotations

from autotable.processor.analysis import content2table
from autotable.processor.file import to_markdown
from autotable.processor.github_prs import update_pr_table
from autotable.storage_model.pull_data import PullRequestData, PullReviewData


def test_update_pr_table():
    repo_fall_name = "gouzil/autotable"
    title_re = r"\[Cleanup\]\[(?P<task_id>[\S\s]+)\]"
    doc_table_content = f"""| 序号     | 所在文件        | 优先级    | 单测覆盖率 |    认领人    | PR  |
| ------ | ------------ |  ------ | :---: | :-------------------------------: | --- |
| 🔵1     | ***/group.py          | p1     |        |                     |   |
| 🔵2     |  ***/group.py          | p1     |       |                     |    |
| 🔵3     |  ***/group.py          | p1     |       |                     |    |
| 🔵4     |  ***/all_gather.py     | p1     |       |            |    |
| 🔵5     |  ***/all_reduce.py     | p1     |       |           |    |
| 🔵6     |  ***/all_to_all.py     | p1     |       |                    |     |
| 🔵7     |  ***/all_to_all.py     | p1     |       |                    |  {repo_fall_name}#1   |
| ~~🔵8~~ |  ~~***/all_to_all.py~~ | ~~p1~~ |       |                    |    |
"""

    review_null = []
    review1 = [PullReviewData("gs12f21sfewf", "APPROVED", "LGTM", "gouzil")]
    review2 = [PullReviewData("gs12f21sfewf", "APPROVED", 'LGTM<!--bot_next="6"-->', "gouzil")]
    pr1 = PullRequestData(1, "[Cleanup][1,2、3] fix test", repo_fall_name, "gouzil", "open", False, review_null)
    pr2 = PullRequestData(2, "[Cleanup][4] fix test", repo_fall_name, "gouzil", "closed", False, review_null)
    pr3 = PullRequestData(3, "[Cleanup][try debug] fix test", repo_fall_name, "gouzil", "open", False, review_null)
    pr4 = PullRequestData(4, "[Cleanup][5] fix test", repo_fall_name, "gouzil", "open", False, review1)
    pr5 = PullRequestData(5, "[Cleanup][6] fix test", repo_fall_name, "gouzil", "open", False, review2)
    pr6 = PullRequestData(6, "[Cleanup][7] fix test", repo_fall_name, "gouzil", "closed", True, review1)
    prs = [pr1, pr2, pr3, pr3, pr4, pr5, pr6]
    res_table_content = to_markdown(update_pr_table(content2table(doc_table_content), title_re, prs))

    res1 = """| 序号     | 所在文件                  | 优先级    | 单测覆盖率 |   认领人    | PR                                             |
| ------ | --------------------- | ------ | :---: | :------: | ---------------------------------------------- |
| 🚧1     | ***/group.py          | p1     |       | 🚧@gouzil | gouzil/autotable#1                             |
| 🚧2     | ***/group.py          | p1     |       | 🚧@gouzil | gouzil/autotable#1                             |
| 🚧3     | ***/group.py          | p1     |       | 🚧@gouzil | gouzil/autotable#1                             |
| 🔵4     | ***/all_gather.py     | p1     |       |          |                                                |
| 🟢5     | ***/all_reduce.py     | p1     |       | 🟢@gouzil | gouzil/autotable#4                             |
| 🟡6     | ***/all_to_all.py     | p1     |       | 🟡@gouzil | gouzil/autotable#5                             |
| ✅7     | ***/all_to_all.py     | p1     |       | ✅@gouzil | gouzil/autotable#1<br/>gouzil/autotable#6<br/> |
| ~~🔵8~~ | ~~***/all_to_all.py~~ | ~~p1~~ |       |          |                                                |
"""  # noqa: E501

    res2 = """| 序号     | 所在文件                  | 优先级    | 单测覆盖率 |   认领人    | PR                                             |
| ------ | --------------------- | ------ | :---: | :------: | ---------------------------------------------- |
| 🚧1     | ***/group.py          | p1     |       | 🚧@gouzil | gouzil/autotable#1                             |
| 🚧2     | ***/group.py          | p1     |       | 🚧@gouzil | gouzil/autotable#1                             |
| 🚧3     | ***/group.py          | p1     |       | 🚧@gouzil | gouzil/autotable#1                             |
| 🔵4     | ***/all_gather.py     | p1     |       |          |                                                |
| 🟢5     | ***/all_reduce.py     | p1     |       | 🟢@gouzil | gouzil/autotable#4                             |
| 🟡6     | ***/all_to_all.py     | p1     |       | 🟡@gouzil | gouzil/autotable#5                             |
| ✅7     | ***/all_to_all.py     | p1     |       | ✅@gouzil | gouzil/autotable#6<br/>gouzil/autotable#1<br/> |
| ~~🔵8~~ | ~~***/all_to_all.py~~ | ~~p1~~ |       |          |                                                |
"""  # noqa: E501

    assert res_table_content in (res1, res2)
