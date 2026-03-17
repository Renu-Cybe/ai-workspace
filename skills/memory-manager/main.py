#!/usr/bin/env python3
"""
Memory Manager - 统一记忆库管理 Skill
整合标签、搜索、分支、看板等功能
"""

import re
import sys
import subprocess
from pathlib import Path

# 添加自我纠错系统
sys.path.insert(0, str(Path.home() / '.claude' / 'memory-bank' / 'tools'))
try:
    from self_correction_unified import UnifiedSelfCorrection
    _sc = UnifiedSelfCorrection("memory-manager")
    HAS_SELF_CORRECTION = True

    def _sc_wrapper(tool_name):
        """自我纠错装饰器"""
        def decorator(func):
            if _sc:
                return _sc.capture_decorator(tool_name=tool_name, operation=func.__name__)(func)
            return func
        return decorator
except ImportError:
    HAS_SELF_CORRECTION = False
    _sc = None
    def _sc_wrapper(tool_name):
        def decorator(func):
            return func
        return decorator

# 工具路径
TOOLS_DIR = Path("C:/Users/Administrator/.claude/projects/C--Users-Administrator/memory/tools")


@_sc_wrapper("MemoryManager")
def run_tool(tool_name, *args):
    """运行工具脚本 - 已集成自我纠错"""
    tool_path = TOOLS_DIR / f"{tool_name}.bat"
    if not tool_path.exists():
        print(f"工具不存在: {tool_path}")
        return False

    cmd = [str(tool_path)] + list(args)
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            encoding='utf-8',
            timeout=30
        )
        print(result.stdout)
        if result.stderr:
            print(result.stderr, file=sys.stderr)
        return result.returncode == 0
    except Exception as e:
        print(f"执行失败: {e}")
        return False


def handle_status_query(query):
    """处理状态查询"""
    patterns = [
        r'(?:检查|显示|查看).*?(?:记忆库|memory).*?(?:状态|统计|看板)',
        r'(?:memory|记忆库).*?(?:status|dashboard|stats)',
        r'^看板$',
        r'^状态$',
    ]

    for pattern in patterns:
        if re.search(pattern, query, re.IGNORECASE):
            return run_tool("dashboard")

    return False


def handle_search(query):
    """处理搜索请求"""
    # 搜索关键词
    search_patterns = [
        r'(?:搜索|查找|找一下).*?(?:关于|包含)?\s*["\']?([^"\']+)["\']?\s*(?:的会话|的文件|的内容)?',
        r'search\s+for\s+["\']?([^"\']+)["\']?',
    ]

    for pattern in search_patterns:
        match = re.search(pattern, query, re.IGNORECASE)
        if match:
            keyword = match.group(1).strip()
            return run_tool("search", keyword, "-p")

    # 按标签搜索
    tag_patterns = [
        r'(?:按标签|标签).*?["\']?([^"\']+)["\']?',
        r'tag[:\s]*["\']?([^"\']+)["\']?',
    ]

    for pattern in tag_patterns:
        match = re.search(pattern, query, re.IGNORECASE)
        if match:
            tag = match.group(1).strip()
            return run_tool("search", "-t", tag)

    return False


def handle_branch(query):
    """处理分支管理"""
    # 切换分支
    switch_patterns = [
        r'(?:切换|转到|去).*?(?:分支|branch)?\s*["\']?([^"\']+)["\']?',
        r'switch\s+to\s+["\']?([^"\']+)["\']?',
    ]

    for pattern in switch_patterns:
        match = re.search(pattern, query, re.IGNORECASE)
        if match:
            branch = match.group(1).strip()
            return run_tool("branch", "-s", branch)

    # 创建分支
    create_patterns = [
        r'(?:创建|新建).*?(?:分支|branch)?\s*["\']?([^"\']+)["\']?',
        r'create\s+(?:branch)?\s*["\']?([^"\']+)["\']?',
    ]

    for pattern in create_patterns:
        match = re.search(pattern, query, re.IGNORECASE)
        if match:
            branch = match.group(1).strip()
            return run_tool("branch", "-c", branch)

    # 显示分支
    if re.search(r'(?:显示|查看|当前).*?(?:分支|branch)', query, re.IGNORECASE):
        return run_tool("branch", "-t")

    # 列出所有分支
    if re.search(r'(?:列出|所有).*?(?:分支|branch)', query, re.IGNORECASE):
        return run_tool("branch", "-l")

    return False


def handle_tagging(query):
    """处理标签管理"""
    # 给所有会话打标签
    if re.search(r'(?:给|为).*?(?:所有)?.*?会话.*?(?:打标签|标签)', query, re.IGNORECASE):
        return run_tool("tag", "-a")

    # 列出所有标签
    if re.search(r'(?:列出|显示|所有).*?(?:标签|tags?)', query, re.IGNORECASE):
        return run_tool("tag", "-l")

    # 重新索引
    if re.search(r'(?:重新|更新).*?(?:索引|index)', query, re.IGNORECASE):
        return run_tool("search", "--index")

    return False


def main():
    """主入口"""
    if len(sys.argv) < 2:
        print("Usage: memory-manager.py <query>")
        sys.exit(1)

    query = " ".join(sys.argv[1:])

    # 按优先级处理
    handlers = [
        handle_status_query,
        handle_search,
        handle_branch,
        handle_tagging,
    ]

    for handler in handlers:
        if handler(query):
            sys.exit(0)

    print(f"无法理解的命令: {query}")
    print("支持的命令示例:")
    print('  - "检查记忆库状态"')
    print('  - "搜索关于 docker 的会话"')
    print('  - "切换到 feature 分支"')
    print('  - "给所有会话打标签"')
    sys.exit(1)


if __name__ == "__main__":
    main()
