@echo off
title Development Server Launcher
echo Starting backend and frontend servers...

rem 启动后端服务
rem "title" 命令可以设置新窗口的标题，比 start 的第一个参数更可靠
start "Backend" cmd /k "title Backend Server && python backend\main.py"

rem 启动前端服务
rem 确保切换目录和运行开发服务是一个原子操作
start "Frontend" cmd /k "title Frontend Dev Server && cd /d frontend && npm run dev"

echo New windows have been opened for servers.