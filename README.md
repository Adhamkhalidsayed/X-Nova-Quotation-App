<h1 align="center">
  <img src="assets/logo.png" alt="X Nova Logo" width="120"/><br/>
  X Nova Quotation App
</h1>

<p align="center">
  A professional desktop quotation management tool for X Nova — built with Python, featuring Google Sheets cloud sync, branded PDF generation, and a full quotation history system.
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Platform-macOS%20%7C%20Windows-blue?style=flat-square"/>
  <img src="https://img.shields.io/badge/Python-3.9%2B-3776AB?style=flat-square&logo=python&logoColor=white"/>
  <img src="https://img.shields.io/badge/Google%20Sheets-Sync%20Enabled-34A853?style=flat-square&logo=google-sheets&logoColor=white"/>
  <img src="https://img.shields.io/badge/PDF-ReportLab-red?style=flat-square"/>
  <img src="https://img.shields.io/badge/License-Private-lightgrey?style=flat-square"/>
</p>

---

## ✨ Features

| Feature | Description |
|---|---|
| 📋 **Quotation Builder** | Select products by category, set quantities, discounts, and markups |
| 🖨️ **Branded PDF Export** | Generates professional A4 PDFs with the X Nova logo, Montserrat font, and company branding |
| 🔢 **Auto Quote Numbering** | Sequential quote numbers in `QT-YYYY-NNN` format, persisted across sessions |
| ☁️ **Google Sheets Sync** | Two-way sync of the product database and quotation history across all devices |
| 📜 **Quotation History** | Browse, re-open, and re-export all previously generated quotations |
| 🔍 **Product & Customer Search** | Live search bars for fast product lookup and customer filtering |
| 💾 **Offline Fallback** | Works fully offline using a local `database.json` cache when no internet is available |
| 🖥️ **Cross-Platform** | Runs natively on macOS and Windows with dedicated launchers |

---

## 📁 Project Structure

```
Quotation_App/
│
├── app.py                    # Main application (UI + PDF generation + logic)
├── sheets_sync.py            # Google Sheets sync module
│
├── Mac_Launcher.command      # One-click launcher for macOS
├── Windows_Launcher.bat      # One-click launcher for Windows
├── Update_App.command        # macOS auto-rebuild & reinstall script
├── Update_App_Windows.bat    # Windows auto-rebuild & reinstall script
│
├── assets/
│   ├── logo.png              # Light mode logo
│   ├── logo_dark.png         # Dark mode logo
│   ├── favicon.icns          # macOS app icon
│   ├── favicon.ico           # Windows app icon
│   └── bg_*.png              # UI background images
│
├── fonts/
│   ├── Montserrat-Regular.ttf
│   └── Montserrat-Bold.ttf
│
├── images/                   # Product images used in PDFs
├── Terms & Conditions.pptx   # Company T&C template
│
└── .gitignore                # Excludes secrets, builds, and user data
```

> **Note:** `client_secret.json`, `token.json`, `database.json`, `history.json`, `config.json`, and all generated PDFs are excluded from version control.

---

## 🚀 Getting Started

### Prerequisites

- **Python 3.9+** installed on your machine
  - macOS: Install via [Homebrew](https://brew.sh/) — `brew install python`
  - Windows: Download from [python.org](https://www.python.org/downloads/)
- A **Google Cloud Service Account** with access to the shared Google Sheet *(for cloud sync)*

### 🍎 macOS — Running from Source

1. Clone the repository:
   ```bash
   git clone https://github.com/Adhamkhalidsayed/X-Nova-Quotation-App.git
   cd X-Nova-Quotation-App
   ```

2. Place your `client_secret.json` Google credentials file in the project root.

3. Double-click **`Mac_Launcher.command`** in Finder.  
   *(It will automatically create a virtual environment and install all dependencies on the first run.)*

### 🪟 Windows — Running from Source

1. Clone the repository and place `client_secret.json` in the project root.

2. Double-click **`Windows_Launcher.bat`**.  
   *(It will automatically create a virtual environment and install all dependencies on the first run.)*

---

## 📦 Building a Standalone macOS App

To compile a standalone `.app` bundle (no Python required to run it):

```bash
# Option 1: Use the auto-updater script (recommended)
# Simply double-click Update_App.command in Finder

# Option 2: Manual build
source venv_mac/bin/activate
pyinstaller --name "X Nova Quotation" \
            --windowed \
            --icon "assets/favicon.icns" \
            --add-data "assets:assets" \
            --add-data "fonts:fonts" \
            --add-data "client_secret.json:." \
            --add-data "sheets_sync.py:." \
            --noconfirm app.py
```

The built app will appear in `dist/` and will also be auto-installed to `/Applications/X Nova Quotation.app`.

---

## ☁️ Google Sheets Sync Setup

The app can sync the product database and quotation history to a shared Google Sheet.

1. Create a **Google Cloud Service Account** and download the JSON key as `client_secret.json`.
2. Share your Google Sheet with the service account email (give **Editor** access).
3. Copy the **Sheet ID** from the URL: `https://docs.google.com/spreadsheets/d/<SHEET_ID>/edit`
4. On first launch, the app will prompt you to paste the Sheet ID, which is saved to `config.json`.

> The app gracefully falls back to a local `database.json` cache if the Google Sheet is unreachable.

---

## 🔄 Updating the App

After modifying `app.py` or any source file, rebuild and reinstall the `.app` bundle in one click:

- **macOS:** Double-click **`Update_App.command`** — it rebuilds, reinstalls to `/Applications`, and launches the new version automatically.
- **Windows:** Double-click **`Update_App_Windows.bat`** — same automated workflow.

---

## 🔐 Security & Privacy

The following files are **never committed to Git** and must be kept private:

| File | Contents |
|---|---|
| `client_secret.json` | Google Service Account credentials |
| `token.json` | OAuth access token |
| `database.json` | Local product database cache |
| `history.json` | Local quotation history |
| `config.json` | App settings (Sheet ID, quote counter) |
| `*.pdf` | Generated customer quotations |

---

## 🛠️ Tech Stack

| Component | Technology |
|---|---|
| UI Framework | [Tkinter](https://docs.python.org/3/library/tkinter.html) + TTK |
| PDF Generation | [ReportLab](https://www.reportlab.com/) + [PyPDF2](https://pypdf2.readthedocs.io/) |
| Image Handling | [Pillow (PIL)](https://pillow.readthedocs.io/) |
| Cloud Sync | [gspread](https://docs.gspread.org/) + Google Sheets API |
| App Packaging | [PyInstaller](https://pyinstaller.org/) |
| Typography | Montserrat (Google Fonts) |

---

## 📄 License

This is a **private internal tool** for X Nova. All rights reserved.  
Unauthorized distribution or use outside of X Nova is not permitted.

---

<p align="center">
  Built with ❤️ for <strong>X Nova</strong>
</p>
