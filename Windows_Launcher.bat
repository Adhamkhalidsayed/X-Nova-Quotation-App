@echo off
echo Starting X Nova Quotation Generator...
cd /d "%~dp0"

REM Check if a Windows virtual environment exists (kept separate from Mac's 'venv')
if not exist "venv_win" (
    echo Setting up Windows Python environment...
    python -m venv venv_win
)
call venv_win\Scripts\activate.bat
echo Verifying dependencies...
pip install reportlab pypdf2 pillow gspread google-auth google-auth-oauthlib google-api-python-client pymupdf


REM Run the app in the foreground to see any errors
python app.py
pause
