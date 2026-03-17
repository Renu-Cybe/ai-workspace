"""
统一自我纠错系统集成模块
整合基础版 + 增强版功能，提供完整的工作流支持

功能概览：
1. 错误捕获和记录（基础版）
2. 模式分析和知识提取（增强版）
3. 实时风险检查（增强版）
4. 预防清单生成（增强版）
5. 学习报告生成（增强版）
6. CLI 命令行工具
"""

import functools
import traceback
import sys
import json
from typing import Callable, Any, Dict, List, Optional
from pathlib import Path
from datetime import datetime

# 添加上级目录到路径
tools_dir = Path(__file__).parent
sys.path.insert(0, str(tools_dir))

# 导入基础版
from self_correction import (
    ErrorTracker,
    record_error,
    record_fix,
    check_task,
    ExperienceQuery,
    WeeklyReport
)

# 导入增强版
from self_correction_enhanced import (
    EnhancedSelfCorrection,
    ErrorPatternAnalyzer,
    KnowledgeExtractor,
    PreventionGenerator,
    RealtimeWarningSystem,
    analyze_errors as enhanced_analyze,
    get_prevention_guide,
    check_risk,
    generate_learning_report,
    search_knowledge
)


class UnifiedSelfCorrection:
    """
    统一自我纠错系统
    整合基础版和增强版的所有功能
    """

    def __init__(self, session_name: str = None):
        self.session_name = session_name or f"session-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        self.tracker = ErrorTracker(self.session_name)
        self.enhanced = EnhancedSelfCorrection()
        self.warning_system = RealtimeWarningSystem()
        self.session_errors = []
        self.session_fixes = []

    # ==================== 错误捕获 ====================

    def capture_decorator(self, tool_name: str, operation: str = None):
        """错误捕获装饰器（增强版）"""
        def decorator(func: Callable) -> Callable:
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                # 1. 操作前风险检查
                operation_name = operation or func.__name__
                self._pre_operation_check(tool_name, operation_name)

                try:
                    # 2. 执行操作
                    result = func(*args, **kwargs)
                    return result
                except Exception as e:
                    # 3. 捕获并记录错误
                    error = self._handle_error(e, tool_name, operation_name, args, kwargs)
                    raise

            return wrapper
        return decorator

    def _pre_operation_check(self, tool: str, operation: str):
        """操作前检查"""
        # 基础版历史检查
        check_result = check_task(tool, operation)
        if check_result['history_count'] > 0:
            print(f"⚠️  历史错误提醒: {tool} 有 {check_result['history_count']} 次错误记录")
            if check_result['prevention_tips']:
                print("预防建议:")
                for tip in check_result['prevention_tips'][:3]:
                    print(f"  • {tip}")

        # 增强版实时风险检查
        risks = self.warning_system.check_risk(tool, operation)
        if risks:
            print(f"\n🚨 实时风险警告 ({len(risks)} 项):")
            for risk in risks:
                icon = "🔴" if risk['level'] == 'high' else "🟡" if risk['level'] == 'medium' else "🟢"
                print(f"  {icon} [{risk['level'].upper()}] {risk['type']}: {risk['message']}")
                if risk.get('prevention'):
                    print(f"      预防: {', '.join(risk['prevention'][:2])}")

    def _handle_error(self, e: Exception, tool: str, operation: str, args, kwargs) -> Any:
        """处理错误并记录"""
        # 基础版错误记录
        error = self.tracker.capture(
            error_type=self._classify_error(e),
            message=str(e),
            tool=tool,
            operation=operation,
            severity=self._assess_severity(e),
            input_data={'args': str(args), 'kwargs': str(kwargs)},
            stack_trace=traceback.format_exc(),
            tags=self._extract_tags(e)
        )
        self.session_errors.append(error)
        print(f"❌ 错误已记录: {error.id}")

        # 增强版知识提取
        try:
            extractor = KnowledgeExtractor()
            error_dict = error.to_dict()
            knowledge = extractor.extract_from_error({
                'id': error.id,
                'error_type': error.error_type,
                'severity': error.severity,
                'message': error.message,
                'context': {
                    'tool': error.context.tool if error.context else tool,
                    'operation': error.context.operation if error.context else operation,
                    'tags': error.context.tags if error.context and error.context.tags else self._extract_tags(e)
                }
            })
            if knowledge:
                extractor.save_knowledge(knowledge)
                print(f"💡 知识已提取: {knowledge.title}")
        except Exception as ex:
            print(f"  知识提取失败: {ex}")

        return error

    # ==================== 知识管理 ====================

    def search_knowledge_base(self, query: str, tags: List[str] = None) -> List[Dict]:
        """搜索知识库"""
        return search_knowledge(query, tags=tags or [])

    def get_prevention_guide(self, tool: str, operation: str = None) -> Dict:
        """获取预防指南"""
        return get_prevention_guide(tool, operation or 'unknown')

    # ==================== 分析和学习 ====================

    def analyze_session(self) -> Dict:
        """分析当前会话"""
        return {
            'session_name': self.session_name,
            'errors_recorded': len(self.session_errors),
            'fixes_recorded': len(self.session_fixes),
            'patterns': self._analyze_patterns(),
            'improvement_rate': self._calculate_improvement_rate()
        }

    def _analyze_patterns(self) -> List[Dict]:
        """分析会话中的错误模式"""
        if len(self.session_errors) < 2:
            return []

        analyzer = ErrorPatternAnalyzer()
        error_dicts = []
        for e in self.session_errors:
            error_dict = {
                'error_type': e.error_type,
                'tool': e.context.tool if e.context else 'unknown',
                'operation': e.context.operation if e.context else 'unknown',
                'message': e.message,
                'tags': e.context.tags if e.context else []
            }
            error_dicts.append(error_dict)

        return analyzer._cluster_errors(error_dicts)

    def _calculate_improvement_rate(self) -> float:
        """计算改进率"""
        if not self.session_errors:
            return 100.0
        if not self.session_fixes:
            return 0.0
        return min(100.0, (len(self.session_fixes) / len(self.session_errors)) * 100)

    def generate_report(self, days: int = 7) -> str:
        """生成学习报告"""
        return generate_learning_report(days=days)

    # ==================== 辅助方法 ====================

    @staticmethod
    def _classify_error(e: Exception) -> str:
        """分类错误类型"""
        error_msg = str(e).lower()
        error_type = type(e).__name__.lower()

        if 'timeout' in error_msg or 'connection' in error_msg:
            return 'api_error'
        elif 'permission' in error_msg or 'access denied' in error_msg:
            return 'permission_error'
        elif 'not found' in error_msg or 'no such file' in error_msg:
            return 'resource_error'
        elif 'memory' in error_msg:
            return 'resource_error'
        elif 'invalid' in error_msg or 'syntax' in error_msg:
            return 'logic_error'
        elif 'unicode' in error_msg or 'encode' in error_msg or 'decode' in error_msg:
            return 'encoding_error'
        else:
            return 'tool_execution_error'

    @staticmethod
    def _assess_severity(e: Exception) -> str:
        """评估严重级别"""
        error_msg = str(e).lower()

        if any(kw in error_msg for kw in ['critical', 'fatal', 'crash']):
            return 'critical'
        elif any(kw in error_msg for kw in ['permission', 'access denied']):
            return 'high'
        elif any(kw in error_msg for kw in ['timeout', 'retry', 'temporary']):
            return 'medium'
        else:
            return 'low'

    @staticmethod
    def _extract_tags(e: Exception) -> List[str]:
        """提取标签"""
        tags = []
        error_msg = str(e).lower()
        error_type = type(e).__name__.lower()

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
        if 'encode' in error_msg or 'unicode' in error_msg:
            tags.append('encoding')
        if 'windows' in error_msg or 'win32' in error_msg:
            tags.append('windows')

        return tags


