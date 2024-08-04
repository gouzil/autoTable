from __future__ import annotations

from autotable.autotable_type.autotable_type import StatusType
from autotable.processor.utils import TablePeople_list_repeat
from autotable.storage_model.table import TablePeople


def test_table_people():
    tp1 = TablePeople(StatusType.PENDING, "gouzil")
    tp2 = TablePeople(StatusType.PENDING, "gouzi")
    tp3 = TablePeople(StatusType.CLAIMED, "gouzil")
    tp4 = TablePeople(StatusType.COMPLETED, "gouzil")
    tp5 = TablePeople(StatusType.PENDING, "gouzil")
    tp_list = [tp1, tp2, tp3, tp2, tp4, tp5]

    assert tp1 == tp5
    assert tp1 != tp2
    assert tp1 != tp3
    assert TablePeople_list_repeat(tp_list) == [tp4, tp2]
