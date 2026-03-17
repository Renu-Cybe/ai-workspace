@echo off
chcp 65001 >nul
title Memory Bank - Branch Switcher

:: Memory Bank 分支切换脚本
:: 根据 git 分支切换记忆上下文

set MEMORY_BANK=%USERPROFILE%\.claude\memory-bank
set CURRENT_BRANCH=%~1

if "%CURRENT_BRANCH%"=="" (
    :: 自动检测当前分支
    for /f "tokens=*" %%a in ('git branch --show-current 2^>nul') do set CURRENT_BRANCH=%%a
)

if "%CURRENT_BRANCH%"=="" (
    echo [信息] 未检测到 git 分支，使用 main
    set CURRENT_BRANCH=main
)

echo ========================================
echo   Memory Bank - 分支切换
echo ========================================
echo.
echo 当前分支: %CURRENT_BRANCH%
echo.

:: 检查分支目录是否存在
if not exist "%MEMORY_BANK%\%CURRENT_BRANCH%" (
    echo [信息] 分支 '%CURRENT_BRANCH%' 不存在，正在创建...
    mkdir "%MEMORY_BANK%\%CURRENT_BRANCH%\decisions" 2>nul
    mkdir "%MEMORY_BANK%\%CURRENT_BRANCH%\sessions" 2>nul
    mkdir "%MEMORY_BANK%\%CURRENT_BRANCH%\todos" 2>nul
    mkdir "%MEMORY_BANK%\%CURRENT_BRANCH%\context" 2>nul
    echo   ✓ 已创建分支目录
) else (
    echo   ✓ 分支目录已存在
)
echo.

:: 加载分支特定的上下文（如果存在）
if exist "%MEMORY_BANK%\%CURRENT_BRANCH%\context\BRANCH.md" (
    echo [1/2] 加载分支特定上下文...
    type "%MEMORY_BANK%\%CURRENT_BRANCH%\context\BRANCH.md" 2>nul | head -20
    echo.
)

:: 显示分支状态
echo [2/2] 分支状态:
echo   - 决策: %MEMORY_BANK%\%CURRENT_BRANCH%\decisions\
dir /b "%MEMORY_BANK%\%CURRENT_BRANCH%\decisions\" 2>nul | find /c /v ""
echo   - 会话: %MEMORY_BANK%\%CURRENT_BRANCH%\sessions\
dir /b "%MEMORY_BANK%\%CURRENT_BRANCH%\sessions\" 2>nul | find /c /v ""
echo   - 待办: %MEMORY_BANK%\%CURRENT_BRANCH%\todos\
dir /b "%MEMORY_BANK%\%CURRENT_BRANCH%\todos\" 2>nul | find /c /v ""
echo.

echo ========================================
echo   已切换到分支: %CURRENT_BRANCH%
echo ========================================
echo.
echo 提示:
echo   - 所有新记录将保存到 %CURRENT_BRANCH% 分支
echo   - 共享数据仍从 shared/ 读取
echo   - 使用 'switch-branch ^<name^>' 切换分支
echo.
