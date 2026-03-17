---
name: skill-generating
description: |
  自动化生成符合 Claude Code 官方规范的 Skills。
  根据配置自动生成 SKILL.md、scripts 目录结构和参考文件。
  适用于快速创建标准化技能包，确保符合三层架构规范。

tools: [Write, Read, Bash]
context: fork
---

# Skill Generating

## 用途

自动化生成符合官方规范的 Claude Code Skills，减少手动创建目录结构和编写模板的工作量。

## 适用场景

- 快速创建新的 Claude Code Skill
- 批量生成技能包模板
- 确保技能符合官方三层架构规范
- 学习官方 Skill 结构的最佳实践

## 使用方式

### 1. 交互式生成
```
用户: "生成一个新的 skill"
用户: "创建一个记忆管理 skill"
用户: "帮我生成 skill 模板"
```

### 2. 从配置生成
```
用户: "根据配置生成 skill"
用户: "用 JSON 配置创建 skill"
```

### 3. 验证生成结果
```
用户: "检查生成的 skill 是否合规"
用户: "验证 skill 结构"
```

## 工作流程

1. **接收配置**
   - 通过交互式询问获取 skill 信息
   - 或通过 JSON 配置直接生成

2. **执行生成**
   - 调用 `scripts/generator.py`
   - 创建三层目录结构
   - 生成 SKILL.md、脚本和参考文件

3. **验证结果**
   - 检查目录结构完整性
   - 验证 YAML frontmatter 格式
   - 提示用户如何激活

## 配置格式

```json
{
  "name": "my-skill",
  "description": "简短描述",
  "type": "script|instruction",
  "tools": ["Bash", "Read", "Write"],
  "commands": {
    "run": "运行主功能"
  }
}
```

## 输出结构

```
~/.claude/skills/<skill-name>/
├── SKILL.md
├── scripts/
│   └── processor.py
└── reference/
    └── guide.md
```

## 技术特点

| 特性 | 说明 |
|------|------|
| 官方兼容 | 严格遵循 Claude Skills 规范 |
| 模板丰富 | 内置多种类型模板 |
| 自动验证 | 生成后自动检查合规性 |
| UTF-8 支持 | Windows 环境自动处理编码 |

## 示例

**用户**: "生成一个日志分析的 skill"

**Claude**: 调用 skill-generating 生成标准化结构...
