from __future__ import annotations

from autotable.autotable_type.autotable_type import StatusType


def test_autotable_type_compare():
    # 🔵 < 🚧
    assert not StatusType.PENDING > StatusType.CLAIMED
    # 🔵 < ✅
    assert not StatusType.PENDING > StatusType.COMPLETED
    # 🟢 > 🚧
    assert StatusType.PENDING_MERGE > StatusType.CLAIMED
    # 🟡 < ✅
    assert not StatusType.NEXT_STAGE > StatusType.COMPLETED
    # 🟡 > 🟢
    assert StatusType.NEXT_STAGE > StatusType.PENDING_MERGE
