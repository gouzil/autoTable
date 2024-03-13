from __future__ import annotations

from enum import Enum


# 按使用率排序
class StatusType(Enum):
    PENDING = "🔵"  # 待认领
    CLAIMED = "🚧"  # 已经认领了, 正在迁移中, 可能会有pr, 也可能没有pr
    PENDING_MERGE = "🟢"  # 迁移完成, 等待合并
    NEXT_STAGE = "🟡"  # 当前阶段不需要人力继续跟进, 下阶段推进
    COMPLETED = "✅"  # 迁移完成

    def __gt__(self, other: StatusType) -> bool:
        # self > other
        match (self, other):
            case (
                StatusType.CLAIMED
                | StatusType.COMPLETED
                | StatusType.PENDING_MERGE
                | StatusType.NEXT_STAGE,
                StatusType.PENDING,
            ):
                return True
            case (
                StatusType.PENDING_MERGE
                | StatusType.NEXT_STAGE
                | StatusType.COMPLETED,
                StatusType.CLAIMED,
            ):
                return True
            case (
                StatusType.NEXT_STAGE
                | StatusType.COMPLETED,
                StatusType.PENDING_MERGE,
            ):
                return True
            case (StatusType.COMPLETED, StatusType.NEXT_STAGE):
                return True
            case _:
                return False
