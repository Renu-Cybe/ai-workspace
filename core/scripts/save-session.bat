@echo off
chcp 65001 >nul
title Memory Bank - Save Session

:: Memory Bank 会话结束保存脚本
:: 在会话结束时执行

set MEMORY_BANK=%USERPROFILE%\.claude\memory-bank
set SESSION_FILE=%~1

if "%SESSION_FILE%"=="" (
    echo [错误] 请提供会话文件路径
    echo 用法: save-session ^<session-file^>
    exit /b 1
)

if not exist "%SESSION_FILE%" (
    echo [错误] 会话文件不存在: %SESSION_FILE%
    exit /b 1
)

:: 获取当前日期和分支
for /f "tokens=*" %%a in ('date /t') do set TODAY=%%a
for /f "tokens=*" %%a in ('git branch --show-current 2^>nul') do set BRANCH=%%a
if "%BRANCH%"=="" set BRANCH=main

:: 提取日期 (格式: YYYY-MM-DD)
for /f "tokens=1 delims= " %%a in ('echo %TODAY%') do set DATE_STR=%%a
:: Windows date format varies, use a simpler approach
set DATE_STR=%date:~0,4%-%date:~5,2%-%date:~8,2%

echo ========================================
echo   Memory Bank - 保存会话
echo ========================================
echo.
echo 日期: %DATE_STR%
echo 分支: %BRANCH%
echo 源文件: %SESSION_FILE%
echo.

:: 确保目标目录存在
if not exist "%MEMORY_BANK%\%BRANCH%\sessions" (
    mkdir "%MEMORY_BANK%\%BRANCH%\sessions" 2>nul
)

:: 生成文件名
set TARGET_FILE=%MEMORY_BANK%\%BRANCH%\sessions\%DATE_STR%.md

:: 如果文件已存在，追加内容
if exist "%TARGET_FILE%" (
    echo [信息] 追加到现有文件: %TARGET_FILE%
    echo. >> "%TARGET_FILE%"
    echo --- >> "%TARGET_FILE%"
    echo. >> "%TARGET_FILE%"
    type "%SESSION_FILE%" >> "%TARGET_FILE%"
) else (
    echo [信息] 创建新文件: %TARGET_FILE%
    type "%SESSION_FILE%" > "%TARGET_FILE%"
)

echo   ✓ 会话已保存
echo.

:: 删除 current.md（标记为已完成）
del "%SESSION_FILE%" 2>nul
echo   ✓ 已删除 current.md
echo.

:: 更新索引
echo [信息] 更新会话索引...
python -c "
import json
import os
from pathlib import Path

memory_bank = Path.home() / '.claude/memory-bank'
index_file = memory_bank / 'shared/.index/sessions.json'

if not index_file.exists():
    index = {'sessions': [], 'last_updated': ''}
else:
    with open(index_file, 'r', encoding='utf-8') as f:
        index = json.load(f)

index['sessions'].insert(0, {
    'date': '%DATE_STR%',
    'branch': '%BRANCH%',
    'file': str(memory_bank / '%BRANCH%/sessions/%DATE_STR%.md')
})
index['last_updated'] = '%DATE_STR%'

index_file.parent.mkdir(parents=True, exist_ok=True)
with open(index_file, 'w', encoding='utf-8') as f:
    json.dump(index, f, ensure_ascii=False, indent=2)
" 2>nul

echo   ✓ 索引已更新
echo.

echo ========================================
echo   会话保存完成
echo ========================================
echo.
