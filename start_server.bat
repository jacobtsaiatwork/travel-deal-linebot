@echo off
title 啟動 LINE Bot 伺服器
echo 正在啟動旅遊比價 LINE Bot 伺服器 (Port 8000)...
python -m uvicorn app.main:app --reload
pause
