# Blackboard MVP - 多智能体团队通信系统

基于研究报告 v2 实现的最小可行黑板报系统，借鉴 CrewAI、AutoGen、LangGraph 的设计理念。

---

## 核心特性

- **共享状态通信**：Agent 通过黑板报 JSON 文件间接协作
- **轮询发言机制**：基于回合制的发言选择
- **终止条件支持**：max_turns / consensus / timeout / manual
- **决策追踪**：支持提案、讨论、批准的完整流程
- **状态持久化**：自动保存/恢复讨论状态

---

## 快速开始

### 1. 创建黑板报会话

```python
from coordinator import create_blackboard, MessageType

# 创建 3-Agent 讨论会话
coordinator = create_blackboard(
    participants=["architect", "developer", "reviewer"],
    topic="设计新功能",
    max_turns=9,
    path="blackboard.json"
)

print(f"会话 ID: {coordinator.blackboard['session_id']}")
```

### 2. 运行协调循环

```python
# 获取当前发言人
speaker = coordinator.run_cycle()
print(f"轮到 {speaker} 发言")

# 如果 speaker 为 None，说明讨论已结束
if speaker is None:
    print("讨论已结束")
    print(coordinator.get_summary())
```

### 3. Agent 提交消息

```python
# Architect 提交提案
coordinator.submit_message(
    from_agent="architect",
    content="我建议采用...",
    msg_type=MessageType.PROPOSAL,
    confidence=85
)

# Developer 回应
coordinator.submit_message(
    from_agent="developer",
    content="实现上可行，但是...",
    msg_type=MessageType.RESPONSE
)

# Reviewer 提交决策
coordinator.submit_decision(
    from_agent="reviewer",
    decision_content="通过方案A"
)
```

### 4. 批准决策

```python
# 全员批准后，决策生效
coordinator.approve_decision("architect", "dec_000")
coordinator.approve_decision("developer", "dec_000")
coordinator.approve_decision("reviewer", "dec_000")
```

---

## 完整示例

运行示例讨论：

```bash
cd F:/claude-memory/blackboard-mvp
python examples/demo_discussion.py
```

这将模拟一个完整的 3-Agent 架构讨论，包括：
- Architect 提出技术方案
- Developer 评估可行性
- Reviewer 审查并推动决策
- 全员达成共识

输出文件：
- `examples/discussion_demo.json` - 完整黑板报数据
- `examples/decision_summary.md` - 决策摘要文档

---

## 黑板报数据格式

```json
{
  "version": "2.0",
  "session_id": "abc123",
  "phase": "discussion",
  "participants": ["architect", "developer", "reviewer"],
  "shared_state": {
    "task_outputs": {},
    "message_thread": [],
    "current_turn": 0,
    "next_speaker": "architect",
    "is_complete": false,
    "topic": "设计新功能",
    "decisions": []
  },
  "messages": [
    {
      "id": "msg_000",
      "timestamp": "2025-03-16T10:00:00Z",
      "from": "architect",
      "type": "proposal",
      "content": "...",
      "requires_response": true,
      "confidence": 85
    }
  ],
  "termination_condition": {
    "type": "max_turns",
    "params": {"max_turns": 10}
  }
}
```

---

## 消息类型

| 类型 | 用途 |
|------|------|
| `proposal` | 提出方案或建议 |
| `question` | 提出问题或疑问 |
| `response` | 回应问题或提案 |
| `decision` | 提交决策提案 |
| `handoff` | 主动移交发言权 |
| `task_result` | 任务执行结果 |
| `system` | 系统消息 |

---

## 终止条件

```python
# 最大轮次
coordinator.initialize_session(
    participants=[...],
    topic="...",
    termination={"type": "max_turns", "params": {"max_turns": 10}}
)

# 全员共识
coordinator.initialize_session(
    participants=[...],
    topic="...",
    termination={"type": "consensus"}
)
```

---

## 与 Claude Code Agent 集成

### Agent 的 System Prompt 模板

```python
from agent_prompts import get_agent_prompt

# 获取 Architect 的完整提示词
prompt = get_agent_prompt("architect", "设计新功能")

# 启动 Agent 时传入
agent = Agent(..., system_prompt=prompt)
```

### 手动模式（推荐）

由于 Claude Code Agent 无法直接读取黑板报，建议采用**手动模式**：

1. **你作为协调者**，读取黑板报
2. **你决定**哪个 Agent 发言
3. **你传递**上下文给该 Agent
4. **Agent 生成**回复
5. **你提交**回复到黑板报
6. **重复步骤 1-5**

### 伪代码示例

```python
while True:
    # 1. 读取黑板报
    coordinator = BlackboardCoordinator("blackboard.json")

    # 2. 选择发言人
    speaker = coordinator.run_cycle()
    if speaker is None:
        break

    # 3. 获取该 Agent 的上下文
    context = coordinator.get_context_for_agent(speaker)

    # 4. 启动 Claude Code Agent
    agent = create_agent(speaker, context)
    response = agent.generate_response()

    # 5. 提交回复
    coordinator.submit_message(
        from_agent=speaker,
        content=response
    )
```

---

## 与官方多智能体框架对比

| 特性 | Blackboard MVP | CrewAI | AutoGen | LangGraph |
|------|----------------|--------|---------|-----------|
| 通信方式 | 共享 JSON 文件 | 任务上下文 | 消息队列 | 状态图 |
| 协调方式 | 轮询 | 流程驱动 | 发言选择器 | 状态路由 |
| 状态持久化 | ✅ 文件 | ❌ 内存 | ✅ 支持 | ✅ 内置 |
| 终止条件 | ✅ 支持 | ❌ 无 | ✅ 支持 | ✅ 支持 |
| 复杂度 | 低 | 中 | 高 | 高 |
| 与 Claude Code 集成 | 原生支持 | 需适配 | 需适配 | 需适配 |

---

## 文件结构

```
blackboard-mvp/
├── core/
│   ├── schema.json           # 黑板报 JSON Schema
│   ├── coordinator.py        # 协调器核心实现
│   └── agent_prompts.py      # Agent 提示词模板
├── examples/
│   └── demo_discussion.py    # 3-Agent 讨论示例
├── tests/
│   └── test_output.json      # 测试输出
└── README.md                 # 本文档
```

---

## 下一步

### 立即可以尝试
1. ✅ 运行 `examples/demo_discussion.py` 查看模拟讨论
2. ✅ 修改示例中的发言内容，测试不同场景
3. ✅ 手动编辑 `blackboard.json` 模拟 Agent 回复

### 短期增强
- [ ] 添加更多发言选择策略（LLM 选择、基于置信度）
- [ ] 实现条件路由（基于消息内容动态路由）
- [ ] 添加并行执行支持（多个 Agent 同时处理子任务）

### 中期目标
- [ ] 创建 CLI 工具自动化协调流程
- [ ] 添加 Web UI 可视化讨论过程
- [ ] 与 memory-bank 系统集成

---

## 参考

- [研究报告 v1](../memory-bank/main/research/2026-03-16-main-002_[multi-agent][communication].md)
- [研究报告 v2](../memory-bank/main/research/2026-03-16-main-003_[multi-agent][v2-latest].md)
- [CrewAI](https://github.com/crewAIInc/crewAI)
- [AutoGen](https://github.com/microsoft/autogen)
- [LangGraph](https://github.com/langchain-ai/langgraph)
