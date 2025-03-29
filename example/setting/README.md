# 设置

## 介绍

提供一个实例配置文件，用于持久化存储配置文件

## 命令

```bash
# 指定配置文件
autotable issue-update gouzil/autoTable 18 -c example/setting/autotable.toml

# 自动查询配置文件
# 优先级: 参数指定值 > 用户指定配置文件 > 当前目录下的 autotable.toml > 系统存储配置文件
# 存储配置文件路径: /Users/<user>/Library/Application Support/autotable
autotable issue-update gouzil/autoTable 18
```

## 配置文件

```toml
# autotable.toml
# 该文件用于存储 autotable 的配置文件

# 默认配置, 最外层写和 common 都可以，同时存在时会优先选择 common 内的配置
token = "gh_token"
log_level = "INFO"

[common]
token = "1213"
log_level = "INFO"

# 每个 issue 单独的配置
# 格式为 [repo_settings.<owner>.<repo>.<issue_number>]
[repo_settings.paddlepaddle.paddle.123]
token = "gh_token"
log_level = "INFO"

[repo_settings.gouzil.autoTable.123]
token = "gh_token"
log_level = "DEBUG"

```
