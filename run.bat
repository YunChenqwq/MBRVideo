@echo off
setlocal

:: 设置当前目录下的 Python38 路径
set PYTHON_DIR=%~dp0Python38

:: 检查 python.exe 是否存在
if not exist "%PYTHON_DIR%\python.exe" (
    echo Error: python.exe not found in %PYTHON_DIR%
    pause
    exit /b 1
)

:: 运行 gui.py
"%PYTHON_DIR%\python.exe" "%~dp0gui.py"

pause