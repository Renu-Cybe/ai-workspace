"""
增强版自我纠错系统 (Self-Correction Enhanced)
基于四自框架的错误分析、预防和知识沉淀系统

新增功能：
- 错误模式挖掘：发现错误间的隐藏关联
- 智能防范生成：自动创建预防性检查清单
- 经验知识库：将错误转化为可复用的学习资料
- 实时预警监控：主动识别潜在风险
- 自动修复推荐：基于相似错误推荐解决方案

作者: Claude Code
版本: 2.0
"""

import os
import json
import hashlib
import re
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple, Set
from dataclasses import dataclass, asdict, field
from collections import defaultdict
from enum import Enum
import subprocess

# 目录结构
BASE_DIR = Path(os.path.expanduser("~/.claude/memory-bank"))
ERRORS_DIR = BASE_DIR / "errors"
FIXES_DIR = BASE_DIR / "fixes"
LESSONS_DIR = BASE_DIR / "lessons"
PATTERNS_DIR = BASE_DIR / "patterns"
KNOWLEDGE_DIR = BASE_DIR / "knowledge"
WARNINGS_DIR = BASE_DIR / "warnings"

for d in [ERRORS_DIR, FIXES_DIR, LESSONS_DIR, PATTERNS_DIR, KNOWLEDGE_DIR, WARNINGS_DIR]:
    d.mkdir(parents=True, exist_ok=True)


class ErrorCategory(Enum):
    """错误分类体系"""
    DEPENDENCY = "dependency"  # 依赖缺失/版本冲突
    CONFIGURATION = "configuration"  # 配置错误
    NETWORK = "network"  # 网络/连接问题
    PERMISSION = "permission"  # 权限问题
    RESOURCE = "resource"  # 资源不足
    LOGIC = "logic"  # 逻辑错误
    INTERFACE = "interface"  # 接口/API 错误
    ENVIRONMENT = "environment"  # 环境问题
    UNKNOWN = "unknown"


@dataclass
class ErrorSignature:
    """错误特征签名 - 用于识别相似错误"""
    error_type: str
    tool: str
    operation: str
    keywords: List[str]
    stack_hash: Optional[str] = None

    def to_dict(self) -> Dict:
        return asdict(self)

    def similarity_score(self, other: 'ErrorSignature') -> float:
        """计算与另一个签名的相似度 (0-1)"""
        score = 0.0
        weights = 0.0

        # 错误类型匹配 (+30%)
        if self.error_type == other.error_type:
            score += 0.3
        weights += 0.3

        # 工具匹配 (+20%)
        if self.tool == other.tool:
            score += 0.2
        weights += 0.2

        # 操作匹配 (+20%)
        if self.operation == other.operation:
            score += 0.2
        weights += 0.2

        # 关键词重叠 (+30%)
        if self.keywords and other.keywords:
            overlap = len(set(self.keywords) & set(other.keywords))
            union = len(set(self.keywords) | set(other.keywords))
            if union > 0:
                score += 0.3 * (overlap / union)
        weights += 0.3

        return score / weights if weights > 0 else 0.0


@dataclass
class ErrorPattern:
    """错误模式 - 一组相关联的错误"""
    pattern_id: str
    name: str
    description: str
    signatures: List[ErrorSignature]
    root_cause: str
    prevention_strategy: str
    related_errors: List[str]
    occurrence_count: int = 0
    first_seen: Optional[str] = None
    last_seen: Optional[str] = None
    tags: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict:
        return {
            'pattern_id': self.pattern_id,
            'name': self.name,
            'description': self.description,
            'signatures': [s.to_dict() for s in self.signatures],
            'root_cause': self.root_cause,
            'prevention_strategy': self.prevention_strategy,
            'related_errors': self.related_errors,
            'occurrence_count': self.occurrence_count,
            'first_seen': self.first_seen,
            'last_seen': self.last_seen,
            'tags': self.tags
        }

    @classmethod
    def from_dict(cls, data: Dict) -> 'ErrorPattern':
        signatures = [ErrorSignature(**s) for s in data.get('signatures', [])]
        return cls(
            pattern_id=data['pattern_id'],
            name=data['name'],
            description=data['description'],
            signatures=signatures,
            root_cause=data['root_cause'],
            prevention_strategy=data['prevention_strategy'],
            related_errors=data.get('related_errors', []),
            occurrence_count=data.get('occurrence_count', 0),
            first_seen=data.get('first_seen'),
            last_seen=data.get('last_seen'),
            tags=data.get('tags', [])
        )


