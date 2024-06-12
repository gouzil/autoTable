from __future__ import annotations

import re

# 定义中文符号
chinese_character = r"、，。！？；：()《》【】“”\‘\’"  # noqa: RUF001
# 定义对应的英文符号
english_character = r',,.!?;:()<>[]""\'\''


_translate_table = str.maketrans(chinese_character, english_character)


pat_title = re.compile(r"(?P<prefix>[a-zA-Z]+)[^\[]*?((?P<no>(\d+))|(\[(?P<no_start>\d+)-(?P<no_end>\d+)\]))")


def str_translate(input: str) -> str:
    return input.translate(_translate_table)


def clean_title(title: str) -> str:
    if title is not None and not title.strip():
        return title

    title = str_translate(title)

    if title.lower().startswith("no."):
        # just return the title: No.1,3-4
        return title

    # format title:
    # A15 -> A-15
    # A+2,A*4，A - 1、A- 24,A234\a432 -> A-2,A-4,A-1,A-24,A-234,A432 # noqa: RUF003
    # A-[48-52] -> A-48,A-49,A-50,A-51,A-52
    _title = []
    for match in pat_title.finditer(title):
        if match.group("no"):
            _title.append(match.group("prefix").upper() + "-" + match.group("no"))
        elif match.group("no_start"):
            no_start = int(match.group("no_start"))
            no_end = int(match.group("no_end"))
            for index in range(no_start, no_end + 1):
                _title.append(match.group("prefix").upper() + "-" + str(index))
        else:
            pass
    return ",".join(_title) or title
