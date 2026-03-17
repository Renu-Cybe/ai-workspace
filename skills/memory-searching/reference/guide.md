# memory-searching Reference

## 内部实现细节

### 输入格式

```json
{
  "query": "search text",
  "type": "keyword|semantic|temporal",
  "tiers": ["core", "working", "short_term", "long_term"]
}
```

### 输出格式

```json
{
  "status": "ok|error",
  "message": "search complete",
  "result_count": 0,
  "results": []
}
```

### 错误处理

- 输入无效 JSON：返回 error 状态
- 缺少必需参数：返回错误提示
- 搜索异常：返回部分结果

## 开发 notes

- 创建时间: 2026-03-17
- 遵循官方三层架构
- 纯文档型 Skill，无 scripts 目录
