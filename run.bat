@echo off
setlocal

:: ���õ�ǰĿ¼�µ� Python38 ·��
set PYTHON_DIR=%~dp0Python38

:: ��� python.exe �Ƿ����
if not exist "%PYTHON_DIR%\python.exe" (
    echo Error: python.exe not found in %PYTHON_DIR%
    pause
    exit /b 1
)

:: ���� gui.py
"%PYTHON_DIR%\python.exe" "%~dp0gui.py"

pause