@dataclass
class PreventionChecklist:
    """预防性检查清单"""
    checklist_id: str
    name: str
    context: str  # 适用场景
    checks: List[Dict]  # 检查项列表
    auto_verification: Optional[str] = None  # 自动验证代码
    created_at: Optional[str] = None
    usage_count: int = 0
    success_rate: float = 0.0

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now().isoformat()

    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class KnowledgeEntry:
    """知识库条目 - 从错误中提取的经验"""
    entry_id: str
    title: str
    category: str
    problem: str
    solution: str
    code_example: Optional[str] = None
    references: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    created_at: Optional[str] = None
    error_sources: List[str] = field(default_factory=list)

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now().isoformat()

    def to_dict(self) -> Dict:
        return asdict(self)

    def to_markdown(self) -> str:
        """转换为 Markdown 格式"""
        md = f"""# {self.title}

## 问题描述
{self.problem}

## 解决方案
{self.solution}
"""
        if self.code_example:
            md += f"\n## 代码示例\n```python\n{self.code_example}\n```\n"

        if self.references:
            md += "\n## 参考链接\n"
            for ref in self.references:
                md += f"- {ref}\n"

        if self.tags:
            md += f"\n## 标签\n{', '.join(self.tags)}\n"

        md += f"\n---\n*来源: {', '.join(self.error_sources)}*\n"
        md += f"*创建: {self.created_at}*\n"

        return md


