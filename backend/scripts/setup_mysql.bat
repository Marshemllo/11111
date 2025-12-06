@echo off
chcp 65001 >nul
echo ============================================
echo 智能数据分析平台 - MySQL数据库设置
echo ============================================
echo.

set /p MYSQL_PASSWORD=请输入MySQL root密码: 

echo.
echo 正在创建数据库...
mysql -u root -p%MYSQL_PASSWORD% -e "CREATE DATABASE IF NOT EXISTS data_platform DEFAULT CHARACTER SET utf8mb4 DEFAULT COLLATE utf8mb4_unicode_ci;"

if %errorlevel% neq 0 (
    echo 创建数据库失败，请检查MySQL密码是否正确
    pause
    exit /b 1
)

echo 数据库创建成功!
echo.
echo 正在初始化表结构...

cd /d %~dp0..
call venv\Scripts\activate
python scripts\init_db.py

echo.
echo ============================================
echo 设置完成!
echo ============================================
echo.
echo 请更新 .env 文件中的数据库密码:
echo DB_PASSWORD=%MYSQL_PASSWORD%
echo.
pause
