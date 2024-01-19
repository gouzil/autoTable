from __future__ import annotations

from enum import Enum
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from github.PullRequest import PullRequest


class PrType(Enum):
    OPEN = "open"
    CLOSED = "closed"
    MERGED = "merged"


def get_pr_type(pr: PullRequest) -> PrType:
    match pr.state:
        case "open":
            return PrType.OPEN
        case "closed":
            if pr.merged_at is None:
                return PrType.CLOSED
            else:
                return PrType.MERGED
        case _:
            raise NotImplementedError(f"pr state {pr.state} is not supported")
