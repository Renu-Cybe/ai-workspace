#!/usr/bin/env python3
"""
scheduler.py - 定时任务管理器
管理 Claude Code Skills 的定时执行
使用 Windows Task Scheduler (schtasks) 作为底层
"""

import json
import sys
import io
import os
import subprocess
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional

# Force UTF-8 on Windows
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Configuration
SCHEDULER_DIR = Path.home() / ".claude" / "scheduler"
SCRIPTS_DIR = SCHEDULER_DIR / "scripts"
LOGS_DIR = SCHEDULER_DIR / "logs"
TASKS_FILE = SCHEDULER_DIR / "tasks.json"

def ensure_dirs():
    """确保目录存在"""
    SCHEDULER_DIR.mkdir(parents=True, exist_ok=True)
    SCRIPTS_DIR.mkdir(parents=True, exist_ok=True)
    LOGS_DIR.mkdir(parents=True, exist_ok=True)

def load_tasks() -> Dict[str, Any]:
    """加载任务配置"""
    if TASKS_FILE.exists():
        try:
            return json.loads(TASKS_FILE.read_text(encoding='utf-8'))
        except:
            pass
    return {"version": "1.0", "tasks": {}}

def save_tasks(tasks: Dict[str, Any]):
    """保存任务配置"""
    ensure_dirs()
    TASKS_FILE.write_text(json.dumps(tasks, ensure_ascii=False, indent=2), encoding='utf-8')

def create_bat_script(task_name: str, skill_name: str) -> Path:
    """创建批处理脚本"""
    ensure_dirs()
    script_path = SCRIPTS_DIR / f"{task_name}.bat"

    bat_content = f'''@echo off
chcp 65001 >nul
echo [{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}] Running {task_name}...

:: Change to Claude Code directory
cd /d %USERPROFILE%\\.claude

:: Run the skill
echo {{\"action\": \"run\", \"timestamp\": \"{datetime.now().isoformat()}\"}} | skill {skill_name}

:: Log completion
echo [{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}] {task_name} completed. >> %USERPROFILE%\\.claude\\scheduler\\logs\\{task_name}.log
'''

    script_path.write_text(bat_content, encoding='utf-8')
    return script_path

def parse_schedule(schedule_type: str, **kwargs) -> Dict[str, str]:
    """解析调度配置为 schtasks 参数"""
    result = {}

    if schedule_type == "daily":
        # /SC DAILY /ST HH:MM
        time_str = kwargs.get("time", "00:00")
        result["schedule"] = "DAILY"
        result["time"] = time_str.replace(":", "")

    elif schedule_type == "weekly":
        # /SC WEEKLY /D MON /ST HH:MM
        day_map = {"mon": "MON", "tue": "TUE", "wed": "WED",
                   "thu": "THU", "fri": "FRI", "sat": "SAT", "sun": "SUN"}
        day = day_map.get(kwargs.get("day", "mon").lower(), "MON")
        time_str = kwargs.get("time", "09:00")
        result["schedule"] = "WEEKLY"
        result["days"] = day
        result["time"] = time_str.replace(":", "")

    elif schedule_type == "monthly":
        # /SC MONTHLY /D 1 /ST HH:MM
        day = kwargs.get("date", "1")
        time_str = kwargs.get("time", "00:00")
        result["schedule"] = "MONTHLY"
        result["date"] = day
        result["time"] = time_str.replace(":", "")

    elif schedule_type == "once":
        # /SC ONCE /ST HH:MM
        time_str = kwargs.get("time", datetime.now().strftime("%H:%M"))
        result["schedule"] = "ONCE"
        result["time"] = time_str.replace(":", "")

    return result

