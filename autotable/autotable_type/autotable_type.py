from __future__ import annotations

from enum import Enum

from typing_extensions import Self


# 按使用率排序
class StatusType(Enum):
    def __new__(cls, value: object) -> Self:
        obj = object.__new__(cls)
        obj.index = len(cls.__members__) + 1
        obj._value_ = value
        return obj

    PENDING = "🔵"  # 待认领
    CLAIMED = "🙋"  # 认领
    REPAIRING = "🚧"  # 正在迁移中, 有pr
    PENDING_MERGE = "🟢"  # 迁移完成, 等待合并
    NEXT_STAGE = "🟡"  # 当前阶段不需要人力继续跟进, 下阶段推进
    COMPLETED = "✅"  # 迁移完成

    def __lt__(self, other: StatusType) -> bool:
        return self.index < other.index
