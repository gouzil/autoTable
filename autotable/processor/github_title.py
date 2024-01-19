from __future__ import annotations

from loguru import logger


class titleBase:
    def __init__(self, title_content: str) -> None:
        self.title_content = title_content
        assert self.title_content, "Title content is empty"

    # 模式分发器
    def distribution_parser(self) -> titleBase:
        match self.title_content:
            # [No.1, 2-3]
            # [No.1、2-3]
            # [No.1，2-3]  # noqa: RUF003
            # [No.1, 2-3]
            case x if ("、" in x or "," in x or "，" in x) and "-" in x:  # noqa: RUF001
                return mixTitle(x)
            # [No.1]
            case x if x.strip().isdigit():
                return singleTitle(x)
            # [No.1-2]
            case x if "-" in x:
                return multipleTitle(x)
            # [No.1、2]
            case x if "、" in x:
                return multipleSingleTitle(x, "、")
            # [No.1, 2]
            case x if "," in x:
                return multipleSingleTitle(x, ",")
            # [No.1，2]  # noqa: RUF003
            case x if "，" in x:  # noqa: RUF001
                return multipleSingleTitle(x, "，")  # noqa: RUF001
            case _:
                logger.error(f"Title {self.title_content} is not supported")
                raise RuntimeError(f"Title {self.title_content} is not supported")

    # 转换成数字
    def mate(self) -> list[int]:
        raise NotImplementedError("Please do not call the mate of titleBase")


# 连续标题
class multipleTitle(titleBase):
    def __init__(self, title_content: str) -> None:
        super().__init__(title_content)

    def mate(self) -> list[int]:
        title_content = self.title_content.strip()
        assert "-" in title_content
        (start_index, end_index) = title_content.split("-")
        assert start_index.isdigit() and end_index.isdigit()
        return list(range(int(start_index), int(end_index) + 1))


# 单标题
class singleTitle(titleBase):
    def __init__(self, title_content: str) -> None:
        super().__init__(title_content)

    def mate(self) -> list[int]:
        # [No.1]
        if self.title_content.strip().isdigit():
            return [int(self.title_content)]
        return []


# 多个单标题
class multipleSingleTitle(titleBase):
    def __init__(self, title_content: str, separator: str) -> None:
        super().__init__(title_content)
        self.separator = separator

    def mate(self) -> list[int]:
        res: list[int] = []
        # 切片
        for i in self.title_content.split(self.separator):
            i = i.strip()
            if i.isdigit():
                res.append(int(i))
            else:
                logger.error(f'Title "{self.title_content}" to int failed')
        return res


# 混合标题
class mixTitle(titleBase):
    def __init__(self, title_content: str) -> None:
        super().__init__(title_content)

    def mate(self) -> list[int]:
        separator: str = ""
        if "、" in self.title_content:
            separator = "、"
        elif "," in self.title_content:
            separator = ","
        else:
            raise NotImplementedError("Title {self.title_content} is not supported")
        res: list[int] = []
        for i in self.title_content.split(separator):
            i = i.strip()
            res.extend(x for x in titleBase(i).distribution_parser().mate())

        return res
