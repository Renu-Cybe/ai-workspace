---
name: scheduler
description: |
  定时任务管理器，统一管理 Claude Code Skills 的定时执行。
  支持添加、删除、列出、启用/禁用定时任务。
  底层使用 Windows Task Scheduler，提供自然语言操作接口。
  适用于自动执行 memory-cleanup、developer-growth-analysis 等定期任务。

tools: [Bash, Read, Write, Edit]
context: fork
---

# Scheduler - 定时任务管理器

统一的定时任务管理 Skill，协调其他 Skills 的自动执行。

## 功能

- 添加定时任务（每天、每周、每月、自定义）
- 删除定时任务
- 列出所有定时任务
- 启用/禁用任务
- 立即运行任务
- 查看任务执行历史

## 使用方式

### 自然语言触发

```bash
# 添加定时任务
"每天凌晨清理记忆库"
"每周一早上生成成长报告"
"每周五下班前生成 changelog"

# 管理任务
"列出所有定时任务"
"删除记忆库清理任务"
"禁用成长分析任务"
"立即运行技能验证"

# 查看状态
"显示定时任务状态"
"检查哪些技能设置了定时任务"
```

### JSON 接口

```bash
# 添加任务
echo '{"action": "add", "name": "memory-cleanup", "schedule": "daily", "time": "00:00"}' | skill scheduler

# 列出任务
echo '{"action": "list"}' | skill scheduler

# 删除任务
echo '{"action": "remove", "name": "memory-cleanup"}' | skill scheduler

# 立即运行
echo '{"action": "run", "name": "memory-cleanup"}' | skill scheduler
```

## 预设任务模板

| 任务 | 建议频率 | 命令 |
|------|---------|------|
| memory-cleanup | 每天 00:00 | `echo '{"action":"add","name":"memory-cleanup","schedule":"daily","time":"00:00"}' \| skill scheduler` |
| developer-growth-analysis | 每周一 09:00 | `echo '{"action":"add","name":"dev-growth","schedule":"weekly","day":"mon","time":"09:00","skill":"developer-growth-analysis"}' \| skill scheduler` |
| skill-validating | 每周日 20:00 | `echo '{"action":"add","name":"skill-check","schedule":"weekly","day":"sun","time":"20:00","skill":"skill-validating"}' \| skill scheduler` |
| changelog-generator | 每周五 17:00 | `echo '{"action":"add","name":"weekly-changelog","schedule":"weekly","day":"fri","time":"17:00","skill":"changelog-generator"}' \| skill scheduler` |

## 技术实现

底层使用 Windows Task Scheduler (`schtasks` 命令)：
- 创建 `.bat` 脚本作为任务执行入口
- 使用 `schtasks /Create` 创建定时任务
- 使用 `schtasks /Query` 查询任务状态
- 使用 `schtasks /Delete` 删除任务
- 使用 `schtasks /Run` 立即执行任务

任务脚本存储在 `~/.claude/scheduler/` 目录：
```
~/.claude/scheduler/
├── tasks.json          # 任务配置
├── logs/               # 执行日志
└── scripts/            # 任务脚本
    ├── memory-cleanup.bat
    ├── dev-growth.bat
    └── ...
```
