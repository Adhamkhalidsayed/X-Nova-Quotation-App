import tkinter as tk
from tkinter import ttk

root = tk.Tk()
root.geometry("400x300")
root.title("Test Tkinter")

style = ttk.Style()
# Try clam
if 'clam' in style.theme_names():
    style.theme_use('clam')
style.layout('TNotebook.Tab', [])
style.configure('TNotebook', background="#f0f0f0")
style.configure('TFrame', background="#f0f0f0")

notebook = ttk.Notebook(root)
notebook.pack(fill='both', expand=True)

frame1 = ttk.Frame(notebook)
notebook.add(frame1, text="Tab 1")
ttk.Label(frame1, text="Hello World").pack(pady=20)

root.after(3000, root.destroy) # Auto close after 3s
root.mainloop()
