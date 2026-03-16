# Memory Bank

> 分支感知的记忆管理系统
> 借鉴 RIPER Workflow 的 memory-bank 架构

## 目录结构

```
memory-bank/
├── main/                    # 主分支记忆
│   ├── decisions/          # 关键决策记录
│   ├── sessions/           # 会话历史
│   ├── todos/              # 已完成的待办
│   └── context/            # 持续上下文
├── [feature-*/              # 功能分支记忆（动态创建）
│   ├── decisions/
│   ├── sessions/
│   ├── todos/
│   └── context/
├── shared/                 # 跨分支共享记忆
│   ├── decisions/
│   ├── sessions/
│   └── todos/
└── .index/                 # 索引和元数据
    ├── full-text.db        # SQLite FTS5 全文索引
    ├── tags.json           # 标签映射
    └── metadata.json       # 文件元数据
```

## 文件命名规范

### 会话文件
```
[date]-[branch]-[number]_[tag1][tag2].md

示例:
- 2026-03-16-main-001_[memory-system][skill-dev].md
- 2026-03-17-feature-search-001_[sqlite][fts5].md
```

### 决策文件
```
[date]-[branch]-DECISION-[title].md

示例:
- 2026-03-16-main-DECISION-storage-architecture.md
- 2026-03-17-feature-auth-DECISION-jwt-vs-session.md
```

### 待办文件
```
[date]-[branch]-TODO-[title]-[status].md

示例:
- 2026-03-16-main-TODO-implement-search-DONE.md
- 2026-03-17-feature-api-TODO-add-tests-ACTIVE.md
```

## 使用流程

### 1. 启动时
```
1. 检测当前 git 分支
2. 切换到对应 memory-bank/[branch]/
3. 加载 context/ 中的持续上下文
4. 检查是否有未完成的 todos
```

### 2. 会话进行中
```
1. 关键决策 → 写入 decisions/
2. 会话内容 → 写入 sessions/
3. 完成任务 → 移动到 todos/ 并重命名
```

### 3. 会话结束时
```
1. 自动提取标签
2. 重命名文件添加标签
3. 更新索引
4. 归档到对应目录
```

### 4. 分支切换时
```
1. 保存当前分支 context
2. 加载目标分支 context
3. 显示相关历史决策
```

## 分类说明

### decisions/
记录关键架构决策、技术选型、重要约定。

**包含**:
- 架构设计决策
- 技术选型对比
- API 设计规范
- 重要配置变更

### sessions/
完整的会话历史记录。

**包含**:
- 对话全文
- 代码生成记录
- 问题解决方案
- 探索过程

### todos/
已完成或正在进行的任务。

**包含**:
- 已完成的任务
- 正在进行的任务（带 ACTIVE 标记）
- 任务完成时间和结果

### context/
跨会话持续的上下文信息。

**包含**:
- 项目概况
- 当前状态摘要
- 待解决问题列表
- 重要链接和引用

## 索引系统

### full-text.db (SQLite FTS5)
```sql
-- 会话内容全文索引
CREATE VIRTUAL TABLE sessions USING fts5(
    path,           -- 文件路径
    content,        -- 文件内容
    branch,         -- 所属分支
    tags,           -- 标签
    created_at      -- 创建时间
);
```

### tags.json
```json
{
    "docker": ["2026-03-16-main-001", "2026-03-17-main-002"],
    "memory-system": ["2026-03-16-main-001"],
    "api-design": ["2026-03-17-feature-auth-001"]
}
```

### metadata.json
```json
{
    "total_sessions": 45,
    "total_decisions": 12,
    "total_todos": 30,
    "storage_mb": 12.5,
    "last_updated": "2026-03-16T20:00:00Z",
    "branches": ["main", "feature-search", "feature-auth"]
}
```

## 迁移说明

原 archive/ 目录内容已迁移到 memory-bank/main/sessions/

后续新会话将自动按分支分类存储。

---

**创建时间**: 2026-03-16
**借鉴项目**: RIPER Workflow (https://github.com/tony/claude-code-riper-5)
