# USER.md - 用户偏好配置

> **四自框架用户配置** - 自感知层：记录用户习惯、偏好和上下文
>
> **四自能力**: 自感知 · 自适应 · 自组织 · 自编译
>
> 此文件在上下文压缩后必须保留

---

## 用户档案

- **用户名**: Administrator
- **位置**: C:\Users\Administrator
- **平台**: Windows 10 Pro
- **Shell**: bash (Git Bash)
- **网络代理**: http://127.0.0.1:23968

## 工作偏好

### 沟通风格
- 语言: 中文为主
- 风格: 简洁直接，避免冗余
- 反馈: 明确指示，及时纠正

### 技术栈偏好
| 类别 | 偏好 |
|------|------|
| 语言 | Python, JavaScript/TypeScript |
| 框架 | React, Node.js |
| 工具 | Claude Code, VS Code |
| 版本控制 | Git |

### 开发习惯
- 先调研再实现
- 重视代码质量和可维护性
- 喜欢自动化工具
- 注重文档和记录

## 项目上下文

### 当前活跃项目
| 项目 | 位置 | 状态 |
|------|------|------|
| ai-workspace | GitHub | 活跃 |
| claude-memory-skills | F:\claude-memory\ | 开源维护 |
| memory-bank | ~/.claude/memory-bank/ | 重构中 |

### 关键路径
- **热数据**: C:\Users\Administrator\.claude\
- **冷数据**: F:\claude-memory\
- **GitHub**: https://github.com/Renu-Cybe/ai-workspace

## 历史决策

### 架构决策
1. **记忆库分层**: C盘=热数据，F盘=冷数据
2. **分支感知**: 基于git分支切换记忆上下文
3. **自我纠错**: 错误记录到 memory-bank/errors/

### 技术选型
1. **Python 3.12**: 主要脚本语言
2. **JSON**: 数据存储格式
3. **Markdown**: 文档标准格式
4. **Git**: 版本控制

## 常用命令

```bash
# 检查网络代理
powershell -Command "Get-ItemProperty -Path 'HKCU:\Software\Microsoft\Windows\CurrentVersion\Internet Settings' | Select-Object ProxyEnable, ProxyServer"

# 查看记忆库状态
ls ~/.claude/memory-bank/

# 生成周错误报告
python ~/.claude/memory-bank/tools/self_correction.py -c "from self_correction import generate_weekly_report; print(generate_weekly_report())"
```

## 特殊需求

- 需要网络代理才能访问外网
- 偏好自动化工具减少重复工作
- 重视知识沉淀和文档化
- 喜欢探索新工具和框架

---
*最后更新: 2026-03-17 | 架构版本: v2.0*
