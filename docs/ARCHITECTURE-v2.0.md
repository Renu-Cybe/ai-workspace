# 架构迁移记录

> **P0 重构** - 统一记忆库架构
> 迁移日期: 2026-03-17

---

## 迁移前架构

```
~/.claude/projects/C--Users-Administrator/memory/
├── MEMORY.md          (186行，臃肿)
├── PROTOCOL.md        (协议)
└── session/
    └── current.md

~/.claude/memory-bank/ (新创建)
├── errors/            (自我纠错)
├── fixes/
└── tools/

F:\claude-memory\memory-bank\ (冷数据)
├── main/
├── feature-test/
└── shared/
```

## 迁移后架构

```
~/.claude/memory-bank/          (统一位置)
├── context/                     (核心上下文)
│   ├── IDENTITY.md             (身份定义)
│   ├── USER.md                 (用户偏好)
│   ├── PROTOCOL.md             (操作协议)
│   └── HEARTBEAT.md            (维护配置)
├── active/                      (热数据)
│   └── MEMORY.md               (精简版，实时状态)
├── main/                        (主分支)
│   ├── decisions/
│   ├── sessions/
│   ├── todos/
│   └── context/
├── feature-test/                (功能分支)
├── errors/                      (错误记录)
├── fixes/                       (修复方案)
├── stats/                       (统计报告)
├── sessions/                    (会话归档)
├── skills/                      (技能知识库)
├── shared/                      (跨分支共享)
├── schedule/                    (定时任务)
└── tools/                       (工具脚本)
```

## 迁移内容

### 1. 拆分 MEMORY.md
| 原内容 | 新位置 | 行数 |
|--------|--------|------|
| 身份定义 | context/IDENTITY.md | ~30 |
| 用户偏好 | context/USER.md | ~20 |
| 维护配置 | context/HEARTBEAT.md | ~40 |
| 实时状态 | active/MEMORY.md | ~30 |
| 协议 | context/PROTOCOL.md | ~50 |

### 2. 迁移 F盘数据
| 源位置 | 目标位置 | 状态 |
|--------|----------|------|
| F:\...\memory-bank\main\ | ~/.claude/memory-bank/main/ | ✅ 完成 |
| F:\...\memory-bank\feature-test\ | ~/.claude/memory-bank/feature-test/ | ✅ 完成 |
| F:\...\memory-bank\shared\ | ~/.claude/memory-bank/shared/ | ✅ 完成 |

### 3. 保留原位置
| 原位置 | 用途 | 说明 |
|--------|------|------|
| ~/.claude/skills/ | Skills | 保持不变 |
| F:\claude-memory\ | 冷数据归档 | 作为备份保留 |

## 路径变更

| 旧路径 | 新路径 |
|--------|--------|
| ~/.claude/projects/.../memory/MEMORY.md | ~/.claude/memory-bank/active/MEMORY.md |
| ~/.claude/projects/.../memory/PROTOCOL.md | ~/.claude/memory-bank/context/PROTOCOL.md |
| F:\claude-memory\memory-bank\main\ | ~/.claude/memory-bank/main/ |

## 后续工作

- [ ] 更新所有脚本中的路径引用
- [ ] 创建分支切换脚本
- [ ] 创建启动加载脚本
- [ ] 更新 hooks 配置
- [ ] 测试完整流程

## 备份

原文件保留在:
- `~/.claude/projects/C--Users-Administrator/memory/` (旧版 MEMORY.md)
- `F:\claude-memory\memory-bank\` (原始冷数据)

---
*迁移完成: 2026-03-17*
