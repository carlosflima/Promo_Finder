@echo off
setlocal
cd /d "%~dp0"
title Promo Finder
where python >nul 2>nul
if errorlevel 1 (
  echo [ERRO] Python nao encontrado. Instale Python 3.10+ e marque Add Python to PATH.
  pause
  exit /b 1
)
if not exist "venv\Scripts\activate.bat" python -m venv venv
call venv\Scripts\activate.bat
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
start "" cmd /c "timeout /t 3 >nul && start http://127.0.0.1:5000"
python app.py
pause
