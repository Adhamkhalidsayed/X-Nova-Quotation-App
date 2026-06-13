import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk

root = tk.Tk()
root.geometry("400x400")

entry = tk.Entry(root)
entry.pack(pady=20)

popup = None
img_cache = {}

def show_popup(event=None):
    global popup
    if popup is not None:
        return
    popup = tk.Toplevel(root)
    popup.wm_overrideredirect(True)
    
    x = entry.winfo_rootx()
    y = entry.winfo_rooty() + entry.winfo_height()
    popup.geometry(f"200x150+{x}+{y}")
    
    tree = ttk.Treeview(popup, show="tree", height=5)
    tree.pack(fill="both", expand=True)
    
    # Just a dummy image for testing
    img = Image.new('RGB', (30, 30), color='red')
    photo = ImageTk.PhotoImage(img)
    img_cache['test'] = photo
    
    tree.insert("", "end", text="Product 1", image=photo)
    tree.insert("", "end", text="Product 2")
    
    def on_select(e):
        selected = tree.selection()
        if selected:
            item = tree.item(selected[0])
            entry.delete(0, tk.END)
            entry.insert(0, item['text'])
        popup.destroy()
        globals()['popup'] = None
        
    tree.bind("<<TreeviewSelect>>", on_select)

entry.bind("<KeyRelease>", show_popup)

root.after(3000, lambda: root.destroy())
root.mainloop()
