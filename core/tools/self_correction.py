"""
自我纠错系统核心模块
Error Tracking & Self-Correction System

功能：
- 错误捕获和记录
- 经验查询和匹配
- 统计和报告生成
- 预防性检查
"""

import os
import json
import hashlib
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from collections import defaultdict

# 错误记录目录
ERRORS_DIR = Path(os.path.expanduser("~/.claude/memory-bank/errors"))
FIXES_DIR = Path(os.path.expanduser("~/.claude/memory-bank/fixes"))
LESSONS_DIR = Path(os.path.expanduser("~/.claude/memory-bank/lessons"))
STATS_DIR = Path(os.path.expanduser("~/.claude/memory-bank/stats"))
INDEX_FILE = ERRORS_DIR / "index.json"

# 确保目录存在
for d in [ERRORS_DIR, FIXES_DIR, LESSONS_DIR, STATS_DIR]:
    d.mkdir(parents=True, exist_ok=True)


@dataclass
class ErrorContext:
    """错误上下文"""
    tool: str
    operation: str
    input: Optional[Dict] = None
    file_path: Optional[str] = None
    tags: Optional[List[str]] = None

    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class ErrorFix:
    """修复方案"""
    solution: str
    action_taken: str
    fix_id: Optional[str] = None
    fixed_at: Optional[str] = None
    verified: bool = False

    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class ErrorRecord:
    """错误记录"""
    error_type: str
    severity: str
    context: ErrorContext
    message: str
    id: Optional[str] = None
    timestamp: Optional[str] = None
    session_id: Optional[str] = None
    stack_trace: Optional[str] = None
    root_cause: Optional[str] = None
    fix: Optional[ErrorFix] = None
    prevention: Optional[Dict] = None
    recurrence: Optional[Dict] = None
    metadata: Optional[Dict] = None

    def __post_init__(self):
        if self.id is None:
            self.id = self._generate_id()
        if self.timestamp is None:
            self.timestamp = datetime.now().isoformat()
        if self.recurrence is None:
            self.recurrence = {"count": 0, "related_errors": []}
        if self.metadata is None:
            self.metadata = {}

    def _generate_id(self) -> str:
        """生成错误ID"""
        today = datetime.now().strftime("%Y-%m-%d")
        count = len(list(ERRORS_DIR.glob(f"{today}-*.json")))
        return f"{today}-{count + 1:03d}"

    def to_dict(self) -> Dict:
        data = asdict(self)
        data['context'] = self.context.to_dict()
        if self.fix:
            data['fix'] = self.fix.to_dict()
        return data

    def save(self) -> str:
        """保存错误记录"""
        filepath = ERRORS_DIR / f"{self.id}.json"
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.to_dict(), f, ensure_ascii=False, indent=2)
        update_index(self)
        return str(filepath)


