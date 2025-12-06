@echo off
chcp 65001 >nul
echo ========================================
echo    智能数据分析平台 - 前端服务
echo ========================================
echo.

REM 检查node_modules
if not exist "node_modules" (
    echo [INFO] 安装依赖...
    npm install
)

echo [INFO] 启动前端服务...
echo [INFO] 访问地址: http://localhost:5173
echo [INFO] 按 Ctrl+C 停止服务
echo.
npm run dev

pause
