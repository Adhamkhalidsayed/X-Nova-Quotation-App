import sys

with open("app.py", "r") as f:
    lines = f.readlines()

content = "".join(lines)

# 1. Inject Dark Mode and Color constants right after "import subprocess" or at the top of GUI section
# Let's find:
# # --- 4. THE DESKTOP WINDOW ---
# root = tk.Tk()
insert_idx = content.find("# --- 4. THE DESKTOP WINDOW ---")

dark_mode_block = """
# Detect macOS dark mode
is_dark_mode = False
try:
    result = subprocess.run(['defaults', 'read', '-g', 'AppleInterfaceStyle'], capture_output=True, text=True, timeout=1)
    is_dark_mode = 'Dark' in result.stdout
except:
    pass

_APP_BG = '#2b2b2b' if is_dark_mode else '#f0f0f0'
_FG = 'white' if is_dark_mode else 'black'

"""
content = content[:insert_idx] + dark_mode_block + content[insert_idx:]

# 2. Window Size and Config
content = content.replace("win_width, win_height = 800, 900", "win_width, win_height = 800, 700")
content = content.replace("root.configure(pady=10)", "root.configure(bg=_APP_BG, pady=10)\nroot.minsize(800, 700)")

# 3. Add ttk Theme and Treeview Styling
# Find:
# style = ttk.Style()
# style.layout('TNotebook.Tab', [])
style_idx = content.find("style = ttk.Style()")
style_end_idx = content.find("style.layout('TNotebook.Tab', [])") + len("style.layout('TNotebook.Tab', [])")

new_style_block = """style = ttk.Style()
if 'clam' in style.theme_names():
    style.theme_use('clam')
style.layout('TNotebook.Tab', [])

# Force background for all ttk elements to match our app background
style.configure('TFrame', background=_APP_BG)
style.configure('TLabelframe', background=_APP_BG, foreground=_FG)
style.configure('TLabelframe.Label', background=_APP_BG, foreground=_FG)
style.configure('TLabel', background=_APP_BG, foreground=_FG)
style.configure('TRadiobutton', background=_APP_BG, foreground=_FG)
style.configure('TCheckbutton', background=_APP_BG, foreground=_FG)

# Fix Treeview Colors for dark mode readability
if is_dark_mode:
    style.configure("Treeview", background="#333333", foreground="white", fieldbackground="#333333", borderwidth=0)
    style.configure("Treeview.Heading", background="#444444", foreground="white", relief="flat")
    style.map("Treeview", background=[('selected', '#1f538d')])
else:
    style.configure("Treeview", background="white", foreground="black", fieldbackground="white", borderwidth=0)
    style.configure("Treeview.Heading", background="#e0e0e0", foreground="black", relief="flat")
    style.map("Treeview", background=[('selected', '#0078D7')])
"""
content = content[:style_idx] + new_style_block + content[style_end_idx:]

# 4. Insert ModernButton class
mb_insert_idx = content.find("# --- Canvas-based custom tab bar with rounded corners ---")
modern_button_code = """
class ModernButton(tk.Canvas):
    def __init__(self, parent, text, command=None, width=160, height=36, radius=18, 
                 bg_color="#6A0dad", hover_color="#800080", fg_color="white", 
                 font=('Helvetica', 11, 'bold'), **kwargs):
        # Determine parent background color for seamless blending
        parent_bg = _APP_BG
            
        super().__init__(parent, width=width, height=height, bg=parent_bg, highlightthickness=0, **kwargs)
        self.command = command
        self.bg_color = bg_color
        self.hover_color = hover_color
        
        # Draw rounded rectangle
        self.rect = self.create_polygon(self._get_pts(0, 0, width, height, radius), smooth=True, fill=bg_color, outline='')
        # Draw text
        self.text_item = self.create_text(width/2, height/2, text=text, fill=fg_color, font=font)
        
        # Bind events
        self.bind('<Button-1>', self.on_click)
        self.bind('<Enter>', self.on_enter)
        self.bind('<Leave>', self.on_leave)
        self.tag_bind(self.rect, '<Button-1>', self.on_click)
        self.tag_bind(self.text_item, '<Button-1>', self.on_click)
        self.tag_bind(self.rect, '<Enter>', self.on_enter)
        self.tag_bind(self.text_item, '<Enter>', self.on_enter)
        
    def _get_pts(self, x1, y1, x2, y2, r):
        return [x1+r,y1, x2-r,y1, x2,y1, x2,y1+r, x2,y2-r, x2,y2, x2-r,y2, x1+r,y2, x1,y2, x1,y2-r, x1,y1+r, x1,y1]

    def on_click(self, event):
        if self.command:
            self.command()
            
    def on_enter(self, event):
        self.itemconfig(self.rect, fill=self.hover_color)
        
    def on_leave(self, event):
        self.itemconfig(self.rect, fill=self.bg_color)

"""
content = content[:mb_insert_idx] + modern_button_code + content[mb_insert_idx:]

# 5. Convert tk.Frame, tk.LabelFrame, tk.Label to ttk
# We need to replace them carefully.
content = content.replace("tk.LabelFrame(", "ttk.LabelFrame(")
content = content.replace("tk.Frame(", "ttk.Frame(")
content = content.replace("tk.Label(", "ttk.Label(")

