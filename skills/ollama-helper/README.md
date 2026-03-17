# Ollama Helper Skill

调用本地 Qwen 模型进行代码辅助

## 快速开始

### 1. 安装快捷命令（推荐）

```bash
# 运行安装脚本
cd ~/.claude/skills/ollama-helper
./install.bat
```

安装后，你可以在任何地方使用 `qw` 和 `qwa` 命令。

### 2. 直接使用（无需安装）

```bash
cd ~/.claude/skills/ollama-helper

# 列出可用模型
./qw.bat list

# 与 Qwen 对话
./qw.bat chat "写一个快速排序算法"

# 代码补全
./qw.bat complete "def fibonacci(n):"

# 代码解释
./qw.bat explain "def quicksort(arr): ..."

# 代码审查
./qw.bat review myfile.py
```

## 命令列表

### qw - 基础调用

| 命令 | 功能 | 示例 |
|------|------|------|
| `qw list` | 列出可用模型 | `qw list` |
| `qw chat "prompt"` | 自由对话 | `qw chat "解释递归"` |
| `qw complete "code"` | 代码补全 | `qw complete "def hello():"` |
| `qw explain "code"` | 代码解释 | `qw explain "lambda x: x*2"` |
| `qw review <file>` | 代码审查 | `qw review script.py` |

### qwa - 自动决策（智能模式）

| 命令 | 功能 | 示例 |
|------|------|------|
| `qwa advise "task"` | 智能决策建议 | `qwa advise "review code"` |
| `qwa review "code"` | 自动代码审查 | `qwa review "def foo():"` |
| `qwa complete "code"` | 自动代码补全 | `qwa complete "class Node:"` |

## 在 Claude Code 中自动调用

Claude 现在会根据任务类型**自动**调用 Qwen：

**自动触发场景**：
- ✅ 代码审查 → 调用 Qwen 生成初稿 → Claude 优化
- ✅ 代码补全 → 调用 Qwen 完成代码 → Claude 验证
- ✅ 代码解释 → 调用 Qwen 解释 → Claude 补充
- ✅ 生成测试 → 调用 Qwen 生成 → Claude 检查

**不触发场景**：
- ❌ 架构设计 → Claude 直接处理
- ❌ 复杂调试 → Claude 直接处理
- ❌ 需求分析 → Claude 直接处理

## 双模型协作示例

用户："帮我审查这段代码"
```python
def bubble_sort(arr):
    n = len(arr)
    for i in range(n):
        for j in range(0, n-i-1):
            if arr[j] > arr[j+1]:
                arr[j], arr[j+1] = arr[j+1], arr[j]
    return arr
```

Claude 自动：
1. 识别任务类型：代码审查 ✅
2. 调用 Qwen：`qwa review "<code>"`
3. 获取 Qwen 反馈（2秒）
4. 整合输出：

```
[Qwen 发现的问题]
- 没有输入验证
- 可以添加类型提示
- 时间复杂度较高

[Claude 的优化建议]
- 添加空列表检查
- 使用 Type hints
- 考虑使用 Timsort（Python内置）

[优化后的代码]
...
```

## 配置

默认模型：`qwen2.5-coder:7b`

修改模型：
```python
# ollama_helper.py 或 ollama_auto.py
DEFAULT_MODEL = "qwen2.5-coder:7b"
```

## 依赖

```bash
pip install requests
```

## 要求

- Ollama 已安装并运行
- Qwen 模型已下载：`ollama pull qwen2.5-coder:7b`

## 文件结构

```
~/.claude/skills/ollama-helper/
├── ollama_helper.py      # 基础调用工具
├── ollama_auto.py        # 自动决策器
├── qw.bat               # 快捷命令（基础）
├── qwa.bat              # 快捷命令（自动）
├── install.bat          # 安装脚本
└── README.md            # 本文档
```

## 故障排除

### 乱码问题
已修复！脚本现在强制使用 UTF-8 编码。

### "Ollama API 未启动"
```bash
# 启动 Ollama
ollama serve
```

### 命令找不到
运行 `install.bat` 或确保 `~/.local/bin` 在 PATH 中。

## 更新日志

**v1.1.0** (2026-03-17)
- ✅ 修复 Windows 编码问题
- ✅ 添加快捷命令 `qw` 和 `qwa`
- ✅ 添加安装脚本
- ✅ 优化自动决策逻辑

**v1.0.0** (2026-03-17)
- 🎉 初始版本
- 基础 Ollama API 调用
- 代码审查/补全/解释功能
