# autoTable 的 mcp-server 服务

## 配置

设置 mcp server 的配置文件

```json
{
  "mcpServers": {
    "FUIyV-a7NQC6rPQSRWkJl": { // mcp server 的 id, 这个是客户端随机的
      "isActive": true,
      "name": "autoTable-server", // mcp server 的名称
      "command": "/<path>/autoTable/.venv/bin/python", // 运行 mcp server 的 python
      "args": [
        "/<path>/autoTable/mcp-server/main.py" // 运行 mcp server 的脚本
      ],
      "env": {
        "CONFIG_PATH": "/<path>/autotable.toml", // 可选: mcp server 的配置文件路径, 参考 autoTable 的配置文件
        "DEFAULT_TOKEN": "github_token", // 可选: mcp server 的默认 token, 不写默认会读取配置文件的 token
      }
    },
  }
}
```

## 基础用法

这里以 cherry studio 为例

### autotable init-issue

在对话中输入:

```
使用autotable初始化一下 /<path>/autoTable/example/init_issue/demo.md 这个文件，并存储到 /<path>/autoTable/demo.md
```

对应的命令:

```bash
autotable init-issue -f /<path>/autoTable/example/init_issue/demo.md
```

工具运行结果:

```json
{
  "params": {
    "input_file_path": "/<path>/autoTable/example/init_issue/demo.md",
    "output_file_path": "/<path>/autoTable/demo.md"
  },
  "response": {
    "content": [
      {
        "type": "text",
        "text": "file created: /<path>/autoTable/demo.md"
      }
    ],
    "isError": false
  }
}
```


### autotable issue-backup

在对话中输入:

```
使用 autotable 备份一下 https://github.com/gouzil/autoTable/issues/18 这个 issue
```

对应的命令:

```bash
autotable issue-backup gouzil/autoTable 18
```

工具运行结果:

```json
{
  "params": {
    "owner_repo": "gouzil/autoTable",
    "issue_id": 18
  },
  "response": {
    "content": [
      {
        "type": "text",
        "text": "Backup for issue 18 saved to /Users/<user>/Library/Application Support/autotable/2025-04-04-20-55-32demo issue.md"
      }
    ],
    "isError": false
  }
}
```

### autotable issue-update

在对话中输入:

```
尝试运行更新 https://github.com/gouzil/autoTable/issues/18 这个issue, 不要更新到远程仓库，把结果存到 /<path>/autoTable/update.md
```

对应的命令:

```bash
autotable issue-update gouzil/autoTable 18 --dry-run
```

工具运行结果:

```json
{
  "params": {
    "owner_repo": "gouzil/autoTable",
    "issue_id": 18,
    "dry_run": true,
    "output_file_path": "/<path>/autoTable/update.md",
    "reset_table": false
  },
  "response": {
    "content": [
      {
        "type": "text",
        "text": "update issue success"
      }
    ],
    "isError": false
  }
}
```

### 类 help 的命令

在对话中输入:

```
怎么使用autotable的issue更新
```

模型回答

```markdown
通过调用 `<mcp-id>` 函数实现，支持本地预览或直接更新到远程仓库。

#### **参数说明**：
1. **owner_repo**（必填）
   - 格式为 `用户名/仓库名`（如：`gouzil/autoTable`）。
   - 如需从 GitHub URL 转换，可用函数 `<mcp-id>`。例如：
     ```json
     {"url": "https://github.com/gouzil/autoTable/issues/18"}
     ```
     返回结果为 `"gouzil/autoTable"`。

2. **issue_id**（必填）
   - 需要更新的 Issue 编号，如 `18`。

3. **dry_run**（可选，默认：`false`）
   - 设为 `true` 时只生成本地文件，不修改远程仓库。
   - 示例：您的上一次操作即用此模式，结果存入指定路径。

4. **output_file_path**（当 `dry_run=true` 时必填）
   - 指定输出的本地文件路径，如 `/Users/<user>/Documents/update.md`。

5. **reset_table**（可选，默认：`false`）
   - 设为 `true` 时会重置表格到初始状态，覆盖现有内容。

```
