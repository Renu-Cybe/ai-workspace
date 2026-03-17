#!/usr/bin/env python3
"""
skill-generating 脚本
官方规范：stdin JSON → stdout JSON, stderr 错误
"""

import json
import sys
import os
import io
from pathlib import Path
from datetime import datetime

# Force UTF-8 on Windows
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')


def log_error(message: str):
    """输出错误到 stderr"""
    print(message, file=sys.stderr)


def generate_skill_md(config: dict) -> str:
    """生成 SKILL.md 内容"""
    name = config.get("name", "my-skill")
    description = config.get("description", "A useful skill")
    tools = config.get("tools", ["Bash", "Read", "Write"])
    tools_str = ", ".join(f'"{t}"' for t in tools)

    return f"""---
name: {name}
description: |
  {description}
tools: [{tools_str}]
context: fork
---

# {name.title().replace("-", " ")}

## 用途

{description}

## 适用场景

- 场景1：xxx
- 场景2：xxx

## 使用方式

### 基础用法
```
用户: "运行 {name}"
用户: "执行 {name}"
```

## 工作流程

1. **接收输入**
   - 解析用户指令

2. **处理逻辑**
   - 执行核心功能

3. **输出结果**
   - 返回执行状态

## 示例

**用户**: "使用 {name}"

**Claude**: 执行中...
"""


def generate_script(config: dict) -> str:
    """生成 scripts/processor.py"""
    name = config.get("name", "my-skill")

    return f'''#!/usr/bin/env python3
"""
{name} processor script
官方规范：stdin JSON → stdout JSON
"""

import json
import sys


def main():
    try:
        # 从 stdin 读取配置
        config = json.load(sys.stdin)

        # TODO: 实现核心逻辑
        result = {{
            "status": "ok",
            "message": "Processing complete",
            "data": config
        }}

        # 输出到 stdout
        print(json.dumps(result, ensure_ascii=False))

    except Exception as e:
        print(json.dumps({{
            "status": "error",
            "message": str(e)
        }}), file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
'''


def generate_reference(config: dict) -> str:
    """生成 reference/guide.md"""
    name = config.get("name", "my-skill")

    return f"""# {name} Reference

## 内部实现细节

### 输入格式

```json
{{
  "param1": "value1",
  "param2": "value2"
}}
```

### 输出格式

```json
{{
  "status": "ok|error",
  "message": "result message",
  "data": {{}}
}}
```

### 错误处理

- 输入无效 JSON：返回 error 状态
- 缺少必需参数：返回错误提示
- 执行异常：stderr 输出错误信息

## 开发 notes

- 创建时间: {datetime.now().isoformat()}
- 遵循官方三层架构
"""


def create_skill(config: dict) -> dict:
    """创建 skill 目录结构"""
    name = config.get("name", "my-skill")
    skills_dir = Path.home() / ".claude" / "skills" / name

    result = {
        "skill_name": name,
        "created_at": datetime.now().isoformat(),
        "files_created": [],
        "errors": []
    }

    try:
        # 创建目录
        scripts_dir = skills_dir / "scripts"
        reference_dir = skills_dir / "reference"

        skills_dir.mkdir(parents=True, exist_ok=True)
        scripts_dir.mkdir(exist_ok=True)
        reference_dir.mkdir(exist_ok=True)

        # 创建 SKILL.md
        skill_md = skills_dir / "SKILL.md"
        skill_md.write_text(generate_skill_md(config), encoding="utf-8")
        result["files_created"].append(str(skill_md))

        # 创建 scripts/processor.py
        if config.get("has_script", True):
            processor = scripts_dir / "processor.py"
            processor.write_text(generate_script(config), encoding="utf-8")
            result["files_created"].append(str(processor))

        # 创建 reference/guide.md
        guide = reference_dir / "guide.md"
        guide.write_text(generate_reference(config), encoding="utf-8")
        result["files_created"].append(str(guide))

        result["status"] = "ok"

    except Exception as e:
        result["status"] = "error"
        result["errors"].append(str(e))

    return result


def main():
    """主入口：从 stdin 读取，stdout 输出"""
    try:
        # 读取配置
        if sys.stdin.isatty():
            # 交互模式，使用默认配置
            config = {
                "name": "example-skill",
                "description": "An example skill",
                "tools": ["Bash", "Read", "Write"]
            }
        else:
            config = json.load(sys.stdin)

        # 验证必需字段
        if "name" not in config:
            raise ValueError("Missing required field: name")

        # 创建 skill
        result = create_skill(config)

        # 输出结果
        print(json.dumps(result, ensure_ascii=False, indent=2))

        # 退出码
        sys.exit(0 if result.get("status") == "ok" else 1)

    except json.JSONDecodeError as e:
        log_error(f"Invalid JSON: {e}")
        print(json.dumps({"status": "error", "message": f"Invalid JSON: {e}"}))
        sys.exit(1)

    except Exception as e:
        log_error(f"Error: {e}")
        print(json.dumps({"status": "error", "message": str(e)}))
        sys.exit(1)


if __name__ == "__main__":
    main()
