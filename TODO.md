autotable:
 - [x] `StatusType` 的 `__gt__` 大小顺序目前还没想好
 - [ ] 支持多仓库 pr 搜索
 - [ ] 支持自定义 `StatusType` 图标
 - [ ] 支持初始化表格时自动填充 `StatusType` 为 `StatusType.TODO`
 - [ ] 支持初始化看板信息

ci:
 - [ ] 将 build 后的 wheel 文件上传到当前 job 的 Artifacts 上，在 tests 时下载 wheel 文件进行测试