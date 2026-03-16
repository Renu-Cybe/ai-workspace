# Claude Memory Skills

> 一套专为 Claude Code 记忆库管理设计的官方 Skills

[![Awesome](https://awesome.re/badge.svg)](https://awesome.re)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

---

## 简介

Claude Memory Skills 是一套帮助用户高效管理 Claude Code 长期记忆库的 Skills。包含自动归档、定时清理、文档爬取等功能，解决记忆库无限增长的问题。

## 核心特性

- 🧹 **自动清理**: 智能归档过期会话，限制历史文件数量
- 📚 **技能生成**: 从任意文档网站自动生成 Claude Skills
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

### 2. 初始化记忆库

```bash
# 创建记忆库目录结构
mkdir -p ~/.claude/projects/<project-name>/memory
mkdir -p /f/claude-memory/{archive,backup,decisions,projects}
```

### 3. 开始使用

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

## 记忆库架构

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

## 协议规范

### 启动时必须执行

```
1. 检查 session/current.md 是否存在
   ├── 存在 → 询问"上次异常结束，是否恢复？"
   └── 不存在 → 正常开始

2. 执行清理检查 bash cleanup.sh

3. 确认存储架构
```

### 对话进行中实时写入

- 关键决策 → 追加到 `session/current.md`
- 状态更新 → 写入 `MEMORY.md`

### 结束清理

- `current.md` → 归档到 `F:\claude-memory\archive\`
- 清空 `current.md`
- 更新 `MEMORY.md`

## 安装要求

- Claude Code CLI
- Bash (Windows Git Bash / WSL / macOS / Linux)
- Python 3 (可选，用于 skill-seeker 的高级功能)

## 贡献指南

欢迎提交 PR！请遵循以下规范：

1. 每个 Skill 放在 `skills/<skill-name>/` 目录
2. 必须包含 `SKILL.md` (YAML frontmatter + 说明)
3. 在 README 中添加 Skill 介绍
4. 更新目录结构文档

## 相关资源

- [Claude Code 官方文档](https://docs.anthropic.com/claude-code)
- [Awesome Claude Skills](https://github.com/ComposioHQ/awesome-claude-skills)
- [Tinyash Skill 介绍](https://www.tinyash.com/blog/claude-code-skill/)

## 许可协议

MIT License - 详见 [LICENSE](./LICENSE)

---

**Made with ❤️ for Claude Code users**
