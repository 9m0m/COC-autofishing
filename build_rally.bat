@echo off
title BUILD AUTO RALLY EXE
cd /d "%~dp0"

echo ========================================================
echo   BAT DAU DONG GOI AUTO RALLY BANG PYINSTALLER
echo ========================================================
pyinstaller auto_rally.spec --noconfirm
if %errorlevel% neq 0 (
    echo.
    echo [LOI] Dong goi that bai!
    pause
    exit /b 1
)

echo.
echo ========================================================
echo [THANH CONG] File exe da duoc tao tai: dist\auto_rally.exe
echo ========================================================
pause
