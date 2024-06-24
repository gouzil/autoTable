from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from github.PullRequest import PullRequest
    from github.PullRequestReview import PullRequestReview

APPNAME = "autotable"
APPAUTHOR = "gouzil"
CONSOLE_SUCCESSFUL = "✓"
CONSOLE_ERROR = "✗"


# processor/github_prs cache
global_error_prs: set[PullRequest] = set()
global_pr_reviews_cache: dict[int, list[PullRequestReview]] = {}
