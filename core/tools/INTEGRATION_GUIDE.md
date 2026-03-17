# 统一自我纠错系统 - 集成指南

## 概述

统一自我纠错系统整合了基础版和增强版的所有功能，提供完整的错误捕获、分析、预防和学习能力。

## 功能特性

| 功能 | 基础版 | 增强版 | 统一版 |
|------|--------|--------|--------|
| 错误捕获和记录 | ✅ | ✅ | ✅ |
| 经验查询 | ✅ | ✅ | ✅ |
| 错误模式分析 | ❌ | ✅ | ✅ |
| 知识提取 | ❌ | ✅ | ✅ |
| 实时风险警告 | ❌ | ✅ | ✅ |
| 预防清单生成 | ❌ | ✅ | ✅ |
| 学习报告 | ✅ | ✅ | ✅ |
| CLI 工具 | ❌ | ❌ | ✅ |

## 安装

1. 确保 `tools` 目录在 PATH 中：
```bash
# Windows
set PATH=%PATH%;C:\Users\Administrator\.claude\memory-bank\tools

# 或使用 PowerShell
[Environment]::SetEnvironmentVariable("PATH", $env:PATH + ";C:\Users\Administrator\.claude\memory-bank\tools", "User")
```

2. 验证安装：
```bash
sc
```

## CLI 用法

### 1. 分析错误模式
```bash
# 分析最近 7 天
sc analyze

# 分析最近 30 天
sc analyze -d 30
```

### 2. 操作前检查
```bash
# 检查工具风险
sc check WebFetch

# 检查具体操作
sc check Bash -o "git clone"
```

### 3. 生成学习报告
```bash
# 生成周报
sc report

# 生成月报并保存
sc report -d 30 -o monthly_report.md
```

### 4. 搜索知识库
```bash
# 基本搜索
sc search timeout

# 按标签过滤
sc search timeout -t network api
```

## Python API 用法

### 基础用法

```python
from self_correction_unified import UnifiedSelfCorrection

# 创建实例
sc = UnifiedSelfCorrection("my-session")

# 使用装饰器自动捕获错误
@sc.capture_decorator(tool_name="WebFetch", operation="fetch page")
def fetch_data(url):
    # 可能出错的操作
    pass
```

### 操作前检查

```python
from self_correction_unified import check_before_operation

# 检查风险
result = check_before_operation("WebFetch", "fetch documentation")

if result['history']['history_count'] > 0:
    print(f"历史错误: {result['history']['history_count']} 次")

if result['risks']:
    for risk in result['risks']:
        print(f"[{risk['level']}] {risk['message']}")
```

### 知识库搜索

```python
# 搜索知识
results = sc.search_knowledge_base("timeout", tags=["network"])

for item in results:
    print(f"{item['title']}: {item['category']}")
```

### 会话分析

```python
# 分析当前会话
analysis = sc.analyze_session()

print(f"错误数: {analysis['errors_recorded']}")
print(f"改进率: {analysis['improvement_rate']:.1f}%")
```

## 文件结构

```
memory-bank/
├── errors/                 # 错误记录
│   ├── index.json         # 错误索引
│   └── 2026-03-17-001.json # 具体错误
├── knowledge/             # 知识库
│   ├── *.json            # 结构化知识
│   └── *.md              # 可读文档
├── fixes/                # 修复记录
├── lessons/              # 经验总结
└── tools/
    ├── self_correction.py              # 基础版
    ├── self_correction_enhanced.py     # 增强版
    ├── self_correction_unified.py      # 统一版 ⭐
    ├── self_correction_integration.py  # 集成模块
    └── sc.bat                          # CLI 入口
```

## 工作流集成

### 1. 会话开始前检查
```python
from self_correction_unified import check_before_operation

def before_tool_use(tool: str, operation: str):
    result = check_before_operation(tool, operation)
    # 根据检查结果决定是否继续
    if any(r['level'] == 'high' for r in result['risks']):
        print("高风险操作，建议先解决问题")
```

### 2. 自动错误捕获
```python
from self_correction_unified import unified_capture

@unified_capture(tool_name="Bash", operation="network command")
def run_network_command(cmd):
    # 自动捕获和记录错误
    import subprocess
    return subprocess.run(cmd, shell=True)
```

### 3. 会话结束分析
```python
# 会话结束时
analysis = sc.analyze_session()
if analysis['errors_recorded'] > 0:
    report = sc.generate_report(days=1)
    # 保存或发送报告
```

## 与现有工具集成

### 与 Skill Seeker 集成
```python
# 在爬取文档前检查
sc.check_before_operation("WebFetch", "crawl documentation")
```

### 与 Memory Cleanup 集成
```python
# 清理前分析错误模式
sc.analyze_and_learn(days=30)
```

### 与 Video Summarizer 集成
```python
# 视频处理前检查
@sc.capture_decorator(tool_name="Whisper", operation="transcribe")
def transcribe_video(video_path):
    pass
```

## 配置

### 环境变量
```bash
# 错误记录目录
export ERROR_LOG_DIR="~/.claude/memory-bank/errors"

# 知识库目录
export KNOWLEDGE_DIR="~/.claude/memory-bank/knowledge"
```

### 相似度阈值
编辑 `self_correction_enhanced.py`：
```python
# 错误聚类相似度阈值（默认 0.6）
SIMILARITY_THRESHOLD = 0.6
```

## 最佳实践

1. **操作前检查**: 使用 `check_before_operation()` 在执行关键操作前检查风险
2. **装饰器捕获**: 使用 `@capture_decorator` 自动捕获和记录错误
3. **定期分析**: 定期运行 `sc analyze` 发现错误模式
4. **知识复用**: 遇到问题时先用 `sc search` 查询知识库
5. **持续学习**: 每周运行 `sc report` 生成学习报告

## 故障排除

### Unicode 编码错误
Windows 下如果遇到编码问题，确保使用 UTF-8：
```python
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
```

### 找不到 Python
确保 Python 3.12+ 已安装，或在 `sc.bat` 中修改 PYTHON 路径。

### 权限错误
确保对 `memory-bank` 目录有读写权限。

## 升级路径

1. **从基础版升级**: 直接使用统一版 API，向后兼容
2. **从增强版升级**: 统一版包含所有增强功能
3. **迁移数据**: 自动兼容现有错误记录和知识库
