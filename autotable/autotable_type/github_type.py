from __future__ import annotations

from enum import Enum

from autotable.autotable_type.autotable_type import StatusType
from autotable.storage_model.pull_data import PullRequestData


class PrType(Enum):
    OPEN = "open"
    CLOSED = "closed"
    MERGED = "merged"

    def match_pr_table(self) -> StatusType:
        match self:
            case PrType.OPEN:
                return StatusType.REPAIRING
            case PrType.MERGED:
                return StatusType.COMPLETED
            case PrType.CLOSED:
                return StatusType.PENDING
            case _:
                raise NotImplementedError(f"pr to autotable StatusType {self} is not supported")


def get_pr_type(pr: PullRequestData) -> PrType:
    match pr.state:
        case "open":
            return PrType.OPEN
        case "closed":
            if pr.merged:
                return PrType.MERGED
            else:
                return PrType.CLOSED
        case _:
            raise NotImplementedError(f"pr state {pr.state} is not supported")
