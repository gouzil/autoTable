from __future__ import annotations

from autotable.autotable_type.autotable_type import StatusType
from autotable.autotable_type.github_type import PrType


def test_autotable_type_compare():
    # 🚧 > 🔵
    assert StatusType.CLAIMED > StatusType.PENDING
    # ✅ > 🔵
    assert StatusType.COMPLETED > StatusType.PENDING
    # 🟢 > 🚧
    assert StatusType.PENDING_MERGE > StatusType.CLAIMED
    # 🟡 > 🟢
    assert StatusType.NEXT_STAGE > StatusType.PENDING_MERGE
    # ✅ > 🟡
    assert StatusType.COMPLETED > StatusType.NEXT_STAGE
    # ✅ < 🟡
    assert not StatusType.NEXT_STAGE > StatusType.COMPLETED


def test_PrType():
    # 🚧
    assert PrType.OPEN.match_pr_table() == StatusType.CLAIMED
    # ✅
    assert PrType.MERGED.match_pr_table() == StatusType.COMPLETED
    # 🔵
    assert PrType.CLOSED.match_pr_table() == StatusType.PENDING
