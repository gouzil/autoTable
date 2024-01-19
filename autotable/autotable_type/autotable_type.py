from __future__ import annotations

from enum import Enum

from autotable.autotable_type.github_type import PrType


# 按使用率排序
class StatusType(Enum):
    PENDING = "🔵"  # 待认领
    CLAIMED = "🚧"  # 已经认领了, 正在迁移中, 可能会有pr, 也可能没有pr
    PENDING_MERGE = "🟢"  # 迁移完成, 等待合并
    COMPLETED = "✅"  # 迁移完成
    NEXT_STAGE = "🟡"  # 当前阶段不需要人力继续跟进, 下阶段推进


def match_pr_table(prType: PrType) -> StatusType:
    match prType:
        case PrType.OPEN:
            return StatusType.CLAIMED
        case PrType.MERGED:
            return StatusType.PENDING_MERGE
        case PrType.CLOSED:
            return StatusType.PENDING
        case _:
            raise NotImplementedError(f"pr to autotable StatusType {prType} is not supported")
