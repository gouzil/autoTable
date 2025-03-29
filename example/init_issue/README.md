# 初始化 issue 任务表格

## 介绍

通过 `autotable` 命令行工具，初始化 issue 任务表格，自动生成表格和统计信息。

## 命令

```bash
autotable init-issue -f example/init_issue/demo.md
```

## 输出效果

autotable 做下面几件事

* 格式化表格
* 初始化所有任务状态为 🔵
* 清空最后两列数据
* 更新状态统计表

```markdown
<details>

<summary>

#### 🔚 第 1 批 🎉

</summary>

<!--table_start="A"-->
| 序号   | 文件             | API 数量 | 认领人 Github id | PR 链接 |
| ---- | -------------- | ------ | ------------- | ----- |
| 🔵A-1 | `auto_file.py` | 4      |               |       |
| 🔵A-2 | `auto_gen.py`  | 7      |               |       |
<!--table_end="A"-->


</details>

<details>

<summary>

#### 🔚 第 2 批 🎉

</summary>

<!--table_start="B"-->
| 序号    | 文件               | API 数量 | 认领人 Github id | PR 链接 |
| ----- | ---------------- | ------ | ------------- | ----- |
| 🔵B-01 | `auto_rm.py`     | 1      |               |       |
| 🔵B-02 | `auto_create.py` | 2      |               |       |
<!--table_end="B"-->

</details>

> 注意：上述 API 数量仅为参考，若多个模块之间相互引用，会导致统计数量增多。

----

 ⭐️ **提交PR 模版** ⭐️：
+ **// ------- PR 标题  --------**
```
[Typing][A-1] Add type annotations for `auto_file.py`
```

或者多个任务：
```
[Typing][A-1,A-2,A-3] Add type annotations for `auto_create/*`
```


<!--title_name="\[Typing\]\[(?P<task_id>[\S\s]+)\]"-->
<!--pr_search_content="/\[Typing\]/"-->

 ⭐️ **认领方式** ⭐️：
请大家以 comment 的形式认领任务，如：
```
【报名】：A-1、A-3
```
<!--enter="(\[|【)报名(\]|】)(:|：)(?P<task_id>[\S\s]+)"-->

**状态介绍**：
✅：已经完全迁移，所有单测都OK！
🟢：审核完毕待合入，合入之后完全迁移！
🔵：可认领！
🟡：当前阶段不需要人力继续跟进，下阶段推进
🚧：迁移中，单测还没有过，还没有审核完。

大致正常流程为:
🔵 -> 🚧 -> 🟢 -> ✅

异常流程为:
🔵 -> 🚧 -> 🟡

## 看板信息

<!--stats start bot-->
| 📊任务数量 | 🔵可认领 | 🚧迁移中 | 🟢待合入 | ✅完成 | 🟡下阶段推进 | 🏁完成率 |
| ----- | ---- | ---- | ---- | --- | ------ | ---- |
| 4     | 4    | 0    | 0    | 0   | 0      | 0.0% |
<!--stats end bot-->
<!--contributors start bot-->
<!--contributors end bot-->
```
