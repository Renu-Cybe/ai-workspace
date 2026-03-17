"""
自我纠错系统集成演示
展示如何在实际工作流中使用统一纠错系统
"""

import sys
import io
from pathlib import Path

# 修复 Windows 编码
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# 添加工具目录
sys.path.insert(0, str(Path(__file__).parent))

from self_correction_unified import (
    UnifiedSelfCorrection,
    unified_capture,
    check_before_operation,
    quick_analyze
)


def demo_1_basic_usage():
    """演示1: 基本用法 - 装饰器捕获错误"""
    print("=" * 60)
    print("演示1: 错误捕获装饰器")
    print("=" * 60)

    # 创建统一纠错系统实例
    sc = UnifiedSelfCorrection("demo-session")

    # 使用装饰器自动捕获错误
    @sc.capture_decorator(tool_name="Bash", operation="network command")
    def risky_network_operation():
        """模拟网络操作"""
        raise TimeoutError("Connection timeout after 30s")

    try:
        risky_network_operation()
    except Exception as e:
        print(f"\n捕获到错误: {e}")

    print("\n✅ 错误已被记录并提取知识")


def demo_2_pre_operation_check():
    """演示2: 操作前检查"""
    print("\n" + "=" * 60)
    print("演示2: 操作前风险检查")
    print("=" * 60)

    # 检查 WebFetch 操作
    result = check_before_operation("WebFetch", "fetch documentation")

    print(f"\n工具: {result['tool']}")
    print(f"操作: {result['operation']}")

    if result['history']['history_count'] > 0:
        print(f"\n⚠️  历史错误: {result['history']['history_count']} 次")

    if result['risks']:
        print(f"\n🚨 检测到 {len(result['risks'])} 个风险:")
        for risk in result['risks']:
            print(f"   [{risk['level']}] {risk['message']}")
    else:
        print("\n✅ 无明显风险")


def demo_3_knowledge_search():
    """演示3: 知识库搜索"""
    print("\n" + "=" * 60)
    print("演示3: 知识库搜索")
    print("=" * 60)

    sc = UnifiedSelfCorrection()

    # 搜索网络相关错误
    results = sc.search_knowledge_base("timeout", tags=["network"])

    print(f"\n找到 {len(results)} 条相关知识:")
    for item in results[:3]:
        print(f"\n📖 {item['title']}")
        print(f"   分类: {item['category']}")


def demo_4_session_analysis():
    """演示4: 会话分析"""
    print("\n" + "=" * 60)
    print("演示4: 会话分析")
    print("=" * 60)

    sc = UnifiedSelfCorrection("analysis-demo")

    # 模拟记录一些错误
    try:
        raise TimeoutError("Network timeout")
    except Exception as e:
        sc._handle_error(e, "WebFetch", "fetch page", (), {})

    try:
        raise PermissionError("Access denied")
    except Exception as e:
        sc._handle_error(e, "Bash", "git clone", (), {})

    # 分析会话
    analysis = sc.analyze_session()

    print(f"\n会话名称: {analysis['session_name']}")
    print(f"错误数量: {analysis['errors_recorded']}")
    print(f"修复数量: {analysis['fixes_recorded']}")
    print(f"改进率: {analysis['improvement_rate']:.1f}%")


def demo_5_prevention_guide():
    """演示5: 预防指南"""
    print("\n" + "=" * 60)
    print("演示5: 获取预防指南")
    print("=" * 60)

    sc = UnifiedSelfCorrection()

    guide = sc.get_prevention_guide("Bash", "git clone")

    print(f"\n工具: {guide['tool']}")
    print(f"操作: {guide['operation']}")
    print(f"风险等级: {guide['risk_level']}")

    if guide['warnings']:
        print("\n⚠️  警告:")
        for warning in guide['warnings']:
            print(f"   [{warning['level']}] {warning['message']}")

    if guide['prevention_suggestions']:
        print("\n💡 预防建议:")
        for suggestion in guide['prevention_suggestions'][:3]:
            print(f"   • {suggestion}")


def demo_6_cli_usage():
    """演示6: CLI 命令示例"""
    print("\n" + "=" * 60)
    print("演示6: CLI 命令用法")
    print("=" * 60)

    print("""
命令行用法示例:

1. 分析错误模式:
   sc analyze -d 30

2. 操作前检查:
   sc check WebFetch -o "fetch page"

3. 生成学习报告:
   sc report -d 7 -o weekly_report.md

4. 搜索知识库:
   sc search timeout -t network api

Python API 用法:

    from self_correction_unified import UnifiedSelfCorrection

    # 创建实例
    sc = UnifiedSelfCorrection("my-session")

    # 使用装饰器
    @sc.capture_decorator(tool_name="MyTool")
    def my_function():
        pass

    # 操作前检查
    result = check_before_operation("Tool", "operation")

    # 搜索知识
    knowledge = sc.search_knowledge_base("keyword")
    """)


if __name__ == "__main__":
    print("🚀 统一自我纠错系统集成演示\n")

    demos = [
        demo_1_basic_usage,
        demo_2_pre_operation_check,
        demo_3_knowledge_search,
        demo_4_session_analysis,
        demo_5_prevention_guide,
        demo_6_cli_usage,
    ]

    for demo in demos:
        try:
            demo()
        except Exception as e:
            print(f"\n❌ 演示失败: {e}")

    print("\n" + "=" * 60)
    print("✅ 所有演示完成!")
    print("=" * 60)
    print("\n提示: 将 tools 目录添加到 PATH 即可使用 'sc' 命令")
