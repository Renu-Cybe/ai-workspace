@echo off
chcp 65001 >nul
title Memory Bank - Load Context

:: Memory Bank 上下文加载脚本
:: 在对话开始时自动加载核心上下文

set MEMORY_BANK=%USERPROFILE%\.claude\memory-bank

echo ========================================
echo   Memory Bank - 加载核心上下文
echo ========================================
echo.

:: 检查目录结构
if not exist "%MEMORY_BANK%\context\IDENTITY.md" (
    echo [错误] 记忆库结构不完整
    echo 请确认已执行 P0 重构
    exit /b 1
)

echo [1/4] 加载 IDENTITY.md...
type "%MEMORY_BANK%\context\IDENTITY.md" 2>nul | head -30
echo.

echo [2/4] 加载 USER.md...
type "%MEMORY_BANK%\context\USER.md" 2>nul | head -20
echo.

echo [3/4] 加载 PROTOCOL.md...
type "%MEMORY_BANK%\context\PROTOCOL.md" 2>nul | head -20
echo.

echo [4/4] 加载 HEARTBEAT.md...
type "%MEMORY_BANK%\context\HEARTBEAT.md" 2>nul | head -20
echo.

echo ========================================
echo   上下文加载完成
echo ========================================
echo.
echo 记忆库位置: %MEMORY_BANK%
echo 当前分支: main
echo.

:: 检查是否有当前会话
if exist "%MEMORY_BANK%\..\projects\C--Users-Administrator\memory\session\current.md" (
    echo [警告] 检测到未完成的会话
echo   位置: session/current.md
echo   建议: 询问用户是否恢复
echo.
)

:: 显示快速参考
echo 快速命令:
echo   - 查看状态: type %MEMORY_BANK%\active\MEMORY.md
echo   - 记录错误: python %MEMORY_BANK%\tools\self_correction.py
echo   - 切换分支: switch-branch ^<branch-name^>
echo.
