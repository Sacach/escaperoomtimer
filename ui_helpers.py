import tkinter as tk
from tkinter import filedialog

def browse_file(entry_widget, filetypes=(("All files", "*.*"),)):
    filename = filedialog.askopenfilename(filetypes=filetypes)
    if filename:
        entry_widget.delete(0, tk.END)
        entry_widget.insert(0, filename)

def labeled_entry(parent, label_text, default_value="", width=50, bg_color="black", font_color ="yellow"):
    frame = tk.Frame(parent, bg=bg_color)
    frame.pack(pady=3, padx=10, anchor="w")
    label = tk.Label(frame, text=label_text, bg=bg_color, fg=font_color, width=15, anchor="w")
    label.grid(row=0, column=0, sticky="w")
    entry = tk.Entry(frame, width=width)
    entry.insert(0, str(default_value))
    entry.grid(row=0, column=1, padx=5, sticky="we")
    frame.grid_columnconfigure(1, weight=1)
    return entry

def labeled_entry_with_browse(parent, label_text, default_value, filetypes, bg_color="black",  font_color ="yellow"):
    frame = tk.Frame(parent, bg=bg_color)
    frame.pack(pady=3, padx=10, anchor="w")
    label = tk.Label(frame, text=label_text, bg=bg_color, fg=font_color, width=15, anchor="w")
    label.grid(row=0, column=0, sticky="w")
    entry = tk.Entry(frame, width=50)
    entry.insert(0, default_value)
    entry.grid(row=0, column=1, padx=5, sticky="we")
    tk.Button(frame, text="Browse",
              command=lambda: browse_file(entry, filetypes)).grid(row=0, column=2, padx=5)
    frame.grid_columnconfigure(1, weight=1)
    return entry
