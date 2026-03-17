# Video Summarizer Skill

提取 YouTube 和 Bilibili 视频字幕并生成结构化总结。

> ⚠️ **状态**: 开发中 / 搁置待优化
> **最后更新**: 2026-03-17
> **已知问题**: B站反爬限制、YouTube需要登录

## 当前功能状态

| 功能 | 状态 | 备注 |
|------|------|------|
| YouTube 软字幕提取 | ✅ 可用 | youtube-transcript-api |
| YouTube 自动生成字幕 | ✅ 可用 | 无需登录 |
| B站 CC 字幕提取 | ⚠️ 部分可用 | API可能返回空 |
| Whisper 本地转录 | ✅ 已集成 | base模型 |
| yt-dlp 音频下载 | ❌ 受限 | 需用户环境支持cookies |
| 音频文件直接转录 | ✅ 可用 | 可手动下载后转录 |

## 已知限制

1. **B站反爬** (HTTP 412) - 无法自动下载音频
2. **YouTube登录** - 部分视频需要登录验证
3. **会员视频** - 暂不支持

## 后续优化方向

- [ ] 支持 cookies.txt 导入
- [ ] 支持本地音频文件直接转录
- [ ] 优化 B站 API 调用策略
- [ ] 添加缓存机制避免重复下载
- [ ] 支持更多视频平台

---

## 功能

- **YouTube**: 官方字幕 / 自动生成字幕 / Whisper 语音识别
- **Bilibili**: CC 字幕（UP主上传）/ Whisper 语音识别
- **语言优先级**: 中文 > 英文 > 日文
- **降级策略**: 无字幕时自动使用 Whisper 转录音频

## 工作模式

```
视频链接 → 检测平台 → 尝试提取软字幕 → 失败？→ Whisper 转录
                                          ↓
                                    生成结构化总结
```

## 文件说明

```
video-summarizer/
├── settings.json          # Skill 配置
├── README.md              # 本文档
└── tools/
    ├── extract_video.py   # 字幕提取脚本（已优化）
    ├── requirements.txt   # Python 依赖
    └── install.bat        # Windows 安装脚本
```

## 安装

### 系统依赖（必须）

**ffmpeg**: 音频处理
- Windows: `choco install ffmpeg` 或从 [官网](https://ffmpeg.org/download.html) 下载
- macOS: `brew install ffmpeg`
- Linux: `sudo apt install ffmpeg`

### Python 依赖

```bash
pip install youtube-transcript-api yt-dlp openai-whisper openai requests
```

### 可选：GPU 加速（推荐）

```bash
# NVIDIA GPU
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

# Apple Silicon
pip install torch torchvision torchaudio
```

## 使用

### 在 Claude Code 中

```
总结这个视频：https://www.youtube.com/watch?v=xxxxx
```

```
提取 B站视频 https://www.bilibili.com/video/BVxxxxx 的内容
```

### 命令行测试

```bash
python tools/extract_video.py "https://www.youtube.com/watch?v=xxxxx"
python tools/extract_video.py "https://www.bilibili.com/video/BVxxxxx"

# 使用 OpenAI Whisper API（更快，需要 API Key）
python tools/extract_video.py "https://www.youtube.com/watch?v=xxxxx" --whisper-mode api
```

### 环境变量

```bash
# 使用 Whisper API 模式时需要
export OPENAI_API_KEY="your-api-key"
```

## 输出格式

Claude 会生成结构化总结：

```
## 视频标题

### 核心要点
- 要点 1
- 要点 2
- 要点 3
...

### 关键时间戳
- 00:00 开场
- 02:30 核心概念
...

### 补充说明
...
```

## 支持的链接格式

**YouTube:**
- `https://www.youtube.com/watch?v=xxxxx`
- `https://youtu.be/xxxxx`
- `https://youtube.com/shorts/xxxxx`

**Bilibili:**
- `https://www.bilibili.com/video/BVxxxxx`
- `https://b23.tv/BVxxxxx`

## 限制

- 仅支持有字幕的视频（YouTube 自动生成字幕或 B站 CC 字幕）
- 无字幕视频会自动使用 Whisper 转录（需要下载音频，耗时较长）
- Whisper 转录需要较多计算资源（建议 GPU 加速）
- 无法处理会员专属视频
- 无法处理被下架/删除的视频

## 文件说明

```
video-summarizer/
├── settings.json          # Skill 配置（Claude 读取）
├── README.md              # 本文档
└── tools/
    ├── extract_video.py   # 字幕提取脚本
    ├── requirements.txt   # Python 依赖
    └── install.bat        # Windows 安装脚本
```

## License

MIT
