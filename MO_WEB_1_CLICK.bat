@echo off
chcp 65001 >nul
title AgriBot AI Eco-Green - May Chu Cay Trong
color 0A

echo ====================================================================
echo   * DANG KHOI DONG HE THONG KHUYEN NGHI CAY TRONG AGRIBOT AI *
echo ====================================================================
echo [*] Dang khoi chay may chu localhost:5000...
echo [*] Trinh duyet se tu dong mo len man hinh sau 2 giay...
echo.

cd /d "%~dp0"

:: Kiem tra neu port 5000 da chay thi mo thang trinh duyet
netstat -ano | findstr :5000 | findstr LISTENING >nul
if %errorlevel% == 0 (
    echo [*] May chu da san sang! Dang mo trinh duyet...
    start http://127.0.0.1:5000
    exit /b
)

:: Mo trinh duyet sau 2 giay
start "" cmd /c "timeout /t 2 /nobreak >nul & start http://127.0.0.1:5000"

:: Khoi dong may chu Flask
python wsgi.py
