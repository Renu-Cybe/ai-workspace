# 记忆库操作协议 v2.0
# ~/.claude/memory-bank/context/PROTOCOL.md

> **四自框架操作协议** - 自感知 · 自适应 · 自组织 · 自编译
>
> 本协议定义了基于四自理念的记忆库操作规范

## 重要：四自框架操作规范

本框架基于四个核心自演化能力设计，操作时必须遵循：

| 能力 | 含义 | 操作要求 |
|------|------|----------|
| **自感知** | 感知自身状态和环境 | 每次启动必须加载核心上下文 |
| **自适应** | 根据上下文调整行为 | 检测 git 分支并加载对应上下文 |
| **自组织** | 自动维护结构和关系 | 自动创建目录，自动归档，自动索引 |
| **自编译** | 生成和优化组件 | 根据需求生成 Skill，优化性能 |

## 存储架构 v2.0（四自实现）

基于四自理念的统一存储架构：

### 自感知层（核心上下文）
```
~/.claude/memory-bank/context/       # 自感知：定义身份、偏好、协议、维护
├── IDENTITY.md                      # 自感知：AI 身份定义
├── USER.md                          # 自感知：用户偏好
├── PROTOCOL.md                      # 自感知：本协议
└── HEARTBEAT.md                     # 自感知：维护配置
```

### 自适应层（分支特定数据）
```
~/.claude/memory-bank/[branch]/      # 自适应：根据分支加载不同数据
├── decisions/                       # 自适应：分支特定决策
├── sessions/                        # 自适应：分支特定会话
├── todos/                           # 自适应：分支特定任务
└── context/                         # 自适应：分支特定上下文
```

### 自组织层（自动维护）
```
~/.claude/memory-bank/shared/        # 自组织：跨分支共享数据
├── .index/                          # 自组织：自动索引
└── tags.json                        # 自组织：自动标签映射
```

### 自编译层（生成和优化）
```
~/.claude/memory-bank/tools/         # 自编译：性能优化工具
└── performance_optimizer.py         # 自编译：62x 性能优化

~/.claude/memory-bank/scripts/       # 自编译：自动化脚本
├── load-context.bat                 # 自编译：加载上下文
├── switch-branch.bat                # 自编译：切换分支
└── save-session.bat                 # 自编译：保存会话
```

### 冷热分离（持久化）
```
F:\claude-memory\                    # 冷数据（历史归档）
├── backup\                          # 压缩备份
└── archive\                         # 旧归档
```
└── cleanup.log                  # 清理日志
```

## 启动流程（四自流程）

### 1. 自感知 - 加载核心上下文
```
启动时必须首先加载自感知层：
├── context/IDENTITY.md    # 感知自身身份
├── context/USER.md        # 感知用户偏好
├── context/PROTOCOL.md    # 感知操作规范
└── context/HEARTBEAT.md   # 感知维护配置
```

### 2. 自适应 - 检测并适应环境
```
检测当前 git 分支
└── 确定 [branch] = main 或 feature-xxx

加载分支上下文
└── [branch]/context/PROJECT.md (如果存在)

自适应启用优化
├── 多文件读取 → 启用 ParallelReader
├── 重复读取 → 启用 FileCache
└── 长输出 → 启用 ResponseOptimizer
```

### 3. 自感知 - 检查历史会话
```
检查 session/current.md
├── 存在且非空 → 询问"上次异常结束，是否恢复？"
└── 不存在/空 → 正常开始
```

### 4. 自组织 - 执行清理检查
```
调用 memory-cleanup skill 或 "检查记忆库"
└── 自动归档过期文件，更新索引
```

## 对话进行（四自协同）

### 自感知 - 实时记录
- **关键决策** → 追加到 `[branch]/decisions/`
- **状态更新** → 写入 `active/MEMORY.md`
- **错误记录** → 追加到 `errors/`

### 自适应 - 动态调整
- 根据任务类型调整策略
- 根据性能数据启用优化

### 自组织 - 自动维护
- 自动更新索引
- 自动提取标签
- 自动维护目录结构

### 自编译 - 持续优化
- 收集使用模式
- 生成优化建议
- 编译新知识

## 会话结束（四自归档）

### 1. 自组织 - 自动归档
```
保存会话
└── current.md → [branch]/sessions/[date]-[number].md

更新索引
└── 更新 shared/.index/sessions.json

清空 current.md
```

### 2. 自感知 - 更新状态
```
更新 active/MEMORY.md 状态
└── 记录本次会话完成情况
```
4. 更新 active/MEMORY.md 状态
```

**文件命名规范:**
```
[date]-[branch]-[number]_[tag1][tag2].md
示例: 2026-03-16-main-001_[memory-system][skill-dev].md
```

### 5. 文件位置总览
| 文件 | 位置 | 作用 |
|------|------|------|
| 本协议 | `~/.claude/memory-bank/context/PROTOCOL.md` | 操作规范 |
| 当前状态 | `~/.claude/memory-bank/active/MEMORY.md` | 实时状态 |
| 当前会话 | `~/.claude/memory-bank/session/current.md` | 实时备份 |
| 主分支记忆 | `~/.claude/memory-bank/main/` | 分支感知记忆库 ⭐ |
| 功能分支 | `~/.claude/memory-bank/[branch]/` | 动态创建 |
| 共享数据 | `~/.claude/memory-bank/shared/` | 跨分支共享 |
| 冷数据备份 | `F:\claude-memory\backup\` | 压缩归档 |
| 加载脚本 | `~/.claude/memory-bank/scripts/load-context.bat` | 启动加载 |
| 切换脚本 | `~/.claude/memory-bank/scripts/switch-branch.bat` | 分支切换 |
| 性能工具 | `~/.claude/memory-bank/tools/performance_optimizer.py` | 性能优化 |
| **Skill: cleanup** | `~/.claude/skills/memory-cleanup/` | 官方 Skill：清理记忆库 |
| **Skill: seeker** | `~/.claude/skills/skill-seeker/` | 官方 Skill：文档转技能 |

## 定时清理机制（四自实现）

**自组织 + 自编译协同工作**

### 触发方式
```bash
# 自然语言触发（推荐）
"检查记忆库"     → 调用 memory-cleanup skill（自编译生成）
"模拟清理"       → 执行 dry-run 模式
"记忆库状态"     → 显示统计信息

# 脚本触发（自编译）
py ~/.claude/memory-bank/tools/performance_optimizer.py
```

### 清理规则（自组织）
- 时间规则: `sessions/` 超过30天的文件归档到 `F:\claude-memory\backup\YYYYMM\`
- 数量规则: `sessions/` 超过100个时，保留最新100个
- 压缩格式: `.gz` (冷数据)

### 日志位置
**自感知**: `F:\claude-memory\cleanup.log`

---
VERSION: 2.0.0
PHILOSOPHY: 四自框架 (自感知 · 自适应 · 自组织 · 自编译)
LAST_UPDATE: 2026-03-17
