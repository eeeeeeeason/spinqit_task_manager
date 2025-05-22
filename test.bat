
@echo off
setlocal enabledelayedexpansion

python --version
echo %errorlevel%
if %errorlevel% equ 0 (
    echo 检测到python，继续安装...
    :: 执行安装脚本
    pip install spinqit_task_manager
    if %errorlevel% neq 0 (
        echo 安装 spinqit_task_manager 失败，请检查网络或pip配置。
        pause
        exit /b 1
    )
    else (
        echo 安装完成！
        pause
        exit /b 0
    )
) else (
    echo 没有检测到合适的Python环境，请安装Python 3.10+。
    echo 请访问 https://www.python.org/downloads/ 下载并安装。
)
pause