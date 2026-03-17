#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能双模型决策器 - 自动调用 Qwen 辅助
集成到 Claude Code 工作流
"""

import subprocess
import json
import sys
import os
from typing import Optional, Dict, Any

# Fix Windows encoding
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

OLLAMA_SKILL_PATH = "C:/Users/Administrator/.claude/skills/ollama-helper/ollama_helper.py"


class LocalModelAdvisor:
    """本地模型顾问 - 在特定场景自动调用 Qwen"""

    # 任务类型 -> 是否推荐本地模型
    TASK_RECOMMENDATIONS = {
        "code_review": {"use_local": True, "reason": "代码专用模型更擅长"},
        "code_complete": {"use_local": True, "reason": "快速补全，节省API成本"},
        "explain_code": {"use_local": True, "reason": "本地模型足够"},
        "generate_tests": {"use_local": True, "reason": "模式化代码生成"},
        "algorithm_design": {"use_local": False, "reason": "需要复杂推理"},
        "architecture_design": {"use_local": False, "reason": "需要 Claude 的强推理"},
        "debug_complex": {"use_local": False, "reason": "复杂调试需要强模型"},
    }

    def analyze_task(self, task_description: str) -> Dict[str, Any]:
        """分析任务类型，返回建议"""
        task_lower = task_description.lower()

        # 简单关键词匹配
        if any(kw in task_lower for kw in ["review", "审查", "检查代码", "code review"]):
            return {"use_local": True, "reason": "Code specialist model is better"}
        elif any(kw in task_lower for kw in ["complete", "补全", "生成代码", "finish"]):
            return {"use_local": True, "reason": "Fast completion, save API cost"}
        elif any(kw in task_lower for kw in ["explain", "解释", "说明", "what does"]):
            return {"use_local": True, "reason": "Local model sufficient"}
        elif any(kw in task_lower for kw in ["test", "测试", "unittest", "pytest"]):
            return {"use_local": True, "reason": "Pattern-based code generation"}
        elif any(kw in task_lower for kw in ["algorithm", "算法", "optimize", "performance"]):
            return {"use_local": False, "reason": "Complex reasoning needed"}
        elif any(kw in task_lower for kw in ["architecture", "架构", "design system"]):
            return {"use_local": False, "reason": "Need Claude's strong reasoning"}
        else:
            return {"use_local": False, "reason": "Use Claude"}

    def call_qwen(self, prompt: str, timeout: int = 60) -> str:
        """调用本地 Qwen 模型"""
        try:
            result = subprocess.run(
                ["py", OLLAMA_SKILL_PATH, "chat", prompt],
                capture_output=True,
                text=True,
                timeout=timeout
            )
            return result.stdout
        except subprocess.TimeoutExpired:
            return "本地模型响应超时，建议切换到 Claude"
        except Exception as e:
            return f"调用本地模型失败: {e}"

    def dual_model_consult(self, task: str, context: str = "") -> Dict[str, str]:
        """双模型咨询模式 - Claude + Qwen"""
        analysis = self.analyze_task(task)

        if analysis["use_local"]:
            print(f"[Auto-Advisor] 推荐调用本地 Qwen: {analysis['reason']}")

            # 构建提示词
            prompt = f"""Task: {task}

Context:
{context}

Please help with this programming task."""

            qwen_response = self.call_qwen(prompt)

            return {
                "recommendation": analysis["reason"],
                "claude_should": "审核和优化 Qwen 的输出",
                "qwen_output": qwen_response,
                "suggested_workflow": "Qwen 生成初稿 -> Claude 审查改进"
            }
        else:
            return {
                "recommendation": analysis["reason"],
                "claude_should": "直接处理",
                "use": "Claude (kimi-k2.5)"
            }


# 全局实例
advisor = LocalModelAdvisor()


def auto_advise(task: str, context: str = ""):
    """
    自动决策是否调用本地模型

    使用方式:
    from ollama_auto import auto_advise
    result = auto_advise("审查这段代码", code_content)
    """
    return advisor.dual_model_consult(task, context)


def auto_code_review(code: str):
    """自动代码审查 - 调用 Qwen"""
    print("[Auto-Mode] 调用本地 Qwen 进行代码审查...")
    prompt = f"""Review this code and identify issues:

```python
{code}
```

Focus on:
1. Bugs and errors
2. Performance issues
3. Style improvements
4. Best practices"""

    return advisor.call_qwen(prompt)


def auto_code_complete(partial_code: str):
    """自动代码补全 - 调用 Qwen"""
    print("[Auto-Mode] 调用本地 Qwen 补全代码...")
    prompt = f"""Complete this code:

```python
{partial_code}
```

Continue the implementation:"""

    return advisor.call_qwen(prompt)


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("""
智能双模型决策器

用法:
  python ollama_auto.py <任务类型> [内容]

任务类型:
  review <code>     - 自动代码审查
  complete <code>   - 自动代码补全
  advise "<task>"   - 智能决策建议

示例:
  python ollama_auto.py review "def hello(): print('hi')"
  python ollama_auto.py complete "def fibonacci(n):"
  python ollama_auto.py advise "优化这个排序算法"
        """)
        sys.exit(0)

    command = sys.argv[1]
    content = sys.argv[2] if len(sys.argv) > 2 else ""

    if command == "review":
        result = auto_code_review(content)
        print("\n" + "="*50)
        print("Qwen 审查结果:")
        print("="*50)
        print(result)

    elif command == "complete":
        result = auto_code_complete(content)
        print("\n" + "="*50)
        print("Qwen 补全结果:")
        print("="*50)
        print(result)

    elif command == "advise":
        result = auto_advise(content)
        print("\n" + "="*50)
        print("智能决策建议:")
        print("="*50)
        for key, value in result.items():
            print(f"\n{key}:")
            if len(value) > 200:
                print(value[:200] + "...")
            else:
                print(value)

    else:
        print(f"未知命令: {command}")
