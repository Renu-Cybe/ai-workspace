"""
自我纠错系统集成模块
自动捕获工具调用错误并记录到 memory-bank
"""

import functools
import traceback
from typing import Callable, Any
from pathlib import Path
import sys

# 添加上级目录到路径
tools_dir = Path(__file__).parent
sys.path.insert(0, str(tools_dir))

from self_correction import ErrorTracker, record_error, check_task, ExperienceQuery


class ErrorCapture:
    """错误捕获装饰器 - 自动记录工具调用错误"""

    def __init__(self, tool_name: str, operation: str = None):
        self.tool_name = tool_name
        self.operation = operation
        self.tracker = ErrorTracker()

    def __call__(self, func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # 任务前检查
            check_result = check_task(self.tool_name, self.operation or func.__name__)
            if check_result['history_count'] > 0:
                print(f"⚠️ 注意: {self.tool_name} 曾有 {check_result['history_count']} 次错误记录")
                if check_result['prevention_tips']:
                    print("预防建议:")
                    for tip in check_result['prevention_tips'][:3]:
                        print(f"  • {tip}")

            try:
                result = func(*args, **kwargs)
                return result
            except Exception as e:
                # 捕获并记录错误
                error = self.tracker.capture(
                    error_type=self._classify_error(e),
                    message=str(e),
                    tool=self.tool_name,
                    operation=self.operation or func.__name__,
                    severity=self._assess_severity(e),
                    input_data={'args': str(args), 'kwargs': str(kwargs)},
                    stack_trace=traceback.format_exc(),
                    tags=self._extract_tags(e)
                )
                print(f"❌ 错误已记录: {error.id}")
                raise

        return wrapper

    def _classify_error(self, e: Exception) -> str:
        """分类错误类型"""
        error_msg = str(e).lower()

        if 'timeout' in error_msg or 'connection' in error_msg:
            return 'api_error'
        elif 'permission' in error_msg or 'access denied' in error_msg:
            return 'permission_error'
        elif 'not found' in error_msg or 'no such file' in error_msg:
            return 'resource_error'
        elif 'memory' in error_msg or 'out of' in error_msg:
            return 'resource_error'
        elif 'invalid' in error_msg or 'syntax' in error_msg:
            return 'logic_error'
        else:
            return 'tool_execution_error'

    def _assess_severity(self, e: Exception) -> str:
        """评估严重级别"""
        error_msg = str(e).lower()

        if any(kw in error_msg for kw in ['critical', 'fatal', 'crash']):
            return 'critical'
        elif any(kw in error_msg for kw in ['permission', 'access denied', 'unauthorized']):
            return 'high'
        elif any(kw in error_msg for kw in ['timeout', 'retry', 'temporary']):
            return 'medium'
        else:
            return 'low'

    def _extract_tags(self, e: Exception) -> list:
        """从错误信息提取标签"""
        tags = []
        error_msg = str(e).lower()

        if 'network' in error_msg or 'connection' in error_msg:
            tags.append('network')
        if 'timeout' in error_msg:
            tags.append('timeout')
        if 'api' in error_msg:
            tags.append('api')
        if 'file' in error_msg:
            tags.append('file')
        if 'git' in error_msg:
            tags.append('git')

        return tags


class SelfCorrectionSession:
    """
    自我纠错会话包装器
    包装整个会话，自动捕获和记录错误
    """

    def __init__(self, session_name: str = None):
        self.session_name = session_name or f"session-{__import__('datetime').datetime.now().strftime('%Y%m%d-%H%M%S')}"
        self.tracker = ErrorTracker(self.session_name)
        self.error_count = 0
        self.fix_count = 0

    def record_tool_error(self, tool: str, operation: str, error: Exception, **kwargs):
        """记录工具错误"""
        record = self.tracker.capture(
            error_type=getattr(error, 'error_type', 'tool_execution_error'),
            message=str(error),
            tool=tool,
            operation=operation,
            severity=getattr(error, 'severity', 'medium'),
            **kwargs
        )
        self.error_count += 1
        return record

    def record_fix(self, error_id: str, solution: str, action_taken: str, root_cause: str = None):
        """记录修复"""
        from self_correction import record_fix
        record_fix(error_id, solution, action_taken, root_cause)
        self.fix_count += 1

    def get_session_summary(self) -> dict:
        """获取会话摘要"""
        return {
            'session_name': self.session_name,
            'errors_recorded': self.error_count,
            'fixes_recorded': self.fix_count,
            'improvement_rate': (self.fix_count / self.error_count * 100) if self.error_count > 0 else 100
        }

    def show_prevention_tips(self, tool: str):
        """显示预防建议"""
        query = ExperienceQuery()
        tips = query.get_prevention_tips(tool=tool)
        if tips:
            print(f"\n💡 {tool} 预防建议:")
            for i, tip in enumerate(tips[:5], 1):
                print(f"  {i}. {tip}")


# 便捷使用函数

def capture_errors(tool_name: str, operation: str = None):
    """错误捕获装饰器工厂"""
    return ErrorCapture(tool_name, operation)


def start_correction_session(name: str = None) -> SelfCorrectionSession:
    """启动自我纠错会话"""
    return SelfCorrectionSession(name)


def check_before_use(tool: str, operation: str = None) -> dict:
    """使用工具前检查"""
    return check_task(tool, operation or 'unknown')


# 集成示例
if __name__ == "__main__":
    print("=== 自我纠错系统集成测试 ===\n")

    # 1. 使用装饰器捕获错误
    print("1. 测试错误捕获装饰器...")

    @capture_errors(tool_name="Bash", operation="test command")
    def risky_operation():
        raise RuntimeError("模拟网络超时")

    try:
        risky_operation()
    except:
        print("   错误已被捕获并记录")

    # 2. 会话包装器
    print("\n2. 测试会话包装器...")
    session = start_correction_session("test-session")

    try:
        raise ValueError("测试错误")
    except Exception as e:
        error = session.record_tool_error("WebFetch", "fetch page", e)
        print(f"   会话记录错误: {error.id}")

    # 3. 任务前检查
    print("\n3. 测试任务前检查...")
    result = check_before_use("WebFetch", "fetch documentation")
    print(f"   历史错误: {result['history_count']}")

    # 4. 会话摘要
    print("\n4. 会话摘要:")
    summary = session.get_session_summary()
    print(f"   错误数: {summary['errors_recorded']}")
    print(f"   修复数: {summary['fixes_recorded']}")

    print("\n=== 集成测试完成 ===")