class ErrorPatternAnalyzer:
    """错误模式分析器"""

    def __init__(self):
        self.patterns_dir = PATTERNS_DIR

    def analyze_errors(self, days: int = 30) -> List[ErrorPattern]:
        """分析近期错误，发现模式"""
        # 加载近期错误
        cutoff_date = datetime.now() - timedelta(days=days)
        errors = self._load_recent_errors(cutoff_date)

        if len(errors) < 2:
            return []

        # 聚类分析
        clusters = self._cluster_errors(errors)

        # 生成模式
        patterns = []
        for cluster in clusters:
            if len(cluster) >= 2:  # 至少2个错误才形成模式
                pattern = self._create_pattern_from_cluster(cluster)
                patterns.append(pattern)
                self._save_pattern(pattern)

        return patterns

    def _load_recent_errors(self, cutoff_date: datetime) -> List[Dict]:
        """加载指定日期之后的错误"""
        errors = []
        for filepath in ERRORS_DIR.glob("*.json"):
            if filepath.name == "index.json":
                continue
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    error = json.load(f)
                error_date = datetime.fromisoformat(error.get('timestamp', '2000-01-01'))
                if error_date >= cutoff_date:
                    errors.append(error)
            except Exception:
                continue
        return errors

    def _cluster_errors(self, errors: List[Dict]) -> List[List[Dict]]:
        """对错误进行聚类"""
        clusters = []
        visited = set()

        for i, error1 in enumerate(errors):
            if i in visited:
                continue

            cluster = [error1]
            visited.add(i)

            sig1 = self._extract_signature(error1)

            for j, error2 in enumerate(errors[i+1:], i+1):
                if j in visited:
                    continue

                sig2 = self._extract_signature(error2)
                similarity = sig1.similarity_score(sig2)

                if similarity >= 0.6:  # 相似度阈值
                    cluster.append(error2)
                    visited.add(j)

            if len(cluster) >= 2:
                clusters.append(cluster)

        return clusters

    def _extract_signature(self, error: Dict) -> ErrorSignature:
        """从错误记录中提取特征签名"""
        context = error.get('context', {})
        message = error.get('message', '')

        # 提取关键词
        keywords = self._extract_keywords(message)

        return ErrorSignature(
            error_type=error.get('error_type', 'unknown'),
            tool=context.get('tool', 'unknown'),
            operation=context.get('operation', 'unknown'),
            keywords=keywords,
            stack_hash=self._hash_stack_trace(error.get('stack_trace', ''))
        )

    def _extract_keywords(self, message: str) -> List[str]:
        """从错误消息中提取关键词"""
        # 常见技术关键词
        tech_patterns = [
            r'\b(git|npm|pip|docker|python|node|java|go)\b',
            r'\b(permission|denied|access|forbidden)\b',
            r'\b(timeout|connection|refused|network)\b',
            r'\b(not found|404|missing|no such file)\b',
            r'\b(memory|cpu|disk|resource)\b',
            r'\b(invalid|error|failed|exception)\b',
            r'\b(api|request|response|http)\b',
            r'\b(config|configuration|setting)\b',
        ]

        keywords = set()
        message_lower = message.lower()

        for pattern in tech_patterns:
            matches = re.findall(pattern, message_lower)
            keywords.update(matches)

        return list(keywords)

    def _hash_stack_trace(self, stack_trace: Optional[str]) -> Optional[str]:
        """对堆栈跟踪进行哈希"""
        if not stack_trace:
            return None
        # 只取前5行进行哈希，忽略行号变化
        lines = stack_trace.strip().split('\n')[:5]
        normalized = ' '.join(lines)
        return hashlib.md5(normalized.encode()).hexdigest()[:16]

    def _create_pattern_from_cluster(self, cluster: List[Dict]) -> ErrorPattern:
        """从错误簇创建模式"""
        # 提取共同特征
        error_types = set(e.get('error_type') for e in cluster)
        tools = set(e.get('context', {}).get('tool') for e in cluster)

        # 生成模式ID
        pattern_id = f"pattern-{datetime.now().strftime('%Y%m%d')}-{len(list(self.patterns_dir.glob('*.json'))) + 1:03d}"

        # 提取签名
        signatures = [self._extract_signature(e) for e in cluster]

        # 分析根因
        root_causes = [e.get('root_cause', '') for e in cluster if e.get('root_cause')]
        common_root_cause = self._find_common_string(root_causes) if root_causes else "待分析"

        # 生成预防策略
        prevention = self._generate_prevention_strategy(cluster)

        # 生成模式名称
        name = f"{list(error_types)[0] if error_types else 'Unknown'} 在 {list(tools)[0] if tools else 'Unknown'}"

        return ErrorPattern(
            pattern_id=pattern_id,
            name=name,
            description=f"发现 {len(cluster)} 个相关错误",
            signatures=signatures,
            root_cause=common_root_cause,
            prevention_strategy=prevention,
            related_errors=[e.get('id') for e in cluster],
            occurrence_count=len(cluster),
            first_seen=min(e.get('timestamp') for e in cluster),
            last_seen=max(e.get('timestamp') for e in cluster),
            tags=list(error_types) + list(tools)
        )

    def _find_common_string(self, strings: List[str]) -> str:
        """找出字符串列表中的共同子串"""
        if not strings:
            return ""
        if len(strings) == 1:
            return strings[0]

        # 简化处理：返回最长公共子串或最常见模式
        words_count = defaultdict(int)
        for s in strings:
            words = s.lower().split()
            for word in set(words):
                words_count[word] += 1

        # 返回出现频率最高的词组合
        common_words = [w for w, c in words_count.items() if c >= len(strings) * 0.5]
        return ' '.join(common_words[:5]) if common_words else strings[0]

    def _generate_prevention_strategy(self, cluster: List[Dict]) -> str:
        """基于错误簇生成预防策略"""
        strategies = []

        # 收集所有预防措施
        all_preventions = []
        for error in cluster:
            prevention = error.get('prevention', {})
            checks = prevention.get('check_before', [])
            all_preventions.extend(checks)

        # 找出最常见的预防措施
        if all_preventions:
            prevention_count = defaultdict(int)
            for p in all_preventions:
                prevention_count[p] += 1

            top_preventions = sorted(prevention_count.items(), key=lambda x: x[1], reverse=True)[:3]
            strategies = [p for p, _ in top_preventions]

        if not strategies:
            strategies = ["执行前进行环境检查", "增加错误处理和重试机制"]

        return '\n'.join(f"- {s}" for s in strategies)

    def _save_pattern(self, pattern: ErrorPattern):
        """保存模式到文件"""
        filepath = self.patterns_dir / f"{pattern.pattern_id}.json"
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(pattern.to_dict(), f, ensure_ascii=False, indent=2)

    def load_patterns(self) -> List[ErrorPattern]:
        """加载所有已发现的模式"""
        patterns = []
        for filepath in self.patterns_dir.glob("*.json"):
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                patterns.append(ErrorPattern.from_dict(data))
            except Exception:
                continue
        return patterns


