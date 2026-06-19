#!/bin/bash
echo "Starting X Nova Quotation Generator..."
cd "$(dirname "$0")"

if [ ! -d "venv_mac" ]; then
    echo "Setting up Mac Python environment..."
    if [ -x "/opt/homebrew/bin/python3" ]; then
        /opt/homebrew/bin/python3 -m venv venv_mac
    elif [ -x "/usr/local/bin/python3" ]; then
        /usr/local/bin/python3 -m venv venv_mac
    else
        python3 -m venv venv_mac
    fi
fi

source venv_mac/bin/activate
echo "Verifying dependencies..."
pip install reportlab pypdf2 pillow gspread google-auth google-auth-oauthlib google-api-python-client pymupdf

# Run the app in the foreground
python3 app.py
