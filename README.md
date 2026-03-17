# Claude Code Workspace

> **四自增强框架** · 自感知 · 自适应 · 自组织 · 自编译
>
> 记忆库管理 + 性能优化 + 技能开发

[![Awesome](https://awesome.re/badge.svg)](https://awesome.re)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

---

## 简介

Claude Code Workspace 是一个基于**四自理念**设计的增强框架：

| 自感知 | 自适应 | 自组织 | 自编译 |
|--------|--------|--------|--------|
| 感知自身状态和环境 | 根据上下文自动调整 | 自动维护结构和关系 | 根据需求生成组件 |

为 Claude Code 提供**记忆库管理**、**性能优化**和**技能开发**三大核心能力。

### 三大组成部分

```
┌─────────────────────────────────────────────────────────┐
│                  Claude Code Workspace                   │
├──────────────┬──────────────────┬───────────────────────┤
│  🧠 Core     │   ⚡ Skills      │   🔧 Tools            │
│  核心框架    │   官方技能       │   开发工具            │
├──────────────┼──────────────────┼───────────────────────┤
│ • 分支感知   │ • memory-cleanup │ • performance_optimizer│
│ • 性能优化   │ • skill-seeker   │ • branch_manager      │
│ • 自动化脚本 │ • video-summarizer│ • auto_tagger        │
│ • 上下文管理 │ • (11+ skills)   │ • ...                 │
└──────────────┴──────────────────┴───────────────────────┘
```

- **Core Framework**: 分支感知的记忆库架构 + 性能优化工具集
- **Skills**: 11+ 官方 Claude Code Skills，支持自然语言触发
- **Tools**: 底层工具库，支持脚本化调用

**适用场景**: 长期项目开发、多分支协作、大规模记忆库管理、性能敏感型工作流

---

## 核心特性（四自实现）

| 能力 | 特性 | 说明 |
|------|------|------|
| **自感知** | 🧠 分支感知 | 每个 git 分支拥有独立记忆空间 |
| **自适应** | ⚡ 性能优化 | 并行读取 (62x 加速)、LRU 缓存、响应压缩 |
| **自组织** | 🧹 自动清理 | 智能归档、自动索引、智能标签 |
| **自编译** | 📚 技能生成 | 从文档自动生成 Claude Skills |
| **基础** | 🌡️ 冷热分离 | C盘热数据 + F盘冷数据架构 |
| **规范** | 📝 完整协议 | 标准化的记忆库操作流程 |

## 快速开始

### 1. 安装 Skills（官方技能）

```bash
# 克隆仓库
git clone https://github.com/Renu-Cybe/ai-workspace.git

# 安装 Skills 到 Claude Code
cp -r ai-workspace/skills/* ~/.claude/skills/

# 现在可以用自然语言触发
# "检查记忆库"
# "从 https://docs.example.com 生成技能"
```

### 2. 安装 Core Framework（核心框架）

```bash
# 安装核心框架
cp -r ai-workspace/core/* ~/.claude/memory-bank/

# 初始化目录结构
mkdir -p ~/.claude/memory-bank/{active,main,shared,errors,fixes,tools,scripts}
mkdir -p ~/.claude/memory-bank/main/{decisions,sessions,todos,context}
```

### 3. 启动使用

```bash
# 加载核心上下文
~/.claude/memory-bank/scripts/load-context.bat

# 测试性能优化
python ~/.claude/memory-bank/tools/performance_optimizer.py
```

---

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

### 完整 Skills 列表

| Skill | 功能 | 触发示例 |
|-------|------|----------|
| **memory-cleanup** | 记忆库清理归档 | `"检查记忆库"` |
| **skill-seeker** | 文档爬取生成技能 | `"从 https://docs.example.com 生成技能"` |
| **video-summarizer** | 视频字幕提取总结 | `"总结这个 YouTube 视频"` |
| **memory-manager** | 统一记忆库管理 | `"查看记忆库状态"` |
| **changelog-generator** | 自动生成 changelog | `"生成发布日志"` |
| **content-research-writer** | 内容研究与写作 | `"研究并撰写文章"` |
| **artifacts-builder** | 创建可视化 artifacts | `"创建一个交互式图表"` |
| **brand-guidelines** | Anthropic 品牌风格 | `"应用品牌风格"` |
| **canvas-design** | 画布设计创作 | `"设计一个海报"` |
| **developer-growth-analysis** | 开发者成长分析 | `"分析我的编码习惯"` |
| **connect** | 连接 500+ 应用 | `"发送邮件到..."` |

---

## Core Framework (New in v2.0)

基于**四自理念**的分支感知记忆库核心框架。

### 四自实现

| 能力 | 实现组件 | 说明 |
|------|----------|------|
| **自感知** | IDENTITY.md, HEARTBEAT.md, active/MEMORY.md | 感知自身状态、环境、历史 |
| **自适应** | switch-branch, 动态协议加载 | 根据 git 分支调整上下文 |
| **自组织** | 自动目录创建, 智能归档, 自动索引 | 自动维护结构和数据关系 |
| **自编译** | performance_optimizer (62x 加速) | 根据需求生成和优化组件 |

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

## 协议规范（四自流程）

### 启动流程 - 自感知

```
1. 加载核心上下文（感知自身身份和环境）
   ├── context/IDENTITY.md    # 自感知：我是谁
   ├── context/USER.md        # 自感知：用户是谁
   ├── context/PROTOCOL.md    # 自感知：操作规范
   └── context/HEARTBEAT.md   # 自感知：维护配置

2. 检测当前 git 分支（感知环境）
   └── 确定 [branch] = main 或 feature-xxx

3. 检查 session/current.md（感知历史）
   ├── 存在 → 询问"上次异常结束，是否恢复？"
   └── 不存在 → 正常开始
```

### 运行流程 - 自适应

```
1. 根据分支自适应加载上下文
   └── [branch]/context/PROJECT.md

2. 根据任务自适应启用优化
   ├── 多文件读取 → 启用 ParallelReader
   ├── 重复读取 → 启用 FileCache
   └── 长输出 → 启用 ResponseOptimizer

3. 对话中实时记录
   ├── 关键决策 → [branch]/decisions/
   ├── 状态更新 → active/MEMORY.md
   └── 错误记录 → errors/
```

### 维护流程 - 自组织

```
1. 自动目录维护
   └── 切换分支时自动创建目录结构

2. 自动归档
   └── 会话结束 → [branch]/sessions/ + 更新索引

3. 自动清理
   └── 定期归档旧文件到 F:\claude-memory\backup\
```

### 扩展流程 - 自编译

```
1. 生成新 Skill
   └── 输入文档 URL → skill-seeker → Skill 包

2. 性能优化
   └── 监控数据 → performance_optimizer → 优化建议

3. 知识编译
   └── 原始文档 → 结构化知识 → 上下文文件
```

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

### v2.0.0 (2026-03-17) - 四自框架

基于**自感知、自适应、自组织、自编译**四自理念的全新架构：

- 🧠 **自感知**: IDENTITY.md, HEARTBEAT.md, 状态追踪系统
- 🔄 **自适应**: 分支感知上下文、自适应缓存策略
- 🏗️ **自组织**: 自动目录创建、智能归档、自动索引
- ⚙️ **自编译**: Skill生成、性能优化 (62x 加速)、知识编译
- ✨ 新增自动化脚本集
- 📝 统一的记忆库目录结构
- 📚 完整的架构迁移文档

### v1.0.0
- 🧹 memory-cleanup Skill
- 🕷️ skill-seeker Skill
- 🌡️ 冷热数据分离架构

---

**四自框架** · 自感知 · 自适应 · 自组织 · 自编译

*Latest Release: v2.0.0 | [查看全部版本](./CHANGELOG.md) | [GitHub](https://github.com/Renu-Cybe/ai-workspace)*
