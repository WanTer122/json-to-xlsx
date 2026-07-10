@echo off
chcp 65001 >nul
cd /d "%~dp0"

echo ========================================
echo   JSON转Excel — 打包为 exe
echo ========================================
echo.

for /f "delims=" %%P in ('where py 2^>nul') do (
    set "PY=%%P"
    goto :found_py
)
where python >nul 2>&1
if %errorlevel%==0 (
    set "PY=python"
    goto :found_py
)
echo [错误] 未找到 Python，请先安装 Python 3.10 或更高版本。
pause
exit /b 1

:found_py
echo [1/3] 安装/更新依赖...
"%PY%" -m pip install -r requirements.txt pyinstaller --quiet
if %errorlevel% neq 0 (
    echo [错误] 依赖安装失败。
    pause
    exit /b 1
)

echo [2/3] 开始打包（约 1-3 分钟）...
"%PY%" -m PyInstaller --noconfirm --clean json-to-xlsx.spec
if %errorlevel% neq 0 (
    echo [错误] 打包失败。
    pause
    exit /b 1
)

echo [3/3] 打包完成！
echo.
echo 输出目录: %~dp0dist\JSON转Excel\
echo 将 dist\JSON转Excel 整个文件夹压缩后分享即可。
echo.
pause
