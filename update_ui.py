import re

with open("app.py", "r") as f:
    content = f.read()

# 1. Inject _APP_BG and _FG
content = content.replace(
    "is_dark_mode = 'Dark' in result.stdout\nexcept:\n    pass\n",
    "is_dark_mode = 'Dark' in result.stdout\nexcept:\n    pass\n\n_APP_BG = '#2b2b2b' if is_dark_mode else '#f0f0f0'\n_FG = 'white' if is_dark_mode else 'black'\n"
)

# 2. Configure root window
content = content.replace("root.configure(pady=10)", "root.configure(bg=_APP_BG, pady=10)")

# 3. Inject styles
style_block = """style = ttk.Style()
if 'clam' in style.theme_names():
    style.theme_use('clam')
style.layout('TNotebook.Tab', [])

style.configure('TFrame', background=_APP_BG)
style.configure('TLabelframe', background=_APP_BG, foreground=_FG)
style.configure('TLabelframe.Label', background=_APP_BG, foreground=_FG)
style.configure('TLabel', background=_APP_BG, foreground=_FG)

if is_dark_mode:
    style.configure("Treeview", background="#333333", foreground="white", fieldbackground="#333333", borderwidth=0)
    style.configure("Treeview.Heading", background="#444444", foreground="white", relief="flat")
    style.map("Treeview", background=[('selected', '#1f538d')])
else:
    style.configure("Treeview", background="white", foreground="black", fieldbackground="white", borderwidth=0)
    style.configure("Treeview.Heading", background="#e0e0e0", foreground="black", relief="flat")
    style.map("Treeview", background=[('selected', '#0078D7')])
"""
content = content.replace(
    "style = ttk.Style()\nif 'clam' in style.theme_names():\n    style.theme_use('clam')\nstyle.layout('TNotebook.Tab', [])\n",
    style_block
)

# 4. Fix ModernButton
button_fallback = """        # Determine parent background color for seamless blending
        parent_bg = _APP_BG
"""
content = re.sub(
    r"        # Determine parent background color for seamless blending.*?if not parent_bg.*?        ",
    button_fallback,
    content,
    flags=re.DOTALL
)

# 5. Convert tk.LabelFrame, tk.Frame, tk.Label to ttk
content = content.replace("tk.LabelFrame", "ttk.LabelFrame")
content = content.replace("tk.Frame", "ttk.Frame")
content = content.replace("tk.Label", "ttk.Label")

# 6. Fix padx/pady in ttk.LabelFrame
content = content.replace(", padx=10, pady=10", ", padding=10")
content = content.replace(", padx=15, pady=15", ", padding=15")

# 7. Add root tk import if it doesn't exist (we need to make sure ttk is imported, which it is)
# We also have one tk.Label(root, image=logo_photo) -> ttk.Label(root, image=logo_photo)
# We have tk.Label(..., font=(...), bg=_APP_BG) -> ttk.Label(..., font=(...))

with open("app.py", "w") as f:
    f.write(content)

print("Done")