class PreventionGenerator:
    """预防策略生成器"""

    def __init__(self):
        self.lessons_dir = LESSONS_DIR

    def generate_checklist(self, tool: str, operation: str, error_patterns: List[ErrorPattern]) -> PreventionChecklist:
        """为特定工具/操作生成预防检查清单"""
        checklist_id = f"checklist-{tool}-{operation}-{datetime.now().strftime('%Y%m%d')}"

        checks = []

        # 基于错误模式生成检查项
        for pattern in error_patterns:
            if any(sig.tool == tool for sig in pattern.signatures):
                checks.append({
                    'item': f"检查: {pattern.name}",
                    'description': pattern.description,
                    'verification': pattern.prevention_strategy,
                    'severity': 'high' if pattern.occurrence_count >= 3 else 'medium'
                })

        # 添加通用检查项
        checks.extend(self._get_generic_checks(tool, operation))

        # 生成自动验证代码
        auto_verify = self._generate_verification_code(tool, operation, checks)

        checklist = PreventionChecklist(
            checklist_id=checklist_id,
            name=f"{tool} - {operation} 预检清单",
            context=f"执行 {tool} 的 {operation} 操作前",
            checks=checks,
            auto_verification=auto_verify
        )

        self._save_checklist(checklist)
        return checklist

    def _get_generic_checks(self, tool: str, operation: str) -> List[Dict]:
        """获取通用检查项"""
        generic_checks = {
            'Bash': [
                {'item': '检查命令语法', 'description': '确保命令格式正确', 'verification': '使用 echo 测试命令', 'severity': 'high'},
                {'item': '检查文件存在性', 'description': '操作前验证文件/目录存在', 'verification': 'test -f 或 test -d', 'severity': 'medium'},
            ],
            'Python': [
                {'item': '检查依赖安装', 'description': '确保所需包已安装', 'verification': 'pip list | grep package', 'severity': 'high'},
                {'item': '检查Python版本', 'description': '确认版本兼容性', 'verification': 'python --version', 'severity': 'medium'},
            ],
            'Git': [
                {'item': '检查分支状态', 'description': '确认当前分支正确', 'verification': 'git branch', 'severity': 'high'},
                {'item': '检查远程连接', 'description': '验证远程仓库可访问', 'verification': 'git remote -v', 'severity': 'medium'},
            ],
        }
        return generic_checks.get(tool, [])

    def _generate_verification_code(self, tool: str, operation: str, checks: List[Dict]) -> str:
        """生成自动验证代码"""
        code_lines = [
            "#!/usr/bin/env python3",
            f"# 自动验证脚本: {tool} - {operation}",
            "",
            "import subprocess",
            "import sys",
            "",
            "def run_check(name, command):",
            "    print(f'检查: {name}')",
            "    try:",
            "        result = subprocess.run(command, shell=True, capture_output=True, text=True)",
            "        if result.returncode == 0:",
            "            print(f'  ✓ 通过')",
            "            return True",
            "        else:",
            "            print(f'  ✗ 失败: {result.stderr}')",
            "            return False",
            "    except Exception as e:",
            "        print(f'  ✗ 异常: {e}')",
            "        return False",
            "",
            "def main():",
            "    all_passed = True",
            ""
        ]

        for check in checks:
            name = check['item']
            # 简化的命令生成
            if 'verification' in check:
                verification = check['verification']
                code_lines.append(f"    all_passed &= run_check('{name}', '{verification}')")

        code_lines.extend([
            "",
            "    if all_passed:",
            "        print('\\n✓ 所有检查通过')",
            "        return 0",
            "    else:",
            "        print('\\n✗ 部分检查未通过')",
            "        return 1",
            "",
            "if __name__ == '__main__':",
            "    sys.exit(main())"
        ])

        return '\n'.join(code_lines)

    def _save_checklist(self, checklist: PreventionChecklist):
        """保存检查清单"""
        filepath = self.lessons_dir / f"{checklist.checklist_id}.json"
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(checklist.to_dict(), f, ensure_ascii=False, indent=2)


