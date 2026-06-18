import tkinter as tk
from tkinter import ttk, messagebox, filedialog, simpledialog
# pyrefly: ignore [missing-import]
from PIL import Image, ImageTk
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from PyPDF2 import PdfWriter, PdfReader
import io
import os
import json
import textwrap
import re
import uuid
from datetime import datetime
import sheets_sync

import os
import sys
import platform
from pathlib import Path
import urllib.request
import threading
import zipfile
import tempfile
import shutil
import subprocess

APP_VERSION = "1.0.4"
VERSION_URL = "https://raw.githubusercontent.com/Adhamkhalidsayed/X-Nova-Quotation-App/master/version.json"

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

def perform_update(download_url):
    update_win = tk.Toplevel(root)
    update_win.title("Updating...")
    update_win.geometry("300x100")
    update_win.resizable(False, False)
    # Center the window
    update_win.update_idletasks()
    x = root.winfo_x() + (root.winfo_width() // 2) - 150
    y = root.winfo_y() + (root.winfo_height() // 2) - 50
    update_win.geometry(f"+{x}+{y}")
    update_win.grab_set()

    lbl = tk.Label(update_win, text="Downloading update...\nPlease wait, the app will restart.", font=("Montserrat", 10))
    lbl.pack(expand=True, fill="both", padx=10, pady=10)

    def update_thread():
        try:
            temp_dir = tempfile.mkdtemp()
            zip_path = os.path.join(temp_dir, "update.zip")
            
            req = urllib.request.Request(download_url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req) as response, open(zip_path, 'wb') as out_file:
                shutil.copyfileobj(response, out_file)
            
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(temp_dir)
            
            is_mac = sys.platform == 'darwin'
            if is_mac:
                app_path = os.path.join(temp_dir, "X Nova Quotation.app")
                if not os.path.exists(app_path):
                    for folder in os.listdir(temp_dir):
                        if os.path.isdir(os.path.join(temp_dir, folder)):
                            potential_app = os.path.join(temp_dir, folder, "X Nova Quotation.app")
                            if os.path.exists(potential_app):
                                app_path = potential_app
                                break

                if not os.path.exists(app_path):
                    raise Exception("Could not find X Nova Quotation.app in downloaded update.")

                script_path = os.path.join(temp_dir, "update.sh")
                with open(script_path, "w") as f:
                    f.write("#!/bin/bash\n")
                    f.write("sleep 2\n")
                    f.write('rm -rf "/Applications/X Nova Quotation.app"\n')
                    f.write(f'cp -R "{app_path}" "/Applications/X Nova Quotation.app"\n')
                    f.write('xattr -rd com.apple.quarantine "/Applications/X Nova Quotation.app"\n')
                    f.write('open "/Applications/X Nova Quotation.app"\n')
                    f.write('rm "$0"\n')
                
                os.chmod(script_path, 0o755)
                subprocess.Popen([script_path], start_new_session=True)
                os._exit(0)

            else:
                exe_path = os.path.join(temp_dir, "X Nova Quotation.exe")
                if not os.path.exists(exe_path):
                    for folder in os.listdir(temp_dir):
                        if os.path.isdir(os.path.join(temp_dir, folder)):
                            potential_exe = os.path.join(temp_dir, folder, "X Nova Quotation.exe")
                            if os.path.exists(potential_exe):
                                exe_path = potential_exe
                                break
                
                if not os.path.exists(exe_path):
                    raise Exception("Could not find X Nova Quotation.exe in downloaded update.")

                current_exe = sys.executable
                script_path = os.path.join(temp_dir, "update.bat")
                with open(script_path, "w") as f:
                    f.write("@echo off\n")
                    f.write("timeout /t 2 /nobreak >nul\n")
                    f.write(f'move /y "{exe_path}" "{current_exe}"\n')
                    f.write(f'start "" "{current_exe}"\n')
                    f.write('del "%~f0"\n')

                CREATE_NO_WINDOW = getattr(subprocess, 'CREATE_NO_WINDOW', 0x08000000)
                subprocess.Popen([script_path], creationflags=CREATE_NO_WINDOW)
                os._exit(0)

        except Exception as e:
            def show_error():
                messagebox.showerror("Update Error", f"Failed to update:\n{e}")
                update_win.destroy()
            root.after(0, show_error)

    threading.Thread(target=update_thread, daemon=True).start()

def parse_version(v):
    return tuple(map(int, (v.split("."))))

def check_for_updates(manual=False):
    def fetch_version():
        try:
            import time
            url = f"{VERSION_URL}?t={int(time.time())}"
            req = urllib.request.Request(url, headers={'Cache-Control': 'no-cache'})
            with urllib.request.urlopen(req, timeout=5) as response:
                data = json.loads(response.read().decode())
                
            online_version = data.get("version", "0.0.0")
            if parse_version(online_version) > parse_version(APP_VERSION):
                is_mac = sys.platform == 'darwin'
                download_url = (
                    "https://github.com/Adhamkhalidsayed/X-Nova-Quotation-App/releases/latest/download/X-Nova-Quotation-Mac.zip" 
                    if is_mac else 
                    "https://github.com/Adhamkhalidsayed/X-Nova-Quotation-App/releases/latest/download/X-Nova-Quotation-Win.zip"
                )
                notes = data.get("notes", "")

                if download_url:
                    def prompt_user():
                        msg = f"A new version ({online_version}) is available!\n\nRelease Notes:\n{notes}\n\nWould you like to update now?"
                        if messagebox.askyesno("Update Available", msg, parent=root):
                            perform_update(download_url)
                    root.after(500, prompt_user) # Wait a bit for UI to settle
            else:
                if manual:
                    root.after(0, lambda: messagebox.showinfo("Up to Date", f"You are already running the latest version ({APP_VERSION}).", parent=root))
        except Exception as e:
            if manual:
                root.after(0, lambda: messagebox.showerror("Update Error", f"Failed to check for updates.\n{e}", parent=root))
            else:
                print(f"Failed to check for updates: {e}")

    threading.Thread(target=fetch_version, daemon=True).start()


# --- REGISTER MONTSERRAT FONT ---
pdfmetrics.registerFont(TTFont('Montserrat', get_resource_path('fonts/Montserrat-Regular.ttf')))
pdfmetrics.registerFont(TTFont('Montserrat-Bold', get_resource_path('fonts/Montserrat-Bold.ttf')))

# --- 1. LOAD DATABASE FROM JSON FILE (OR CLOUD) ---
def load_database():
    cloud_db = sheets_sync.load_products_from_sheet()
    if cloud_db is not None:
        # Save cloud data to local cache
        with open(get_data_path("database.json"), "w") as f:
            json.dump(cloud_db, f, indent=4)
        return cloud_db

    if os.path.exists(get_data_path("database.json")):
        with open(get_data_path("database.json"), "r") as f:
            return json.load(f)
    else:
        messagebox.showwarning("Warning", "database.json not found! Creating an empty one.")
        empty_db = {"Access Control System": [], "Safety System": []}
        with open(get_data_path("database.json"), "w") as f:
            json.dump(empty_db, f, indent=4)
        return empty_db

# Initialize sync before loading data
sheets_sync.init_sync()
products_db = load_database()
current_quote_items = {}

def get_next_quote_number():
    """Return next sequential quote number like QT-2026-001 and persist the counter."""
    config_path = get_data_path("config.json")
    config = {}
    if os.path.exists(config_path):
        with open(config_path, "r") as f:
            config = json.load(f)
    year = datetime.now().strftime("%Y")
    last_year = config.get("quote_number_year", year)
    last_num  = config.get("quote_number_counter", 0)
    if last_year != year:
        last_num = 0  # Reset counter for new year
    last_num += 1
    config["quote_number_year"] = year
    config["quote_number_counter"] = last_num
    with open(config_path, "w") as f:
        json.dump(config, f, indent=4)
    return f"QT-{year}-{last_num:03d}"
group_base_categories = {}  # Maps group_key -> base category name

# --- 2. DROPDOWN & LIST LOGIC ---
def refresh_dropdowns():
    categories = list(products_db.keys())
    combo_category['values'] = categories
    combo_db_category['values'] = categories
    combo_del_category['values'] = categories
    if categories:
        combo_category.current(0)
        combo_db_category.current(0)
        combo_del_category.current(0)

def update_product_dropdown(event=None):
    category = combo_category.get()
    if category in products_db:
        product_names = [p["name"] for p in products_db[category]]
        combo_product['values'] = product_names
        if product_names:
            combo_product.set(product_names[0])
            preview_product_image()
        else:
            lbl_product_preview.config(image='')
            lbl_product_preview.image = None

def preview_product_image(event=None):
    category = combo_category.get()
    prod_name = combo_product.get()
    if category in products_db:
        prod = next((p for p in products_db[category] if p["name"] == prod_name), None)
        if prod and prod.get("image"):
            img_path = prod["image"]
            # Handle possible old paths
            if "images/" in img_path and not img_path.startswith(get_data_path("")):
                img_path = get_data_path("images/" + img_path.split("images/")[-1])
                
            if os.path.exists(img_path):
                try:
                    img = Image.open(img_path)
                    img.thumbnail((120, 120))  # resize to fit
                    photo = ImageTk.PhotoImage(img)
                    lbl_product_preview.config(image=photo, text="")
                    lbl_product_preview.image = photo
                    return
                except Exception:
                    pass
    lbl_product_preview.config(image='', text="No Image")
    lbl_product_preview.image = None

def add_product():
    category = combo_category.get()
    prod_name = combo_product.get()
    qty = entry_qty.get()
    room = entry_room.get().strip()

    if not category or not prod_name or not qty:
        messagebox.showerror("Error", "Please select a product and enter a quantity.")
        return

    prod_details = next((p for p in products_db[category] if p["name"] == prod_name), None)
    if not prod_details:
        return

    # Build group key: "Category - Room" if room provided, else just "Category"
    group_key = f"{category} - {room}" if room else category

    if group_key not in current_quote_items:
        current_quote_items[group_key] = []
    group_base_categories[group_key] = category
    
    # Check if product already exists in this group
    existing = next((p for p in current_quote_items[group_key] if p["name"] == prod_name), None)
    
    if existing:
        # Add quantity to existing product
        old_qty = int(existing["qty"].replace(" pieces", ""))
        new_qty = old_qty + int(qty)
        existing["qty"] = f"{new_qty} pieces"
        
        # Refresh the treeview to show updated quantity
        for item in tree.get_children():
            values = tree.item(item, "values")
            if values[0] == group_key and values[1] == prod_name:
                tree.item(item, values=(group_key, prod_name, new_qty, prod_details["price"]))
                break
    else:
        # Add as new product
        current_quote_items[group_key].append({
            "name": prod_details["name"],
            "desc": prod_details["desc"],
            "qty": f"{qty} pieces",
            "price": prod_details["price"],
            "image": prod_details.get("image", "")
        })
        tree.insert("", tk.END, values=(group_key, prod_details["name"], qty, prod_details["price"]))
    
    entry_qty.delete(0, tk.END)

def clear_list():
    global current_quote_items, group_base_categories
    current_quote_items = {}
    group_base_categories = {}
    for item in tree.get_children():
        tree.delete(item)

def remove_product():
    selected = tree.selection()
    if not selected:
        messagebox.showerror("Error", "Please select a product to remove.")
        return
    
    item = selected[0]
    values = tree.item(item, "values")
    category = values[0]
    prod_name = values[1]
    
    # Remove from current_quote_items
    if category in current_quote_items:
        current_quote_items[category] = [p for p in current_quote_items[category] if p["name"] != prod_name]
        if not current_quote_items[category]:
            del current_quote_items[category]
    
    tree.delete(item)

def edit_quantity():
    selected = tree.selection()
    if not selected:
        messagebox.showerror("Error", "Please select a product to edit.")
        return
    
    item = selected[0]
    values = tree.item(item, "values")
    category = values[0]
    prod_name = values[1]
    current_qty = int(values[2])
    
    new_qty = simpledialog.askinteger("Edit Quantity", f"Enter new quantity for:\n{prod_name}", initialvalue=current_qty, minvalue=0)
    
    if new_qty is None:
        return  # User cancelled
    
    if new_qty == 0:
        # Remove the product
        if category in current_quote_items:
            current_quote_items[category] = [p for p in current_quote_items[category] if p["name"] != prod_name]
            if not current_quote_items[category]:
                del current_quote_items[category]
        tree.delete(item)
    else:
        # Update quantity
        if category in current_quote_items:
            for p in current_quote_items[category]:
                if p["name"] == prod_name:
                    p["qty"] = f"{new_qty} pieces"
                    break
        tree.item(item, values=(category, prod_name, new_qty, values[3]))

#3.generate pdf button functionality
def generate_pdf():
    client_name = entry_name.get()
    client_location = entry_location.get()
    revision_version = entry_version.get()
    quote_number = entry_quote_number.get().strip() or get_next_quote_number()
    # Update the UI field with the confirmed number
    entry_quote_number.delete(0, tk.END)
    entry_quote_number.insert(0, quote_number)

    if not client_name or not current_quote_items:
        messagebox.showerror("Error", "Please enter a Client Name and add products.")
        return

    try:
        packet = io.BytesIO()
        can = canvas.Canvas(packet, pagesize=A4)
        page_width, page_height = A4
        page_number = 0  # Track page numbers for category/product pages
        
        # --- PAGE 2: PROJECT INFO (no page number) ---
        # 1. Draw Background First
        if os.path.exists(get_resource_path("assets/bg_page2.png")):
            can.drawImage(get_resource_path("assets/bg_page2.png"), 0, 0, width=page_width, height=page_height)
        
        # 2. Draw Text on top
        can.setFillColor("white")
        can.setFont("Montserrat-Bold", 30)
        can.drawString(50, 400, client_name)
        can.setFont("Montserrat", 24)
        can.drawString(50, 365, client_location)
        can.setFont("Montserrat", 12)
        can.drawString(50, 120, "Presented By: X Nova Smart Spaces Solutions")
        can.drawString(50, 100, f"Version: {revision_version}")
        can.drawString(50, 80, f"Date: {datetime.now().strftime('%d %B %Y')}")
        can.drawString(50, 60, f"Quotation No: {quote_number}")
        can.showPage()

        # --- GROUP items by base category (system) ---
        from collections import OrderedDict
        systems = OrderedDict()  # base_category -> list of (group_key, products)
        for group_key, products in current_quote_items.items():
            base_cat = group_base_categories.get(group_key, group_key)
            if base_cat not in systems:
                systems[base_cat] = []
            systems[base_cat].append((group_key, products))
        
        all_category_totals = {}  # Track totals for summary page (by base category)
        
        for base_category, groups in systems.items():
            system_total = 0
            
            # --- Category Title Page (one per system) ---
            if os.path.exists(get_resource_path("assets/bg_category.png")):
                can.drawImage(get_resource_path("assets/bg_category.png"), 0, 0, width=page_width, height=page_height)
            
            can.setFont("Montserrat-Bold", 55)
            can.setFillColor("purple")
            
            # Wrap long category names across multiple lines (left-aligned)
            cat_lines = textwrap.wrap(base_category, width=15)
            cat_y = 400 + ((len(cat_lines) - 1) * 35)
            for line in cat_lines:
                can.drawString(30, cat_y, line)
                cat_y -= 70
            
            can.setFillColorRGB(0, 0, 0)
            
            page_number += 1
            can.setFont("Montserrat", 10)
            can.drawCentredString(page_width-30, 30, f"{page_number}")
            can.showPage()
            
            # --- Product Table Pages (one per room/group within the system) ---
            for group_key, products in groups:
                if os.path.exists(get_resource_path("assets/bg_products.png")):
                    can.drawImage(get_resource_path("assets/bg_products.png"), 0, 0, width=page_width, height=page_height)

                y_pos = 745
                
                # Draw group name at the top (e.g. "Control System - Room 1" or just "Control System")
                can.setFont("Montserrat-Bold", 22)
                can.setFillColor("purple")
                can.drawCentredString(page_width / 2, y_pos, group_key)
                can.setFillColorRGB(0, 0, 0)
                
                y_pos -= 45
                can.setFont("Montserrat-Bold", 14)
                can.drawString(45, y_pos, "Image")
                can.drawString(190, y_pos, "Description")
                can.drawString(455, y_pos, "Qty")
                can.drawString(520, y_pos, "Price")
                
                can.line(45, y_pos - 10, 560, y_pos - 10)
                
                # Font sizes and spacing for products
                NAME_FONT_SIZE = 12
                DESC_FONT_SIZE = 11
                QTY_FONT_SIZE = 12
                NAME_LINE_SPACING = 15
                DESC_LINE_SPACING = 14
                IMG_MIN = 50
                IMG_MAX = 130
                ROW_PADDING = 20
                DESC_X = 190  # Description column start (after image area)
                DESC_WRAP = 30  # Wrap width for description text
                
                for p in products:
                    # Calculate product total
                    try:
                        qty_str = str(p.get('qty', '0'))
                        price_str = str(p.get('price', '0'))
                        qty_num = float(re.sub(r'[^\d.]', '', qty_str) or 0)
                        price_num = float(re.sub(r'[^\d.]', '', price_str) or 0)
                        system_total += (qty_num * price_num)
                    except Exception as e:
                        print(f"Error calculating price: {e}")
                    
                    # Pre-calculate wrapped text to determine dynamic row height
                    name_lines = textwrap.wrap(p['name'], width=DESC_WRAP)
                    desc_lines = textwrap.wrap(p['desc'], width=DESC_WRAP)
                    
                    # Combined height: name lines + gap + desc lines
                    combined_text_height = (len(name_lines) * NAME_LINE_SPACING) + 6 + (len(desc_lines) * DESC_LINE_SPACING)
                    
                    # Dynamic image size: scale to text height, clamped to min/max
                    img_size = max(IMG_MIN, min(IMG_MAX, combined_text_height))
                    content_height = max(img_size, combined_text_height)
                    row_height = content_height + ROW_PADDING
                    
                    # PAGE BREAK: Check if this row fits BEFORE drawing
                    if y_pos - row_height < 80:
                        page_number += 1
                        can.setFont("Montserrat", 10)
                        can.drawCentredString(page_width-30, 30, f"{page_number}")
                        
                        can.showPage()
                        if os.path.exists(get_resource_path("assets/bg_products.png")):
                            can.drawImage(get_resource_path("assets/bg_products.png"), 0, 0, width=page_width, height=page_height)
                        
                        y_pos = 745
                        can.setFont("Montserrat-Bold", 22)
                        can.setFillColor("purple")
                        can.drawCentredString(page_width / 2, y_pos, group_key)
                        can.setFillColorRGB(0, 0, 0)
                        
                        y_pos -= 45
                        can.setFont("Montserrat-Bold", 14)
                        can.drawString(45, y_pos, "Image")
                        can.drawString(190, y_pos, "Description")
                        can.drawString(455, y_pos, "Qty")
                        can.drawString(520, y_pos, "Price")
                        can.line(45, y_pos - 10, 560, y_pos - 10)
                    
                    y_pos -= row_height
                    
                    # Draw Product Image (dynamically sized, vertically centered)
                    img_path = p.get("image", "")
                    # Try to resolve image path: support absolute paths, relative paths,
                    # and bare filenames stored in the Application Support images folder
                    if img_path:
                        if not os.path.exists(img_path):
                            # Try as a bare filename in Application Support/images
                            candidate = get_data_path(os.path.join("images", os.path.basename(img_path)))
                            if os.path.exists(candidate):
                                img_path = candidate
                            else:
                                img_path = ""  # Can't find it
                    if img_path and os.path.exists(img_path):
                        try:
                            img_y = y_pos + (content_height - img_size) / 2
                            can.drawImage(img_path, 45, img_y, width=img_size, height=img_size, preserveAspectRatio=True, mask='auto')
                        except Exception as e:
                            print(f"Could not draw image {img_path}: {e}")
                    
                    # Draw product name (bold) then description (regular) in same column
                    text_y = y_pos + content_height - 4
                    
                    # Product Name (bold, top of description area)
                    can.setFont("Montserrat-Bold", NAME_FONT_SIZE)
                    for line in name_lines:
                        can.drawString(DESC_X, text_y, line)
                        text_y -= NAME_LINE_SPACING
                    
                    # Small gap between name and description
                    text_y -= 4
                    
                    # Description (regular, below name)
                    can.setFont("Montserrat", DESC_FONT_SIZE)
                    for line in desc_lines:
                        can.drawString(DESC_X, text_y, line)
                        text_y -= DESC_LINE_SPACING
                    
                    # Qty and Price (vertically centered)
                    center_y = y_pos + content_height / 2
                    can.setFont("Montserrat", QTY_FONT_SIZE)
                    can.drawString(455, center_y - 4, p['qty'])
                    can.drawString(520, center_y - 4, p['price'])
                    
                    # Dynamic separator line below all content
                    can.line(45, y_pos - 5, 560, y_pos - 5)

                # Add page number before flushing the product page
                page_number += 1
                can.setFont("Montserrat", 10)
                can.drawCentredString(page_width-30, 30, f"{page_number}")
                
                can.showPage()
            
            # --- Category Total Page (one per system, sums all rooms) ---
            if os.path.exists(get_resource_path("assets/bg_category.png")):
                can.drawImage(get_resource_path("assets/bg_category.png"), 0, 0, width=page_width, height=page_height)
                
            # Draw Logo at top
            if os.path.exists(get_resource_path("assets/logo_dark.png")):
                try:
                    img_logo_tot = Image.open(get_resource_path("assets/logo_dark.png"))
                    aspect_ratio = img_logo_tot.width / img_logo_tot.height
                    new_height = 40
                    new_width = int(new_height * aspect_ratio)
                    logo_x = (page_width - new_width) / 2
                    can.drawImage(get_resource_path("assets/logo_dark.png"), logo_x, page_height - 100, width=new_width, height=new_height, preserveAspectRatio=True, mask='auto')
                except:
                    pass

            # Draw rounded rectangle in center
            box_width = 500
            box_height = 160
            box_x = (page_width - box_width) / 2
            box_y = (page_height - box_height) / 2
            can.setStrokeColorRGB(0.1, 0.1, 0.4)
            can.setLineWidth(1)
            can.roundRect(box_x, box_y, box_width, box_height, 10, stroke=1, fill=0)
            
            # Left side text: Category \n Total
            can.setFillColorRGB(0, 0, 0)
            can.setFont("Montserrat-Bold", 24)
            cat_lines = textwrap.wrap(base_category, width=22)
            text_y = box_y + box_height/2 + 20
            for line in cat_lines:
                can.drawString(box_x + 40, text_y, line)
                text_y -= 30
            can.setFont("Montserrat-Bold", 18)
            can.drawString(box_x + 40, text_y, "Total")
            
            # Right side text: The calculated total number
            formatted_total = f"${system_total:,.0f}"
            can.setFont("Montserrat-Bold", 32)
            total_width = pdfmetrics.stringWidth(formatted_total, "Montserrat-Bold", 32)
            can.drawString(box_x + box_width - 40 - total_width, box_y + box_height/2 - 25, formatted_total)
            
            # Add page number
            page_number += 1
            can.setFont("Montserrat", 10)
            can.setFillColorRGB(0, 0, 0)
            can.drawCentredString(page_width-30, 27, f"{page_number}")
            
            # Store system total for summary page
            all_category_totals[base_category] = system_total
            
            can.showPage()

        # --- TOTAL PRICES SUMMARY PAGE ---
        if os.path.exists(get_resource_path("assets/bg_category.png")):
            can.drawImage(get_resource_path("assets/bg_category.png"), 0, 0, width=page_width, height=page_height)
        
        # Draw Logo at top
        if os.path.exists(get_resource_path("assets/logo_dark.png")):
            try:
                img_logo_sum = Image.open(get_resource_path("assets/logo_dark.png"))
                aspect_ratio = img_logo_sum.width / img_logo_sum.height
                new_height = 40
                new_width = int(new_height * aspect_ratio)
                logo_x = (page_width - new_width) / 2
                can.drawImage(get_resource_path("assets/logo_dark.png"), logo_x, page_height - 100, width=new_width, height=new_height, preserveAspectRatio=True, mask='auto')
            except:
                pass
        
        # Title: "Total Prices"
        can.setFont("Montserrat-Bold", 30)
        can.setFillColor("purple")
        title_y = page_height - 150
        can.drawCentredString(page_width / 2, title_y, "Total Prices")
        
        # Table setup
        table_width = 500
        table_x = (page_width - table_width) / 2
        col_split = table_x + 300  # Where "System" column ends and "Total" column begins
        row_height = 70
        
        # Calculate number of rows: header + systems + installation + total + discounted
        num_systems = len(all_category_totals)
        
        # Get discount value
        try:
            discount_pct = float(entry_discount.get().strip() or 0)
        except ValueError:
            discount_pct = 0
        
        # Total rows = header + systems + installation + total + (discount if applicable)
        num_rows = 1 + num_systems + 2  # header + systems + installation + total
        if discount_pct > 0:
            num_rows += 1
        
        total_table_height = num_rows * row_height
        table_top = title_y - 30
        table_bottom = table_top - total_table_height
        
        # Draw outer rounded border
        can.setStrokeColorRGB(0.1, 0.1, 0.4)
        can.setLineWidth(2.5)
        can.roundRect(table_x, table_bottom, table_width, total_table_height, 12, stroke=1, fill=0)
        
        # --- Header Row ---
        header_y = table_top - row_height
        can.setFont("Montserrat-Bold", 20)
        can.setFillColorRGB(0, 0, 0)
        can.drawCentredString((table_x + col_split) / 2, header_y + 22, "System")
        can.drawCentredString((col_split + table_x + table_width) / 2, header_y + 22, "Total")
        
        # Header bottom line
        can.setStrokeColorRGB(0.1, 0.1, 0.4)
        can.setLineWidth(1.5)
        can.line(table_x + 5, header_y, table_x + table_width - 5, header_y)
        
        # --- System Rows ---
        current_y = header_y
        systems_subtotal = 0
        for cat_name, cat_total in all_category_totals.items():
            systems_subtotal += cat_total
            row_bottom = current_y - row_height
            
            can.setFont("Montserrat-Bold", 18)
            can.setFillColorRGB(0, 0, 0)
            # Wrap category name if too long
            cat_display_lines = textwrap.wrap(cat_name, width=20)
            if len(cat_display_lines) > 1:
                text_start_y = current_y - row_height/2 + (len(cat_display_lines) - 1) * 10
                for cl in cat_display_lines:
                    can.drawCentredString((table_x + col_split) / 2, text_start_y, cl)
                    text_start_y -= 20
            else:
                can.drawCentredString((table_x + col_split) / 2, current_y - row_height/2 - 5, cat_name)
            
            can.setFont("Montserrat-Bold", 18)
            formatted_cat_total = f"${cat_total:,.2f}"
            can.drawCentredString((col_split + table_x + table_width) / 2, current_y - row_height/2 - 5, formatted_cat_total)
            
            # Row separator line
            can.setStrokeColorRGB(0.7, 0.7, 0.7)
            can.setLineWidth(0.5)
            can.line(table_x + 5, row_bottom, table_x + table_width - 5, row_bottom)
            
            current_y = row_bottom
        
        # --- 10% Installation Row ---
        installation = systems_subtotal * 0.10
        install_bottom = current_y - row_height
        
        # Purple separator line above installation
        can.setStrokeColor("purple")
        can.setLineWidth(2)
        can.line(table_x + 5, current_y, table_x + table_width - 5, current_y)
        
        can.setFont("Montserrat-Bold", 18)
        can.setFillColorRGB(0, 0, 0)
        can.drawCentredString((table_x + col_split) / 2, current_y - row_height/2 - 5, "10% Installation")
        can.setFont("Montserrat-Bold", 18)
        formatted_install = f"${installation:,.2f}"
        can.drawCentredString((col_split + table_x + table_width) / 2, current_y - row_height/2 - 5, formatted_install)
        
        # Row separator
        can.setStrokeColorRGB(0.7, 0.7, 0.7)
        can.setLineWidth(0.5)
        can.line(table_x + 5, install_bottom, table_x + table_width - 5, install_bottom)
        
        current_y = install_bottom
        
        # --- Grand Total Row ---
        grand_total = systems_subtotal + installation
        total_bottom = current_y - row_height
        
        can.setFont("Montserrat-Bold", 18)
        can.setFillColorRGB(0, 0, 0)
        can.drawCentredString((table_x + col_split) / 2, current_y - row_height/2 + 8, "Total")
        can.setFont("Montserrat-Bold", 13)
        can.drawCentredString((table_x + col_split) / 2, current_y - row_height/2 - 12, "in US Dollar")
        
        can.setFont("Montserrat-Bold", 22)
        formatted_grand = f"${grand_total:,.2f}"
        can.drawCentredString((col_split + table_x + table_width) / 2, current_y - row_height/2 - 5, formatted_grand)
        
        current_y = total_bottom
        
        # --- Discounted Total Row (if applicable) ---
        if discount_pct > 0:
            can.setStrokeColorRGB(0.7, 0.7, 0.7)
            can.setLineWidth(0.5)
            can.line(table_x + 5, current_y, table_x + table_width - 5, current_y)
            
            discounted_total = grand_total * (1 - discount_pct / 100)
            discount_bottom = current_y - row_height
            
            can.setFont("Montserrat-Bold", 18)
            can.setFillColorRGB(0.2, 0.6, 0.2)  # Green color
            can.drawCentredString((table_x + col_split) / 2, current_y - row_height/2 + 8, "Total Discounted")
            can.setFont("Montserrat-Bold", 12)
            can.drawCentredString((table_x + col_split) / 2, current_y - row_height/2 - 12, f"{int(discount_pct)}% Discount Applied")
            
            can.setFont("Montserrat-Bold", 22)
            formatted_disc = f"${discounted_total:,.2f}"
            can.drawCentredString((col_split + table_x + table_width) / 2, current_y - row_height/2 - 5, formatted_disc)
            
            current_y = discount_bottom
        
        # Page number
        page_number += 1
        can.setFont("Montserrat", 10)
        can.setFillColorRGB(0, 0, 0)
        can.drawCentredString(page_width-30, 27, f"{page_number}")
        
        can.showPage()

        can.save()
        packet.seek(0)

        # MERGE FIXED COVERS AND DYNAMIC PAGES
        output = PdfWriter()
        if os.path.exists(get_resource_path("assets/cover.pdf")):
            cover_page = PdfReader(get_resource_path("assets/cover.pdf")).pages[0]
            cover_page.scale_to(float(page_width), float(page_height))
            output.add_page(cover_page)
            
        for page in PdfReader(packet).pages: output.add_page(page)
        
        if os.path.exists(get_resource_path("assets/terms.pdf")):
            for page in PdfReader(get_resource_path("assets/terms.pdf")).pages:
                page.scale_to(float(page_width), float(page_height))
                output.add_page(page)
            
        pdf_name = f"{quote_number}_{client_name.replace(' ', '_')}.pdf"
        desktop = os.path.join(str(Path.home()), "Desktop")
        filename = filedialog.asksaveasfilename(
            title="Save Quotation PDF",
            initialdir=desktop,
            initialfile=pdf_name,
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")]
        )
        if not filename:
            return  # User cancelled the save dialog

        with open(filename, "wb") as f:
            output.write(f)

        save_name = os.path.basename(filename)
        messagebox.showinfo("Success", f"Quotation saved successfully:\n{save_name}")
        
        # Auto-save to history
        save_to_history(client_name, client_location, revision_version, current_quote_items, quote_number)

    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {str(e)}")

# --- HISTORY FUNCTIONS ---
HISTORY_FILE = get_data_path("history.json")

def load_history():
    cloud_history = sheets_sync.load_history_from_sheet()
    if cloud_history is not None:
        # Save cloud history to local cache
        with open(HISTORY_FILE, "w") as f:
            json.dump(cloud_history, f, indent=4)
        return cloud_history

    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r") as f:
            return json.load(f)
    return []

def save_history(history_data):
    with open(HISTORY_FILE, "w") as f:
        json.dump(history_data, f, indent=4)
        
    # Push to cloud
    sheets_sync.save_history_to_sheet(history_data)

def save_to_history(client_name, client_location, revision_version, items, quote_number=""):
    history = load_history()
    
    # Check if entry with same client name + version exists → update it
    existing = None
    for entry in history:
        if entry["client_name"] == client_name and entry["revision_version"] == revision_version:
            existing = entry
            break
    
    if existing:
        existing["date"] = datetime.now().strftime("%Y-%m-%d %H:%M")
        existing["client_location"] = client_location
        existing["items"] = items
    else:
        history.append({
            "id": str(uuid.uuid4()),
            "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "quote_number": quote_number,
            "client_name": client_name,
            "client_location": client_location,
            "revision_version": revision_version,
            "items": items
        })
    
    save_history(history)
    # Refresh history treeview if it exists
    try:
        refresh_history_tree()
    except Exception:
        pass

def refresh_history_tree():
    for item in history_tree.get_children():
        history_tree.delete(item)
    history = load_history()
    for entry in history:
        history_tree.insert("", tk.END, iid=entry["id"], values=(
            entry.get("quote_number", ""),
            entry["date"],
            entry["client_name"],
            entry.get("client_location", ""),
            entry["revision_version"]
        ))

def load_quotation():
    selected = history_tree.selection()
    if not selected:
        messagebox.showerror("Error", "Please select a quotation to load.")
        return
    
    entry_id = selected[0]
    history = load_history()
    entry = next((e for e in history if e["id"] == entry_id), None)
    if not entry:
        messagebox.showerror("Error", "Quotation not found in history.")
        return
    
    # Clear current state
    global current_quote_items
    current_quote_items = {}
    for item in tree.get_children():
        tree.delete(item)
    
    # Populate client fields
    entry_quote_number.delete(0, tk.END)
    entry_quote_number.insert(0, entry.get("quote_number", ""))
    entry_name.delete(0, tk.END)
    entry_name.insert(0, entry["client_name"])
    entry_location.delete(0, tk.END)
    entry_location.insert(0, entry.get("client_location", ""))
    entry_version.delete(0, tk.END)
    entry_version.insert(0, entry["revision_version"])
    
    # Populate quote items and rebuild group_base_categories
    global group_base_categories
    current_quote_items = entry["items"]
    group_base_categories = {}
    for group_key, products in current_quote_items.items():
        if " - " in group_key:
            possible_base = group_key.rsplit(" - ", 1)[0]
            if possible_base in products_db:
                group_base_categories[group_key] = possible_base
            else:
                group_base_categories[group_key] = group_key
        else:
            group_base_categories[group_key] = group_key
        for p in products:
            qty_display = p["qty"].replace(" pieces", "")
            tree.insert("", tk.END, values=(group_key, p["name"], qty_display, p["price"]))
    
    # Switch to generator tab
    notebook.select(tab_generator)
    messagebox.showinfo("Loaded", f"Quotation {entry.get('quote_number','')} for '{entry['client_name']}' loaded.\nYou can now edit and regenerate it.")

def duplicate_quotation():
    """Load a history entry but clear the quote number so a new one is auto-assigned."""
    selected = history_tree.selection()
    if not selected:
        messagebox.showerror("Error", "Please select a quotation to duplicate.")
        return
    entry_id = selected[0]
    history = load_history()
    entry = next((e for e in history if e["id"] == entry_id), None)
    if not entry:
        messagebox.showerror("Error", "Quotation not found in history.")
        return
    global current_quote_items
    current_quote_items = {}
    for item in tree.get_children():
        tree.delete(item)
    # Clear quote number so a fresh one is auto-assigned on generate
    entry_quote_number.delete(0, tk.END)
    entry_name.delete(0, tk.END)
    entry_name.insert(0, entry["client_name"])
    entry_location.delete(0, tk.END)
    entry_location.insert(0, entry.get("client_location", ""))
    entry_version.delete(0, tk.END)
    # Bump version
    old_ver = entry["revision_version"]
    try:
        parts = old_ver.split(".")
        parts[-1] = str(int(parts[-1]) + 1)
        new_ver = ".".join(parts)
    except Exception:
        new_ver = old_ver + " (copy)"
    entry_version.insert(0, new_ver)
    global group_base_categories
    current_quote_items = entry["items"]
    group_base_categories = {}
    for group_key, products in current_quote_items.items():
        if " - " in group_key:
            possible_base = group_key.rsplit(" - ", 1)[0]
            if possible_base in products_db:
                group_base_categories[group_key] = possible_base
            else:
                group_base_categories[group_key] = group_key
        else:
            group_base_categories[group_key] = group_key
        for p in products:
            qty_display = p["qty"].replace(" pieces", "")
            tree.insert("", tk.END, values=(group_key, p["name"], qty_display, p["price"]))
    notebook.select(tab_generator)
    messagebox.showinfo("Duplicated", f"Quotation duplicated from '{entry['client_name']}'.\nA new quote number will be assigned when you generate.")

def delete_history_entry():
    selected = history_tree.selection()
    if not selected:
        messagebox.showerror("Error", "Please select a quotation to delete.")
        return
    
    entry_id = selected[0]
    history = load_history()
    entry = next((e for e in history if e["id"] == entry_id), None)
    
    if entry:
        confirm = messagebox.askyesno("Confirm Delete", f"Delete quotation for '{entry['client_name']}'?")
        if confirm:
            history = [e for e in history if e["id"] != entry_id]
            save_history(history)
            refresh_history_tree()


# Detect macOS dark mode
import subprocess
is_dark_mode = False
try:
    result = subprocess.run(['defaults', 'read', '-g', 'AppleInterfaceStyle'], capture_output=True, text=True, timeout=1)
    is_dark_mode = 'Dark' in result.stdout
except:
    pass

_APP_BG = '#2b2b2b' if is_dark_mode else '#f0f0f0'
_FG = 'white' if is_dark_mode else 'black'

# --- 4. THE DESKTOP WINDOW ---
root = tk.Tk()
root.title("X Nova Quotation Generator")
win_width, win_height = 800, 800
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
x = (screen_width - win_width) // 2
y = (screen_height - win_height) // 2
root.geometry(f"{win_width}x{win_height}+{x}+{y}")
root.configure(bg=_APP_BG, pady=10)
root.minsize(800, 700)

main_frame = tk.Frame(root, bg=_APP_BG)
main_frame.pack(fill="both", expand=True)

try:
    icon = tk.PhotoImage(file=get_resource_path("assets/favicon.png"))
    root.iconphoto(True, icon)
except Exception:
    pass


# Theme colors for custom tabs
if is_dark_mode:
    _CLR_BAR = '#2d2d2d'
    _CLR_ACT = '#505050'
    _CLR_ACT_F = '#ffffff'
    _CLR_INA = '#3a3a3a'
    _CLR_INA_F = '#999999'
    _CLR_HOV = '#454545'
else:
    _CLR_BAR = '#e8e8e8'
    _CLR_ACT = '#ffffff'
    _CLR_ACT_F = '#333333'
    _CLR_INA = '#d0d0d0'
    _CLR_INA_F = '#666666'
    _CLR_HOV = '#dcdcdc'

try:
    logo_file = get_resource_path("assets/logo_dark.png") if is_dark_mode else get_resource_path("assets/logo.png")
    img_logo = Image.open(logo_file)
    aspect_ratio = img_logo.width / img_logo.height
    new_height = 50
    new_width = int(new_height * aspect_ratio)
    img_logo = img_logo.resize((new_width, new_height), Image.Resampling.LANCZOS)
    logo_photo = ImageTk.PhotoImage(img_logo)
    lbl_logo = ttk.Label(main_frame, image=logo_photo)
    lbl_logo.image = logo_photo
    lbl_logo.pack(pady=10)
except Exception:
    ttk.Label(main_frame, text="X Nova Smart Spaces", font=("Helvetica", 16, "bold")).pack(pady=5)


style = ttk.Style()
# if 'clam' in style.theme_names():
#     style.theme_use('clam')
style.layout('TNotebook.Tab', [])
style.configure('TNotebook', borderwidth=0, highlightthickness=0)

# Force background for all ttk elements to match our app background
style.configure('TFrame', background=_APP_BG, borderwidth=0, highlightthickness=0)
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



class ModernButton(tk.Canvas):
    def __init__(self, parent, text, command=None, width=160, height=36, radius=18, 
                 bg_color="#6A0dad", hover_color="#800080", fg_color="white", 
                 font=('Helvetica', 14, 'bold'), **kwargs):
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
        
        # Bind events (only tag bindings to avoid double-fire)
        self.tag_bind(self.rect, '<Button-1>', self.on_click)
        self.tag_bind(self.text_item, '<Button-1>', self.on_click)
        self.tag_bind(self.rect, '<Enter>', self.on_enter)
        self.tag_bind(self.text_item, '<Enter>', self.on_enter)
        self.bind('<Leave>', self.on_leave)
        
    def _get_pts(self, x1, y1, x2, y2, r):
        return [x1+r,y1, x2-r,y1, x2,y1, x2,y1+r, x2,y2-r, x2,y2, x2-r,y2, x1+r,y2, x1,y2, x1,y2-r, x1,y1+r, x1,y1]

    def on_click(self, event):
        if self.command:
            self.command()
            
    def on_enter(self, event):
        self.itemconfig(self.rect, fill=self.hover_color)
        
    def on_leave(self, event):
        self.itemconfig(self.rect, fill=self.bg_color)

# --- Canvas-based custom tab bar with rounded corners ---
_TAB_NAMES = ['Generate Quote', 'Database', 'History', 'About']
_TW, _TH, _TR, _TG = 150, 34, 12, 6  # width, height, radius, gap
_CH = _TH + 14
_TOTAL = len(_TAB_NAMES) * _TW + (len(_TAB_NAMES) - 1) * _TG

tab_canvas = tk.Canvas(main_frame, height=_CH, bg=_CLR_BAR, highlightthickness=0)
tab_canvas.pack(fill='x')

_tab_rects = []
_tab_texts = []
_current_tab = 0

def _rr(cv, x1, y1, x2, y2, r, **kw):
    pts = [x1+r,y1, x2-r,y1, x2,y1, x2,y1+r, x2,y2-r, x2,y2, x2-r,y2, x1+r,y2, x1,y2, x1,y2-r, x1,y1+r, x1,y1]
    return cv.create_polygon(pts, smooth=True, **kw)

_last_tab_width = 0

def _draw_tabs(event=None):
    global _last_tab_width
    if event:
        if event.width == _last_tab_width:
            return
        _last_tab_width = event.width
        
    tab_canvas.delete('all')
    _tab_rects.clear()
    _tab_texts.clear()
    cw = tab_canvas.winfo_width()
    if cw < 10:
        cw = 800
    sx = (cw - _TOTAL) / 2
    y1 = (_CH - _TH) / 2
    y2 = y1 + _TH
    for i, name in enumerate(_TAB_NAMES):
        x1 = sx + i * (_TW + _TG)
        x2 = x1 + _TW
        act = (i == _current_tab)
        rect = _rr(tab_canvas, x1, y1, x2, y2, _TR, fill=_CLR_ACT if act else _CLR_INA, outline='')
        txt = tab_canvas.create_text((x1+x2)/2, (y1+y2)/2, text=name,
                fill=_CLR_ACT_F if act else _CLR_INA_F,
                font=('Helvetica', 14, 'bold') if act else ('Helvetica', 14))
        _tab_rects.append(rect)
        _tab_texts.append(txt)
        for item in (rect, txt):
            tab_canvas.tag_bind(item, '<Button-1>', lambda e, idx=i: notebook.select(idx))
            tab_canvas.tag_bind(item, '<Enter>', lambda e, idx=i: _hover(idx, True))
            tab_canvas.tag_bind(item, '<Leave>', lambda e, idx=i: _hover(idx, False))

def _hover(idx, entering):
    if idx == _current_tab:
        return
    tab_canvas.itemconfig(_tab_rects[idx], fill=_CLR_HOV if entering else _CLR_INA)

def _tab_changed(*_):
    global _current_tab
    try:
        _current_tab = notebook.index(notebook.select())
    except Exception:
        _current_tab = 0
        
    try:
        if _current_tab == 1:  # Database Tab is active
            if platform.system() == 'Linux':
                root.bind_all("<Button-4>", _db_scroll_global)
                root.bind_all("<Button-5>", _db_scroll_global)
            else:
                root.bind_all("<MouseWheel>", _db_scroll_global)
        else:
            if platform.system() == 'Linux':
                root.unbind_all("<Button-4>")
                root.unbind_all("<Button-5>")
            else:
                root.unbind_all("<MouseWheel>")
    except Exception:
        pass
        
    _draw_tabs()

tab_canvas.bind('<Configure>', _draw_tabs)

class TabManager(tk.Frame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.tabs = []
        self._current_index = 0
        
    def add(self, frame, text=""):
        self.tabs.append(frame)
        if len(self.tabs) == 1:
            frame.pack(fill="both", expand=True)
            
    def select(self, idx=None):
        if idx is None:
            return self.tabs[self._current_index] if self.tabs else None
        if isinstance(idx, int) and 0 <= idx < len(self.tabs):
            if self.tabs[self._current_index].winfo_ismapped():
                self.tabs[self._current_index].pack_forget()
            self._current_index = idx
            self.tabs[self._current_index].pack(fill="both", expand=True)
            _tab_changed()
            
    def index(self, tab_id):
        if isinstance(tab_id, int): return tab_id
        if tab_id in self.tabs: return self.tabs.index(tab_id)
        return self._current_index

notebook = TabManager(main_frame, bg=_APP_BG)
notebook.pack(fill='both', expand=True)

# ================= TAB 1: GENERATE QUOTE =================
tab_generator = ttk.Frame(notebook)
notebook.add(tab_generator, text="Generate Quote")

frame_client = ttk.LabelFrame(tab_generator, text="1. Client Details", padding=10)
frame_client.pack(fill="x", pady=5, padx=10)
ttk.Label(frame_client, text="Quotation No:").grid(row=0, column=0, sticky="w")
quote_num_frame = ttk.Frame(frame_client)
quote_num_frame.grid(row=0, column=1, sticky="w", pady=2, padx=5)
entry_quote_number = tk.Entry(quote_num_frame, width=20)
entry_quote_number.pack(side="left")
ttk.Label(quote_num_frame, text="  (leave blank to auto-assign)", foreground="gray").pack(side="left")
ttk.Label(frame_client, text="Client Name:").grid(row=1, column=0, sticky="w")
entry_name = tk.Entry(frame_client, width=60)
entry_name.grid(row=1, column=1, pady=2, padx=5)
ttk.Label(frame_client, text="Project Location:").grid(row=2, column=0, sticky="w")
entry_location = tk.Entry(frame_client, width=60)
entry_location.grid(row=2, column=1, pady=2, padx=5)
ttk.Label(frame_client, text="Revision Version:").grid(row=3, column=0, sticky="w")
entry_version = tk.Entry(frame_client, width=60)
entry_version.insert(0, "1.0.0") 
entry_version.grid(row=3, column=1, pady=2, padx=5)
ttk.Label(frame_client, text="Discount %:").grid(row=4, column=0, sticky="w")
entry_discount = tk.Entry(frame_client, width=20)
entry_discount.insert(0, "0")
entry_discount.grid(row=4, column=1, sticky="w", pady=2, padx=5)

frame_products = ttk.LabelFrame(tab_generator, text="2. Add Products to Quote", padding=10)
frame_products.pack(fill="x", pady=5, padx=10)
ttk.Label(frame_products, text="Category:").grid(row=0, column=0, sticky="w")
combo_category = ttk.Combobox(frame_products, values=list(products_db.keys()), state="readonly", width=50)
combo_category.grid(row=0, column=1, pady=2, padx=5)
combo_category.bind("<<ComboboxSelected>>", update_product_dropdown)
ttk.Label(frame_products, text="Product:").grid(row=1, column=0, sticky="w")
combo_product = ttk.Combobox(frame_products, state="readonly", width=50)
combo_product.grid(row=1, column=1, pady=2, padx=5)

ttk.Label(frame_products, text="Room Name:").grid(row=2, column=0, sticky="w")
entry_room = tk.Entry(frame_products, width=30)
entry_room.grid(row=2, column=1, sticky="w", pady=2, padx=5)
ttk.Label(frame_products, text="(optional)", font=("Helvetica", 9, "italic")).grid(row=2, column=1, sticky="e", padx=5)

ttk.Label(frame_products, text="Quantity:").grid(row=3, column=0, sticky="w")
entry_qty = tk.Entry(frame_products, width=20)
entry_qty.grid(row=3, column=1, sticky="w", pady=2, padx=5)
ModernButton(frame_products, text="+ Add Product", width=130, height=34, radius=17, bg_color="#4CAF50", hover_color="#45a049", font=("Helvetica", 10, "bold"), command=add_product).grid(row=4, column=1, sticky="e", pady=5)

# Image Preview Label on the right side
lbl_product_preview = ttk.Label(frame_products, text="Preview", width=15, anchor="center")
lbl_product_preview.grid(row=0, column=2, rowspan=5, padx=20, pady=5)
combo_product.bind("<<ComboboxSelected>>", preview_product_image)
# Pack bottom elements FIRST so they reserve space (bottom-up order)
ModernButton(tab_generator, text="Generate PDF Quotation", width=250, height=45, radius=22, bg_color="#6A0dad", hover_color="#800080", font=("Helvetica", 12, "bold"), command=generate_pdf).pack(side="bottom", pady=8)

btn_frame = ttk.Frame(tab_generator)
btn_frame.pack(side="bottom", fill="x", padx=15, pady=(0, 5))
ModernButton(btn_frame, text="Remove Selected", width=140, height=32, radius=16, bg_color="#f44336", hover_color="#da190b", font=("Helvetica", 10, "bold"), command=remove_product).pack(side="left", padx=5)
ModernButton(btn_frame, text="Edit Quantity", width=120, height=32, radius=16, bg_color="#2196F3", hover_color="#0b7dda", font=("Helvetica", 10, "bold"), command=edit_quantity).pack(side="left", padx=5)
ModernButton(btn_frame, text="Clear List", width=100, height=32, radius=16, bg_color="#ff9800", hover_color="#e68a00", font=("Helvetica", 10, "bold"), command=clear_list).pack(side="left", padx=5)

frame_list = ttk.LabelFrame(tab_generator, text="3. Items in Quotation", padding=5)
frame_list.pack(fill="both", expand=True, pady=(5, 0), padx=10)
tree = ttk.Treeview(frame_list, columns=("Category", "Product", "Qty", "Price"), show="headings", height=5)
for col, width in zip(("Category", "Product", "Qty", "Price"), (100, 250, 50, 70)):
    tree.heading(col, text=col)
    tree.column(col, width=width)
tree.pack(fill="both", expand=True)

# ================= TAB 2: DATABASE =================
tab_database = ttk.Frame(notebook)
notebook.add(tab_database, text="Database")

# Setup scrollable area for Database tab
db_canvas = tk.Canvas(tab_database, borderwidth=0, highlightthickness=0)
db_scrollbar = ttk.Scrollbar(tab_database, orient="vertical", command=db_canvas.yview)
scrollable_db_frame = ttk.Frame(db_canvas)

def _on_scrollable_db_configure(event):
    db_canvas.configure(scrollregion=db_canvas.bbox("all"))

scrollable_db_frame.bind("<Configure>", _on_scrollable_db_configure)

_last_db_canvas_width = 0
def _on_canvas_configure(event):
    global _last_db_canvas_width
    if event.width == _last_db_canvas_width:
        return
    _last_db_canvas_width = event.width
    db_canvas.itemconfig(canvas_window, width=event.width)

db_canvas.bind('<Configure>', _on_canvas_configure)
canvas_window = db_canvas.create_window((0, 0), window=scrollable_db_frame, anchor="nw")
db_canvas.configure(yscrollcommand=db_scrollbar.set)

db_canvas.pack(side="left", fill="both", expand=True)
db_scrollbar.pack(side="right", fill="y")

# ── Scroll fix ───────────────────────────────────────────────────────────────
# macOS sends <MouseWheel> to the FOCUSED widget, not the hovered one.
# Strategy:
#   1. root.bind_all catches everything globally.
#   2. For widgets inside the db frame that consume scroll themselves
#      (Entry, Combobox, Listbox, Text, Spinbox), we bind at the INSTANCE level
#      (which fires before the class handler) and return 'break' so the widget
#      never scrolls itself — the canvas scrolls instead.
#   That binding is applied in _apply_db_scroll_override() called before mainloop.

def _do_canvas_scroll(event):
    """Scroll db_canvas based on event.delta / button number."""
    try:
        if platform.system() == 'Windows':
            db_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        elif platform.system() == 'Darwin':
            db_canvas.yview_scroll(int(-1 * event.delta), "units")
        else:
            if event.num == 4:
                db_canvas.yview_scroll(-1, "units")
            elif event.num == 5:
                db_canvas.yview_scroll(1, "units")
    except Exception:
        pass

def _db_scroll_global(event):
    """Root-level handler: scroll canvas if mouse is hovering over it."""
    try:
        mx, my = event.x_root, event.y_root
        cx = db_canvas.winfo_rootx()
        cy = db_canvas.winfo_rooty()
        cw = db_canvas.winfo_width()
        ch = db_canvas.winfo_height()
        if cx <= mx <= cx + cw and cy <= my <= cy + ch:
            _do_canvas_scroll(event)
    except Exception:
        pass

# Global catch-all (fires last, after widget class handlers)
if platform.system() == 'Linux':
    root.bind_all('<Button-4>', _db_scroll_global)
    root.bind_all('<Button-5>', _db_scroll_global)
else:
    root.bind_all('<MouseWheel>', _db_scroll_global)

# Widget types that consume scroll and need to be overridden inside the db frame
_SCROLL_CONSUMING = (tk.Entry, tk.Listbox, tk.Text, tk.Spinbox,
                     ttk.Combobox, ttk.Spinbox, ttk.Entry)

def _widget_scroll_override(event):
    """Instance-level handler for widgets inside the db frame.
    Fires BEFORE the class handler; redirects scroll to canvas and stops propagation."""
    _do_canvas_scroll(event)
    return 'break'  # prevents the widget's own class-level scroll handler

def _apply_db_scroll_override(widget):
    """Walk the db frame tree and override scroll on any scroll-consuming widget."""
    if isinstance(widget, _SCROLL_CONSUMING):
        if platform.system() == 'Linux':
            widget.bind('<Button-4>', _widget_scroll_override)
            widget.bind('<Button-5>', _widget_scroll_override)
        else:
            widget.bind('<MouseWheel>', _widget_scroll_override)
    for child in widget.winfo_children():
        _apply_db_scroll_override(child)

# ---- Search / Browse panel ----
frame_search_db = ttk.LabelFrame(scrollable_db_frame, text="🔍  Browse & Search Products", padding=10)
frame_search_db.pack(fill="x", pady=(10, 0), padx=20)

search_db_row = ttk.Frame(frame_search_db)
search_db_row.pack(fill="x")
ttk.Label(search_db_row, text="Search:").pack(side="left", padx=(0, 5))
search_db_var = tk.StringVar()
entry_search_db = tk.Entry(search_db_row, textvariable=search_db_var, width=50)
entry_search_db.pack(side="left", padx=5)

db_browser_tree = ttk.Treeview(frame_search_db, columns=("Category", "Name", "Price", "Description"), show="headings", height=5)
for col, width in zip(("Category", "Name", "Price", "Description"), (150, 200, 90, 350)):
    db_browser_tree.heading(col, text=col)
    db_browser_tree.column(col, width=width)
db_browser_tree.pack(fill="x", pady=(5, 0))

def populate_db_browser(filter_text=""):
    for item in db_browser_tree.get_children():
        db_browser_tree.delete(item)
    q = filter_text.lower()
    for cat, prods in products_db.items():
        for p in prods:
            if (q in cat.lower() or q in p.get("name","").lower() or q in p.get("desc","").lower()):
                db_browser_tree.insert("", tk.END, values=(cat, p.get("name",""), p.get("price",""), p.get("desc","")))

def on_search_db_changed(*args):
    populate_db_browser(search_db_var.get())

search_db_var.trace_add("write", on_search_db_changed)
populate_db_browser()

def browse_image():
    filepath = filedialog.askopenfilename(title="Select Product Image", filetypes=[("Image Files", "*.png *.jpg *.jpeg")])
    if filepath:
        # Check if the file is in the images folder
        if "images/" in filepath:
            filepath = filepath.split("images/")[-1]
            filepath = get_data_path("images/" + filepath)
        entry_db_img.delete(0, tk.END)
        entry_db_img.insert(0, filepath)

def update_db_product_dropdown(event=None):
    cat = combo_db_category.get()
    if cat in products_db:
        products = [p["name"] for p in products_db[cat]]
        combo_db_name['values'] = products
    else:
        combo_db_name['values'] = []
    combo_db_name.set('')
    # Clear fields when category changes
    text_db_desc.delete("1.0", tk.END)
    entry_db_price.delete(0, tk.END)
    entry_db_img.delete(0, tk.END)

def load_product_details_for_editing(event=None):
    cat = combo_db_category.get()
    name = combo_db_name.get()
    if cat in products_db:
        prod = next((p for p in products_db[cat] if p["name"] == name), None)
        if prod:
            text_db_desc.delete("1.0", tk.END)
            text_db_desc.insert("1.0", prod.get("desc", ""))
            
            price_str = prod.get("price", "")
            entry_db_price.delete(0, tk.END)
            if price_str.startswith("EGP"):
                combo_currency.set("EGP")
                entry_db_price.insert(0, price_str.replace("EGP ", "").strip())
            elif price_str.startswith("$"):
                combo_currency.set("USD ($)")
                entry_db_price.insert(0, price_str.replace("$", "").strip())
            else:
                entry_db_price.insert(0, price_str.strip())
                
            entry_db_img.delete(0, tk.END)
            entry_db_img.insert(0, prod.get("image", ""))

def save_to_database():
    cat = combo_db_category.get().strip()
    name = combo_db_name.get().strip()
    desc = text_db_desc.get("1.0", tk.END).strip()
    raw_price = entry_db_price.get().strip()
    img = entry_db_img.get().strip()
    
    currency = combo_currency.get()
    if currency == "USD ($)":
        price = f"${raw_price}"
    else:
        price = f"EGP {raw_price}"
    
    if not cat or not name or not raw_price:
        messagebox.showerror("Error", "Category, Name, and Price are required.")
        return
        
    if cat not in products_db:
        products_db[cat] = []
        
    # Check if product already exists
    existing_product = next((p for p in products_db[cat] if p["name"] == name), None)
    
    if existing_product:
        existing_product["desc"] = desc
        existing_product["price"] = price
        existing_product["image"] = img
        action_msg = "updated"
    else:
        products_db[cat].append({
            "name": name,
            "desc": desc,
            "price": price,
            "image": img
        })
        action_msg = "added"
    
    # Save to file
    with open(get_data_path("database.json"), "w") as f:
        json.dump(products_db, f, indent=4)
        
    # Push to cloud
    sheets_sync.save_products_to_sheet(products_db)
    sheets_sync.sync_images_up()
        
    # Update UI Dropdowns
    combo_category['values'] = list(products_db.keys())
    combo_db_category['values'] = list(products_db.keys())
    combo_del_category['values'] = list(products_db.keys())
    update_db_product_dropdown()
    populate_db_browser(search_db_var.get())
    
    # Clear fields
    combo_db_name.set('')
    text_db_desc.delete("1.0", tk.END)
    entry_db_price.delete(0, tk.END)
    entry_db_img.delete(0, tk.END)
    
    messagebox.showinfo("Success", f"Product '{name}' {action_msg} successfully in {cat}!")

frame_add_db = ttk.LabelFrame(scrollable_db_frame, text="Add / Edit Product in Database", padding=15)
frame_add_db.pack(fill="x", pady=5, padx=20)

ttk.Label(frame_add_db, text="Category:").grid(row=0, column=0, sticky="w", pady=5)
combo_db_category = ttk.Combobox(frame_add_db, values=list(products_db.keys()), width=45)
combo_db_category.grid(row=0, column=1, pady=5, padx=5, sticky="w")
combo_db_category.bind("<<ComboboxSelected>>", update_db_product_dropdown)
ttk.Label(frame_add_db, text="(Type a new category name or select existing)", font=("Helvetica", 10, "italic")).grid(row=1, column=1, sticky="w", padx=5)

ttk.Label(frame_add_db, text="Product Name:").grid(row=2, column=0, sticky="w", pady=5)
combo_db_name = ttk.Combobox(frame_add_db, width=45)
combo_db_name.grid(row=2, column=1, pady=5, padx=5, sticky="w")
combo_db_name.bind("<<ComboboxSelected>>", load_product_details_for_editing)

ttk.Label(frame_add_db, text="Description:").grid(row=3, column=0, sticky="nw", pady=2)
text_db_desc = tk.Text(frame_add_db, width=45, height=3)
text_db_desc.grid(row=3, column=1, pady=2, padx=5, sticky="w")

ttk.Label(frame_add_db, text="Price (numbers only):").grid(row=4, column=0, sticky="w", pady=5)
price_frame = ttk.Frame(frame_add_db)
price_frame.grid(row=4, column=1, pady=5, padx=5, sticky="w")
entry_db_price = tk.Entry(price_frame, width=20)
entry_db_price.pack(side="left")
combo_currency = ttk.Combobox(price_frame, values=["USD ($)", "EGP"], state="readonly", width=10)
combo_currency.current(0)
combo_currency.pack(side="left", padx=5)

ttk.Label(frame_add_db, text="Image Path:").grid(row=5, column=0, sticky="w", pady=5)
img_frame = ttk.Frame(frame_add_db)
img_frame.grid(row=5, column=1, pady=5, padx=5, sticky="w")
entry_db_img = tk.Entry(img_frame, width=45)
entry_db_img.pack(side="left")
ModernButton(img_frame, text="Browse...", width=90, height=30, radius=15, bg_color="#607d8b", hover_color="#455a64", font=("Helvetica", 10, "bold"), command=browse_image).pack(side="left", padx=5)

ModernButton(frame_add_db, text="Save / Update Product", width=220, height=40, radius=20, bg_color="#4CAF50", hover_color="#45a049", font=("Helvetica", 12, "bold"), command=save_to_database).grid(row=6, column=1, pady=(10, 30), sticky="e")

# ================= DELETE FROM DATABASE =================
def update_del_product_dropdown(event=None):
    cat = combo_del_category.get()
    if cat in products_db:
        products = [p["name"] for p in products_db[cat]]
        combo_del_product['values'] = products
        if products:
            combo_del_product.current(0)
        else:
            combo_del_product.set('')
    else:
        combo_del_product['values'] = []
        combo_del_product.set('')

def delete_product():
    cat = combo_del_category.get()
    prod_name = combo_del_product.get()
    
    if not cat or not prod_name:
        messagebox.showerror("Error", "Select a category and product to delete.")
        return
        
    if cat in products_db:
        # Filter out the product
        original_count = len(products_db[cat])
        products_db[cat] = [p for p in products_db[cat] if p["name"] != prod_name]
        
        if len(products_db[cat]) < original_count:
            with open(get_data_path("database.json"), "w") as f:
                json.dump(products_db, f, indent=4)
            sheets_sync.save_products_to_sheet(products_db)
            update_del_product_dropdown()
            if combo_category.get() == cat:
                update_product_dropdown()
            messagebox.showinfo("Success", f"Product '{prod_name}' deleted successfully.")
        else:
            messagebox.showerror("Error", "Product not found.")

def delete_category():
    cat = combo_del_category.get()
    
    if not cat:
        messagebox.showerror("Error", "Select a category to delete.")
        return
        
    if cat in products_db:
        confirm = messagebox.askyesno("Confirm Delete", f"Are you sure you want to completely delete the category '{cat}' and all its products?")
        if confirm:
            del products_db[cat]
            with open(get_data_path("database.json"), "w") as f:
                json.dump(products_db, f, indent=4)
            sheets_sync.save_products_to_sheet(products_db)
            refresh_dropdowns()

            categories = list(products_db.keys())
            combo_category['values'] = categories
            combo_db_category['values'] = categories
            combo_del_category['values'] = categories
            
            if categories:
                combo_del_category.current(0)
                update_del_product_dropdown()
            else:
                combo_category.set('')
                combo_db_category.set('')
                combo_del_category.set('')
                combo_del_product['values'] = []
                combo_del_product.set('')
                
            messagebox.showinfo("Success", f"Category '{cat}' deleted successfully.")

frame_del_db = ttk.LabelFrame(scrollable_db_frame, text="Delete from Database", padding=10)
frame_del_db.pack(fill="x", pady=5, padx=20)

ttk.Label(frame_del_db, text="Category:").grid(row=0, column=0, sticky="w", pady=5)
combo_del_category = ttk.Combobox(frame_del_db, values=list(products_db.keys()), state="readonly", width=35)
combo_del_category.grid(row=0, column=1, pady=5, padx=5, sticky="w")
combo_del_category.bind("<<ComboboxSelected>>", update_del_product_dropdown)

ModernButton(frame_del_db, text="Delete Category", width=140, height=32, radius=16, bg_color="#f44336", hover_color="#da190b", font=("Helvetica", 10, "bold"), command=delete_category).grid(row=0, column=2, padx=5, pady=5, sticky="w")

ttk.Label(frame_del_db, text="Product:").grid(row=1, column=0, sticky="w", pady=5)
combo_del_product = ttk.Combobox(frame_del_db, state="readonly", width=35)
combo_del_product.grid(row=1, column=1, pady=5, padx=5, sticky="w")

ModernButton(frame_del_db, text="Delete Product", width=140, height=32, radius=16, bg_color="#f44336", hover_color="#da190b", font=("Helvetica", 10, "bold"), command=delete_product).grid(row=1, column=2, padx=5, pady=5, sticky="w")

# ================= TAB 3: HISTORY =================
tab_history = ttk.Frame(notebook)
notebook.add(tab_history, text="History")

frame_history = ttk.LabelFrame(tab_history, text="Past Quotations", padding=10)
frame_history.pack(fill="both", expand=True, pady=10, padx=20)

history_tree = ttk.Treeview(frame_history, columns=("QT No", "Date", "Client", "Location", "Version"), show="headings", height=15)
for col, width in zip(("QT No", "Date", "Client", "Location", "Version"), (110, 130, 200, 150, 80)):
    history_tree.heading(col, text=col)
    history_tree.column(col, width=width)
history_tree.pack(fill="both", expand=True)

hist_btn_frame = ttk.Frame(tab_history)
hist_btn_frame.pack(fill="x", pady=10, padx=10)

ModernButton(hist_btn_frame, text="Load & Edit", width=130, height=36, radius=18, bg_color="#2196F3", hover_color="#0b7dda", font=("Helvetica", 11, "bold"), command=load_quotation).pack(side="left", padx=5)
ModernButton(hist_btn_frame, text="Duplicate", width=120, height=36, radius=18, bg_color="#ff9800", hover_color="#e68900", font=("Helvetica", 10, "bold"), command=duplicate_quotation).pack(side="left", padx=5)
ModernButton(hist_btn_frame, text="Delete Entry", width=120, height=36, radius=18, bg_color="#f44336", hover_color="#da190b", font=("Helvetica", 10, "bold"), command=delete_history_entry).pack(side="left", padx=5)
ModernButton(hist_btn_frame, text="Refresh List", width=120, height=36, radius=18, bg_color="#607d8b", hover_color="#455a64", font=("Helvetica", 10, "bold"), command=refresh_history_tree).pack(side="left", padx=5)

def manual_sync():
    """Manually push local data to cloud and pull remote data."""
    global products_db
    if not sheets_sync.is_sync_available():
        if sheets_sync.init_sync():
            messagebox.showinfo("Sync", "Successfully connected to Google Sheets!")
        else:
            messagebox.showwarning("Sync", "Sync failed. Check credentials.json, config.json, and internet connection.")
            return
    
    # Push local data up first
    sheets_sync.save_products_to_sheet(products_db)
    history = load_history()
    sheets_sync.save_history_to_sheet(history)
    sheets_sync.sync_images_up()
    
    # Then pull remote data down
    products, history = sheets_sync.pull_all()
    if products is not None and history is not None:
        products_db = products
        with open(get_data_path("database.json"), "w") as f:
            json.dump(products, f, indent=4)
        with open(HISTORY_FILE, "w") as f:
            json.dump(history, f, indent=4)
            
        refresh_dropdowns()
        refresh_history_tree()
        messagebox.showinfo("Sync", "Data synchronized successfully!\nLocal data pushed & remote data pulled.")
    else:
        messagebox.showerror("Sync", "Error pulling data from Google Sheets.")

ModernButton(hist_btn_frame, text="Sync Now (Cloud)", width=150, height=36, radius=18, bg_color="#6A0dad", hover_color="#800080", font=("Helvetica", 10, "bold"), command=manual_sync).pack(side="right", padx=5)

# Initialize History List
try:
    refresh_history_tree()
except:
    pass


# --- ABOUT TAB ---
tab_about = ttk.Frame(notebook)
notebook.add(tab_about, text="About")

about_container = tk.Frame(tab_about, bg=_APP_BG)
about_container.place(relx=0.5, rely=0.5, anchor="center")

try:
    lbl_about_logo = ttk.Label(about_container, image=logo_photo)
    lbl_about_logo.pack(pady=20)
except:
    pass

ttk.Label(about_container, text="X Nova Quotation App", font=("Helvetica", 24, "bold")).pack(pady=10)
ttk.Label(about_container, text=f"Version {APP_VERSION}", font=("Helvetica", 14)).pack(pady=5)
ttk.Label(about_container, text="Built for X Nova Smart Spaces", font=("Helvetica", 12, "italic"), foreground="#888888").pack(pady=(0, 30))

ModernButton(about_container, text="Check for Updates", width=220, height=45, radius=22, 
             bg_color="#2196F3", hover_color="#0b7dda", font=("Helvetica", 14, "bold"), 
             command=lambda: check_for_updates(manual=True)).pack(pady=10)


# Apply instance-level scroll override to all scroll-consuming widgets inside
# the database frame (Entry, Combobox, Listbox, etc.) so they don't swallow
# the scroll event — the canvas scrolls instead.
_apply_db_scroll_override(scrollable_db_frame)

# Check for updates when the app starts
check_for_updates()

root.mainloop()