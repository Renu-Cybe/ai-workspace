# 记忆库操作协议 v1.0
# C:\Users\Administrator\.claude\projects\C--Users-Administrator\memory\PROTOCOL.md

## 重要：读取本文件后，必须遵守以下规则

### 1. 存储架构（冷热分离 + Memory Bank）
- **C盘**（热数据，启动必需）：本协议、当前状态、当前会话
- **F盘**（冷数据，历史归档）：F:\claude-memory\
  - **memory-bank\**  : 分支感知记忆库 ⭐ 新架构
    - main\         : 主分支记忆
      - decisions\  : 关键决策
      - sessions\   : 会话历史
      - todos\      : 已完成待办
      - context\    : 持续上下文
    - [feature-*]\  : 功能分支记忆（动态创建）
    - shared\       : 跨分支共享记忆
    - .index\       : 索引和元数据
  - backup\         : 备份文件
  - archive\        : 旧归档（已迁移到 memory-bank）
  - decisions\      : 旧决策（待迁移）
  - projects\       : 项目历史

### 2. 启动时必须执行（更新版）
```
1. 检测当前 git 分支
   └── 确定 memory-bank/[branch]/ 上下文

2. 加载分支上下文
   └── 读取 memory-bank/[branch]/context/PROJECT.md

3. 检查 session/current.md 是否存在且非空
   ├── 存在 → 询问用户"上次异常结束，是否恢复/归档/丢弃？"
   └── 不存在/空 → 正常开始

4. 执行清理检查
   └── bash cleanup.sh 或 "检查记忆库"
```

### 3. 对话进行中实时写入
- 关键决策立即追加到 session/current.md
- 当前状态更新到 MEMORY.md

### 4. 结束归档（更新版）
```
1. 自动提取标签
   └── 分析会话内容生成 [tag1][tag2]

2. 重命名文件
   └── current.md → [date]-[branch]-[number]_[tag1][tag2].md

3. 归档到 memory-bank
   └── 移动到 memory-bank/[branch]/sessions/

4. 更新索引
   └── 更新 .index/tags.json 和 metadata.json

5. 清空 current.md

6. 更新 MEMORY.md 状态
```

**文件命名规范:**
```
[date]-[branch]-[number]_[tag1][tag2].md
示例: 2026-03-16-main-001_[memory-system][skill-dev].md
```

### 5. 文件位置总览
| 文件 | 位置 | 作用 |
|------|------|------|
| 本协议 | C:\...\memory\PROTOCOL.md | 操作规范 |
| 当前状态 | C:\...\memory\MEMORY.md | 热数据 |
| 当前会话 | C:\...\memory\session\current.md | 实时备份 |
| **Memory Bank** | F:\claude-memory\memory-bank\ | **分支感知记忆库** ⭐ |
| 历史会话 | F:\...\memory-bank\main\sessions\ | 按分支分类 |
| 关键决策 | F:\...\memory-bank\main\decisions\ | 架构决策记录 |
| 持续上下文 | F:\...\memory-bank\main\context\ | 跨会话上下文 |
| 备份文件 | F:\claude-memory\backup\ | 压缩备份 |
| 清理脚本 | C:\...\memory\cleanup.sh | 定时清理 |
| **Skill Seeker** | C:\...\memory\tools\skill_seeker.py | 文档爬取脚本 |
| **Memory Cleanup Skill** | ~/.claude/skills/memory-cleanup/ | 官方 Skill：清理记忆库 |
| **Skill Seeker Skill** | ~/.claude/skills/skill-seeker/ | 官方 Skill：文档转技能 |

### 6. 定时清理机制
```
启动时自动执行: bash cleanup.sh
手动触发: bash cleanup.sh manual
模拟运行: bash cleanup.sh dry-run
```

**自然语言触发（Official Skill）:**
```
"检查记忆库"     → 调用 memory-cleanup skill
"模拟清理"       → 执行 dry-run 模式
"记忆库状态"     → 显示统计信息
```

**清理规则:**
- 时间规则: 超过30天的文件压缩到 backup/YYYYMM/
- 数量规则: archive/ 超过50个时，保留最新的50个，其余压缩
- 压缩格式: .gz

**日志位置:** F:\claude-memory\cleanup.log

---
LAST_UPDATE: 2026-03-16
FALLBACK_DISK: F
