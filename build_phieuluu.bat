@echo off
title DONG GOI AUTO PHIEU LUU CO VAT (.EXE)
cd /d "%~dp0"

echo Dang kiem tra PyInstaller...
pyinstaller --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [CANH BAO] Dang cai dat PyInstaller...
    pip install pyinstaller
)

echo Dang dong goi auto_phieuluu.exe...
pyinstaller auto_phieuluu.spec --noconfirm --clean

if %errorlevel% equ 0 (
    echo.
    echo ========================================================
    echo   DONG GOI THANH CONG!
    echo   File chay nam tai: dist\auto_phieuluu.exe
    echo ========================================================
) else (
    echo.
    echo [LOI] Qua trinh dong goi gap su co!
)
pause
