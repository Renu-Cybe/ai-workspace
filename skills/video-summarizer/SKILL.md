---
name: video-summarizer
description: |
  提取 YouTube 和 Bilibili 视频字幕并生成结构化总结。
  优先提取官方字幕，无字幕时使用 Whisper 语音识别。
  支持软字幕、自动生成字幕和音频转录。

tools: [Bash]
context: fork
---

# Video Summarizer

## 用途

提取视频平台字幕内容并生成结构化总结。支持字幕提取和语音转录双模式。

## 支持平台

| 平台 | 字幕类型 | 说明 |
|------|---------|------|
| **YouTube** | 官方字幕 / 自动生成字幕 / Whisper 转录 | 三级降级策略 |
| **Bilibili** | CC 字幕（UP主上传）/ Whisper 转录 | API 获取失败时转录 |

## 工作模式

```
视频链接 → 检测平台 → 尝试提取软字幕 → 失败？→ 下载音频 → Whisper 转录
                                          ↓
                                    生成结构化总结
```

## 使用方式

### 1. 基础用法（自动模式）
```
用户: "总结这个视频 https://www.youtube.com/watch?v=xxxxx"
用户: "提取 B站视频 https://www.bilibili.com/video/BVxxxxx 的内容"
```

### 2. 指定 Whisper 模式
```
用户: "使用 API 转录这个视频 https://youtu.be/xxxxx"
用户: "本地转录 https://www.bilibili.com/video/BVxxxxx"
```

## 工作流程

1. **接收视频链接**
   - 识别 YouTube 或 Bilibili 链接
   - 支持多种 URL 格式

2. **提取字幕**
   - YouTube：使用 youtube-transcript-api 获取字幕列表
   - Bilibili：调用官方 API 获取 CC 字幕
   - 按语言优先级选择：中文 > 英文 > 日文

3. **降级策略**（字幕提取失败时）
   - 下载视频音频（使用 yt-dlp）
   - 使用 Whisper 转录音频
   - 本地模式：使用 openai-whisper 库
   - API 模式：调用 OpenAI Whisper API（更快）

4. **生成总结**
   - 视频信息（标题、平台、语言、来源）
   - 核心要点（3-7条）
   - 关键时间戳（软字幕/Whisper 分段）
   - 补充说明

## 输出格式

```
## 视频标题

### 视频信息
- 平台: YouTube/Bilibili
- 语言: zh/en/ja
- 来源: 官方字幕 / Whisper 转录

### 核心要点
1. 要点 1
2. 要点 2
3. 要点 3
...

### 关键时间戳
- 00:00 开场/介绍
- 02:30 核心内容
...

### 补充说明
- 如果 source 是 whisper_local/whisper_api，说明是语音识别结果
- 转录准确率一般在 85-95%，关键信息请核对原视频
```

## 技术实现

### 依赖
```bash
pip install youtube-transcript-api yt-dlp openai-whisper openai requests
```

### 系统依赖
- **ffmpeg**: 音频处理（必须）

### 字幕提取脚本
`tools/extract_video.py` - 核心提取逻辑

### 调用参数
```bash
# 本地模式（默认）
python tools/extract_video.py "<URL>"

# API 模式
python tools/extract_video.py "<URL>" --whisper-mode api
```

### 语言优先级
```python
['zh', 'zh-CN', 'zh-TW', 'zh-Hans', 'zh-Hant',  # 中文
 'en', 'en-US', 'en-GB',                         # 英文
 'ja', 'ja-JP']                                  # 日文
```

## 限制说明

| 限制 | 说明 | 解决方案 |
|------|------|---------|
| **硬字幕** | 画面内嵌字幕无法直接提取 | Whisper 可识别音频，忽略画面字幕 |
| **无语音** | 纯背景音乐/无解说视频 | 无法处理 |
| **会员视频** | 需要登录的视频 | 暂不支持 |
| **版权限制** | 部分视频禁用字幕/音频下载 | 无法解决 |
| **Whisper 耗时** | 本地转录 1 分钟视频约需 10-30 秒 | 使用 API 模式更快 |

## 参数

通过 `$ARGUMENTS` 接收：
- `<URL>` - 视频链接（必需）

## 示例对话

**用户**: "总结这个视频：https://www.youtube.com/watch?v=dQw4w9WgXcQ"

**Claude**:
```
正在提取字幕...

## Never Gonna Give You Up

### 视频信息
- 平台: YouTube
- 语言: en
- 来源: 自动生成字幕

### 核心要点
1. 这是一首经典流行歌曲
2. 歌词表达了坚定的承诺和感情
3. 视频以 Rick Astley 的标志性舞步闻名
...
```

**用户**: "分析这个 B站视频 https://www.bilibili.com/video/BV1xxxxx"

**Claude**:
```
未找到官方字幕，正在使用 Whisper 转录...
（这可能需要一些时间）

## 视频标题

### 视频信息
- 平台: Bilibili
- 语言: zh
- 来源: Whisper 转录

### 核心要点
1. ...
...

⚠️ 注意：此内容为 Whisper 语音识别结果，准确率约 90%，关键信息请核对原视频。
```

## 相关文件

- **提取脚本**: `tools/extract_video.py`
- **安装脚本**: `tools/install.bat`
- **依赖**: `tools/requirements.txt`
