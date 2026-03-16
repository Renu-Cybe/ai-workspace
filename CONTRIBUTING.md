# Contributing to Claude Memory Skills

感谢你的贡献！以下是参与指南。

## 如何贡献

### 报告问题

1. 使用 GitHub Issues 提交 bug 或功能建议
2. 提供清晰的问题描述和复现步骤
3. 标注相关 Skill 名称

### 提交代码

1. Fork 本仓库
2. 创建功能分支: `git checkout -b feature/new-skill`
3. 提交更改: `git commit -m 'Add new skill: xxx'`
4. 推送分支: `git push origin feature/new-skill`
5. 创建 Pull Request

## Skill 开发规范

### 目录结构

```
skills/<skill-name>/
├── SKILL.md              # 必需：Skill 定义文件
├── README.md             # 可选：详细说明
├── examples/             # 可选：示例文件
└── assets/               # 可选：图片等资源
```

### SKILL.md 格式

```yaml
---
name: skill-name
description: |
  简短的 Skill 描述，说明用途和适用场景。
  支持多行文本。
tools: [Bash, Read, Write, Edit]
context: fork
---

# Skill 名称

## 用途

详细说明这个 Skill 的用途。

## 使用方式

### 触发示例
```
用户: "触发指令示例1"
用户: "触发指令示例2"
```

## 工作流程

1. 步骤一
2. 步骤二
3. 步骤三

## 注意事项

- 重要提示1
- 重要提示2
```

### YAML Frontmatter 字段

| 字段 | 必需 | 说明 |
|------|------|------|
| `name` | ✅ | Skill 名称，小写+连字符 |
| `description` | ✅ | 简短描述，用于匹配用户意图 |
| `tools` | ✅ | 需要的工具列表 |
| `context` | ❌ | 执行上下文，建议用 `fork` |
| `agent` | ❌ | 使用的 Agent 类型 |

### 命名规范

- Skill 名称：小写字母 + 连字符，如 `memory-cleanup`
- 描述清晰：一句话说明用途
- 触发自然：用户使用自然语言即可触发

## 代码风格

- 使用清晰的注释
- 保持简洁，避免过度工程
- 优先使用 Claude Code 原生工具

## 测试要求

提交前请测试：

1. Skill 能正确安装
2. 触发指令能匹配
3. 功能按预期工作

## 文档更新

修改 README.md 时：

- 在 Skills 列表中添加新 Skill
- 更新目录结构（如有变化）
- 保持格式一致

## 许可协议

提交即表示你同意将你的贡献在 MIT 许可下发布。

---

有任何问题？欢迎创建 Issue 讨论！