# Fix LabelFrame padding
content = content.replace(", padx=10, pady=10)", ", padding=10)")
content = content.replace(", padx=15, pady=15)", ", padding=15)")

# The logo has bg=_APP_BG or tk.Label doesn't need it because we converted to ttk.Label
# Wait, lbl_logo = ttk.Label(root, image=logo_photo) works fine!

# 6. Replace all tk.Button with ModernButton and precise colors!
buttons = [
    ('tk.Button(frame_products, text="+ Add Product", command=add_product)',
     'ModernButton(frame_products, text="+ Add Product", width=130, height=34, radius=17, bg_color="#4CAF50", hover_color="#45a049", font=("Helvetica", 10, "bold"), command=add_product)'),
     
    ('tk.Button(btn_frame, text="Remove Selected", command=remove_product)',
     'ModernButton(btn_frame, text="Remove Selected", width=140, height=32, radius=16, bg_color="#f44336", hover_color="#da190b", font=("Helvetica", 10, "bold"), command=remove_product)'),
     
    ('tk.Button(btn_frame, text="Edit Quantity", command=edit_quantity)',
     'ModernButton(btn_frame, text="Edit Quantity", width=120, height=32, radius=16, bg_color="#2196F3", hover_color="#0b7dda", font=("Helvetica", 10, "bold"), command=edit_quantity)'),
     
    ('tk.Button(btn_frame, text="Clear List", command=clear_list)',
     'ModernButton(btn_frame, text="Clear List", width=100, height=32, radius=16, bg_color="#ff9800", hover_color="#e68a00", font=("Helvetica", 10, "bold"), command=clear_list)'),
     
    ('tk.Button(tab_generator, text="Generate PDF Quotation", font=("Helvetica", 12, "bold"), command=generate_pdf)',
     'ModernButton(tab_generator, text="Generate PDF Quotation", width=250, height=45, radius=22, bg_color="#6A0dad", hover_color="#800080", font=("Helvetica", 12, "bold"), command=generate_pdf)'),
     
    ('tk.Button(img_frame, text="Browse...", command=browse_image)',
     'ModernButton(img_frame, text="Browse...", width=90, height=30, radius=15, bg_color="#607d8b", hover_color="#455a64", font=("Helvetica", 10, "bold"), command=browse_image)'),
     
    ('tk.Button(frame_add_db, text="Save to Database", font=("Helvetica", 12, "bold"), bg="green", fg="black", command=save_to_database)',
     'ModernButton(frame_add_db, text="Save to Database", width=220, height=40, radius=20, bg_color="#4CAF50", hover_color="#45a049", font=("Helvetica", 12, "bold"), command=save_to_database)'),
     
    ('tk.Button(frame_del_db, text="Delete Category", fg="red", command=delete_category)',
     'ModernButton(frame_del_db, text="Delete Category", width=140, height=32, radius=16, bg_color="#f44336", hover_color="#da190b", font=("Helvetica", 10, "bold"), command=delete_category)'),
     
    ('tk.Button(frame_del_db, text="Delete Product", fg="red", command=delete_product)',
     'ModernButton(frame_del_db, text="Delete Product", width=140, height=32, radius=16, bg_color="#f44336", hover_color="#da190b", font=("Helvetica", 10, "bold"), command=delete_product)'),
     
    ('tk.Button(hist_btn_frame, text="Load & Edit Quotation", font=("Helvetica", 11, "bold"), command=load_quotation)',
     'ModernButton(hist_btn_frame, text="Load & Edit Quotation", width=180, height=36, radius=18, bg_color="#2196F3", hover_color="#0b7dda", font=("Helvetica", 11, "bold"), command=load_quotation)'),
     
    ('tk.Button(hist_btn_frame, text="Delete Entry", fg="red", command=delete_history_entry)',
     'ModernButton(hist_btn_frame, text="Delete Entry", width=120, height=36, radius=18, bg_color="#f44336", hover_color="#da190b", font=("Helvetica", 10, "bold"), command=delete_history_entry)'),
     
    ('tk.Button(hist_btn_frame, text="Refresh List", command=refresh_history_tree)',
     'ModernButton(hist_btn_frame, text="Refresh List", width=120, height=36, radius=18, bg_color="#607d8b", hover_color="#455a64", font=("Helvetica", 10, "bold"), command=refresh_history_tree)'),
     
    ('tk.Button(hist_btn_frame, text="Sync Now (Cloud)", bg="blue", fg="black", command=manual_sync)',
     'ModernButton(hist_btn_frame, text="Sync Now (Cloud)", width=150, height=36, radius=18, bg_color="#6A0dad", hover_color="#800080", font=("Helvetica", 10, "bold"), command=manual_sync)')
]

for old, new in buttons:
    if old not in content:
        print(f"WARNING: Could not find button to replace: {old}")
    content = content.replace(old, new)

# Wait, we need to make sure ttk is imported. It is imported at the top as: from tkinter import ttk
with open("app.py", "w") as f:
    f.write(content)

print("UI Update Complete")
