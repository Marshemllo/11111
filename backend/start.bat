@echo off
chcp 65001 >nul
echo ========================================
echo    智能数据分析平台 - 后端服务
echo ========================================
echo.

REM 检查虚拟环境
if exist "venv\Scripts\activate.bat" (
    echo [INFO] 激活虚拟环境...
    call venv\Scripts\activate.bat
) else (
    echo [WARN] 虚拟环境不存在，使用系统Python
)

REM 检查依赖
echo [INFO] 检查依赖...
pip show fastapi >nul 2>&1
if errorlevel 1 (
    echo [INFO] 安装依赖...
    pip install -r requirements.txt
)

REM 启动服务
echo.
echo [INFO] 启动后端服务...
echo [INFO] API文档: http://localhost:8000/docs
echo [INFO] 按 Ctrl+C 停止服务
echo.
python run.py

pause
