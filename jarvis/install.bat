@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo === J.A.R.V.I.S. o'rnatilmoqda ===
where python >nul 2>nul
if errorlevel 1 (
  echo Python topilmadi. https://www.python.org/downloads/ dan Python 3.11+ o'rnating
  echo va o'rnatishda "Add python.exe to PATH" belgisini qo'ying.
  pause
  exit /b 1
)
python -m venv .venv
call .venv\Scripts\activate.bat
python -m pip install --upgrade pip
pip install -r requirements.txt
if not exist .env copy .env.example .env >nul
echo.
echo Tayyor! Endi .env faylini Bloknotda ochib, API kalitingizni yozing.
notepad .env
echo So'ng start.bat ni ikki marta bosing.
pause
