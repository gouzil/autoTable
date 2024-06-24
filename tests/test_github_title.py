from __future__ import annotations

from autotable.processor.github_title import titleBase


# [No.1]
def test_single_title():
    title = "1"
    assert titleBase(title).distribution_parser().mate() == ["1"]


# [No.1-2]
def test_multiple_title():
    title = "1-4"
    assert titleBase(title).distribution_parser().mate() == ["1", "2", "3", "4"]


def test_multiple_single_title():
    # [No.1、2]
    title1 = "1、2"
    # [No.1，2]  # noqa: RUF003
    title2 = "1，2"  # noqa: RUF001
    # [No.1,2]
    title3 = "1,2"
    # [No.1, 2]
    title4 = "1, 2"

    assert titleBase(title1).distribution_parser().mate() == ["1", "2"]
    assert titleBase(title2).distribution_parser().mate() == ["1", "2"]
    assert titleBase(title3).distribution_parser().mate() == ["1", "2"]
    assert titleBase(title4).distribution_parser().mate() == ["1", "2"]


# [No.1, 2-4]
def test_mix_title():
    title1 = "1, 2-4, 6"
    title2 = "1、 2-4、 6"
    title3 = "A-[48-52]"
    title4 = "A-70][A-71"

    assert titleBase(title1).distribution_parser().mate() == ["1", "2", "3", "4", "6"]
    assert titleBase(title2).distribution_parser().mate() == ["1", "2", "3", "4", "6"]
    assert titleBase(title3).distribution_parser().mate() == ["A-48", "A-49", "A-50", "A-51", "A-52"]
    assert titleBase(title4).distribution_parser().mate() == ["A-70", "A-71"]


# 常见的几种错别字测试
def test_typo():
    title1 = "A+2"
    title2 = "A*4"
    title3 = "A - 1"
    title4 = "A- 24"
    title5 = "A234"
    title6 = "a432"

    title_all = r"A+2,A*4，A - 1、A- 24,A234\a432"  # noqa: RUF001

    assert titleBase(title1).distribution_parser().mate() == ["A-2"]
    assert titleBase(title2).distribution_parser().mate() == ["A-4"]
    assert titleBase(title3).distribution_parser().mate() == ["A-1"]
    assert titleBase(title4).distribution_parser().mate() == ["A-24"]
    assert titleBase(title5).distribution_parser().mate() == ["A-234"]
    assert titleBase(title6).distribution_parser().mate() == ["A-432"]
    assert titleBase(title_all).distribution_parser().mate() == ["A-2", "A-4", "A-1", "A-24", "A-234", "A-432"]
