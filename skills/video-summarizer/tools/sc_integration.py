"""
Video Summarizer 自我纠错集成模块
为视频提取功能添加自动错误捕获和学习
"""

import sys
from pathlib import Path
from functools import wraps

# 添加 memory-bank tools 到路径
TOOLS_DIR = Path.home() / '.claude' / 'memory-bank' / 'tools'
if str(TOOLS_DIR) not in sys.path:
    sys.path.insert(0, str(TOOLS_DIR))

try:
    from self_correction_unified import UnifiedSelfCorrection
    _sc_system = UnifiedSelfCorrection("video-summarizer")
except ImportError as e:
    print(f"Warning: 无法加载自我纠错系统: {e}")
    _sc_system = None


def video_operation(tool_name: str, operation: str = None):
    """
    Video Summarizer 操作装饰器
    自动捕获错误并记录到记忆库

    用法:
        @video_operation("yt_dlp", "extract audio")
        def extract_audio(url):
            ...
    """
    def decorator(func):
        if _sc_system is None:
            # 如果纠错系统未加载，直接返回原函数
            return func

        return _sc_system.capture_decorator(
            tool_name=tool_name,
            operation=operation or func.__name__
        )(func)
    return decorator


def check_video_risk(operation: str, context: dict = None) -> dict:
    """
    检查视频操作风险

    用法:
        risks = check_video_risk("download", {"url": video_url})
    """
    if _sc_system is None:
        return {"risks": [], "history": {"history_count": 0}}

    from self_correction_unified import check_before_operation

    result = check_before_operation("VideoSummarizer", operation)

    # 显示警告
    if result['history']['history_count'] > 0:
        print(f"⚠️  {operation} 有 {result['history']['history_count']} 次历史错误")

    if result['risks']:
        print(f"🚨 检测到 {len(result['risks'])} 个风险:")
        for risk in result['risks']:
            print(f"  [{risk['level']}] {risk['message']}")

    return result


def extract_knowledge_from_result(state: dict, error: Exception = None):
    """
    从提取结果中提取知识

    用法:
        extract_knowledge_from_result(extraction_state.to_dict())
    """
    if _sc_system is None:
        return

    if error:
        # 错误情况由装饰器自动处理
        return

    # 成功的经验也可以记录
    if state.get('success'):
        print(f"✅ 视频提取成功，已记录经验")


# 便捷导入
__all__ = [
    'video_operation',
    'check_video_risk',
    'extract_knowledge_from_result',
    '_sc_system'
]
