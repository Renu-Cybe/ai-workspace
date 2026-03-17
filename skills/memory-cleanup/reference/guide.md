# memory-cleanup Reference

## 内部实现细节

### 输入格式

```json
{
  "action": "cleanup|check|simulate",
  "days": 30,
  "archive_limit": 50
}
```

### 输出格式

```json
{
  "status": "ok|error",
  "message": "cleanup result",
  "cleaned_files": [],
  "archived_files": [],
  "stats": {
    "total_size_before": 0,
    "total_size_after": 0
  }
}
```

### 错误处理

- 权限不足：返回错误提示
- 磁盘空间不足：跳过压缩步骤
- 归档失败：记录日志继续执行

## 开发 notes

- 创建时间: 2026-03-17
- 遵循官方三层架构
- 纯文档型 Skill，无 scripts 目录
