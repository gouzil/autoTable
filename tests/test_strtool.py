from __future__ import annotations

from autotable.utils.strtool import str_translate


def test_str_translate():
    title = "【paddle_test No.9】编译优化 paddle_test 推全"

    assert str_translate(title) == "[paddle_test No.9]编译优化 paddle_test 推全"
