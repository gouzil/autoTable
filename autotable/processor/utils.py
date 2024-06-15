from __future__ import annotations

from autotable.autotable_type.autotable_type import StatusType
from autotable.processor.analysis import analysis_table_more_people
from autotable.storage_model.table import TablePeople


def update_table_people(status: StatusType, user_name: str, table_row: str) -> str:
    # 处理人名
    # 第一位是@位, 第二位是状态位
    people_names: list[TablePeople] = [TablePeople(status, user_name)]
    people_names.extend([TablePeople(StatusType(x[0]), x[2:]) for x in analysis_table_more_people(table_row)])
    people_names = TablePeople_list_repeat(people_names)
    table_people_names: str = ""
    if len(people_names) == 1:
        table_people_names = f"{people_names[0].status.value}@{people_names[0].github_id}"
    else:
        for people in people_names:
            # 这里全部以 pr 状态为主
            if people.github_id not in table_people_names:
                table_people_names += f"{people.status.value}@{people.github_id}<br/>"
    return table_people_names


# TODO: 考虑移动到 TablePeople 类中
# TablePeople 去重, 这里会调整状态
def TablePeople_list_repeat(TablePeople_list: list[TablePeople]) -> list[TablePeople]:
    res: list[TablePeople] = []
    for people in TablePeople_list:
        write = True
        for res_index, res_data in enumerate(res):
            if people.github_id == res_data.github_id and people.status == res_data.status:
                write = False
                break
            if people.github_id != res_data.github_id:
                continue
            # 取较大的那个状态更新
            if res_data.status > people.status:
                write = False
            else:
                res[res_index].status = people.status
                write = False
        if write:
            res.append(people)

    return res
