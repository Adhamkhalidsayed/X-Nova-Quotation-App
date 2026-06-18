"""
sheets_sync.py - Google Sheets synchronization module for X Nova Quotation App.

This module provides functions to read/write product data and quotation history
to a Google Sheet, enabling multi-device sync across the company.

Requirements:
    pip install gspread google-auth

Setup:
    1. Place credentials.json (Google Service Account key) in the app directory
    2. Set google_sheet_id and sync_enabled=true in config.json
    3. Share the Google Sheet with the service account email (Editor access)
"""

import json
import os
import sys
from pathlib import Path

# Track whether sync is available
_sync_available = False
_sheet = None
_drive_service = None
_config = {}

def get_resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

def get_data_path(filename):
    home = str(Path.home())
    if sys.platform == 'darwin':
        path = os.path.join(home, 'Library', 'Application Support', 'X Nova Quotation')
    elif sys.platform == 'win32':
        path = os.path.join(os.environ.get('APPDATA', home), 'X Nova Quotation')
    else:
        path = os.path.join(home, '.xnova_quotation')
    os.makedirs(path, exist_ok=True)
    return os.path.join(path, filename)

try:
    import gspread
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from googleapiclient.discovery import build
    from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload
    import io
    _gspread_installed = True
except ImportError:
    _gspread_installed = False



def _load_config():
    """Load sync configuration from config.json."""
    global _config
    config_path = get_data_path("config.json")
    if os.path.exists(config_path):
        with open(config_path, "r") as f:
            _config = json.load(f)
    return _config


def init_sync():
    """
    Initialize the Google Sheets connection using OAuth 2.0.
    Returns True if sync is ready, False otherwise.
    """
    global _sync_available, _sheet

    config = _load_config()

    if not config.get("sync_enabled", False):
        print("[Sync] Disabled in config.json")
        return False

    if not _gspread_installed:
        print("[Sync] google-auth-oauthlib not installed.")
        return False

    client_secret_path = get_resource_path("client_secret.json")
    if not os.path.exists(client_secret_path):
        print("[Sync] client_secret.json not found. Please download your OAuth Client ID.")
        return False

    sheet_id = config.get("google_sheet_id", "")
    if not sheet_id:
        print("[Sync] google_sheet_id not set in config.json")
        return False

    try:
        scopes = [
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive"
        ]
        
        creds = None
        token_path = get_data_path('token.json')
        
        # Load cached credentials if they exist
        if os.path.exists(token_path):
            creds = Credentials.from_authorized_user_file(token_path, scopes)
            
        # If no valid credentials, let the user log in
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(client_secret_path, scopes)
                creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open(token_path, 'w') as token:
                token.write(creds.to_json())

        client = gspread.authorize(creds)
        _sheet = client.open_by_key(sheet_id)
        
        global _drive_service
        _drive_service = build('drive', 'v3', credentials=creds)
        
        folder_id = config.get("drive_images_folder_id", "")
        if not folder_id:
            file_metadata = {
                'name': 'Quotation App Images',
                'mimeType': 'application/vnd.google-apps.folder'
            }
            folder = _drive_service.files().create(body=file_metadata, fields='id').execute()
            folder_id = folder.get('id')
            config["drive_images_folder_id"] = folder_id
            config_path = get_data_path("config.json")
            with open(config_path, "w") as f:
                json.dump(config, f, indent=4)
            print(f"[Sync] Created Google Drive folder 'Quotation App Images' with ID: {folder_id}")

        _sync_available = True
        print("[Sync] Connected to Google Sheets and Drive successfully!")
        return True
    except Exception as e:
        print(f"[Sync] Failed to connect: {e}")
        _sync_available = False
        return False


def is_sync_available():
    """Check if sync is currently active."""
    return _sync_available


# ===================== PRODUCTS =====================

