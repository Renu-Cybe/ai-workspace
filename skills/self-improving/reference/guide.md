# self-improving Reference

## 内部实现细节

### 输入格式

```json
{
  "action": "record|analyze|recommend|reflect",
  "task_type": "...",
  "strategy": "...",
  "success": true,
  "duration_sec": 0.0
}
```

### 输出格式

```json
{
  "status": "ok|error",
  "records_count": 0,
  "success_rate": 0.0,
  "recommendation": "...",
  "confidence": 0.0
}
```

### 错误处理

- 输入无效 JSON：返回 error 状态
- 缺少必需参数：返回错误提示
- 执行异常：stderr 输出错误信息

## 开发 notes

- 创建时间: 2026-03-17
- 遵循官方三层架构
- 主脚本: scripts/improvement_tracker.py
