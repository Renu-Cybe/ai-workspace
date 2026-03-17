# skill-validating Reference

## 内部实现细节

### 输入格式

```json
{
  "skill_name": "target-skill",
  "validate_all": false
}
```

### 输出格式

```json
{
  "status": "ok|error",
  "score": 100,
  "errors": [],
  "warnings": [],
  "suggestions": []
}
```

### 错误处理

- Skill 不存在：返回 error 状态
- 格式错误：列出具体错误
- 验证失败：返回详细报告

## 开发 notes

- 创建时间: 2026-03-17
- 遵循官方三层架构
- 主脚本: scripts/validator.py
