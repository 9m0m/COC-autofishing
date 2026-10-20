@echo off
title CAI DAT THU VIEN CHO AUTO CAU CA
cd /d "%~dp0"

echo ========================================================
echo   KIEM TRA MOI TRUONG PYTHON...
echo ========================================================

python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [LOI] Khong tim thay Python tren may tinh cua ban!
    echo.
    echo Huong dan khac phuc:
    echo 1. Truy cap https://www.python.org/downloads/ va tai Python 3.10 tro len.
    echo 2. Khi cai dat, BAT BUOC phai tick vao o:
    echo    "[v] Add python.exe to PATH" o duoi cung truoc khi bam Install.
    echo 3. Sau khi cai xong, mo lai file cai_dat.bat nay.
    echo.
    pause
    exit /b 1
)

echo Python da san sang!
echo.
echo ========================================================
echo   DANG CAI DAT CAC THU VIEN CAN THIET (OPENCV, MSS, PYAUTOGUI)...
echo ========================================================
python -m pip install -r requirements.txt

if %errorlevel% neq 0 (
    echo.
    echo [CANH BAO] Co loi xay ra trong qua trinh cai dat thu vien.
    echo Vui long kiem tra ket noi mang va thu lai.
    pause
    exit /b 1
)

echo.
echo ========================================================
echo   CAI DAT HOAN TAT 100%!
echo.
echo   Cac buoc tiep theo:
echo   1. Mo gia lap (BlueStacks / LDPlayer) vao game va den ho cau.
echo   2. (Tuy chon) Chay file 'kiem_tra_vi_tri.bat' de kiem tra khung hinh.
echo   3. Chay file 'run_auto.bat' de bat dau cau ca tu dong!
echo ========================================================
pause