# ==================== 便捷函数 ====================

def unified_capture(tool_name: str, operation: str = None):
    """统一错误捕获装饰器"""
    system = UnifiedSelfCorrection()
    return system.capture_decorator(tool_name, operation)


def check_before_operation(tool: str, operation: str = None) -> Dict:
    """操作前检查（基础+增强）"""
    result = {
        'tool': tool,
        'operation': operation or 'unknown',
        'history': check_task(tool, operation or 'unknown'),
        'risks': check_risk(tool, operation or 'unknown'),
        'prevention': get_prevention_guide(tool, operation or 'unknown')
    }
    return result


def quick_analyze(days: int = 7) -> Dict:
    """快速分析"""
    return enhanced_analyze(days=days)


# ==================== CLI 接口 ====================

def cli_main():
    """命令行接口"""
    import argparse
    import io

    # 修复 Windows 编码
    if sys.platform == 'win32':
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

    parser = argparse.ArgumentParser(description='统一自我纠错系统 CLI')
    subparsers = parser.add_subparsers(dest='command', help='可用命令')

    # 分析命令
    analyze_parser = subparsers.add_parser('analyze', help='分析错误模式')
    analyze_parser.add_argument('-d', '--days', type=int, default=7, help='分析天数')

    # 检查命令
    check_parser = subparsers.add_parser('check', help='操作前检查')
    check_parser.add_argument('tool', help='工具名称')
    check_parser.add_argument('-o', '--operation', help='操作名称')

    # 报告命令
    report_parser = subparsers.add_parser('report', help='生成学习报告')
    report_parser.add_argument('-d', '--days', type=int, default=7, help='报告天数')
    report_parser.add_argument('-o', '--output', help='输出文件')

    # 搜索命令
    search_parser = subparsers.add_parser('search', help='搜索知识库')
    search_parser.add_argument('query', help='搜索关键词')
    search_parser.add_argument('-t', '--tags', nargs='+', help='标签过滤')

    args = parser.parse_args()

    if args.command == 'analyze':
        print(f"🔍 分析近 {args.days} 天的错误模式...")
        result = enhanced_analyze(days=args.days)
        print(f"\n✅ 分析完成:")
        print(f"  发现 {result['patterns_found']} 个错误模式")
        print(f"  提取 {result['knowledge_extracted']} 条知识")
        print(f"  生成 {result['checklists_generated']} 份预防清单")

    elif args.command == 'check':
        print(f"🛡️  检查 {args.tool} 操作风险...")
        result = check_before_operation(args.tool, args.operation)

        if result['history']['history_count'] > 0:
            print(f"\n⚠️  历史错误: {result['history']['history_count']} 次")

        if result['risks']:
            print(f"\n🚨 实时风险 ({len(result['risks'])} 项):")
            for risk in result['risks']:
                print(f"  [{risk['level']}] {risk['message']}")

    elif args.command == 'report':
        print(f"📊 生成近 {args.days} 天学习报告...")
        report = generate_learning_report(days=args.days)

        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                f.write(report)
            print(f"✅ 报告已保存: {args.output}")
        else:
            print("\n" + "=" * 50)
            print(report[:1000])
            print("...")

    elif args.command == 'search':
        print(f"🔎 搜索知识库: '{args.query}'...")
        results = search_knowledge(args.query, tags=args.tags or [])
        print(f"\n找到 {len(results)} 条结果:")
        for item in results[:5]:
            print(f"\n📖 {item['title']}")
            print(f"   分类: {item['category']}")
            print(f"   标签: {', '.join(item['tags'])}")

    else:
        parser.print_help()


if __name__ == "__main__":
    cli_main()
