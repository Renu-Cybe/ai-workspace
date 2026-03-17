# MEMORY.md - 当前状态

> **四自框架实时状态** - 自感知 · 自适应 · 自组织 · 自编译
> 详细历史已迁移到 context/ 和 sessions/

---

## 当前状态 | 2026-03-17

| 任务 | 状态 | 备注 |
|------|------|------|
| **P0 架构重构** | ✅ 已完成 | 统一记忆目录结构 |
| **数据迁移** | ✅ 已完成 | F盘 → ~/.claude/memory-bank/
| **脚本验证** | ✅ 已完成 | load-context, switch-branch 工作正常
| **性能优化工具** | ✅ 已完成 | 62.3x 加速验证通过
| **自我纠错系统** | ✅ 完成 | 已部署测试 |
| **网络代理配置** | ✅ 已解决 | HTTP_PROXY=http://127.0.0.1:23968 |

## 本次会话

### 已完成
- ✅ 创建统一记忆目录结构
- ✅ 拆分 MEMORY.md → context/
- ✅ 部署自我纠错系统
- ✅ OpenClaw 深度分析
- ✅ 性能优化工具模块
- ✅ 迁移 F:\claude-memory\memory-bank\ 数据

### 进行中
- 🔄 持续优化和文档完善

## 快速链接

| 文件 | 用途 |
|------|------|
| [IDENTITY.md](./context/IDENTITY.md) | AI身份定义 |
| [USER.md](./context/USER.md) | 用户偏好 |
| [PROTOCOL.md](./context/PROTOCOL.md) | 操作协议 |
| [HEARTBEAT.md](./context/HEARTBEAT.md) | 维护配置 |

## 工具快捷方式

```bash
# 查看状态
ls ~/.claude/memory-bank/

# 记录错误
python ~/.claude/memory-bank/tools/self_correction.py

# 性能优化工具
py ~/.claude/memory-bank/tools/performance_optimizer.py

# 检查当前分支
git branch --show-current
```

## 关键路径

- **记忆库**: `~/.claude/memory-bank/`
- **技能**: `~/.claude/skills/`
- **冷数据**: `F:\claude-memory\`

## ⚠️ 记忆使用规范（必读）

### 避免记忆失效

**场景**：GitHub 用户名已知（`Renu-Cybe`），但仍重复询问

**正确做法**：
1. 任务开始前，**主动读取** `context/USER.md` 和 `context/IDENTITY.md`
2. 涉及用户信息时，**先查记忆**再询问
3. 已记录的信息**直接引用**，不要再次请求

**自检清单**：
- [ ] 是否读取了 context/ 下的核心记忆？
- [ ] 用户信息是否已存在？
- [ ] 是否有重复询问已记录信息的风险？

**违规示例**：
```
❌ "请告诉我你的 GitHub 用户名" （已知 Renu-Cybe）
✅ "使用记忆中的 GitHub 账号 Renu-Cybe..."
```

---
*架构版本: v2.0 | 会话ID: 2026-03-17-restructure*