def add_task(config: Dict[str, Any]) -> Dict[str, Any]:
    """添加定时任务"""
    task_name = config.get("name")
    skill_name = config.get("skill", task_name)
    schedule_type = config.get("schedule", "daily")

    if not task_name:
        return {"status": "error", "message": "Missing task name"}

    # 创建批处理脚本
    script_path = create_bat_script(task_name, skill_name)

    # 解析调度配置
    schedule_config = parse_schedule(
        schedule_type,
        time=config.get("time", "00:00"),
        day=config.get("day", "mon"),
        date=config.get("date", "1")
    )

    # 构建 schtasks 命令
    task_cmd = f'schtasks /Create /TN "ClaudeScheduler\\{task_name}" /TR "{script_path}"'

    if schedule_config.get("schedule") == "DAILY":
        task_cmd += f' /SC DAILY /ST {schedule_config["time"]}'
    elif schedule_config.get("schedule") == "WEEKLY":
        task_cmd += f' /SC WEEKLY /D {schedule_config["days"]} /ST {schedule_config["time"]}'
    elif schedule_config.get("schedule") == "MONTHLY":
        task_cmd += f' /SC MONTHLY /D {schedule_config["date"]} /ST {schedule_config["time"]}'
    elif schedule_config.get("schedule") == "ONCE":
        task_cmd += f' /SC ONCE /ST {schedule_config["time"]}'

    # 强制覆盖
    task_cmd += ' /F'

    try:
        result = subprocess.run(task_cmd, capture_output=True, text=True, shell=True)

        if result.returncode == 0:
            # 保存任务配置
            tasks = load_tasks()
            tasks["tasks"][task_name] = {
                "skill": skill_name,
                "schedule": schedule_type,
                "time": config.get("time", "00:00"),
                "day": config.get("day"),
                "date": config.get("date"),
                "script": str(script_path),
                "created": datetime.now().isoformat(),
                "enabled": True
            }
            save_tasks(tasks)

            return {
                "status": "ok",
                "message": f"Task '{task_name}' created successfully",
                "schedule": schedule_config,
                "next_run": f"Will run {schedule_type} at {config.get('time', '00:00')}"
            }
        else:
            return {"status": "error", "message": result.stderr or "Failed to create task"}

    except Exception as e:
        return {"status": "error", "message": str(e)}

def remove_task(config: Dict[str, Any]) -> Dict[str, Any]:
    """删除定时任务"""
    task_name = config.get("name")

    if not task_name:
        return {"status": "error", "message": "Missing task name"}

    try:
        # 删除 Windows 任务
        result = subprocess.run(
            f'schtasks /Delete /TN "ClaudeScheduler\\{task_name}" /F',
            capture_output=True, text=True, shell=True
        )

        # 删除配置
        tasks = load_tasks()
        if task_name in tasks["tasks"]:
            del tasks["tasks"][task_name]
            save_tasks(tasks)

        return {
            "status": "ok",
            "message": f"Task '{task_name}' removed"
        }

    except Exception as e:
        return {"status": "error", "message": str(e)}

def list_tasks(config: Dict[str, Any]) -> Dict[str, Any]:
    """列出所有定时任务"""
    try:
        # 查询 Windows 任务
        result = subprocess.run(
            'schtasks /Query /TN "ClaudeScheduler\\" /FO CSV /NH 2>nul || echo "No tasks"',
            capture_output=True, text=True, shell=True
        )

        # 加载本地配置
        tasks = load_tasks()

        output = {
            "status": "ok",
            "tasks": [],
            "count": 0
        }

        # 解析任务列表
        if result.returncode == 0 and "No tasks" not in result.stdout:
            for line in result.stdout.strip().split('\n'):
                if line and ',' in line:
                    parts = line.split('","')
                    if len(parts) >= 2:
                        task_name = parts[0].strip('"').replace('ClaudeScheduler\\', '')
                        task_info = tasks["tasks"].get(task_name, {})

                        output["tasks"].append({
                            "name": task_name,
                            "skill": task_info.get("skill", task_name),
                            "schedule": task_info.get("schedule", "unknown"),
                            "time": task_info.get("time", "unknown"),
                            "enabled": "Running" in line or "Ready" in line,
                            "next_run": parts[1].strip('"') if len(parts) > 1 else "unknown"
                        })

        # 也列出本地配置中但未在 schtasks 中的任务
        for name, info in tasks["tasks"].items():
            if not any(t["name"] == name for t in output["tasks"]):
                output["tasks"].append({
                    "name": name,
                    "skill": info.get("skill", name),
                    "schedule": info.get("schedule", "unknown"),
                    "time": info.get("time", "unknown"),
                    "enabled": info.get("enabled", True),
                    "next_run": "not scheduled in Task Scheduler"
                })

        output["count"] = len(output["tasks"])
        return output

    except Exception as e:
        return {"status": "error", "message": str(e)}

