@echo off
chcp 65001 >nul
echo ===========================================
echo  Video Summarizer - 依赖安装脚本
echo ===========================================
echo.

:: 检查 Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未检测到 Python，请先安装 Python 3.8+
    echo 下载地址: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo [1/3] 检测到 Python 版本:
python --version
echo.

:: 检查 ffmpeg
echo [2/3] 检查 ffmpeg...
ffmpeg -version >nul 2>&1
if errorlevel 1 (
    echo [警告] 未检测到 ffmpeg，请手动安装:
    echo   - 方式1: choco install ffmpeg
    echo   - 方式2: 从 https://ffmpeg.org/download.html 下载
    echo.
    echo 安装完成后请重新运行此脚本。
    pause
    exit /b 1
)
echo ffmpeg 已安装
echo.

:: 安装 Python 依赖
echo [3/3] 安装 Python 依赖...
pip install youtube-transcript-api yt-dlp openai-whisper openai requests -q

if errorlevel 1 (
    echo [错误] 依赖安装失败
    pause
    exit /b 1
)

echo.
echo ===========================================
echo  安装完成！
echo ===========================================
echo.
echo 使用方法:
echo   python tools/extract_video.py "视频链接"
echo.
echo 示例:
echo   python tools/extract_video.py "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
echo.
echo Whisper 模式:
echo   本地模式（默认）: 使用本地 Whisper 模型
echo   API 模式: 设置 OPENAI_API_KEY 后使用 --whisper-mode api
echo.
pause
