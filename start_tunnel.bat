@echo off
title LINE 專用 HTTPS 通道 (請勿關閉此視窗)
color 0A
cls
echo ================================================================
echo   【重要提醒】
echo   1. 請「保持這個視窗開啟」，縮小即可，千萬不要關閉！
echo      若關閉此視窗，通道會立即斷線並顯示「no tunnel here」。
echo   2. 每次重新開啟此視窗，網址都會重新產生，
echo      請務必使用最新產生的那組網址。
echo ================================================================
echo.
echo 正在建立安全通道，請稍候 3 秒...
echo.

ssh -o StrictHostKeyChecking=no -o ServerAliveInterval=10 -o ServerAliveCountMax=6 -R 80:127.0.0.1:8000 nokey@localhost.run

echo.
echo ================================================================
echo 通道已離線。請檢查網路或按任意鍵重新啟動...
echo ================================================================
pause
