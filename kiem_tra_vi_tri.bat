@echo off
title KIEM TRA VI TRI CAN CHINH - AUTO CAU CA
cd /d "%~dp0"
echo ========================================================
echo   DANG KIEM TRA VI TRI NHAN DIEN TREN GIA LAP...
echo ========================================================
python test_preview.py
echo.
echo ========================================================
echo   Neu cac vong tron trum dung nut: Ban co the chay auto!
echo   Neu bi lech: Hay bao lai de tinh chinh nhe.
echo ========================================================
pause
