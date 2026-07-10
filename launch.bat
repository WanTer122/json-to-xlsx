@echo off
cd /d "%~dp0"

for /d %%i in ("%LOCALAPPDATA%\Python\pythoncore-*") do (
    if exist "%%i\pythonw.exe" (
        "%%i\pythonw.exe" "%~dp0app.py"
        exit /b 0
    )
)

where pythonw >nul 2>&1
if %errorlevel%==0 (
    pythonw "%~dp0app.py"
    exit /b 0
)

where python >nul 2>&1
if %errorlevel%==0 (
    python "%~dp0app.py"
    exit /b 0
)

mshta "javascript:alert('未找到 Python，请先安装 Python 3。');close()"
exit /b 1
