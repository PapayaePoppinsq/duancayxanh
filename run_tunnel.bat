@echo off
title Cloudflare Tunnel - AgriBot AI Eco-Green
echo ================================================================
echo   🌾 KHOI DONG DUONG HAM CLOUDFLARE TUNNEL - AGRIBOT AI 🌾
echo ================================================================
echo [*] Dang ket noi may chu localhost:5000 toi mang toan cau Cloudflare...
echo [*] Duong link cong khai se hien thi ben duoi trong vai giay.
echo [*] Gui link do cho bat ky ai tren the gioi de ho truy cap vao web!
echo ================================================================
echo.
"%~dp0cloudflared.exe" tunnel --url http://localhost:5000
pause