class ErrorTracker:
    """错误追踪器 - 捕获和记录错误"""

    def __init__(self, session_id: Optional[str] = None):
        self.session_id = session_id or self._generate_session_id()
        self.errors: List[ErrorRecord] = []
        self.current_error: Optional[ErrorRecord] = None

    def _generate_session_id(self) -> str:
        """生成会话ID"""
        return f"session-{datetime.now().strftime('%Y%m%d-%H%M%S')}"

    def capture(self,
                error_type: str,
                message: str,
                tool: str,
                operation: str,
                severity: str = "medium",
                input_data: Optional[Dict] = None,
                file_path: Optional[str] = None,
                tags: Optional[List[str]] = None,
                stack_trace: Optional[str] = None) -> ErrorRecord:
        """捕获错误"""
        context = ErrorContext(
            tool=tool,
            operation=operation,
            input=input_data,
            file_path=file_path,
            tags=tags or []
        )

        error = ErrorRecord(
            error_type=error_type,
            severity=severity,
            context=context,
            message=message,
            session_id=self.session_id,
            stack_trace=stack_trace
        )

        error.save()
        self.errors.append(error)
        self.current_error = error

        return error

    def fix(self,
            solution: str,
            action_taken: str,
            root_cause: Optional[str] = None,
            prevention_checks: Optional[List[str]] = None,
            early_warning: Optional[str] = None) -> ErrorRecord:
        """记录修复方案"""
        if not self.current_error:
            raise ValueError("No current error to fix")

        fix_id = f"{self.current_error.id}-fix"

        self.current_error.fix = ErrorFix(
            fix_id=fix_id,
            solution=solution,
            action_taken=action_taken,
            fixed_at=datetime.now().isoformat(),
            verified=True
        )

        if root_cause:
            self.current_error.root_cause = root_cause

        self.current_error.prevention = {
            "check_before": prevention_checks or [],
            "early_warning": early_warning or ""
        }

        self.current_error.save()

        # 同时保存到 fixes 目录
        fix_file = FIXES_DIR / f"{fix_id}.md"
        self._save_fix_markdown(fix_file, self.current_error)

        return self.current_error

    def _save_fix_markdown(self, filepath: Path, error: ErrorRecord):
        """保存修复方案为 Markdown"""
        content = f"""# 修复方案: {error.id}

## 错误信息
- **类型**: {error.error_type}
- **严重级别**: {error.severity}
- **时间**: {error.timestamp}
- **消息**: {error.message}

## 根因分析
{error.root_cause or '待分析'}

## 解决方案
{error.fix.solution if error.fix else '待修复'}

## 具体行动
```
{error.fix.action_taken if error.fix else ''}
```

## 预防措施
{chr(10).join(['- ' + check for check in error.prevention.get('check_before', [])]) if error.prevention else '- 待补充'}

## 早期预警
{error.prevention.get('early_warning', '待补充') if error.prevention else ''}

---
*记录时间: {datetime.now().isoformat()}*
"""
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)


def update_index(error: ErrorRecord):
    """更新错误索引"""
    if not INDEX_FILE.exists():
        index = {
            "version": "1.0",
            "description": "错误索引，用于快速检索和统计",
            "last_updated": datetime.now().isoformat(),
            "stats": {
                "total_errors": 0,
                "total_fixed": 0,
                "total_recurring": 0,
                "by_type": defaultdict(int),
                "by_severity": defaultdict(int)
            },
            "recent_errors": [],
            "recurring_patterns": [],
            "tags_index": defaultdict(list)
        }
    else:
        with open(INDEX_FILE, 'r', encoding='utf-8') as f:
            index = json.load(f)

    # 更新统计
    index["stats"]["total_errors"] += 1
    index["stats"]["by_type"][error.error_type] = index["stats"]["by_type"].get(error.error_type, 0) + 1
    index["stats"]["by_severity"][error.severity] = index["stats"]["by_severity"].get(error.severity, 0) + 1

    if error.fix and error.fix.verified:
        index["stats"]["total_fixed"] += 1

    # 添加到最近错误列表（保留最近50个）
    index["recent_errors"].insert(0, {
        "id": error.id,
        "timestamp": error.timestamp,
        "error_type": error.error_type,
        "severity": error.severity,
        "message": error.message[:100] + "..." if len(error.message) > 100 else error.message
    })
    index["recent_errors"] = index["recent_errors"][:50]

    # 更新标签索引
    if error.context and error.context.tags:
        for tag in error.context.tags:
            if tag not in index["tags_index"]:
                index["tags_index"][tag] = []
            index["tags_index"][tag].append(error.id)

    index["last_updated"] = datetime.now().isoformat()

    with open(INDEX_FILE, 'w', encoding='utf-8') as f:
        json.dump(index, f, ensure_ascii=False, indent=2)


