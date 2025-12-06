@echo off
chcp 65001 >nul
echo ========================================
echo    智能数据分析平台 - 一键启动
echo ========================================
echo.

echo [INFO] 启动后端服务...
start "Backend" cmd /k "cd /d %~dp0backend && start.bat"

timeout /t 3 /nobreak >nul

echo [INFO] 启动前端服务...
start "Frontend" cmd /k "cd /d %~dp0frontend && start.bat"

echo.
echo [OK] 服务已启动
echo.
echo 后端API: http://localhost:8000
echo 前端页面: http://localhost:5173
echo API文档: http://localhost:8000/docs
echo.
pause
