@echo off
setlocal
chcp 65001 >nul
cd /d "%~dp0"
where py >nul 2>nul
if not errorlevel 1 (set "PY=py -3") else (set "PY=python")
%PY% --version >nul 2>nul
if errorlevel 1 (echo Python 3.10+ is required to build this EXE. & pause & exit /b 1)
%PY% -m pip install -r requirements.txt pyinstaller
if errorlevel 1 (echo Dependency installation failed. & pause & exit /b 1)
%PY% -m PyInstaller --noconfirm --clean --onefile --windowed --name "YandexDownloader32" --icon "app.ico" --add-data "app.ico;." --add-data "app.png;." --add-data "logo_header.png;." --add-data "completion.wav;." app.pyw
if errorlevel 1 (echo EXE build failed. & pause & exit /b 1)
echo.
echo Done: dist\YandexDownloader32.exe
pause