class KnowledgeExtractor:
    """知识提取器 - 从错误中提取可复用的知识"""

    def __init__(self):
        self.knowledge_dir = KNOWLEDGE_DIR

    def extract_from_error(self, error: Dict) -> Optional[KnowledgeEntry]:
        """从单个错误中提取知识"""
        # 只有已修复的错误才提取知识
        if not error.get('fix', {}).get('verified'):
            return None

        entry_id = f"knowledge-{error.get('id')}"

        # 生成标题
        title = self._generate_title(error)

        # 分类
        category = self._categorize_error(error)

        # 格式化问题和解决方案
        problem = self._format_problem(error)
        solution = self._format_solution(error)

        # 生成代码示例
        code_example = self._generate_code_example(error)

        # 提取标签
        tags = self._extract_tags(error)

        return KnowledgeEntry(
            entry_id=entry_id,
            title=title,
            category=category,
            problem=problem,
            solution=solution,
            code_example=code_example,
            tags=tags,
            error_sources=[error.get('id')],
            references=[]
        )

    def extract_from_pattern(self, pattern: ErrorPattern) -> Optional[KnowledgeEntry]:
        """从错误模式中提取知识"""
        if pattern.occurrence_count < 2:
            return None

        entry_id = f"knowledge-{pattern.pattern_id}"

        return KnowledgeEntry(
            entry_id=entry_id,
            title=f"【模式】{pattern.name}",
            category="pattern",
            problem=f"多次发生以下错误模式: {pattern.description}",
            solution=f"根因: {pattern.root_cause}\n\n预防策略:\n{pattern.prevention_strategy}",
            code_example=None,
            tags=pattern.tags,
            error_sources=pattern.related_errors
        )

    def _generate_title(self, error: Dict) -> str:
        """生成知识条目标题"""
        error_type = error.get('error_type', 'Unknown')
        tool = error.get('context', {}).get('tool', 'Unknown')
        message = error.get('message', '')[:50]

        # 提取关键信息
        if 'timeout' in message.lower():
            return f"{tool} 超时错误处理"
        elif 'permission' in message.lower() or 'access' in message.lower():
            return f"{tool} 权限问题解决方案"
        elif 'not found' in message.lower() or '404' in message:
            return f"{tool} 资源未找到处理"
        elif 'network' in message.lower() or 'connection' in message.lower():
            return f"{tool} 网络连接问题"
        else:
            return f"{tool} - {error_type} 错误处理"

    def _categorize_error(self, error: Dict) -> str:
        """对错误进行分类"""
        error_type = error.get('error_type', '').lower()
        message = error.get('message', '').lower()

        if 'timeout' in message or 'network' in message or 'connection' in message:
            return ErrorCategory.NETWORK.value
        elif 'permission' in message or 'denied' in message or 'access' in message:
            return ErrorCategory.PERMISSION.value
        elif 'not found' in message or '404' in message or 'missing' in message:
            return ErrorCategory.RESOURCE.value
        elif 'config' in message or 'setting' in message:
            return ErrorCategory.CONFIGURATION.value
        elif 'pip' in message or 'npm' in message or 'install' in message:
            return ErrorCategory.DEPENDENCY.value
        else:
            return ErrorCategory.UNKNOWN.value

    def _format_problem(self, error: Dict) -> str:
        """格式化问题描述"""
        lines = [
            f"**错误类型**: {error.get('error_type')}",
            f"**工具**: {error.get('context', {}).get('tool')}",
            f"**操作**: {error.get('context', {}).get('operation')}",
            f"**错误信息**: {error.get('message')}",
        ]

        if error.get('root_cause'):
            lines.append(f"**根因**: {error.get('root_cause')}")

        return '\n'.join(lines)

    def _format_solution(self, error: Dict) -> str:
        """格式化解决方案"""
        fix = error.get('fix', {})
        lines = []

        if fix.get('solution'):
            lines.append(f"**解决方案**: {fix['solution']}")

        if fix.get('action_taken'):
            lines.append(f"**具体行动**:\n```\n{fix['action_taken']}\n```")

        prevention = error.get('prevention', {})
        if prevention.get('check_before'):
            lines.append("**预防措施**:")
            for check in prevention['check_before']:
                lines.append(f"- {check}")

        return '\n\n'.join(lines)

    def _generate_code_example(self, error: Dict) -> Optional[str]:
        """生成代码示例"""
        action = error.get('fix', {}).get('action_taken', '')

        # 如果行动已经是代码，直接返回
        if '```' in action or any(kw in action for kw in ['import ', 'def ', 'class ', 'pip ', 'git ']):
            # 提取代码块
            if '```' in action:
                match = re.search(r'```(?:\w+)?\n(.*?)```', action, re.DOTALL)
                if match:
                    return match.group(1).strip()
            return action

        return None

    def _extract_tags(self, error: Dict) -> List[str]:
        """提取标签"""
        tags = set()

        # 从上下文提取
        context = error.get('context', {})
        if context.get('tool'):
            tags.add(context['tool'])
        if context.get('tags'):
            tags.update(context['tags'])

        # 从错误类型提取
        if error.get('error_type'):
            tags.add(error['error_type'])

        return list(tags)

    def save_knowledge(self, entry: KnowledgeEntry):
        """保存知识条目"""
        # 保存 JSON
        json_path = self.knowledge_dir / f"{entry.entry_id}.json"
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(entry.to_dict(), f, ensure_ascii=False, indent=2)

        # 保存 Markdown
        md_path = self.knowledge_dir / f"{entry.entry_id}.md"
        with open(md_path, 'w', encoding='utf-8') as f:
            f.write(entry.to_markdown())

    def search_knowledge(self, query: str, tags: Optional[List[str]] = None) -> List[KnowledgeEntry]:
        """搜索知识库"""
        results = []

        for filepath in self.knowledge_dir.glob("*.json"):
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)

                # 标签过滤
                if tags:
                    entry_tags = set(data.get('tags', []))
                    if not any(tag in entry_tags for tag in tags):
                        continue

                # 关键词匹配
                content = f"{data.get('title', '')} {data.get('problem', '')} {data.get('solution', '')}"
                if query.lower() in content.lower():
                    results.append(KnowledgeEntry(**data))

            except Exception:
                continue

        return results


