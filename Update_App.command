#!/bin/bash
set -e

# Change to the directory of this script
cd "$(dirname "$0")"

echo "========================================"
echo "   X Nova Quotation - Auto Updater"
echo "========================================"
echo ""

echo "[1/4] Activating Virtual Environment..."
source venv_mac/bin/activate

echo "[2/4] Rebuilding App via PyInstaller..."
rm -rf build dist
pyinstaller --name "X Nova Quotation" \
            --windowed \
            --icon "assets/favicon.icns" \
            --add-data "assets:assets" \
            --add-data "fonts:fonts" \
            --add-data "client_secret.json:." \
            --add-data "sheets_sync.py:." \
            --noconfirm app.py

echo "[3/4] Installing to /Applications..."
rm -rf "/Applications/X Nova Quotation.app"
cp -R "dist/X Nova Quotation.app" "/Applications/X Nova Quotation.app"

echo "[4/4] Removing Quarantine Flag..."
xattr -rd com.apple.quarantine "/Applications/X Nova Quotation.app"

echo ""
echo "========================================"
echo "   Update Complete!"
echo "========================================"
echo "Launching App..."
open "/Applications/X Nova Quotation.app"

# Optional: Close the terminal window after 3 seconds
sleep 3
osascript -e 'tell application "Terminal" to close (every window whose name contains "Update_App")' &
exit 0
