# autoTable

一些小规定：
* 在第一列为序号列，第一列的第一个字符串位置为状态位，如🚧、🔵等
* 最后一列为 PR 列，多 PR 使用`<br/>`分割, 例如：`#1<br/>#2`
* 倒数第二列为认领人列，多认领人使用`<br/>`分割，认领人 `@` 符号前一位为状态位，如`🚧@gouzil<br/>🔵@gouzil`

## 安装

源码安装

```bash
pdm install
```
仓库安装

```bash
pip install git+https://github.com/gouzil/autoTable
```

## 使用方式

备份

```bash
autotable issue-backup gouzil/autoTable 18 github_pat_*****
```

更新

```bash
autotable issue-update gouzil/autoTable 18 github_pat_******
```

不更新远程issue, 仅缓存本地issue

```bash
autotable issue-update gouzil/autoTable 18 --dry-run github_pat_******
```

仅更新统计

```bash
autotable issue-update-stats gouzil/autoTable 18 github_pat_******
```

清理本地文件
```bash
autotable clean
```

自检查
```bash
autotable doctor
```

更多选项请查看 `--help`

## 注释说明

### 适用于 issue 内部
* 表示一个表格的开始和结束, A到Z大写
```md
<!--table_start="A"-->
|  序号  |  文件位置  |  认领人  |  PR  |
| :---: | :---: | :---: | :---: |
| 🚧A-1 | amp_o2_pass.py |  🚧@gouzil  | #1 |
| 🔵A-2 | test_cummax_op.py |   |  |
<!--table_end="A"-->

...

<!--table_start="B"-->
...
<!--table_end="B"-->
```

* 正则标题, 这里只需要获取任务序号，需要与表格序号一致，除状态位

```md
<!--title_name="\[Cleanup\]\[(?P<task_id>[\S\s]+)\]"-->
```

`[Cleanup][A-1] clean some VarType for test` 取 `A-1`


* 正则报名信息，这里同样只需要获取所有的任务序号

```md
<!--enter="(\[|【)报名(\]|】)(:|：)(?P<task_id>[\S\s]+)"-->
```

`【报名】：1、3、12-13` 取 `1、3、12-13`

#### 以下 bot 部分可以不写

* 更新统计表，这里会根据状态进行补充数据，完成率的图标恒定为🏁，(如果有写标签就一定要写表格)
```md
<!--stats start bot-->
| 任务数量 | 🔵可认领 | 🚧迁移中 | 🟢待合入 | ✅完成 | 🟡下阶段推进 | 🏁完成率  |
| ---- | ---- | ---- | ---- | --- | ------ | ----- |
| 46   | 8    | 14   | 5    | 19  | 0      | 41.3% |
<!--stats end bot-->
```

* 贡献者名单，这个有写就会自动添加，不需要手动添加
```md
<!--contributors start bot-->
<!--contributors end bot-->
```

* 自定义 repo, 设置了这个参数会从这个 repo 中获取 pulls 信息
```md
<!--repo="gouzil/autoTable"--> 单repo
<!--repo="gouzil/autoTable;gouzil/test"--> 多repo
```
例子：
```md
<!--table_start="A"-->
<!--repo="gouzil/autoTable"-->
|  序号  |  文件位置  |  认领人  |  PR  |
| :---: | :---: | :---: | :---: |
| 🚧A-1 | amp_o2_pass.py |  🚧@gouzil  | #1 |
| 🔵A-2 | test_cummax_op.py |   |  |
<!--table_end="A"-->
```

### 适用于 PR 内，在 APPROVED 时添加

* 根据`bot_next`内的任务序号去改变状态为🟡
```md
<!--bot_next="A-1"-->
```


