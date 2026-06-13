import re

with open("app.py", "r") as f:
    content = f.read()

# Fix tttk
content = content.replace("tttk.", "ttk.")

# Move _APP_BG definition before line 569
# Right now, root.configure is at 569, and is_dark_mode check is at 578.
# We will move the is_dark_mode block to before root.configure.

is_dark_mode_block = """is_dark_mode = False
try:
    result = subprocess.run(['defaults', 'read', '-g', 'AppleInterfaceStyle'], capture_output=True, text=True, timeout=1)
    is_dark_mode = 'Dark' in result.stdout
except:
    pass

_APP_BG = '#2b2b2b' if is_dark_mode else '#f0f0f0'
_FG = 'white' if is_dark_mode else 'black'
"""

# Remove existing is_dark_mode block
content = re.sub(r"is_dark_mode = False.*?except:\n    pass\n", "", content, flags=re.DOTALL)
content = content.replace("_APP_BG = '#2b2b2b' if is_dark_mode else '#f0f0f0'\n_FG = 'white' if is_dark_mode else 'black'\n", "")

# Insert it before root = tk.Tk()
insert_pos = content.find("root = tk.Tk()")
content = content[:insert_pos] + is_dark_mode_block + "\n" + content[insert_pos:]

with open("app.py", "w") as f:
    f.write(content)

print("Done")