class RealtimeWarningSystem:
    """实时预警系统"""

    def __init__(self):
        self.warnings_dir = WARNINGS_DIR
        self.pattern_analyzer = ErrorPatternAnalyzer()

    def check_risk(self, tool: str, operation: str, context: Optional[Dict] = None) -> List[Dict]:
        """检查操作风险"""
        warnings = []

        # 1. 检查历史错误
        history_risks = self._check_history_risks(tool, operation)
        warnings.extend(history_risks)

        # 2. 检查模式匹配
        pattern_risks = self._check_pattern_risks(tool, operation, context)
        warnings.extend(pattern_risks)

        # 3. 检查环境风险
        env_risks = self._check_environment_risks(tool)
        warnings.extend(env_risks)

        return warnings

    def _check_history_risks(self, tool: str, operation: str) -> List[Dict]:
        """检查历史错误风险"""
        risks = []

        # 加载近期错误
        cutoff = datetime.now() - timedelta(days=7)
        for filepath in ERRORS_DIR.glob("*.json"):
            if filepath.name == "index.json":
                continue
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    error = json.load(f)

                error_date = datetime.fromisoformat(error.get('timestamp', '2000-01-01'))
                if error_date < cutoff:
                    continue

                context = error.get('context', {})
                if context.get('tool') == tool:
                    risks.append({
                        'level': 'medium',
                        'type': 'history',
                        'message': f"该工具近期有错误记录: {error.get('error_type')}",
                        'error_id': error.get('id'),
                        'prevention': error.get('prevention', {}).get('check_before', [])
                    })

            except Exception:
                continue

        return risks

    def _check_pattern_risks(self, tool: str, operation: str, context: Optional[Dict]) -> List[Dict]:
        """检查模式风险"""
        risks = []

        patterns = self.pattern_analyzer.load_patterns()
        for pattern in patterns:
            if any(sig.tool == tool for sig in pattern.signatures):
                if pattern.occurrence_count >= 3:
                    risks.append({
                        'level': 'high',
                        'type': 'pattern',
                        'message': f"发现高频错误模式: {pattern.name}",
                        'pattern_id': pattern.pattern_id,
                        'prevention': pattern.prevention_strategy.split('\n')
                    })

        return risks

    def _check_environment_risks(self, tool: str) -> List[Dict]:
        """检查环境风险"""
        risks = []

        # 检查网络代理（针对需要网络的工具）
        network_tools = ['WebFetch', 'WebSearch', 'git', 'pip', 'npm', 'curl', 'wget']
        if tool in network_tools:
            proxy = os.environ.get('HTTP_PROXY') or os.environ.get('HTTPS_PROXY')
            if not proxy:
                risks.append({
                    'level': 'low',
                    'type': 'environment',
                    'message': '未检测到网络代理配置，外部请求可能失败',
                    'prevention': ['检查 HTTP_PROXY/HTTPS_PROXY 环境变量']
                })

        return risks

    def generate_early_warning(self, session_context: Dict) -> Optional[str]:
        """生成早期预警"""
        warnings = []

        # 基于会话上下文分析
        current_tool = session_context.get('current_tool')
        recent_operations = session_context.get('recent_operations', [])

        if current_tool:
            risks = self.check_risk(current_tool, recent_operations[-1] if recent_operations else '')
            if risks:
                warnings.append(f"当前操作 ({current_tool}) 有风险提示:")
                for risk in risks:
                    warnings.append(f"  [{risk['level'].upper()}] {risk['message']}")

        if warnings:
            return '\n'.join(warnings)
        return None


