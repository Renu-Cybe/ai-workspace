# skill-generating Reference

## 内部实现细节

### 输入格式

```json
{
  "name": "skill-name",
  "description": "A useful skill",
  "tools": ["Bash", "Read", "Write"],
  "has_script": true
}
```

### 输出格式

```json
{
  "status": "ok|error",
  "skill_name": "...",
  "files_created": [],
  "errors": []
}
```

### 错误处理

- 输入无效 JSON：返回 error 状态
- 缺少必需字段：返回错误提示
- 创建失败：记录错误信息

## 开发 notes

- 创建时间: 2026-03-17
- 遵循官方三层架构
- 主脚本: scripts/generator.py
