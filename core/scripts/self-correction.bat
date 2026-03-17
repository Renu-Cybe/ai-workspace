@echo off
chcp 65001 >nul
title Self-Correction Tool

:: 获取脚本所在目录
set SCRIPT_DIR=%~dp0
set PYTHON_SCRIPT=%SCRIPT_DIR%self_correction.py

echo ========================================
echo   自我纠错系统 - 命令行工具
echo ========================================
echo.

if "%~1"=="" goto :show_help

if /i "%~1"=="record" goto :record_error
if /i "%~1"=="fix" goto :record_fix
if /i "%~1"=="check" goto :check_task
if /i "%~1"=="find" goto :find_similar
if /i "%~1"=="report" goto :generate_report
if /i "%~1"=="list" goto :list_errors
if /i "%~1"=="show" goto :show_error
if /i "%~1"=="help" goto :show_help

echo [错误] 未知命令: %~1
goto :show_help

:record_error
python %PYTHON_SCRIPT% -c "
import sys
sys.path.insert(0, r'%SCRIPT_DIR%')
from self_correction import record_error
error = record_error(
    error_type='%~2' or 'unknown',
    message='%~3' or 'No message provided',
    tool='%~4' or 'unknown',
    operation='%~5' or 'unknown',
    severity='%~6' or 'medium'
)
print(f'错误已记录: {error.id}')
"
goto :end

:record_fix
if "%~2"=="" (
    echo [错误] 请提供错误ID
    echo 用法: self-correction fix ^<error_id^> ^<solution^> ^<action^>
    goto :end
)
echo 记录修复方案...
python %PYTHON_SCRIPT% -c "
import sys
sys.path.insert(0, r'%SCRIPT_DIR%')
from self_correction import record_fix
result = record_fix(
    error_id='%~2',
    solution='%~3' or 'Fixed',
    action_taken='%~4' or 'Action taken'
)
if result:
    print(f'修复已记录: {result.id}')
else:
    print('错误ID不存在')
"
goto :end

:check_task
if "%~2"=="" (
    echo [错误] 请提供工具名
    echo 用法: self-correction check ^<tool^> [operation]
    goto :end
)
python %PYTHON_SCRIPT% -c "
import sys
import json
sys.path.insert(0, r'%SCRIPT_DIR%')
from self_correction import check_task
result = check_task('%~2', '%~3' or 'unknown')
print(f\"工具: %~2\")
print(f\"历史错误: {result['history_count']}\")
if result['warning']:
    print(f\"警告: {result['warning']}\")
if result['prevention_tips']:
    print(\"\\n预防建议:\")
    for tip in result['prevention_tips'][:5]:
        print(f\"  - {tip}\")
"
goto :end

:find_similar
python %PYTHON_SCRIPT% -c "
import sys
sys.path.insert(0, r'%SCRIPT_DIR%')
from self_correction import find_similar
errors = find_similar(error_type='%~2' or None, limit=5)
print(f\"找到 {len(errors)} 个相似错误\\n\")
for e in errors:
    print(f\"ID: {e['id']}\")
    print(f\"  类型: {e['error_type']}\")
    print(f\"  消息: {e['message'][:60]}...\")
    print(f\"  相似度: {e.get('_similarity_score', 0)}\")
    print()
"
goto :end

:generate_report
echo 生成周错误报告...
python %PYTHON_SCRIPT% -c "
import sys
sys.path.insert(0, r'%SCRIPT_DIR%')
from self_correction import generate_weekly_report
report = generate_weekly_report()
print('报告内容:')
print('=' * 50)
print(report[:2000])
print('...')
print('=' * 50)
print('\\n完整报告已保存到 ~/.claude/memory-bank/stats/')
"
goto :end

:list_errors
python %PYTHON_SCRIPT% -c "
import json
from pathlib import Path
errors_dir = Path.home() / '.claude/memory-bank/errors'
index_file = errors_dir / 'index.json'
if index_file.exists():
    with open(index_file, 'r', encoding='utf-8') as f:
        index = json.load(f)
    print(f\"总错误数: {index['stats']['total_errors']}\")
    print(f\"已修复: {index['stats']['total_fixed']}\")
    print('\\n最近错误:')
    for e in index['recent_errors'][:10]:
        print(f\"  {e['id']} [{e['severity']}] {e['error_type']}\")
else:
    print('暂无错误记录')
"
goto :end

:show_error
if "%~2"=="" (
    echo [错误] 请提供错误ID
    echo 用法: self-correction show ^<error_id^>
    goto :end
)
python %PYTHON_SCRIPT% -c "
import sys
sys.path.insert(0, r'%SCRIPT_DIR%')
from self_correction import ExperienceQuery
query = ExperienceQuery()
error = query.get_error_by_id('%~2')
if error:
    print(f\"ID: {error['id']}\")
    print(f\"时间: {error['timestamp']}\")
    print(f\"类型: {error['error_type']}\")
    print(f\"严重级别: {error['severity']}\")
    print(f\"消息: {error['message']}\")
    if error.get('root_cause'):
        print(f\"\\n根因: {error['root_cause']}\")
    if error.get('fix'):
        print(f\"\\n修复方案: {error['fix']['solution']}\")
else:
    print('错误未找到')
"
goto :end

:show_help
echo 用法: self-correction ^<command^> [args...]
echo.
echo 可用命令:
echo   record ^<type^> ^<message^> ^<tool^> ^<operation^> [severity]
echo     记录一个新错误
echo     示例: self-correction record api_error "Timeout" WebFetch "fetch page"
echo.
echo   fix ^<error_id^> ^<solution^> ^<action^>
echo     记录修复方案
echo     示例: self-correction fix 2026-03-17-001 "Add retry" "Implemented retry"
echo.
echo   check ^<tool^> [operation]
echo     任务前检查历史错误
echo     示例: self-correction check WebFetch "fetch page"
echo.
echo   find [error_type]
echo     查找相似错误
echo     示例: self-correction find api_error
echo.
echo   report
echo     生成周错误报告
echo.
echo   list
echo     列出最近错误
echo.
echo   show ^<error_id^>
echo     显示错误详情
echo     示例: self-correction show 2026-03-17-001
echo.
echo   help
echo     显示此帮助信息
echo.

:end
