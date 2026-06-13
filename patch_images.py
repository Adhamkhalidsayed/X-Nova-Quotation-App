import os

with open("sheets_sync.py", "r") as f:
    content = f.read()
    
content = content.replace('os.path.join(os.path.dirname(os.path.abspath(__file__)), "images")', 'get_data_path("images")')

with open("sheets_sync.py", "w") as f:
    f.write(content)

with open("app.py", "r") as f:
    content = f.read()

# Replace hardcoded "images/" strings
content = content.replace('filepath = "images/" + filepath', 'filepath = get_data_path("images/" + filepath)')

with open("app.py", "w") as f:
    f.write(content)

print("Images patched!")
