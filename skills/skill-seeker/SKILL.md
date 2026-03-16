---
name: skill-seeker
description: |
  自动爬取任意技术文档网站，提取关键内容生成 Claude Code 技能包。
  适用于为新框架、库或工具快速生成 Claude 可用的知识技能，
  特别是当 Claude 的训练数据不包含该技术的最新文档时。

tools: [Bash, Read, Write, Glob]
context: fork
---

# Skill Seeker

## 用途

将任何技术文档网站转换为 Claude Code 可用的技能包。

## 适用场景

- 学习新框架（如 LangGraph、CrewAI、AutoGen）
- 为项目特定工具生成 Claude 技能
- 创建团队共享的技术知识库
- 跟进文档更新频繁的快速迭代项目

## 使用方式

### 1. 基础爬取
```
用户: "从 https://docs.example.com 生成技能包"
用户: "爬取 react.dev 文档做成 skill"
用户: "给 https://python.langchain.com 生成知识包"
```

### 2. 指定输出名称
```
用户: "爬取 https://docs.crewai.com 命名为 crewai-docs"
用户: "从 https://ollama.ai/docs 生成 ollama-skill"
```

### 3. 限制爬取范围
```
用户: "爬取 https://docs.pydantic.dev 最多10页"
用户: "快速扫描 https://fastapi.tiangolo.com 只取5页"
```

## 工作流程

1. **接收 URL 和参数**
   - 从用户输入提取文档网站 URL
   - 识别输出名称（可选，默认自动生成）
   - 识别最大页数（可选，默认10页）

2. **执行爬取**
   - 调用 `tools/skill_seeker.py`
   - 递归抓取同域名页面
   - 提取正文文本和代码示例

3. **生成技能包**
   - 输出到 `~/.claude/skills/<name>/`
   - 包含 `knowledge.md`（提取的内容）
   - 包含 `skill.json`（技能配置）

4. **验证和提示**
   - 显示生成的文件列表
   - 提示用户如何激活和使用

## 输出结构

```
~/.claude/skills/<skill-name>/
├── knowledge.md          # 提取的文档内容
├── skill.json            # 技能配置
└── source.url            # 原始文档地址记录
```

## 技术特点

| 特性 | 说明 |
|------|------|
| 自动递归 | 自动发现和爬取同域名链接 |
| 内容提取 | 提取正文文本和代码块 |
| 去重处理 | 自动过滤重复内容 |
| 分页限制 | 可设置最大爬取页数 |

## 参数

通过 `$ARGUMENTS` 接收：
- `<URL>` - 文档网站地址（必需）
- `<output-name>` - 输出技能名称（可选）
- `<max-pages>` - 最大爬取页数（可选，默认10）

## 示例对话

**用户**: "从 https://docs.crewai.com 生成 crewai 技能包"

**Claude**:
```
开始爬取: https://docs.crewai.com
最大页面数: 10

[1/10] 正在处理: https://docs.crewai.com/
[2/10] 正在处理: https://docs.crewai.com/core/agent
[3/10] 正在处理: https://docs.crewai.com/core/task
...

✅ 技能包已生成: ~/.claude/skills/crewai/
   - knowledge.md (45KB)
   - skill.json

现在你可以使用：
- "使用 crewai 创建一个代理"
- "crewai 如何定义任务"
```

## 支持的文档类型

- ✅ 静态文档网站（ReadTheDocs、Docusaurus、MkDocs）
- ✅ API 参考文档
- ✅ 教程和指南页面
- ✅ 博客文章系列
- ⚠️ 需要 JavaScript 渲染的动态内容（有限支持）

## 注意事项

1. 爬取过程可能需要几分钟，取决于页面数量和大小
2. 尊重目标网站的 robots.txt 和速率限制
3. 生成的技能包可能需要手动编辑以优化提示效果
4. 建议定期重新爬取以获取最新文档更新
5. 对于大型文档网站，建议先小范围测试（如 `max-pages=5`）

## 相关文件

- **脚本**: `C:\Users\Administrator\.claude\projects\C--Users-Administrator\memory\tools\skill_seeker.py`
- **输出目录**: `~/.claude/skills/`
