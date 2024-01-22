from __future__ import annotations

# 定义中文符号
chinese_character = r"，。！？；：()《》【】“”\‘\’"  # noqa: RUF001
# 定义对应的英文符号
english_character = r',.!?;:()<>[]""\'\''


_translate_table = str.maketrans(chinese_character, english_character)


def str_translate(input: str) -> str:
    return input.translate(_translate_table)
