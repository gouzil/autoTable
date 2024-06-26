from __future__ import annotations

from autotable.autotable_type.autotable_type import StatusType
from autotable.autotable_type.github_type import PrType, get_pr_type
from autotable.storage_model.pull_data import PullRequestData


def test_autotable_type_compare():
    # 🚧 > 🔵
    assert StatusType.REPAIRING > StatusType.PENDING
    # ✅ > 🔵
    assert StatusType.COMPLETED > StatusType.PENDING
    # 🟢 > 🚧
    assert StatusType.PENDING_MERGE > StatusType.REPAIRING
    # 🟡 > 🟢
    assert StatusType.NEXT_STAGE > StatusType.PENDING_MERGE
    # ✅ > 🟡
    assert StatusType.COMPLETED > StatusType.NEXT_STAGE
    # ✅ < 🟡
    assert not StatusType.NEXT_STAGE > StatusType.COMPLETED
    # 🙋 > 🔵
    assert StatusType.CLAIMED > StatusType.PENDING
    # 🚧 > 🙋
    assert StatusType.REPAIRING > StatusType.CLAIMED


def test_PrType():
    # 🚧
    assert PrType.OPEN.match_pr_table() == StatusType.REPAIRING
    # ✅
    assert PrType.MERGED.match_pr_table() == StatusType.COMPLETED
    # 🔵
    assert PrType.CLOSED.match_pr_table() == StatusType.PENDING


def test_get_pr_type():
    assert get_pr_type(PullRequestData(1, "title", "repo", "user", "closed", True, [])) == PrType.MERGED
    assert get_pr_type(PullRequestData(1, "title", "repo", "user", "closed", False, [])) == PrType.CLOSED
    assert get_pr_type(PullRequestData(1, "title", "repo", "user", "open", False, [])) == PrType.OPEN

    try:
        get_pr_type(PullRequestData(1, "title", "repo", "user", "error", False, []))
        raise AssertionError()
    except NotImplementedError as e:
        assert str(e) == "pr state error is not supported"
