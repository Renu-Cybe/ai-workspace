# ADR-001: Memory Bank 分支感知架构

## 状态
- **日期**: 2026-03-16
- **状态**: 已接受
- **决策人**: Claude Code (kimi-k2.5) + 用户

## 背景

随着记忆库的发展，我们面临以下问题：
1. 历史会话文件堆积在单一 archive/ 目录，难以查找
2. 不同功能分支的上下文混在一起
3. 关键决策散落在各个会话中，难以追踪
4. 缺乏有效的搜索机制

## 决策

采用 **Memory Bank** 分支感知架构，借鉴 [RIPER Workflow](https://github.com/tony/claude-code-riper-5)。

## 方案对比

| 方案 | 优点 | 缺点 |
|------|------|------|
| **A: 保持现状** | 简单 | 无法扩展，查找困难 |
| **B: 仅添加标签** | 轻度改进 | 没有解决根本问题 |
| **C: Memory Bank** ⭐ | 分支隔离，分类清晰，可扩展 | 需要迁移现有数据 |

## 架构设计

```
memory-bank/
├── main/                    # 主分支记忆
│   ├── decisions/          # 关键决策
│   ├── sessions/           # 会话历史
│   ├── todos/              # 已完成待办
│   └── context/            # 持续上下文
├── [feature-*/              # 功能分支记忆
├── shared/                 # 跨分支共享
└── .index/                 # 索引和元数据
```

## 影响

### 正面影响
- 分支隔离防止上下文污染
- 分类存储便于查找
- 支持全文搜索扩展
- 符合工程最佳实践

### 负面影响
- 需要迁移现有数据
- 增加启动时的分支检测
- 需要维护 .index/ 索引

## 实施计划

1. ✅ 创建目录结构
2. ✅ 迁移现有数据
3. ✅ 更新文档
4. 🔄 实施自动标签
5. 🔄 实施全文搜索
6. 🔄 实施分支切换检测

## 相关资源

- **RIPER Workflow**: https://github.com/tony/claude-code-riper-5
- **调研报告**: F:\claude-memory\claude-memory-skills\docs\RESEARCH-MEMORY-SYSTEMS.md

## 备注

这是记忆库管理系统的重大架构升级，为未来功能（搜索、提醒、分析）奠定基础。
