# Blackboard Coordinator MVP
# 最小可行黑板报协调器
# 实现轮询发言机制和终止条件检查

import json
import uuid
import time
from datetime import datetime
from typing import List, Dict, Any, Optional
from enum import Enum

class Phase(Enum):
    TASK = "task"
    DISCUSSION = "discussion"
    DECISION = "decision"

class MessageType(Enum):
    PROPOSAL = "proposal"
    QUESTION = "question"
    RESPONSE = "response"
    DECISION = "decision"
    HANDOFF = "handoff"
    TASK_RESULT = "task_result"
    SYSTEM = "system"

class TerminationType(Enum):
    MAX_TURNS = "max_turns"
    CONSENSUS = "consensus"
    TIMEOUT = "timeout"
    MANUAL = "manual"

class BlackboardCoordinator:
    """
    黑板报协调器 - 实现多智能体团队的通信管理

    核心职责:
    1. 管理共享状态（黑板报文件）
    2. 选择下一位发言人
    3. 检查终止条件
    4. 协调讨论流程
    """

    def __init__(self, blackboard_path: str = "blackboard.json"):
        self.blackboard_path = blackboard_path
        self.blackboard = None

    def initialize_session(
        self,
        participants: List[str],
        topic: str,
        phase: Phase = Phase.DISCUSSION,
        termination: Dict[str, Any] = None
    ) -> str:
        """
        初始化新的黑板报会话

        Args:
            participants: Agent ID 列表
            topic: 讨论主题
            phase: 初始阶段
            termination: 终止条件配置

        Returns:
            session_id: 会话 ID
        """
        session_id = str(uuid.uuid4())[:8]

        self.blackboard = {
            "version": "2.0",
            "session_id": session_id,
            "phase": phase.value,
            "participants": participants,
            "shared_state": {
                "task_outputs": {},
                "message_thread": [],
                "current_turn": 0,
                "next_speaker": participants[0],
                "is_complete": False,
                "topic": topic,
                "decisions": []
            },
            "messages": [],
            "termination_condition": termination or {
                "type": "max_turns",
                "params": {"max_turns": 10}
            },
            "metadata": {
                "created_at": datetime.utcnow().isoformat() + "Z",
                "updated_at": datetime.utcnow().isoformat() + "Z",
                "coordinator_version": "mvp-1.0"
            }
        }

        # 添加系统初始化消息
        self._add_system_message(f"讨论会话已初始化。主题: {topic}")
        self._add_system_message(f"参与者: {', '.join(participants)}")
        self._add_system_message(f"终止条件: {self.blackboard['termination_condition']['type']}")

        self._save()
        return session_id

    def run_cycle(self) -> Optional[str]:
        """
        运行一轮协调循环

        Returns:
            next_speaker: 下一位发言人，如果讨论结束则返回 None
        """
        self._load()

        # 检查终止条件
        if self._should_terminate():
            self._complete_session("终止条件满足")
            return None

        # 选择下一位发言人
        speaker = self._select_speaker()

        # 更新状态
        self.blackboard["shared_state"]["next_speaker"] = speaker
        self.blackboard["metadata"]["updated_at"] = datetime.utcnow().isoformat() + "Z"
        self._save()

        return speaker

    def submit_message(
        self,
        from_agent: str,
        content: str,
        msg_type: MessageType = MessageType.RESPONSE,
        requires_response: bool = True,
        confidence: Optional[int] = None
    ) -> str:
        """
        Agent 提交消息到黑板报

        Args:
            from_agent: 发送者 Agent ID
            content: 消息内容
            msg_type: 消息类型
            requires_response: 是否需要回复
            confidence: 置信度评分（0-100）

        Returns:
            message_id: 消息 ID
        """
        self._load()

        msg_id = f"msg_{len(self.blackboard['messages']):03d}"
        message = {
            "id": msg_id,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "from": from_agent,
            "type": msg_type.value,
            "content": content,
            "requires_response": requires_response,
            "responded_by": []
        }

        if confidence is not None:
            message["confidence"] = confidence

        # 添加到消息列表
        self.blackboard["messages"].append(message)

        # 更新消息线程
        self.blackboard["shared_state"]["message_thread"].append({
            "turn": self.blackboard["shared_state"]["current_turn"],
            "agent": from_agent,
            "type": msg_type.value,
            "summary": content[:100] + "..." if len(content) > 100 else content
        })

        # 递增轮次
        self.blackboard["shared_state"]["current_turn"] += 1

        self._save()
        return msg_id

    def submit_decision(self, from_agent: str, decision_content: str) -> str:
        """提交决策"""
        decision_id = f"dec_{len(self.blackboard['shared_state']['decisions']):03d}"

        decision = {
            "id": decision_id,
            "content": decision_content,
            "proposed_by": from_agent,
            "approved_by": [from_agent],
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }

        self.blackboard["shared_state"]["decisions"].append(decision)

        # 同时作为消息提交
        msg_id = self.submit_message(
            from_agent=from_agent,
            content=f"[决策提案] {decision_content}",
            msg_type=MessageType.DECISION,
            requires_response=True
        )

        self._save()
        return decision_id

    def approve_decision(self, agent_id: str, decision_id: str) -> bool:
        """Agent 批准决策"""
        self._load()

        for decision in self.blackboard["shared_state"]["decisions"]:
            if decision["id"] == decision_id:
                if agent_id not in decision["approved_by"]:
                    decision["approved_by"].append(agent_id)

                # 检查是否全员通过
                if set(decision["approved_by"]) == set(self.blackboard["participants"]):
                    self._add_system_message(f"决策 '{decision_id}' 已全员通过！")

                self._save()
                return True

        return False

    def get_context_for_agent(self, agent_id: str) -> Dict[str, Any]:
        """
        获取指定 Agent 的上下文

        Returns:
            包含当前状态和相关消息的上下文对象
        """
        self._load()

        # 获取需要此 Agent 响应的消息
        pending_responses = [
            msg for msg in self.blackboard["messages"]
            if msg.get("requires_response") and agent_id not in msg.get("responded_by", [])
        ]

        return {
            "session_id": self.blackboard["session_id"],
            "phase": self.blackboard["phase"],
            "current_turn": self.blackboard["shared_state"]["current_turn"],
            "topic": self.blackboard["shared_state"]["topic"],
            "is_your_turn": self.blackboard["shared_state"]["next_speaker"] == agent_id,
            "participants": self.blackboard["participants"],
            "messages": self.blackboard["messages"],
            "pending_responses": pending_responses,
            "decisions": self.blackboard["shared_state"]["decisions"]
        }

    def get_summary(self) -> str:
        """获取讨论摘要"""
        self._load()

        state = self.blackboard["shared_state"]

        summary = f"""
=== 讨论摘要 ===
会话 ID: {self.blackboard['session_id']}
主题: {state['topic']}
轮次: {state['current_turn']}
消息数: {len(self.blackboard['messages'])}
决策数: {len(state['decisions'])}
状态: {'已完成' if state['is_complete'] else '进行中'}

参与者: {', '.join(self.blackboard['participants'])}

已达成决策:
"""
        for decision in state["decisions"]:
            approved_count = len(decision["approved_by"])
            total_count = len(self.blackboard["participants"])
            summary += f"  - [{approved_count}/{total_count}] {decision['content'][:50]}...\n"

        return summary

    def _select_speaker(self) -> str:
        """选择下一位发言人（轮询模式）"""
        if self.blackboard["phase"] == "discussion":
            # 轮询模式
            current_turn = self.blackboard["shared_state"]["current_turn"]
            participants = self.blackboard["participants"]
            return participants[current_turn % len(participants)]

        elif self.blackboard["phase"] == "decision":
            # 决策阶段：优先选择未响应待处理决策的 Agent
            # 简化实现：继续使用轮询
            return self._select_speaker_round_robin()

        return self._select_speaker_round_robin()

    def _select_speaker_round_robin(self) -> str:
        """轮询选择"""
        current_turn = self.blackboard["shared_state"]["current_turn"]
        participants = self.blackboard["participants"]
        return participants[current_turn % len(participants)]

    def _should_terminate(self) -> bool:
        """检查是否应该终止"""
        termination = self.blackboard["termination_condition"]
        state = self.blackboard["shared_state"]

        if termination["type"] == "max_turns":
            return state["current_turn"] >= termination["params"]["max_turns"]

        elif termination["type"] == "consensus":
            # 检查是否有全员通过的决策
            for decision in state["decisions"]:
                if set(decision["approved_by"]) == set(self.blackboard["participants"]):
                    return True
            return False

        elif termination["type"] == "timeout":
            # 简化实现：检查最后更新时间
            # 实际应比较时间戳
            return False

        return state["is_complete"]

    def _complete_session(self, reason: str):
        """完成会话"""
        self.blackboard["shared_state"]["is_complete"] = True
        self._add_system_message(f"讨论已结束。原因: {reason}")
        self._save()

    def _add_system_message(self, content: str):
        """添加系统消息"""
        msg_id = f"msg_{len(self.blackboard['messages']):03d}"
        self.blackboard["messages"].append({
            "id": msg_id,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "from": "system",
            "type": "system",
            "content": content,
            "requires_response": False,
            "responded_by": []
        })

    def _save(self):
        """保存黑板报到文件"""
        with open(self.blackboard_path, 'w', encoding='utf-8') as f:
            json.dump(self.blackboard, f, ensure_ascii=False, indent=2)

    def _load(self):
        """从文件加载黑板报"""
        if self.blackboard is not None:
            return

        try:
            with open(self.blackboard_path, 'r', encoding='utf-8') as f:
                self.blackboard = json.load(f)
        except FileNotFoundError:
            raise RuntimeError("黑板报文件不存在，请先调用 initialize_session()")


