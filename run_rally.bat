@echo off
title AUTO RALLY SA HAI ME THANH - GOLDRUSH
cd /d "%~dp0"

echo ========================================================
echo   KHOI DONG AUTO RALLY - SA HAI ME THANH (GOLDRUSH)
echo   Phim tat:
echo     - [Ctrl + Q] : Bat dau / Tiep tuc chay
echo     - [ESC]      : Tam dung (lan 1) / Thoat (lan 2)
echo ========================================================

if exist "dist\auto_rally.exe" (
    echo [RUN] Chay ban dong goi san dist\auto_rally.exe...
    "dist\auto_rally.exe"
    goto end
)

python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [LOI] Khong tim thay Python tren may cua ban!
    echo Vui long chay file 'cai_dat.bat' hoac su dung file 'dist\auto_rally.exe'.
    echo.
    pause
    exit /b 1
)

python auto_rally.py

:end
if %errorlevel% neq 0 (
    echo.
    echo Tool da dung lai hoac gap su co.
)
pause
