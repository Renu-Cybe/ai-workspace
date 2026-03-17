# memory-tiering Reference

## 内部实现细节

### 输入格式

```json
{
  "action": "store|query|promote|stats",
  "content": "...",
  "key": "identifier",
  "metadata": {}
}
```

### 输出格式

```json
{
  "status": "ok|error",
  "tier": "core|working|short_term|long_term",
  "importance": 0.0,
  "path": "...",
  "key": "..."
}
```

### 错误处理

- 输入无效 JSON：返回 error 状态
- 缺少必需参数：返回错误提示
- 执行异常：stderr 输出错误信息

## 开发 notes

- 创建时间: 2026-03-17
- 遵循官方三层架构
- 主脚本: scripts/tier_manager.py