def load_products_from_sheet():
    """
    Load product database from the 'Products' worksheet.
    Returns a dict in the same format as database.json:
    {
        "Category Name": [
            {"name": "...", "desc": "...", "price": "$XX", "image": "..."},
            ...
        ]
    }
    """
    if not _sync_available:
        return None

    try:
        ws = _sheet.worksheet("Products")
        rows = ws.get_all_records()  # Returns list of dicts from header row

        products = {}
        for row in rows:
            cat = row.get("Category", "").strip()
            if not cat:
                continue
            if cat not in products:
                products[cat] = []
            products[cat].append({
                "name": row.get("Name", ""),
                "desc": row.get("Description", ""),
                "price": row.get("Price", ""),
                "image": row.get("Image", "")
            })
        return products
    except Exception as e:
        print(f"[Sync] Error loading products: {e}")
        return None


def save_products_to_sheet(products_db):
    """
    Write the entire product database to the 'Products' worksheet.
    Clears existing data and rewrites everything.
    """
    if not _sync_available:
        return False

    try:
        ws = _sheet.worksheet("Products")
        ws.clear()

        # Write header
        header = ["Category", "Name", "Description", "Price", "Image"]
        rows = [header]

        for category, products in products_db.items():
            for p in products:
                rows.append([
                    category,
                    p.get("name", ""),
                    p.get("desc", ""),
                    p.get("price", ""),
                    p.get("image", "")
                ])

        if len(rows) > 1:
            ws.update(range_name=f"A1:E{len(rows)}", values=rows)

        print(f"[Sync] Products synced ({len(rows)-1} products)")
        return True
    except Exception as e:
        print(f"[Sync] Error saving products: {e}")
        return False


# ===================== USERS =====================

def load_users_from_sheet():
    """
    Load users from the 'Users' worksheet.
    Returns a list of dicts: [{'username': '...', 'password_hash': '...', 'role': '...'}]
    """
    if not _sync_available:
        return None

    try:
        ws = _sheet.worksheet("Users")
        rows = ws.get_all_records()
        
        users = []
        for row in rows:
            username = row.get("Username", "").strip()
            if not username:
                continue
            users.append({
                "username": username,
                "password_hash": row.get("Password Hash", ""),
                "role": row.get("Role", "user")
            })
        return users
    except Exception as e:
        print(f"[Sync] Error loading users: {e}")
        return None

def save_users_to_sheet(users_list):
    """
    Write the users list to the 'Users' worksheet.
    """
    if not _sync_available:
        return False

    try:
        ws = _sheet.worksheet("Users")
        ws.clear()

        header = ["Username", "Password Hash", "Role"]
        rows = [header]

        for u in users_list:
            rows.append([
                u.get("username", ""),
                u.get("password_hash", ""),
                u.get("role", "user")
            ])

        if len(rows) > 1:
            ws.update(range_name=f"A1:C{len(rows)}", values=rows)

        print(f"[Sync] Users synced ({len(rows)-1} users)")
        return True
    except Exception as e:
        print(f"[Sync] Error saving users: {e}")
        return False

# ===================== HISTORY =====================

def load_history_from_sheet():
    """
    Load quotation history from the 'History' worksheet.
    Returns a list in the same format as history.json.
    """
    if not _sync_available:
        return None

    try:
        ws = _sheet.worksheet("History")
        rows = ws.get_all_records()

        history = []
        for row in rows:
            items_json = row.get("Items JSON", "{}")
            try:
                items = json.loads(items_json)
            except (json.JSONDecodeError, TypeError):
                items = {}

            history.append({
                "id": row.get("ID", ""),
                "date": row.get("Date", ""),
                "client_name": row.get("Client Name", ""),
                "client_location": row.get("Location", ""),
                "revision_version": row.get("Version", ""),
                "items": items
            })
        return history
    except Exception as e:
        print(f"[Sync] Error loading history: {e}")
        return None


