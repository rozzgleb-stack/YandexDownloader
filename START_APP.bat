@echo off
setlocal
chcp 65001 >nul
cd /d "%~dp0"
where py >nul 2>nul
if not errorlevel 1 (set "PY=py -3") else (set "PY=python")
%PY% --version >nul 2>nul
if errorlevel 1 (
  echo Python 3.10+ is required for source launch. Use the built EXE on computers without Python.
  pause
  exit /b 1
)
%PY% -c "import PIL" >nul 2>nul
if errorlevel 1 (
  echo Installing UI dependencies...
  %PY% -m pip install -r requirements.txt
  if errorlevel 1 (echo Could not install dependencies. & pause & exit /b 1)
)
%PY% app.pyw
if errorlevel 1 pause
