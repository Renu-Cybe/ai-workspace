#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Ollama 本地模型集成 Skill for Claude Code
调用本地 Qwen 模型进行代码生成和补全
"""

import requests
import json
import sys
import os
from typing import Optional

# Fix Windows encoding
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

OLLAMA_HOST = "http://localhost:11434"
DEFAULT_MODEL = "qwen2.5-coder:7b"


def query_ollama(prompt: str, model: str = DEFAULT_MODEL, stream: bool = False) -> str:
    """调用 Ollama API 生成回复"""
    url = f"{OLLAMA_HOST}/api/generate"

    payload = {
        "model": model,
        "prompt": prompt,
        "stream": stream,
        "options": {
            "temperature": 0.7,
            "num_predict": 2048
        }
    }

    try:
        response = requests.post(url, json=payload, timeout=120)
        response.raise_for_status()

        if stream:
            # 处理流式响应
            result = ""
            for line in response.iter_lines():
                if line:
                    data = json.loads(line)
                    result += data.get("response", "")
                    if data.get("done"):
                        break
            return result
        else:
            # 非流式响应
            return response.json().get("response", "")

    except requests.exceptions.ConnectionError:
        return "错误：无法连接到 Ollama。请确保 Ollama 已启动：ollama serve"
    except Exception as e:
        return f"错误：{str(e)}"


def list_models():
    """列出可用的本地模型"""
    url = f"{OLLAMA_HOST}/api/tags"

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        models = response.json().get("models", [])

        print("Available Models:")
        print("-" * 50)
        for model in models:
            name = model.get("name", "unknown")
            size_gb = model.get("size", 0) / (1024**3)
            param_size = model.get("details", {}).get("parameter_size", "unknown")
            print(f"  * {name}")
            print(f"    Size: {size_gb:.1f} GB | Parameters: {param_size}")
        print("-" * 50)

    except Exception as e:
        print(f"Failed to get model list: {e}")


def code_complete(code_context: str, instruction: str = ""):
    """代码补全功能"""
    prompt = f"""你是一个专业的编程助手。请根据以下代码上下文，完成或补全代码。

代码上下文：
```
{code_context}
```

{instruction}

请只输出代码，不要解释："""

    result = query_ollama(prompt)
    print(result)


def code_explain(code: str):
    """代码解释功能"""
    prompt = f"""请详细解释以下代码的工作原理：

```
{code}
```

请用中文解释："""

    result = query_ollama(prompt)
    print(result)


def code_review(code: str):
    """代码审查功能"""
    prompt = f"""请审查以下代码，找出潜在问题并提出改进建议：

```
{code}
```

请从以下方面分析：
1. 代码风格和可读性
2. 潜在 Bug
3. 性能问题
4. 改进建议

用中文回答："""

    result = query_ollama(prompt)
    print(result)


def main():
    if len(sys.argv) < 2:
        print("""
Ollama 本地模型集成工具

用法：
  python ollama_helper.py <命令> [参数]

命令：
  list                    列出可用模型
  complete <代码文件>     代码补全
  explain <代码文件>      代码解释
  review <代码文件>       代码审查
  chat "<提示词>"         自由对话

示例：
  python ollama_helper.py list
  python ollama_helper.py complete mycode.py
  python ollama_helper.py explain "def hello(): print('hi')"
  python ollama_helper.py review myscript.py
        """)
        return

    command = sys.argv[1]

    if command == "list":
        list_models()

    elif command == "complete":
        if len(sys.argv) < 3:
            print("请提供代码文件路径或代码字符串")
            return
        code = sys.argv[2]
        if code.endswith('.py') or code.endswith('.js') or code.endswith('.ts'):
            try:
                with open(code, 'r', encoding='utf-8') as f:
                    code = f.read()
            except:
                pass
        code_complete(code)

    elif command == "explain":
        if len(sys.argv) < 3:
            print("请提供代码")
            return
        code = sys.argv[2]
        code_explain(code)

    elif command == "review":
        if len(sys.argv) < 3:
            print("请提供代码文件")
            return
        code_file = sys.argv[2]
        try:
            with open(code_file, 'r', encoding='utf-8') as f:
                code = f.read()
            code_review(code)
        except Exception as e:
            print(f"读取文件失败: {e}")

    elif command == "chat":
        if len(sys.argv) < 3:
            print("请提供提示词")
            return
        prompt = sys.argv[2]
        result = query_ollama(prompt)
        print(result)

    else:
        # 默认：直接对话
        prompt = " ".join(sys.argv[1:])
        result = query_ollama(prompt)
        print(result)


if __name__ == "__main__":
    main()