def save_history_to_sheet(history_list):
    """
    Write the entire history list to the 'History' worksheet.
    Clears existing data and rewrites everything.
    """
    if not _sync_available:
        return False

    try:
        ws = _sheet.worksheet("History")
        ws.clear()

        header = ["ID", "Date", "Client Name", "Location", "Version", "Items JSON"]
        rows = [header]

        for entry in history_list:
            rows.append([
                entry.get("id", ""),
                entry.get("date", ""),
                entry.get("client_name", ""),
                entry.get("client_location", ""),
                entry.get("revision_version", ""),
                json.dumps(entry.get("items", {}))
            ])

        if len(rows) > 1:
            ws.update(range_name=f"A1:F{len(rows)}", values=rows)

        print(f"[Sync] History synced ({len(rows)-1} entries)")
        return True
    except Exception as e:
        print(f"[Sync] Error saving history: {e}")
        return False


# ===================== IMAGES (DRIVE) =====================

def get_remote_images():
    """Returns a dict of {filename: file_id} from Google Drive."""
    folder_id = _config.get("drive_images_folder_id")
    if not folder_id or not _drive_service:
        return {}
        
    results = _drive_service.files().list(
        q=f"'{folder_id}' in parents and trashed=false",
        fields="files(id, name)",
        pageSize=1000
    ).execute()
    return {f['name']: f['id'] for f in results.get('files', [])}


def sync_images_up():
    """Upload missing local images to Google Drive."""
    if not _sync_available or not _drive_service:
        return
        
    folder_id = _config.get("drive_images_folder_id")
    if not folder_id:
        return
        
    images_dir = get_data_path("images")
    if not os.path.exists(images_dir):
        os.makedirs(images_dir)
        
    remote_images = get_remote_images()
    local_images = [f for f in os.listdir(images_dir) if os.path.isfile(os.path.join(images_dir, f))]
    
    uploaded_count = 0
    for local_file in local_images:
        if local_file not in remote_images and not local_file.startswith('.'):
            file_path = os.path.join(images_dir, local_file)
            file_metadata = {
                'name': local_file,
                'parents': [folder_id]
            }
            media = MediaFileUpload(file_path, resumable=True)
            _drive_service.files().create(body=file_metadata, media_body=media, fields='id').execute()
            uploaded_count += 1
            print(f"[Sync] Uploaded image: {local_file}")
            
    if uploaded_count > 0:
        print(f"[Sync] Finished uploading {uploaded_count} images.")


def sync_images_down():
    """Download missing remote images from Google Drive."""
    if not _sync_available or not _drive_service:
        return
        
    images_dir = get_data_path("images")
    if not os.path.exists(images_dir):
        os.makedirs(images_dir)
        
    remote_images = get_remote_images()
    local_images = [f for f in os.listdir(images_dir) if os.path.isfile(os.path.join(images_dir, f))]
    
    downloaded_count = 0
    for filename, file_id in remote_images.items():
        if filename not in local_images:
            request = _drive_service.files().get_media(fileId=file_id)
            file_path = os.path.join(images_dir, filename)
            
            with io.FileIO(file_path, 'wb') as fh:
                downloader = MediaIoBaseDownload(fh, request)
                done = False
                while done is False:
                    status, done = downloader.next_chunk()
            downloaded_count += 1
            print(f"[Sync] Downloaded image: {filename}")
            
    if downloaded_count > 0:
        print(f"[Sync] Finished downloading {downloaded_count} images.")


def sync_all(products_db, history_list, users_list=None):
    """
    Full sync: push local data to Google Sheets and Drive.
    Returns (products_ok, history_ok, users_ok) tuple.
    """
    if not _sync_available:
        return False, False, False

    p = save_products_to_sheet(products_db)
    h = save_history_to_sheet(history_list)
    u = False
    if users_list is not None:
        u = save_users_to_sheet(users_list)
    sync_images_up()
    return p, h, u


def pull_all():
    """
    Pull all data from Google Sheets and Drive.
    Returns (products_dict, history_list, users_list) or (None, None, None) on failure.
    """
    if not _sync_available:
        return None, None, None

    products = load_products_from_sheet()
    history = load_history_from_sheet()
    users = load_users_from_sheet()
    sync_images_down()
    return products, history, users
