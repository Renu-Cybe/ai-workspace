# Scheduler Skill 使用指南

## 概述

Scheduler 是一个定时任务管理器，基于 Windows Task Scheduler 实现，用于管理 Claude Code Skills 的定时执行。

## 安装前提

- Windows 10/11
- schtasks 命令可用（系统自带）
- 管理员权限（首次创建任务时需要）

## 快速开始

### 1. 列出所有定时任务

```bash
echo '{"action": "list"}' | skill scheduler
```

### 2. 添加每日任务（memory-cleanup）

```bash
echo '{"action": "add", "name": "memory-cleanup", "schedule": "daily", "time": "00:00"}' | skill scheduler
```

### 3. 添加每周任务（developer-growth-analysis）

```bash
echo '{"action": "add", "name": "dev-growth", "skill": "developer-growth-analysis", "schedule": "weekly", "day": "mon", "time": "09:00"}' | skill scheduler
```

## 支持的调度类型

| 类型 | 参数 | 示例 |
|------|------|------|
| daily | time | `"schedule": "daily", "time": "00:00"` |
| weekly | day, time | `"schedule": "weekly", "day": "mon", "time": "09:00"` |
| monthly | date, time | `"schedule": "monthly", "date": "1", "time": "00:00"` |
| once | time | `"schedule": "once", "time": "14:30"` |

星期缩写：mon, tue, wed, thu, fri, sat, sun

## 预设任务模板

### 记忆库清理（每天凌晨）

```bash
echo '{
  "action": "add",
  "name": "memory-cleanup",
  "skill": "memory-cleanup",
  "schedule": "daily",
  "time": "00:00"
}' | skill scheduler
```

### 开发者成长分析（每周一早上）

```bash
echo '{
  "action": "add",
  "name": "dev-growth",
  "skill": "developer-growth-analysis",
  "schedule": "weekly",
  "day": "mon",
  "time": "09:00"
}' | skill scheduler
```

### 技能验证（每周日晚上）

```bash
echo '{
  "action": "add",
  "name": "skill-check",
  "skill": "skill-validating",
  "schedule": "weekly",
  "day": "sun",
  "time": "20:00"
}' | skill scheduler
```

### 生成 Changelog（每周五下班前）

```bash
echo '{
  "action": "add",
  "name": "weekly-changelog",
  "skill": "changelog-generator",
  "schedule": "weekly",
  "day": "fri",
  "time": "17:00"
}' | skill scheduler
```

## 管理任务

### 查看任务状态

```bash
echo '{"action": "list"}' | skill scheduler
```

### 立即运行任务

```bash
echo '{"action": "run", "name": "memory-cleanup"}' | skill scheduler
```

### 禁用任务

```bash
echo '{"action": "disable", "name": "memory-cleanup"}' | skill scheduler
```

### 启用任务

```bash
echo '{"action": "enable", "name": "memory-cleanup"}' | skill scheduler
```

### 删除任务

```bash
echo '{"action": "remove", "name": "memory-cleanup"}' | skill scheduler
```

### 查看日志

```bash
echo '{"action": "logs", "name": "memory-cleanup", "lines": 20}' | skill scheduler
```

## 文件位置

```
~/.claude/scheduler/
├── tasks.json          # 任务配置
├── scripts/            # 批处理脚本
│   ├── memory-cleanup.bat
│   ├── dev-growth.bat
│   └── ...
└── logs/               # 执行日志
    ├── memory-cleanup.log
    └── ...
```

## Windows Task Scheduler 位置

创建的任务位于：`任务计划程序库 > ClaudeScheduler`

你可以通过以下方式查看：
1. 按 Win + R，输入 `taskschd.msc`
2. 在左侧导航栏找到 `任务计划程序库 > ClaudeScheduler`

## 故障排除

### 任务创建失败

- 确保以管理员身份运行 Claude Code
- 检查 schtasks 命令是否可用：`schtasks /?`

### 任务不执行

- 检查任务是否在 Windows Task Scheduler 中显示
- 查看日志文件：`~/.claude/scheduler/logs/`
- 手动运行批处理脚本测试

### 权限问题

首次创建任务需要管理员权限。如果失败，可以：
1. 以管理员身份运行 Claude Code
2. 或手动在 Task Scheduler 中创建任务

## 自然语言触发

支持以下自然语言命令：

- `"列出所有定时任务"`
- `"每天凌晨清理记忆库"`
- `"每周一早上生成成长报告"`
- `"立即运行 memory-cleanup"`
- `"删除 dev-growth 任务"`
- `"禁用 skill-check 任务"`

## 注意事项

1. 任务名称不能包含空格或特殊字符
2. 时间格式为 24 小时制（HH:MM）
3. 删除任务会同时删除配置和 Windows Task Scheduler 中的任务
4. 日志文件会自动追加，建议定期清理
