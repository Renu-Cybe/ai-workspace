# ollama-helper Reference

## 内部实现细节

### 输入格式

```json
{
  "action": "install|run|query",
  "model": "llama2|codellama|...",
  "prompt": "..."
}
```

### 输出格式

```json
{
  "status": "ok|error",
  "message": "result message",
  "output": "..."
}
```

### 错误处理

- Ollama 未安装：提示安装命令
- 模型不存在：自动下载
- 执行超时：返回部分输出

## 开发 notes

- 创建时间: 2026-03-17
- 遵循官方三层架构
- 主脚本: ollama_helper.py
