@echo off
title AUTO RALLY SA HAI ME THANH - GOLDRUSH
cd /d "%~dp0"

python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [LOI] Khong tim thay Python tren may cua ban!
    echo Vui long chay file 'cai_dat.bat' truoc de duoc huong dan.
    echo.
    pause
    exit /b 1
)

echo ========================================================
echo   KHOI DONG AUTO RALLY - SA HAI ME THANH (GOLDRUSH)
echo   Phim tat:
echo     - [Ctrl + Q] : Bat / Tam dung
echo     - [ESC]      : Dung va thoat
echo ========================================================
python auto_rally.py
if %errorlevel% neq 0 (
    echo.
    echo Tool da dung lai hoac gap su co.
)
pause
