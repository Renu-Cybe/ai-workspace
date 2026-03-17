# Claude Memory Skills

> 一套专为 Claude Code 记忆库管理设计的官方 Skills

[![Awesome](https://awesome.re/badge.svg)](https://awesome.re)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

---

## 简介

Claude Memory Skills 是一套帮助用户高效管理 Claude Code 长期记忆库的 Skills。包含自动归档、定时清理、文档爬取等功能，解决记忆库无限增长的问题。

## 核心特性

- 🧠 **分支感知**: 每个 git 分支拥有独立的记忆空间
- 🧹 **自动清理**: 智能归档过期会话，限制历史文件数量
- 📚 **技能生成**: 从任意文档网站自动生成 Claude Skills
- ⚡ **性能优化**: 并行读取 (54x 加速)、LRU 缓存、响应压缩
- 🌡️ **冷热分离**: C盘热数据 + F盘冷数据架构
- 📝 **完整协议**: 标准化的记忆库操作流程

## 快速开始

### 1. 安装 Skills

```bash
# 克隆仓库
git clone https://github.com/Renu-Cybe/ai-workspace.git

# 安装到 Claude Code
cp -r ai-workspace/skills/* ~/.claude/skills/
```

### 2. 安装 Memory Bank Core

```bash
# 复制核心框架
cp -r ai-workspace/core/* ~/.claude/memory-bank/

# 初始化目录结构
mkdir -p ~/.claude/memory-bank/{active,main,shared,errors,fixes}
mkdir -p ~/.claude/memory-bank/main/{decisions,sessions,todos,context}
mkdir -p /f/claude-memory/{archive,backup}
```

### 3. 开始使用

```bash
# 加载核心上下文
~/.claude/memory-bank/scripts/load-context.bat

# 切换分支上下文
~/.claude/memory-bank/scripts/switch-branch.bat feature-xyz

# 运行性能测试
python ~/.claude/memory-bank/tools/performance_optimizer.py
```

**自然语言触发 Skills:**
```
用户: "检查记忆库"
用户: "从 https://docs.example.com 生成技能"
```

## Skills 列表

### 🔧 memory-cleanup
管理记忆库存储空间，自动压缩归档文件。

**触发方式**:
- `"检查记忆库"` - 自动执行清理
- `"模拟清理"` - 预览将要执行的操作
- `"记忆库状态"` - 显示归档统计

**清理规则**:
- 时间规则: 超过30天的文件压缩到 `backup/YYYYMM/`
- 数量规则: `archive/` 超过50个时保留最新50个

[查看详情](./skills/memory-cleanup/SKILL.md)

---

### 🕷️ skill-seeker
爬取任意技术文档网站，生成 Claude Code Skills。

**触发方式**:
- `"从 https://docs.crewai.com 生成技能包"`
- `"爬取 https://react.dev 做成 react 技能"`
- `"快速扫描 https://docs.pydantic.dev 只取5页"`

**工作流程**:
1. 接收文档 URL 和参数
2. 递归爬取同域名页面
3. 提取正文文本和代码示例
4. 生成 `knowledge.md` + `skill.json`

[查看详情](./skills/skill-seeker/SKILL.md)

---

## Core Framework (New in v2.0)

分支感知的 Claude Code 记忆库核心框架。

### 架构概览

```
~/.claude/memory-bank/          # 统一位置
├── context/                     # 核心上下文
│   ├── IDENTITY.md             # AI 身份定义
│   ├── USER.md                 # 用户偏好
│   ├── PROTOCOL.md             # 操作协议
│   └── HEARTBEAT.md            # 维护配置
├── active/                      # 热数据（实时状态）
├── main/                        # 主分支
│   ├── decisions/              # 关键决策
│   ├── sessions/               # 会话历史
│   ├── todos/                  # 任务记录
│   └── context/                # 分支上下文
├── [feature-*/                  # 功能分支（动态创建）
├── shared/                      # 跨分支共享
├── tools/                       # 性能优化工具
└── scripts/                     # 自动化脚本
```

### 核心组件

| 组件 | 用途 | 位置 |
|------|------|------|
| **load-context** | 启动时加载核心上下文 | `scripts/load-context.bat` |
| **switch-branch** | 切换分支上下文 | `scripts/switch-branch.bat` |
| **performance_optimizer** | 性能优化工具集 | `tools/performance_optimizer.py` |

### 性能优化示例

```python
from tools.performance_optimizer import parallel_read, cached_read

# 并行读取多个文件（54x 加速）
results = parallel_read(['file1.md', 'file2.md'])

# 缓存读取
cached = cached_read('large_file.md')
```

[查看 Core Framework 详情](./core/README.md)

---

## 目录结构

### v2.0 新架构 (推荐)

```
~/.claude/memory-bank/          # 统一记忆库位置
├── context/                     # 核心上下文（每次启动加载）
│   ├── IDENTITY.md             # AI 身份定义
│   ├── USER.md                 # 用户偏好
│   ├── PROTOCOL.md             # 操作协议
│   └── HEARTBEAT.md            # 维护配置
├── active/                      # 热数据（实时状态）
│   └── MEMORY.md               # 当前会话状态
├── main/                        # 主分支数据
│   ├── decisions/              # 关键决策记录
│   ├── sessions/               # 会话历史归档
│   ├── todos/                  # 任务记录
│   └── context/                # 分支特定上下文
├── feature-*/                   # 功能分支（动态创建）
├── shared/                      # 跨分支共享数据
├── tools/                       # 性能优化工具
└── scripts/                     # 自动化脚本
```

### v1.0 旧架构（向后兼容）

```
C盘 (热数据)
└── ~/.claude/projects/<project>/memory/
    ├── PROTOCOL.md          # 操作协议
    ├── MEMORY.md            # 当前状态
    ├── cleanup.sh           # 清理脚本
    ├── tools/
    │   └── skill_seeker.py  # 文档爬虫
    └── session/
        └── current.md       # 实时备份

F盘 (冷数据)
└── F:\claude-memory\
    ├── archive\             # 会话历史归档
    ├── backup\              # 压缩备份 (YYYYMM/)
    ├── decisions\           # 决策记录
    ├── projects\            # 项目历史
    └── cleanup.log          # 清理日志
```

**迁移指南**: 详见 [docs/ARCHITECTURE-v2.0.md](./docs/ARCHITECTURE-v2.0.md)

## 协议规范

### 启动流程 (v2.0)

```
1. 检测当前 git 分支
   └── 加载 memory-bank/[branch]/context/

2. 加载核心上下文
   ├── context/IDENTITY.md
   ├── context/USER.md
   ├── context/PROTOCOL.md
   └── context/HEARTBEAT.md

3. 检查 session/current.md 是否存在
   ├── 存在 → 询问"上次异常结束，是否恢复？"
   └── 不存在 → 正常开始

4. 执行清理检查
   └── 调用 memory-cleanup skill
```

### 对话进行中

- **关键决策** → 追加到 `[branch]/decisions/`
- **状态更新** → 写入 `active/MEMORY.md`
- **错误记录** → 追加到 `errors/`

### 会话结束

- `current.md` → 归档到 `[branch]/sessions/`
- 更新索引 `shared/.index/sessions.json`
- 清理 `current.md`
- 更新 `MEMORY.md`

## 安装要求

- Claude Code CLI
- Python 3.8+ (用于 performance_optimizer 和 skill-seeker)
- Windows: `py` 命令可用 / macOS/Linux: `python3`

## 贡献指南

欢迎提交 PR！请遵循以下规范：

1. **Skills** 放在 `skills/<skill-name>/` 目录
2. **Core Framework** 放在 `core/` 目录
3. 必须包含 `SKILL.md` 或 `README.md` 文档
4. 在 README 中添加介绍和链接
5. 更新目录结构文档

## 相关资源

- [Claude Code 官方文档](https://docs.anthropic.com/claude-code)
- [Awesome Claude Skills](https://github.com/ComposioHQ/awesome-claude-skills)
- [Tinyash Skill 介绍](https://www.tinyash.com/blog/claude-code-skill/)

## 许可协议

MIT License - 详见 [LICENSE](./LICENSE)

---

## 更新日志

### v2.0.0 (2026-03-17)
- ✨ 新增分支感知架构 (Core Framework)
- ✨ 新增性能优化工具 (54x 加速)
- ✨ 新增自动化脚本集
- 📝 统一的记忆库目录结构
- 📚 完整的架构迁移文档

### v1.0.0
- 🧹 memory-cleanup Skill
- 🕷️ skill-seeker Skill
- 🌡️ 冷热数据分离架构

---

**Made with for Claude Code users**

*Latest Release: v2.0.0 | [查看全部版本](./CHANGELOG.md)*
