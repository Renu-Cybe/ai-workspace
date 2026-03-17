@echo off
chcp 65001 >nul
echo ==========================================
echo  Whisper 模型预下载工具
echo ==========================================
echo.
echo 由于网络原因，自动下载可能会很慢或失败。
echo 这个脚本会指导你如何手动下载模型文件。
echo.

set MODEL_DIR=%USERPROFILE%\.cache\whisper
if not exist "%MODEL_DIR%" mkdir "%MODEL_DIR%"

echo [1] 模型将保存到: %MODEL_DIR%\base.pt
echo.
echo [2] 请使用以下方式之一下载模型:
echo.
echo    方式 A - 浏览器下载 (推荐):
echo    访问: https://hf-mirror.com/openai/whisper-base/resolve/main/model.pt
echo    保存为: base.pt
echo    放到: %MODEL_DIR%\
echo.
echo    方式 B - 使用迅雷/IDM下载:
echo    URL: https://openaipublic.azureedge.net/main/whisper/models/ed3a0b6b1c0edf879ad9b11b1af5a0e6ab5db9205f891f668f8b0e6c6326e34e/base.pt
echo    文件名: base.pt
echo    放到: %MODEL_DIR%\
echo.
echo    方式 C - 如果你有代理/VPN:
echo    直接运行 extract_video.py 让它自动下载
echo.
echo [3] 验证安装:
echo    文件大小应该是约 145MB
echo    SHA256: ed3a0b6b1c0edf879ad9b11b1af5a0e6ab5db9205f891f668f8b0e6c6326e34e
echo.
echo ==========================================
echo 按任意键打开模型目录...
echo ==========================================
pause >nul

start "" "%MODEL_DIR%"
echo.
echo 目录已打开。请将下载的 base.pt 放到这个文件夹中。
echo.
pause
