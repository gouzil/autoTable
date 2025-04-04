from __future__ import annotations

from autotable.autotable_type import StatusType
from autotable.processor import update_table_people


def test_update_table_people():
    assert update_table_people(StatusType.CLAIMED, "gouzil", "") == f"{StatusType.CLAIMED.value}@gouzil"
    assert (
        update_table_people(StatusType.CLAIMED, "gouzil", f"{StatusType.CLAIMED.value}@gouzil")
        == f"{StatusType.CLAIMED.value}@gouzil"
    )
    assert (
        update_table_people(StatusType.CLAIMED, "gouzil", f"{StatusType.CLAIMED.value}@undefined")
        == f"{StatusType.CLAIMED.value}@gouzil<br/>{StatusType.CLAIMED.value}@undefined<br/>"
    )
    # 测试去重复
    assert (
        update_table_people(StatusType.CLAIMED, "gouzil", f"{StatusType.CLAIMED.value}@gouzil")
        == f"{StatusType.CLAIMED.value}@gouzil"
    )
    assert (
        update_table_people(StatusType.CLAIMED, "gouzil", f"{StatusType.COMPLETED.value}@gouzil")
        == f"{StatusType.COMPLETED.value}@gouzil"
    )
    assert (
        update_table_people(
            StatusType.CLAIMED,
            "gouzil",
            f"{StatusType.COMPLETED.value}@gouzil<br/>{StatusType.CLAIMED.value}@undefined<br/>",
        )
        == f"{StatusType.COMPLETED.value}@gouzil<br/>{StatusType.CLAIMED.value}@undefined<br/>"
    )
    assert (
        update_table_people(
            StatusType.COMPLETED,
            "gouzil",
            f"{StatusType.CLAIMED.value}@gouzil<br/>{StatusType.CLAIMED.value}@undefined<br/>",
        )
        == f"{StatusType.COMPLETED.value}@gouzil<br/>{StatusType.CLAIMED.value}@undefined<br/>"
    )