class ExperienceQuery:
    """经验查询器 - 检索历史错误和解决方案"""

    def __init__(self):
        self.errors_dir = ERRORS_DIR

    def find_similar_errors(self,
                           error_type: Optional[str] = None,
                           tool: Optional[str] = None,
                           tags: Optional[List[str]] = None,
                           keywords: Optional[List[str]] = None,
                           limit: int = 5) -> List[Dict]:
        """
        查找相似错误

        匹配算法：
        1. 相同 error_type +10分
        2. 相同 tool +5分
        3. 相同 tag 每个 +3分
        4. 关键词匹配 +2分
        """
        scores = defaultdict(int)
        error_files = list(self.errors_dir.glob("*.json"))

        for filepath in error_files:
            if filepath.name == "index.json":
                continue

            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    error = json.load(f)

                error_id = error.get('id', filepath.stem)

                # 类型匹配
                if error_type and error.get('error_type') == error_type:
                    scores[error_id] += 10

                # 工具匹配
                context = error.get('context', {})
                if tool and context.get('tool') == tool:
                    scores[error_id] += 5

                # 标签匹配
                error_tags = context.get('tags', [])
                if tags:
                    for tag in tags:
                        if tag in error_tags:
                            scores[error_id] += 3

                # 关键词匹配
                if keywords:
                    message = error.get('message', '').lower()
                    for kw in keywords:
                        if kw.lower() in message:
                            scores[error_id] += 2

            except Exception:
                continue

        # 按分数排序
        sorted_errors = sorted(scores.items(), key=lambda x: x[1], reverse=True)

        # 加载详细内容
        results = []
        for error_id, score in sorted_errors[:limit]:
            filepath = self.errors_dir / f"{error_id}.json"
            if filepath.exists():
                with open(filepath, 'r', encoding='utf-8') as f:
                    error_data = json.load(f)
                    error_data['_similarity_score'] = score
                    results.append(error_data)

        return results

    def get_error_by_id(self, error_id: str) -> Optional[Dict]:
        """根据ID获取错误详情"""
        filepath = self.errors_dir / f"{error_id}.json"
        if filepath.exists():
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        return None

    def get_fix_for_error(self, error_id: str) -> Optional[str]:
        """获取错误的修复方案"""
        fix_file = FIXES_DIR / f"{error_id}-fix.md"
        if fix_file.exists():
            with open(fix_file, 'r', encoding='utf-8') as f:
                return f.read()

        # 尝试从错误记录中读取
        error = self.get_error_by_id(error_id)
        if error and error.get('fix'):
            return error['fix'].get('solution')

        return None

    def get_prevention_tips(self,
                           error_type: Optional[str] = None,
                           tool: Optional[str] = None) -> List[str]:
        """获取预防建议"""
        tips = []

        for filepath in self.errors_dir.glob("*.json"):
            if filepath.name == "index.json":
                continue

            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    error = json.load(f)

                # 过滤条件
                if error_type and error.get('error_type') != error_type:
                    continue

                context = error.get('context', {})
                if tool and context.get('tool') != tool:
                    continue

                prevention = error.get('prevention', {})
                checks = prevention.get('check_before', [])
                tips.extend(checks)

            except Exception:
                continue

        # 去重
        return list(set(tips))

    def check_before_task(self, tool: str, operation: str) -> Dict:
        """
        执行任务前检查 - 返回相关经验和警告
        """
        # 查找相似错误
        similar = self.find_similar_errors(
            tool=tool,
            keywords=[operation],
            limit=3
        )

        # 获取预防建议
        prevention_tips = self.get_prevention_tips(tool=tool)

        # 统计该工具的历史错误数
        history_count = len([
            f for f in self.errors_dir.glob("*.json")
            if f.name != "index.json" and self._check_tool_in_error(f, tool)
        ])

        return {
            "has_history": history_count > 0,
            "history_count": history_count,
            "similar_errors": similar,
            "prevention_tips": prevention_tips,
            "warning": f"该工具/操作曾有 {history_count} 次错误记录，请注意检查。" if history_count > 0 else None
        }

    def _check_tool_in_error(self, filepath: Path, tool: str) -> bool:
        """检查错误记录是否包含指定工具"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                error = json.load(f)
            context = error.get('context', {})
            return context.get('tool') == tool
        except:
            return False


class WeeklyReport:
    """周错误报告生成器"""

    def __init__(self):
        self.errors_dir = ERRORS_DIR
        self.stats_dir = STATS_DIR

    def generate(self, week_offset: int = 0) -> str:
        """
        生成周错误报告

        Args:
            week_offset: 0=本周, -1=上周, 以此类推
        """
        # 计算时间范围
        today = datetime.now()
        week_start = today - timedelta(days=today.weekday() + (week_offset * 7))
        week_end = week_start + timedelta(days=7)

        week_start_str = week_start.strftime("%Y-%m-%d")
        week_end_str = week_end.strftime("%Y-%m-%d")

        # 收集本周错误
        week_errors = []
        for filepath in self.errors_dir.glob("*.json"):
            if filepath.name == "index.json":
                continue

            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    error = json.load(f)

                error_date = error.get('timestamp', '')[:10]
                if week_start_str <= error_date < week_end_str:
                    week_errors.append(error)

            except Exception:
                continue

        # 生成统计
        stats = self._calculate_stats(week_errors)

        # 生成报告
        report = self._format_report(week_start_str, week_end_str, stats, week_errors)

        # 保存报告
        report_file = self.stats_dir / f"weekly-report-{week_start_str}.md"
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report)

        return report

    def _calculate_stats(self, errors: List[Dict]) -> Dict:
        """计算统计信息"""
        stats = {
            "total": len(errors),
            "by_type": defaultdict(int),
            "by_severity": defaultdict(int),
            "by_tool": defaultdict(int),
            "fixed": 0,
            "recurring": 0,
            "avg_fix_time": 0
        }

        fix_times = []

        for error in errors:
            # 类型统计
            stats["by_type"][error.get('error_type', 'unknown')] += 1

            # 严重级别统计
            stats["by_severity"][error.get('severity', 'medium')] += 1

            # 工具统计
            tool = error.get('context', {}).get('tool', 'unknown')
            stats["by_tool"][tool] += 1

            # 修复统计
            if error.get('fix', {}).get('verified'):
                stats["fixed"] += 1

                # 修复时间
                fix_time = error.get('metadata', {}).get('time_to_fix_minutes')
                if fix_time:
                    fix_times.append(fix_time)

            # 复发统计
            if error.get('recurrence', {}).get('count', 0) > 0:
                stats["recurring"] += 1

        if fix_times:
            stats["avg_fix_time"] = sum(fix_times) / len(fix_times)

        return stats

    def _format_report(self, start: str, end: str, stats: Dict, errors: List[Dict]) -> str:
        """格式化报告"""

        # 识别高频问题（出现2次以上）
        recurring_issues = [
            (error_type, count)
            for error_type, count in stats["by_type"].items()
            if count >= 2
        ]

        # 生成改进建议
        recommendations = []
        if stats["by_type"].get('api_error', 0) >= 2:
            recommendations.append("- API 错误较多，建议检查网络配置和请求参数")
        if stats["by_type"].get('tool_execution_error', 0) >= 2:
            recommendations.append("- 工具执行错误频繁，建议增加前置检查")
        if stats["by_severity"].get('critical', 0) > 0:
            recommendations.append("- 存在严重错误，需要优先处理根因")
        if stats["avg_fix_time"] > 10:
            recommendations.append(f"- 平均修复时间较长（{stats['avg_fix_time']:.1f}分钟），建议优化故障处理流程")

        if not recommendations:
            recommendations.append("- 本周错误率正常，继续保持")

        report = f"""# 错误分析报告 ({start} ~ {end})

