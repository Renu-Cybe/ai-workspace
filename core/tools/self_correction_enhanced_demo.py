"""
Self-Correction Enhanced 使用示例
增强版自我纠错系统使用指南
"""

import sys
import io

# 修复 Windows 下的 UTF-8 编码问题
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

from self_correction_enhanced import (
    EnhancedSelfCorrection,
    ErrorPatternAnalyzer,
    KnowledgeExtractor,
    PreventionGenerator,
    RealtimeWarningSystem,
    analyze_errors,
    get_prevention_guide,
    check_risk,
    generate_learning_report,
    search_knowledge
)


def example_1_analyze_and_learn():
    """示例1: 分析错误并提取知识"""
    print("=== 示例1: 分析错误并学习 ===\n")

    # 方式1: 使用便捷函数
    result = analyze_errors(days=30)
    print(f"分析完成:")
    print(f"  - 发现 {result['patterns_found']} 个错误模式")
    print(f"  - 提取 {result['knowledge_extracted']} 条知识")
    print(f"  - 生成 {result['checklists_generated']} 份预防清单")

    # 方式2: 使用类实例（更灵活）
    system = EnhancedSelfCorrection()
    result = system.analyze_and_learn(days=7)  # 只分析最近7天


def example_2_prevention_guide():
    """示例2: 获取操作前的预防指南"""
    print("\n=== 示例2: 预防指南 ===\n")

    # 在操作前检查风险
    guide = get_prevention_guide("Bash", "git clone")

    print(f"工具: {guide['tool']}")
    print(f"操作: {guide['operation']}")
    print(f"风险等级: {guide['risk_level']}")

    if guide['warnings']:
        print("\n⚠️ 警告:")
        for warning in guide['warnings']:
            print(f"  [{warning['level'].upper()}] {warning['message']}")

    if guide['prevention_suggestions']:
        print("\n💡 预防建议:")
        for suggestion in guide['prevention_suggestions'][:5]:
            print(f"  - {suggestion}")


def example_3_realtime_warning():
    """示例3: 实时风险检查"""
    print("\n=== 示例3: 实时风险检查 ===\n")

    warning_system = RealtimeWarningSystem()

    # 模拟即将执行的操作
    risks = warning_system.check_risk("WebFetch", "fetch documentation")

    if risks:
        print(f"发现 {len(risks)} 个风险项:")
        for risk in risks:
            print(f"\n  [{risk['level'].upper()}] {risk['type']}")
            print(f"  消息: {risk['message']}")
            if risk.get('prevention'):
                print(f"  预防: {', '.join(risk['prevention'][:2])}")
    else:
        print("✓ 未发现明显风险")


def example_4_knowledge_search():
    """示例4: 知识库搜索"""
    print("\n=== 示例4: 知识搜索 ===\n")

    # 搜索与网络相关的知识
    results = search_knowledge("timeout", tags=["network"])
    print(f"找到 {len(results)} 条相关知识")

    for item in results[:3]:
        print(f"\n📖 {item['title']}")
        print(f"   分类: {item['category']}")
        print(f"   标签: {', '.join(item['tags'])}")


def example_5_generate_report():
    """示例5: 生成学习报告"""
    print("\n=== 示例5: 学习报告 ===\n")

    report = generate_learning_report(days=30)
    print("报告已生成!")
    print(f"报告长度: {len(report)} 字符")

    # 打印报告前500字符
    print("\n报告预览:")
    print("-" * 50)
    print(report[:500])
    print("...")


def example_6_pattern_analysis():
    """示例6: 深入分析错误模式"""
    print("\n=== 示例6: 错误模式分析 ===\n")

    analyzer = ErrorPatternAnalyzer()

    # 分析近30天的错误
    patterns = analyzer.analyze_errors(days=30)

    print(f"发现 {len(patterns)} 个错误模式:\n")

    for pattern in patterns:
        print(f"🔍 {pattern.name}")
        print(f"   ID: {pattern.pattern_id}")
        print(f"   描述: {pattern.description}")
        print(f"   发生次数: {pattern.occurrence_count}")
        print(f"   相关错误: {', '.join(pattern.related_errors)}")
        print(f"   标签: {', '.join(pattern.tags)}")
        print()


def example_7_knowledge_extraction():
    """示例7: 从错误中提取知识"""
    print("\n=== 示例7: 知识提取 ===\n")

    extractor = KnowledgeExtractor()

    # 示例错误数据
    sample_error = {
        "id": "2026-03-17-001",
        "error_type": "network_timeout",
        "severity": "medium",
        "message": "Connection timeout to external API after 30s",
        "context": {
            "tool": "WebFetch",
            "operation": "fetch documentation",
            "tags": ["network", "timeout", "api"]
        },
        "root_cause": "网络代理未配置，导致外部请求超时",
        "fix": {
            "verified": True,
            "solution": "配置 HTTP_PROXY 环境变量",
            "action_taken": "export HTTP_PROXY=http://127.0.0.1:23968"
        },
        "prevention": {
            "check_before": ["检查代理设置", "测试网络连接"],
            "early_warning": "外部请求前验证网络"
        }
    }

    # 提取知识
    knowledge = extractor.extract_from_error(sample_error)

    if knowledge:
        print(f"提取知识条目:")
        print(f"  ID: {knowledge.entry_id}")
        print(f"  标题: {knowledge.title}")
        print(f"  分类: {knowledge.category}")
        print(f"\n  问题:\n{knowledge.problem}")
        print(f"\n  解决方案:\n{knowledge.solution}")

        # 保存知识
        extractor.save_knowledge(knowledge)
        print("\n  ✓ 知识已保存到知识库")


def example_8_prevention_checklist():
    """示例8: 生成预防检查清单"""
    print("\n=== 示例8: 预防清单生成 ===\n")

    generator = PreventionGenerator()

    # 基于错误模式生成清单
    from self_correction_enhanced import ErrorPattern, ErrorSignature

    patterns = [
        ErrorPattern(
            pattern_id="pattern-001",
            name="Bash 网络超时",
            description="执行 Bash 命令时频繁出现网络超时",
            signatures=[
                ErrorSignature("network_timeout", "Bash", "git clone", ["timeout", "network"]),
            ],
            root_cause="网络不稳定或代理配置问题",
            prevention_strategy="配置代理，增加重试机制",
            related_errors=["2026-03-17-001"],
            occurrence_count=5
        )
    ]

    checklist = generator.generate_checklist("Bash", "git clone", patterns)

    print(f"生成检查清单:")
    print(f"  ID: {checklist.checklist_id}")
    print(f"  名称: {checklist.name}")
    print(f"\n  检查项:")
    for i, check in enumerate(checklist.checks, 1):
        print(f"    {i}. [{check.get('severity', 'medium')}] {check['item']}")
        print(f"       {check.get('description', '')}")

    if checklist.auto_verification:
        print(f"\n  自动验证代码已生成")


if __name__ == "__main__":
    print("🚀 Self-Correction Enhanced 使用示例\n")
    print("=" * 60)

    # 运行所有示例
    examples = [
        example_1_analyze_and_learn,
        example_2_prevention_guide,
        example_3_realtime_warning,
        example_4_knowledge_search,
        example_5_generate_report,
        example_6_pattern_analysis,
        example_7_knowledge_extraction,
        example_8_prevention_checklist,
    ]

    for example in examples:
        try:
            example()
        except Exception as e:
            print(f"\n❌ 示例执行失败: {e}")

    print("\n" + "=" * 60)
    print("✅ 所有示例执行完成!")
