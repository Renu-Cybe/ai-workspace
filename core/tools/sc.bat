@echo off
chcp 65001 >nul
echo ==========================================
echo   统一自我纠错系统 (Unified Self-Correction)
echo ==========================================
echo.

set SCRIPT_DIR=%~dp0
set PYTHON=%LOCALAPPDATA%\Programs\Python\Python313\python.exe

if not exist "%PYTHON%" (
    set PYTHON=%LOCALAPPDATA%\Programs\Python\Python312\python.exe
)

if not exist "%PYTHON%" (
    echo [错误] 未找到 Python，请安装 Python 3.12+
    exit /b 1
)

if "%~1"=="" (
    echo 用法: sc [命令] [选项]
    echo.
    echo 可用命令:
    echo   sc analyze [-d 天数]      分析错误模式
    echo   sc check [工具] [-o 操作] 操作前检查
    echo   sc report [-d 天数]       生成学习报告
    echo   sc search [关键词]        搜索知识库
    echo.
    echo 示例:
    echo   sc analyze -d 30
    echo   sc check WebFetch -o "fetch page"
    echo   sc report -d 7 -o report.md
    echo   sc search timeout -t network api
) else (
    "%PYTHON%" "%SCRIPT_DIR%self_correction_unified.py" %*
)
