import os
import re

APP_PY = "app.py"
SYNC_PY = "sheets_sync.py"

header = """import os
import sys
from pathlib import Path

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
"""

def patch_file(filepath, is_app):
    with open(filepath, "r") as f:
        content = f.read()

    if "get_resource_path" in content:
        print(f"{filepath} already patched.")
        return

    # Replace "assets/..." and "fonts/..." with get_resource_path("assets/...")
    # Using regex to find strings starting with assets/ or fonts/
    content = re.sub(r'("|\')(assets/[^"\']+)("|\')', r'get_resource_path(\1\2\3)', content)
    content = re.sub(r'("|\')(fonts/[^"\']+)("|\')', r'get_resource_path(\1\2\3)', content)
    
    # Replace data json files
    content = re.sub(r'("|\')(database\.json)("|\')', r'get_data_path(\1\2\3)', content)
    content = re.sub(r'("|\')(history\.json)("|\')', r'get_data_path(\1\2\3)', content)
    content = re.sub(r'("|\')(config\.json)("|\')', r'get_data_path(\1\2\3)', content)
    content = re.sub(r'("|\')(token\.json)("|\')', r'get_data_path(\1\2\3)', content)
    content = re.sub(r'("|\')(client_secret\.json)("|\')', r'get_resource_path(\1\2\3)', content)

    # Insert header after imports
    if is_app:
        lines = content.split('\n')
        insert_idx = 0
        for i, line in enumerate(lines):
            if "import sheets_sync" in line:
                insert_idx = i + 1
                break
        lines.insert(insert_idx, "\n" + header + "\n")
        content = '\n'.join(lines)
    else:
        lines = content.split('\n')
        insert_idx = 0
        for i, line in enumerate(lines):
            if "from google.oauth2.credentials" in line:
                insert_idx = i + 1
                break
        lines.insert(insert_idx, "\n" + header + "\n")
        content = '\n'.join(lines)

    with open(filepath, "w") as f:
        f.write(content)
    print(f"{filepath} patched successfully.")

patch_file(APP_PY, True)
patch_file(SYNC_PY, False)
