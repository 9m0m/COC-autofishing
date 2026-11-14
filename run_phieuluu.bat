@echo off
title AUTO PHIEU LUU CO VAT - CLASH OF CRITTERS
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
echo   KHOI DONG AUTO PHIEU LUU CO VAT (RELIC ADVENTURE)
echo   Game: Clash of Critters
echo   Phim tat:
echo     - [Ctrl + Q] : Bat / Tam dung (Pause / Resume)
echo     - [ESC]      : Dung va thoat an toan
echo ========================================================
python auto_phieuluu.py
if %errorlevel% neq 0 (
    echo.
    echo Tool da dung lai hoac gap su co.
)
pause