def run_task(config: Dict[str, Any]) -> Dict[str, Any]:
    """立即运行任务"""
    task_name = config.get("name")

    if not task_name:
        return {"status": "error", "message": "Missing task name"}

    try:
        # 运行 Windows 任务
        result = subprocess.run(
            f'schtasks /Run /TN "ClaudeScheduler\\{task_name}"',
            capture_output=True, text=True, shell=True
        )

        if result.returncode == 0:
            return {
                "status": "ok",
                "message": f"Task '{task_name}' triggered"
            }
        else:
            # 尝试直接运行脚本
            tasks = load_tasks()
            if task_name in tasks["tasks"]:
                script = tasks["tasks"][task_name].get("script")
                if script and Path(script).exists():
                    subprocess.Popen(f'cmd /c "{script}"', shell=True)
                    return {
                        "status": "ok",
                        "message": f"Task '{task_name}' started directly"
                    }

            return {"status": "error", "message": result.stderr or "Failed to run task"}

    except Exception as e:
        return {"status": "error", "message": str(e)}

def enable_task(config: Dict[str, Any], enabled: bool) -> Dict[str, Any]:
    """启用/禁用任务"""
    task_name = config.get("name")

    if not task_name:
        return {"status": "error", "message": "Missing task name"}

    try:
        action = "/Enable" if enabled else "/Disable"
        result = subprocess.run(
            f'schtasks /Change /TN "ClaudeScheduler\\{task_name}" {action}',
            capture_output=True, text=True, shell=True
        )

        # 更新本地配置
        tasks = load_tasks()
        if task_name in tasks["tasks"]:
            tasks["tasks"][task_name]["enabled"] = enabled
            save_tasks(tasks)

        status = "enabled" if enabled else "disabled"
        return {
            "status": "ok",
            "message": f"Task '{task_name}' {status}"
        }

    except Exception as e:
        return {"status": "error", "message": str(e)}

def get_logs(config: Dict[str, Any]) -> Dict[str, Any]:
    """获取任务日志"""
    task_name = config.get("name")
    lines = config.get("lines", 50)

    log_file = LOGS_DIR / f"{task_name}.log" if task_name else None

    if log_file and log_file.exists():
        content = log_file.read_text(encoding='utf-8')
        log_lines = content.split('\n')[-lines:]
        return {
            "status": "ok",
            "task": task_name,
            "logs": '\n'.join(log_lines)
        }
    else:
        # 列出所有日志文件
        logs = []
        if LOGS_DIR.exists():
            for f in sorted(LOGS_DIR.glob("*.log")):
                stat = f.stat()
                logs.append({
                    "task": f.stem,
                    "size": stat.st_size,
                    "modified": datetime.fromtimestamp(stat.st_mtime).isoformat()
                })

        return {
            "status": "ok",
            "logs_available": logs
        }

def main():
    """主入口"""
    try:
        if sys.stdin.isatty():
            # 交互模式 - 显示帮助
            print(json.dumps({
                "status": "ok",
                "message": "Scheduler - 定时任务管理器",
                "usage": {
                    "add": '{"action": "add", "name": "task-name", "schedule": "daily|weekly", "time": "HH:MM"}',
                    "remove": '{"action": "remove", "name": "task-name"}',
                    "list": '{"action": "list"}',
                    "run": '{"action": "run", "name": "task-name"}',
                    "enable": '{"action": "enable", "name": "task-name"}',
                    "disable": '{"action": "disable", "name": "task-name"}',
                    "logs": '{"action": "logs", "name": "task-name", "lines": 50}'
                }
            }, ensure_ascii=False, indent=2))
            return

        config = json.load(sys.stdin)
        action = config.get("action", "list")

        handlers = {
            "add": add_task,
            "remove": remove_task,
            "list": list_tasks,
            "run": run_task,
            "enable": lambda c: enable_task(c, True),
            "disable": lambda c: enable_task(c, False),
            "logs": get_logs
        }

        handler = handlers.get(action, list_tasks)
        result = handler(config)

        print(json.dumps(result, ensure_ascii=False, indent=2))

    except json.JSONDecodeError as e:
        print(json.dumps({"status": "error", "message": f"Invalid JSON: {e}"}))
    except Exception as e:
        print(json.dumps({"status": "error", "message": str(e)}))

if __name__ == "__main__":
    main()
