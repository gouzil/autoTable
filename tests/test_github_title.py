from __future__ import annotations

from autotable.processor.github_title import titleBase


# [No.1]
def test_single_title():
    title = "1"
    assert titleBase(title).distribution_parser().mate() == [1]

# [No.1-2]
def test_multiple_title():
    title = "1-4"
    assert titleBase(title).distribution_parser().mate() == [1,2,3,4]

def test_multiple_single_title():
    # [No.1、2]
    title1 = "1、2"
    # [No.1，2]  # noqa: RUF003
    title2 = "1，2" # noqa: RUF001
    # [No.1,2]
    title3 = "1,2"
    # [No.1, 2]
    title4 = "1, 2"

    assert titleBase(title1).distribution_parser().mate() == [1, 2]
    assert titleBase(title2).distribution_parser().mate() == [1, 2]
    assert titleBase(title3).distribution_parser().mate() == [1, 2]
    assert titleBase(title4).distribution_parser().mate() == [1, 2]

# [No.1, 2-4]
def test_mix_title():
    title1 = "1, 2-4, 6"
    title2 = "1、 2-4、 6"

    assert titleBase(title1).distribution_parser().mate() == [1, 2, 3, 4, 6]
    assert titleBase(title2).distribution_parser().mate() == [1, 2, 3, 4, 6]


