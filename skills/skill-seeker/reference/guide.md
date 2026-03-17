# skill-seeker Reference

## 内部实现细节

### 输入格式

```json
{
  "url": "https://docs.example.com",
  "name": "target-skill-name",
  "sections": ["api", "guide"]
}
```

### 输出格式

```json
{
  "status": "ok|error",
  "message": "crawl complete",
  "skill_path": "...",
  "files_created": []
}
```

### 错误处理

- URL 无效：返回 error 状态
- 爬取失败：记录错误信息
- 解析异常：返回部分结果

## 开发 notes

- 创建时间: 2026-03-17
- 遵循官方三层架构
- 纯文档型 Skill，无 scripts 目录
