# 目录结构说明

本仓库采用以下目录结构：

```
claude-memory-skills/
├── README.md                    # 项目主页说明
├── LICENSE                      # MIT 许可证
├── CONTRIBUTING.md              # 贡献指南
├── .gitignore                   # Git 忽略规则
│
├── skills/                      # Skills 目录
│   ├── memory-cleanup/          # 记忆库清理 Skill
│   │   └── SKILL.md
│   │
│   └── skill-seeker/            # 文档爬取 Skill
│       └── SKILL.md
│
├── docs/                        # 文档目录
│   ├── architecture.md          # 架构说明
│   └── protocol.md              # 协议规范
│
└── assets/                      # 资源文件
    ├── images/                  # 图片
    └── diagrams/                # 架构图
```

## 详细说明

### skills/

存放所有 Claude Code Skills。每个 Skill 一个子目录，必须包含 `SKILL.md`。

### docs/

补充文档，包括：
- 架构设计说明
- 协议规范详解
- 使用教程
- API 文档

### assets/

图片、图表等资源文件。

## 文件命名规范

| 类型 | 规范 | 示例 |
|------|------|------|
| 目录名 | 小写+连字符 | `memory-cleanup` |
| Markdown | 大驼峰或全小写 | `SKILL.md`, `README.md` |
| 图片 | 小写+连字符 | `architecture-diagram.png` |
| 脚本 | 小写+连字符 | `cleanup.sh` |
