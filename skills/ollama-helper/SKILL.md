---
name: ollama-helper
description: |
  调用本地 Ollama 模型（Qwen）进行代码辅助，支持代码补全、解释、审查和聊天
tools: [Bash, Read]
context: fork
---

# Ollama Helper

## 用途

调用本地 Ollama 模型进行代码辅助，无需联网即可使用 AI 能力。

## 适用场景

- 代码补全和生成
- 代码解释和文档
- 代码审查和优化
- 技术问答和聊天

## 使用方式

### 1. 列出可用模型
```
User: "列出 Ollama 模型"
User: "ollama list"
```

### 2. 代码补全
```
User: "补全这段代码"
User: "ollama complete"
```

### 3. 代码解释
```
User: "解释这段代码"
User: "ollama explain"
```

### 4. 代码审查
```
User: "审查这段代码"
User: "ollama review"
```

## 工作流程

1. **接收命令**
   - 解析用户指令
   - 确定操作类型

2. **调用 Ollama**
   - 构建请求参数
   - 发送 API 请求

3. **返回结果**
   - 格式化输出
   - 显示响应内容

## 示例

**User**: "用 ollama 解释这个函数"

**Claude**: 调用本地 Qwen 模型分析代码...