## 概览

| 指标 | 数值 |
|------|------|
| 总错误数 | {stats['total']} |
| 已修复 | {stats['fixed']} |
| 复发错误 | {stats['recurring']} |
| 平均修复时间 | {stats['avg_fix_time']:.1f} 分钟 |

## 错误类型分布

"""

        for error_type, count in sorted(stats["by_type"].items(), key=lambda x: x[1], reverse=True):
            bar = "█" * count
            report += f"- **{error_type}**: {count} {bar}\n"

        report += f"\n## 严重级别分布\n\n"
        for severity, count in sorted(stats["by_severity"].items(), key=lambda x: x[1], reverse=True):
            icon = "🔴" if severity == "critical" else "🟠" if severity == "high" else "🟡" if severity == "medium" else "🟢"
            report += f"- {icon} **{severity}**: {count}\n"

        if recurring_issues:
            report += f"\n## 高频问题（需关注）\n\n"
            for error_type, count in recurring_issues:
                report += f"- ⚠️ **{error_type}**: 发生 {count} 次\n"

        report += f"\n## 工具错误统计\n\n"
        for tool, count in sorted(stats["by_tool"].items(), key=lambda x: x[1], reverse=True):
            report += f"- **{tool}**: {count} 次错误\n"

        report += f"\n## 改进建议\n\n"
        for rec in recommendations:
            report += f"{rec}\n"

        # 添加详细列表
        if errors:
            report += f"\n## 详细错误列表\n\n"
            for error in sorted(errors, key=lambda x: x.get('timestamp', ''), reverse=True):
                error_id = error.get('id', 'unknown')
                error_type = error.get('error_type', 'unknown')
                severity = error.get('severity', 'medium')
                message = error.get('message', '')[:80]
                if len(error.get('message', '')) > 80:
                    message += "..."
                fixed = "✅" if error.get('fix', {}).get('verified') else "❌"

                report += f"- {fixed} `{error_id}` [{severity}] {error_type}: {message}\n"

        report += f"\n---\n*报告生成时间: {datetime.now().isoformat()}*\n"

        return report


# 便捷函数

def record_error(error_type: str,
                 message: str,
                 tool: str,
                 operation: str,
                 severity: str = "medium",
                 **kwargs) -> ErrorRecord:
    """便捷函数：记录错误"""
    tracker = ErrorTracker()
    return tracker.capture(
        error_type=error_type,
        message=message,
        tool=tool,
        operation=operation,
        severity=severity,
        **kwargs
    )


def record_fix(error_id: str,
               solution: str,
               action_taken: str,
               root_cause: Optional[str] = None,
               **kwargs) -> Optional[ErrorRecord]:
    """便捷函数：记录修复"""
    filepath = ERRORS_DIR / f"{error_id}.json"
    if not filepath.exists():
        return None

    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # 重建 ErrorRecord 并修复
    context = ErrorContext(**data.get('context', {}))
    error = ErrorRecord(
        id=data.get('id'),
        timestamp=data.get('timestamp'),
        session_id=data.get('session_id'),
        error_type=data.get('error_type'),
        severity=data.get('severity'),
        context=context,
        message=data.get('message'),
        root_cause=root_cause or data.get('root_cause')
    )

    tracker = ErrorTracker(error.session_id)
    tracker.current_error = error
    return tracker.fix(solution, action_taken, root_cause, **kwargs)


def check_task(tool: str, operation: str) -> Dict:
    """便捷函数：任务前检查"""
    query = ExperienceQuery()
    return query.check_before_task(tool, operation)


def find_similar(**kwargs) -> List[Dict]:
    """便捷函数：查找相似错误"""
    query = ExperienceQuery()
    return query.find_similar_errors(**kwargs)


def generate_weekly_report(week_offset: int = 0) -> str:
    """便捷函数：生成周报告"""
    report_gen = WeeklyReport()
    return report_gen.generate(week_offset)


if __name__ == "__main__":
    # 测试
    print("=== 自我纠错系统测试 ===\n")

    # 1. 记录错误
    print("1. 记录测试错误...")
    error = record_error(
        error_type="api_error",
        message="Connection timeout to external API",
        tool="WebFetch",
        operation="fetch documentation",
        severity="medium",
        tags=["network", "timeout"]
    )
    print(f"   错误ID: {error.id}")

    # 2. 记录修复
    print("\n2. 记录修复方案...")
    record_fix(
        error_id=error.id,
        solution="Add retry mechanism with exponential backoff",
        action_taken="Implemented retry decorator with 3 attempts",
        root_cause="Network instability during peak hours",
        prevention_checks=["检查网络连接状态", "设置超时和重试机制"],
        early_warning="API响应时间超过2秒时预警"
    )
    print(f"   已修复: {error.id}")

    # 3. 任务前检查
    print("\n3. 任务前检查...")
    check_result = check_task("WebFetch", "fetch documentation")
    print(f"   历史错误数: {check_result['history_count']}")
    print(f"   预防建议: {len(check_result['prevention_tips'])} 条")

    # 4. 查找相似
    print("\n4. 查找相似错误...")
    similar = find_similar(error_type="api_error", limit=3)
    print(f"   找到 {len(similar)} 个相似错误")

    # 5. 生成报告
    print("\n5. 生成周报告...")
    report = generate_weekly_report()
    print("   报告已生成")
    print("\n=== 测试完成 ===")