class EnhancedSelfCorrection:
    """增强版自我纠错系统 - 主入口"""

    def __init__(self):
        self.pattern_analyzer = ErrorPatternAnalyzer()
        self.prevention_generator = PreventionGenerator()
        self.knowledge_extractor = KnowledgeExtractor()
        self.warning_system = RealtimeWarningSystem()

    def analyze_and_learn(self, days: int = 30) -> Dict:
        """分析错误并提取知识"""
        print("🔍 分析错误模式...")
        patterns = self.pattern_analyzer.analyze_errors(days)
        print(f"   发现 {len(patterns)} 个错误模式")

        print("📚 提取知识...")
        knowledge_count = 0

        # 从错误中提取
        for filepath in ERRORS_DIR.glob("*.json"):
            if filepath.name == "index.json":
                continue
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    error = json.load(f)
                knowledge = self.knowledge_extractor.extract_from_error(error)
                if knowledge:
                    self.knowledge_extractor.save_knowledge(knowledge)
                    knowledge_count += 1
            except Exception:
                continue

        # 从模式中提取
        for pattern in patterns:
            knowledge = self.knowledge_extractor.extract_from_pattern(pattern)
            if knowledge:
                self.knowledge_extractor.save_knowledge(knowledge)
                knowledge_count += 1

        print(f"   提取 {knowledge_count} 条知识")

        # 生成预防清单
        print("🛡️ 生成预防清单...")
        checklist_count = 0
        tools = set()
        for filepath in ERRORS_DIR.glob("*.json"):
            if filepath.name == "index.json":
                continue
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    error = json.load(f)
                tool = error.get('context', {}).get('tool')
                if tool:
                    tools.add(tool)
            except Exception:
                continue

        for tool in tools:
            relevant_patterns = [p for p in patterns if any(sig.tool == tool for sig in p.signatures)]
            if relevant_patterns:
                # 为每个工具生成一个通用清单
                checklist = self.prevention_generator.generate_checklist(
                    tool, "general", relevant_patterns
                )
                checklist_count += 1

        print(f"   生成 {checklist_count} 份预防清单")

        return {
            'patterns_found': len(patterns),
            'knowledge_extracted': knowledge_count,
            'checklists_generated': checklist_count
        }

    def get_prevention_guide(self, tool: str, operation: str) -> Dict:
        """获取操作前的预防指南"""
        # 检查风险
        warnings = self.warning_system.check_risk(tool, operation)

        # 查找相关知识
        knowledge = self.knowledge_extractor.search_knowledge(query=operation, tags=[tool])

        # 生成建议
        suggestions = []
        for warning in warnings:
            suggestions.extend(warning.get('prevention', []))

        for k in knowledge[:3]:  # 最多3条相关知识
            suggestions.append(f"参考: {k.title}")

        return {
            'tool': tool,
            'operation': operation,
            'risk_level': 'high' if any(w['level'] == 'high' for w in warnings) else 'medium' if warnings else 'low',
            'warnings': warnings,
            'related_knowledge': [{'title': k.title, 'entry_id': k.entry_id} for k in knowledge[:3]],
            'prevention_suggestions': list(set(suggestions))  # 去重
        }

    def generate_learning_report(self, days: int = 30) -> str:
        """生成学习报告"""
        # 加载数据
        patterns = self.pattern_analyzer.load_patterns()
        knowledge_files = list(KNOWLEDGE_DIR.glob("*.md"))

        # 统计
        total_errors = len([f for f in ERRORS_DIR.glob("*.json") if f.name != "index.json"])
        total_patterns = len(patterns)
        total_knowledge = len(knowledge_files)

        # 高频问题
        high_freq_patterns = [p for p in patterns if p.occurrence_count >= 3]

        report = f"""# 🤖 自我纠错学习报告 ({datetime.now().strftime('%Y-%m-%d')})

## 📊 数据概览（近{days}天）

| 指标 | 数值 |
|------|------|
| 错误记录 | {total_errors} |
| 发现模式 | {total_patterns} |
| 知识条目 | {total_knowledge} |

## 🔥 高频问题模式

"""

        if high_freq_patterns:
            for p in high_freq_patterns:
                report += f"""### {p.name}
- **发生次数**: {p.occurrence_count}
- **根因**: {p.root_cause}
- **预防策略**:
{p.prevention_strategy}

"""
        else:
            report += "暂无高频问题模式\n\n"

        report += """## 📚 知识库

"""
        for kf in knowledge_files[:10]:  # 最近10条
            try:
                with open(kf, 'r', encoding='utf-8') as f:
                    content = f.read()
                # 提取标题
                title = content.split('\n')[0].replace('# ', '')
                report += f"- [{title}]({kf.name})\n"
            except Exception:
                continue

        report += f"""

## 💡 核心建议

1. **预防优于修复**: 执行操作前使用预防指南检查风险
2. **模式识别**: 关注高频错误模式，系统性解决问题
3. **知识复用**: 遇到类似问题时先查询知识库

---
*本报告由增强版自我纠错系统自动生成*
"""

        # 保存报告
        report_path = BASE_DIR / f"learning-report-{datetime.now().strftime('%Y%m%d')}.md"
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report)

        return report


