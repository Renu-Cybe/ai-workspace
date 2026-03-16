# 使用指南：在 Claude Code 中运行黑板报讨论

## 快速开始（3 分钟）

### 步骤 1: 初始化黑板报

```python
import sys
sys.path.insert(0, 'F:/claude-memory/blackboard-mvp/core')
from coordinator import create_blackboard, BlackboardCoordinator, MessageType

# 创建会话
coordinator = create_blackboard(
    participants=["architect", "developer", "reviewer"],
    topic="设计 memory-bank 的语义搜索模块",
    max_turns=9,
    path="F:/claude-memory/blackboard-mvp/active_discussion.json"
)

print(f"会话 ID: {coordinator.blackboard['session_id']}")
```

### 步骤 2: 手动协调讨论

由于 Claude Code Agent 无法直接读取黑板报，你需要作为协调者手动管理流程：

```python
# 第 1 轮 - 让 Architect 发言
speaker = coordinator.run_cycle()
print(f"轮到: {speaker}")

# 读取上下文
context = coordinator.get_context_for_agent(speaker)
print(f"主题: {context['topic']}")
print(f"当前轮次: {context['current_turn']}")
```

### 步骤 3: 创建 Agent 并传递上下文

现在启动一个 Claude Code Agent，给它特定的提示词：

**你手动输入到 Agent：**
```
你是 {speaker}，正在参与关于"{context['topic']}"的讨论。

## 你的角色
{根据 speaker 加载 agent_prompts.py 中的对应提示词}

## 讨论历史
{展示 context['messages'] 中的关键消息}

## 当前轮到你发言
请基于以上上下文，提交你的观点。直接回复内容即可。
```

### 步骤 4: 提交 Agent 的回复

Agent 生成回复后，你将其提交到黑板报：

```python
coordinator.submit_message(
    from_agent="architect",
    content="""{Agent 的回复内容}""",
    msg_type=MessageType.PROPOSAL,
    confidence=85
)

print("消息已提交")
```

### 步骤 5: 循环直到结束

重复步骤 2-4，直到 `coordinator.run_cycle()` 返回 `None`（讨论结束）。

---

## 半自动模式（推荐）

为了简化手动操作，可以创建一个脚本自动选择发言人并准备上下文：

```python
def run_blackboard_turn(blackboard_path: str):
    """运行一轮黑板报讨论"""
    coordinator = BlackboardCoordinator(blackboard_path)

    # 选择发言人
    speaker = coordinator.run_cycle()
    if speaker is None:
        print("讨论已结束！")
        print(coordinator.get_summary())
        return None

    # 获取上下文
    context = coordinator.get_context_for_agent(speaker)

    # 准备 Agent 提示词
    from agent_prompts import get_agent_prompt
    system_prompt = get_agent_prompt(speaker, context['topic'])

    # 生成完整提示词
    full_prompt = f"""{system_prompt}

## 当前讨论状态
主题: {context['topic']}
轮次: {context['current_turn']}

## 讨论历史
"""
    # 添加最近的消息
    for msg in context['messages'][-5:]:  # 最近 5 条
        if msg['from'] != 'system':
            full_prompt += f"\n[{msg['from']}] ({msg['type']}): {msg['content'][:200]}...\n"

    full_prompt += f"\n\n## 轮到你发言\n请提交你的回复。"

    print(f"\n{'='*60}")
    print(f"发言人: {speaker}")
    print(f"{'='*60}\n")
    print(full_prompt)

    return speaker

# 使用
speaker = run_blackboard_turn("F:/claude-memory/blackboard-mvp/active_discussion.json")
```

---

## 完整工作流示例

### 场景：讨论 memory-bank 优化方案

```
[你] 运行初始化脚本 -> 创建黑板报

[Round 1]
  协调器: 轮到 architect 发言
  你: 启动 architect Agent，传入上下文
  architect: 生成技术方案
  你: 提交到黑板报

[Round 2]
  协调器: 轮到 developer 发言
  你: 启动 developer Agent
  developer: 评估可行性
  你: 提交到黑板报

[Round 3]
  协调器: 轮到 reviewer 发言
  你: 启动 reviewer Agent
  reviewer: 提出问题
  你: 提交到黑板报

[Round 4-6]
  ...继续讨论直到达成共识...

[End]
  协调器: 讨论结束（达成决策）
  你: 导出决策文档
```

---

## 实用技巧

### 1. 快速查看当前状态

```python
coordinator = BlackboardCoordinator("blackboard.json")
print(coordinator.get_summary())
```

### 2. 导出决策记录

```python
# 保存为 Markdown
decisions = coordinator.blackboard['shared_state']['decisions']
for d in decisions:
    print(f"决策: {d['content']}")
    print(f"批准: {', '.join(d['approved_by'])}")
```

### 3. 修改终止条件

```python
# 延长讨论
coordinator.blackboard['termination_condition']['params']['max_turns'] = 15
coordinator._save()

# 改为共识终止
coordinator.blackboard['termination_condition'] = {
    "type": "consensus",
    "params": {}
}
coordinator._save()
```

---

## 常见问题

**Q: 为什么 Agent 不能直接读取黑板报？**
A: Claude Code 的 Agent 是 fork 模式，每个 Agent 是独立进程，无法访问你当前会话的文件系统。

**Q: 能否实现全自动？**
A: 目前不能，因为需要你来启动 Agent 并传递提示词。未来可以通过 Skill 封装实现更自动化的流程。

**Q: 一个讨论可以跨会话吗？**
A: 可以！黑板报保存为 JSON 文件，随时可以继续。只需重新加载即可。

---

## 文件位置

- 黑板报模板：`F:/claude-memory/blackboard-mvp/core/`
- 示例脚本：`F:/claude-memory/blackboard-mvp/examples/`
- 当前讨论：`F:/claude-memory/blackboard-mvp/active_discussion.json`
