---
name: memory-cleanup
description: |
  清理和归档记忆库中的历史会话文件。自动压缩超过30天的归档文件，
  限制 archive/ 目录最多保留50个最新文件，超出部分压缩到 backup/。
  支持手动触发、自动检查和模拟运行三种模式。

tools: [Bash, Read, Edit, Write]
context: fork
---

# Memory Cleanup Skill

## 用途

管理记忆库的存储空间，防止历史归档文件无限增长。

## 适用场景

- 启动 Claude Code 时自动检查归档状态
- 手动清理过期的会话历史
- 查看归档统计信息（文件数量、备份大小）
- 模拟运行查看将要执行的操作

## 使用方式

### 1. 自动检查（启动时执行）
```
用户: "检查记忆库"
用户: "清理归档文件"
用户: "启动清理检查"
```

### 2. 手动触发
```
用户: "手动清理记忆库"
用户: "执行归档清理"
用户: "运行 cleanup"
```

### 3. 模拟运行
```
用户: "模拟清理"
用户: "查看清理计划"
用户: "dry run 清理"
```

### 4. 查看统计
```
用户: "记忆库状态"
用户: "查看归档统计"
用户: "backup 有多大"
```

## 工作流程

1. **获取当前状态**
   - `!`ls -la ~/.claude/projects/C--Users-Administrator/memory/``
   - `!`ls /f/claude-memory/archive/ | wc -l``
   - `!`du -sh /f/claude-memory/backup/ 2>/dev/null || echo "0M"``

2. **执行清理**
   - 调用 `cleanup.sh` 脚本
   - 读取 `cleanup.log` 显示结果

3. **验证结果**
   - 再次检查 archive/ 和 backup/ 状态
   - 显示清理前后的对比

## 清理规则

| 规则 | 条件 | 操作 |
|------|------|------|
| 时间规则 | 文件超过30天 | 压缩到 `backup/YYYYMM/` |
| 数量规则 | archive/ 超过50个 | 保留最新50个，其余压缩 |

## 文件位置

- **脚本**: `C:\Users\Administrator\.claude\projects\C--Users-Administrator\memory\cleanup.sh`
- **归档目录**: `F:\claude-memory\archive\`
- **备份目录**: `F:\claude-memory\backup\`
- **日志文件**: `F:\claude-memory\cleanup.log`

## 参数

通过 `$ARGUMENTS` 接收：
- `manual` - 手动触发模式
- `dry-run` - 模拟运行，不实际执行
- （无参数）- 启动检查模式

## 示例输出

```
==================================================
开始清理 [手动触发]
==================================================
archive/ 共有 45 个文件
当前状态: archive=45个, backup=12.5MB
完成: 无需清理
```

## 注意事项

1. 压缩格式为 `.gz`，保留原始文件名
2. backup/ 按年月分子目录（如 `backup/202603/`）
3. 清理操作不可逆，建议先使用 dry-run 查看计划
4. 日志会追加写入 `cleanup.log`
