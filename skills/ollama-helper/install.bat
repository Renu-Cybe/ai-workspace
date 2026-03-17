@echo off
chcp 65001 >nul
echo ==========================================
echo    Qwen 快捷命令安装工具
echo ==========================================
echo.

set "SOURCE_DIR=%USERPROFILE%\.claude\skills\ollama-helper"
set "TARGET_DIR=%USERPROFILE%\.local\bin"

if not exist "%TARGET_DIR%" (
    echo Creating %TARGET_DIR%...
    mkdir "%TARGET_DIR%"
)

echo Copying shortcuts...
copy /Y "%SOURCE_DIR%\qw.bat" "%TARGET_DIR%\qw.bat" >nul
copy /Y "%SOURCE_DIR%\qwa.bat" "%TARGET_DIR%\qwa.bat" >nul

echo.
echo ==========================================
echo    安装完成！
echo ==========================================
echo.
echo 现在你可以直接使用以下命令：
echo.
echo   qw list              - 列出可用模型
echo   qw chat "prompt"     - 与 Qwen 对话
echo   qw complete "code"   - 代码补全
echo   qw explain "code"    - 代码解释
echo   qw review file.py    - 代码审查
echo.
echo   qwa advise "task"    - 智能决策建议
echo   qwa review "code"    - 自动代码审查
echo   qwa complete "code"  - 自动代码补全
echo.
echo 注意：确保 %TARGET_DIR% 在你的 PATH 环境变量中
echo.
pause