# 便捷函数
def create_blackboard(
    participants: List[str],
    topic: str,
    max_turns: int = 10,
    path: str = "blackboard.json"
) -> BlackboardCoordinator:
    """
    快速创建黑板报会话

    Usage:
        coordinator = create_blackboard(
            participants=["architect", "developer", "reviewer"],
            topic="设计 memory-bank 的语义搜索模块"
        )
    """
    coordinator = BlackboardCoordinator(path)
    coordinator.initialize_session(
        participants=participants,
        topic=topic,
        termination={
            "type": "max_turns",
            "params": {"max_turns": max_turns}
        }
    )
    return coordinator


if __name__ == "__main__":
    # 简单测试
    print("=== 黑板报协调器 MVP 测试 ===\n")

    # 创建会话
    coord = create_blackboard(
        participants=["architect", "developer", "reviewer"],
        topic="优化 memory-bank 的搜索性能",
        max_turns=6
    )

    print(f"✅ 会话已创建: {coord.blackboard['session_id']}")
    print(f"📋 主题: {coord.blackboard['shared_state']['topic']}")
    print(f"👥 参与者: {', '.join(coord.blackboard['participants'])}\n")

    # 模拟几轮讨论
    for i in range(6):
        speaker = coord.run_cycle()
        if speaker is None:
            break

        print(f"🎤 轮到 [{speaker}] 发言 (轮次 {i+1})")

        # 模拟 Agent 提交消息
        if speaker == "architect":
            coord.submit_message(
                from_agent="architect",
                content="我建议使用向量数据库来优化语义搜索性能",
                msg_type=MessageType.PROPOSAL,
                confidence=85
            )
        elif speaker == "developer":
            coord.submit_message(
                from_agent="developer",
                content="实现方案可行，但需要评估 Chroma 和 Pinecone 的成本",
                msg_type=MessageType.RESPONSE
            )
        elif speaker == "reviewer":
            if i > 3:
                coord.submit_decision("reviewer", "采用 SQLite FTS5 + 向量索引的混合方案")
            else:
                coord.submit_message(
                    from_agent="reviewer",
                    content="同意，但需要添加性能基准测试",
                    msg_type=MessageType.RESPONSE
                )

    print("\n" + coord.get_summary())
    print("\n✅ 测试完成！黑板报已保存到 blackboard.json")
