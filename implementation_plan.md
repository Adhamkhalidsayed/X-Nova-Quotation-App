# Goal Description
The user wants product images to appear directly inside the dropdown menu next to each item, and for the dropdown menu to automatically open when typing to search.

## Technical Context & Tkinter Limitation
> [!WARNING]
> Standard Tkinter dropdowns (`ttk.Combobox`) **do not support images** inside the list. They can only display plain text. Additionally, they do not easily support auto-opening the menu while typing without glitching.

## Proposed Changes: The Custom Dropdown
To achieve exactly what you want, I will build a **Custom Searchable Image Dropdown** from scratch to replace the standard one:

### 1. The Search Entry
- I will replace the product dropdown with a standard text entry box.
- As you type in this box, it will immediately trigger a custom popup list.

### 2. The Custom Image Popup
- When you type (or click the box), a custom dropdown window will appear directly below it.
- This popup will use a `Treeview` widget, which *does* support displaying images next to text.
- As you type, the popup will instantly filter the list and show the product names with their **thumbnail images right beside them**.
- Clicking an item in this list will select it and hide the popup.

## Verification Plan
- Create a `CustomDropdown` logic using `tk.Toplevel` and `ttk.Treeview`.
- Pre-load and resize all product images when the category is selected to ensure the dropdown is fast.
- Ensure the custom popup opens automatically on keypress and closes when an item is selected or focus is lost.
