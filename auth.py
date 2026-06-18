import hashlib
import json
import os
import sys
from pathlib import Path

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

def hash_password(password):
    """Securely hash a password using SHA-256."""
    return hashlib.sha256(password.encode('utf-8')).hexdigest()

def verify_password(password, hashed):
    """Verify a password against a hash."""
    return hash_password(password) == hashed

def load_local_users():
    """Load users from the local cache file."""
    users_path = get_data_path('users.json')
    if os.path.exists(users_path):
        try:
            with open(users_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"[Auth] Error loading users: {e}")
    
    # Return default admin if no file exists
    return [
        {
            "username": "admin",
            "password_hash": hash_password("admin123"),
            "role": "admin"
        }
    ]

def save_local_users(users):
    """Save users to the local cache file."""
    users_path = get_data_path('users.json')
    try:
        with open(users_path, 'w') as f:
            json.dump(users, f, indent=4)
        return True
    except Exception as e:
        print(f"[Auth] Error saving users: {e}")
        return False
