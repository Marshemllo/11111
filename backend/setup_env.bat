@echo off
chcp 65001 >nul
echo ========================================
echo    智能数据分析平台 - 环境配置
echo ========================================
echo.

REM 检查Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] 未找到Python，请先安装Python 3.10+
    pause
    exit /b 1
)

echo [INFO] Python版本:
python --version
echo.

REM 创建虚拟环境
if not exist "venv" (
    echo [INFO] 创建虚拟环境...
    python -m venv venv
    echo [OK] 虚拟环境创建成功
) else (
    echo [INFO] 虚拟环境已存在
)

REM 激活虚拟环境
echo [INFO] 激活虚拟环境...
call venv\Scripts\activate.bat

REM 升级pip
echo [INFO] 升级pip...
python -m pip install --upgrade pip

REM 安装依赖
echo [INFO] 安装项目依赖...
pip install -r requirements.txt

REM 创建必要目录
echo [INFO] 创建必要目录...
if not exist "uploads" mkdir uploads
if not exist "reports" mkdir reports
if not exist "logs" mkdir logs

REM 复制环境配置文件
if not exist ".env" (
    if exist ".env.example" (
        echo [INFO] 创建环境配置文件...
        copy .env.example .env
        echo [WARN] 请编辑 .env 文件配置数据库和API密钥
    )
)

echo.
echo ========================================
echo    环境配置完成！
echo ========================================
echo.
echo 下一步操作:
echo 1. 编辑 .env 文件，配置数据库连接和API密钥
echo 2. 确保MySQL数据库已启动
echo 3. 运行 start.bat 启动后端服务
echo.
pause
