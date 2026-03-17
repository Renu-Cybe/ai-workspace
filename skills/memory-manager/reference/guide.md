# memory-manager Reference

## 内部实现细节

### 输入格式

```json
{
  "action": "dashboard|search|branch|kanban",
  "params": {}
}
```

### 输出格式

```json
{
  "status": "ok|error",
  "message": "result message",
  "data": {}
}
```

### 错误处理

- 输入无效 JSON：返回 error 状态
- 缺少必需参数：返回错误提示
- 工具执行异常：stderr 输出错误信息

## 开发 notes

- 创建时间: 2026-03-17
- 遵循官方三层架构
- 主脚本: main.py
