# video-summarizer Reference

## 内部实现细节

### 输入格式

```json
{
  "url": "https://youtube.com/watch?v=...",
  "language": "zh|en|auto",
  "output_format": "text|json|srt"
}
```

### 输出格式

```json
{
  "status": "ok|error",
  "message": "extraction complete",
  "transcript": "...",
  "summary": "..."
}
```

### 错误处理

- URL 无效：返回 error 状态
- 无字幕：尝试语音转录
- 网络异常：重试 3 次后报错

## 开发 notes

- 创建时间: 2026-03-17
- 遵循官方三层架构
- 主脚本: tools/extract_video.py
