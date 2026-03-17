# Self-Correction 装饰器实装状态

## 实装进度

| Skill | 状态 | 装饰器位置 | 关键函数 |
|-------|------|-----------|----------|
| video-summarizer | ✅ 已实装 | extract_video.py | extract(), _get_youtube_transcript(), _get_bilibili_transcript() |
| memory-manager | ✅ 已实装 | main.py | run_tool() |
| skill-seeker | ⚪ 无需实装 | - | 无 Python 代码（纯文档 Skill） |
| memory-cleanup | ⚪ 无需实装 | - | 无 Python 代码（纯文档 Skill） |

## 验证命令

```bash
# 验证 video-summarizer
cd ~/.claude/skills/video-summarizer/tools
python -c "from extract_video import HAS_SELF_CORRECTION; print(HAS_SELF_CORRECTION)"

# 验证 memory-manager
cd ~/.claude/skills/memory-manager
python -c "from main import HAS_SELF_CORRECTION; print(HAS_SELF_CORRECTION)"
```

## 实装效果

### 1. 自动错误捕获
当装饰的函数抛出异常时，系统会自动：
- 记录错误到 `memory-bank/errors/`
- 提取知识到 `memory-bank/knowledge/`
- 显示实时警告和建议

### 2. 操作前检查
每次调用装饰的函数前，系统会：
- 检查历史错误记录
- 分析实时风险
- 显示预防建议

### 3. 知识自动积累
每次错误都会被转换为知识条目：
- JSON 格式：结构化数据
- Markdown 格式：可读文档
- 支持搜索和复用

## 使用示例

### 当前已实装的行为

当使用 video-summarizer 时：
```python
# 自动捕获的错误会记录到记忆库
extractor = VideoSubtitleExtractor()
result = extractor.extract("https://...")  # 已自动添加装饰器
```

当使用 memory-manager 时：
```python
# 工具执行错误会自动记录
run_tool("dashboard")  # 已自动添加装饰器
```

## 监控命令

```bash
# 查看最近的错误记录
sc analyze -d 1

# 搜索相关知识
sc search timeout

# 生成学习报告
sc report -d 7
```

## 下一步建议

1. **运行测试** - 使用 video-summarizer 处理一个视频，观察自动错误捕获
2. **查看知识库** - 检查 `memory-bank/knowledge/` 中自动生成的知识
3. **定期分析** - 每周运行 `sc analyze` 发现错误模式

## 技术实现

### 装饰器模式
```python
# 集成代码示例
sys.path.insert(0, str(Path.home() / '.claude' / 'memory-bank' / 'tools'))
try:
    from self_correction_unified import UnifiedSelfCorrection
    _sc = UnifiedSelfCorrection("skill-name")
    HAS_SELF_CORRECTION = True
except ImportError:
    HAS_SELF_CORRECTION = False
    _sc = None

def _sc_wrapper(tool_name):
    def decorator(func):
        if _sc:
            return _sc.capture_decorator(tool_name=tool_name)(func)
        return func
    return decorator

@_sc_wrapper("ToolName")
def my_function():
    pass
```

### 容错设计
- 自我纠错系统加载失败时，原功能不受影响
- 装饰器只在系统可用时生效
- 错误捕获本身不会导致功能中断
