@echo off
echo ========================================
echo    X Nova Quotation - Auto Updater (Win)
echo ========================================
echo.

cd /d "%~dp0"

echo [1/4] Activating Virtual Environment...
if not exist "venv_win" (
    echo Setting up Windows Python environment...
    python -m venv venv_win
)
call venv_win\Scripts\activate.bat

echo [2/4] Installing PyInstaller...
pip install pyinstaller

echo [3/4] Rebuilding App via PyInstaller...
rmdir /s /q build
rmdir /s /q dist
pyinstaller --name "X Nova Quotation" ^
            --windowed ^
            --icon "assets\favicon.ico" ^
            --add-data "assets;assets" ^
            --add-data "fonts;fonts" ^
            --add-data "client_secret.json;." ^
            --add-data "sheets_sync.py;." ^
            --noconfirm app.py

echo [4/4] Update Complete!
echo.
echo Launching App...
start "" "dist\X Nova Quotation\X Nova Quotation.exe"

timeout /t 3
exit