# ============ 便捷函数 ============

def analyze_errors(days: int = 30) -> Dict:
    """分析错误并学习"""
    system = EnhancedSelfCorrection()
    return system.analyze_and_learn(days)


def get_prevention_guide(tool: str, operation: str) -> Dict:
    """获取预防指南"""
    system = EnhancedSelfCorrection()
    return system.get_prevention_guide(tool, operation)


def check_risk(tool: str, operation: str) -> List[Dict]:
    """检查操作风险"""
    warning_system = RealtimeWarningSystem()
    return warning_system.check_risk(tool, operation)


def generate_learning_report(days: int = 30) -> str:
    """生成学习报告"""
    system = EnhancedSelfCorrection()
    return system.generate_learning_report(days)


def search_knowledge(query: str, tags: Optional[List[str]] = None) -> List[Dict]:
    """搜索知识库"""
    extractor = KnowledgeExtractor()
    entries = extractor.search_knowledge(query, tags)
    return [e.to_dict() for e in entries]


# ============ 测试 ============

if __name__ == "__main__":
    print("=== 增强版自我纠错系统测试 ===\n")

    # 1. 分析错误并学习
    print("1. 分析错误模式并提取知识...")
    result = analyze_errors(days=30)
    print(f"   模式: {result['patterns_found']}")
    print(f"   知识: {result['knowledge_extracted']}")
    print(f"   清单: {result['checklists_generated']}")

    # 2. 获取预防指南
    print("\n2. 获取 Bash git clone 的预防指南...")
    guide = get_prevention_guide("Bash", "git clone")
    print(f"   风险等级: {guide['risk_level']}")
    print(f"   警告数: {len(guide['warnings'])}")
    print(f"   建议数: {len(guide['prevention_suggestions'])}")

    # 3. 检查风险
    print("\n3. 检查 WebFetch 操作风险...")
    risks = check_risk("WebFetch", "fetch documentation")
    print(f"   风险项: {len(risks)}")

    # 4. 生成报告
    print("\n4. 生成学习报告...")
    report = generate_learning_report()
    print("   报告已生成")

    # 5. 搜索知识
    print("\n5. 搜索 'timeout' 相关知识...")
    knowledge = search_knowledge("timeout", tags=["network"])
    print(f"   找到 {len(knowledge)} 条知识")

    print("\n=== 测试完成 ===")
