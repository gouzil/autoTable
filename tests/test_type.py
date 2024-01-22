from __future__ import annotations

from autotable.autotable_type.autotable_type import StatusType


def test_autotable_type_compare():
    # 🔵 < 🚧
    assert not StatusType.PENDING.compare(StatusType.CLAIMED)
    # 🔵 < ✅
    assert not StatusType.PENDING.compare(StatusType.COMPLETED)
    # 🟢 > 🚧
    assert StatusType.PENDING_MERGE.compare(StatusType.CLAIMED)
    # 🟡 < ✅
    assert not StatusType.NEXT_STAGE.compare(StatusType.COMPLETED)
    # 🟡 > 🟢
    assert StatusType.NEXT_STAGE.compare(StatusType.PENDING_MERGE)
