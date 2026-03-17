---
name: memory-manager
description: |
  统一记忆库管理工具，整合标签、搜索、分支、看板等功能
tools: [Read, Write, Bash, Glob]
context: fork
---

# Memory Manager

统一的记忆库管理 Skill，整合标签、搜索、分支、看板等功能。

## 使用方式

自然语言触发，支持中文和英文。

### 状态查看

- "检查记忆库状态"
- "显示记忆库看板"
- "记忆库统计"
- "显示当前分支"

### 搜索功能

- "搜索关于 [关键词] 的会话"
- "找一下包含 [关键词] 的文件"
- "按标签 [标签名] 搜索"

### 分支管理

- "切换到 [分支名] 分支"
- "创建新分支 [分支名]"
- "列出所有分支"

### 标签管理

- "给所有会话打标签"
- "列出所有标签"
- "重新索引记忆库"

## 底层实现

调用 `~/.claude/projects/C--Users-Administrator/memory/tools/` 目录下的工具：

| 功能 | 底层工具 |
|------|---------|
| 状态看板 | dashboard.bat |
| 全文搜索 | search.bat |
| 分支切换 | branch.bat |
| 自动标签 | tag.bat |
