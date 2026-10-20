@echo off
title AUTO CAU CA DA GIA LAP
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
echo   KHOI DONG AUTO CAU CA (BẢN V12)
echo   Luu y: Nhan giu phim 'q' de dung bat ky luc nao.
echo ========================================================
python auto_cauca.py
if %errorlevel% neq 0 (
    echo.
    echo Tool da dung lai hoac gap su co.
)
pause
