import tkinter as tk
from screeninfo import get_monitors
from settings_manager import load_settings, save_settings
from video_handler import play_video, stop_video
from ui_helpers import labeled_entry, labeled_entry_with_browse
from app_logic import show_help_message, toggle_pause, close_timer

def apply_settings():

    save_settings({
        "TIMER_MINUTES" : int(timer_entry.get()),
        "VIDEO_PATH" : video_entry.get(),
        "HELP_TRACK" : help_entry.get(),
        "INTERVAL_SOUND" : interval_entry.get(),
        "TIME_OVER_SOUND" : end_entry.get(),
        "TIMER_FONT" : (timer_font_entry.get(), int(timer_fontsize_entry.get())),
        "HELP_FONT" : (help_font_entry.get(), int(help_fontsize_entry.get())),
        "TEXT_COLOR" : text_color_entry.get(),
        "BACKGROUND_COLOR" : background_color_entry.get(),
        "BACKGROUND_IMAGE_TIMER": background_image_timer_entry.get(),
        "BACKGROUND_IMAGE_HELP": background_image_help_entry.get(),
        "MONITOR" : selected_monitor.get(),
        "MENU_BACKGROUND_COLOR" : menu_background_color_entry.get(),
        "MENU_HEADING_COLOR" : menu_heading_color_entry.get(),
    })

    confirm_label = tk.Label(settings_frame, text="Settings applied!", fg="green", bg="black")
    confirm_label.pack()
    settings_frame.after(1500, confirm_label.destroy)

    refresh_menu_colors(control_frame)
    # Return to controls after 1.5 seconds
    settings_frame.after(1500, lambda: (
        settings_frame.pack_forget(),
        control_frame.pack(fill="both", expand=True)
    ))

def refresh_menu_colors(frame):
    settings = load_settings()

    bg_color = settings.get("MENU_BACKGROUND_COLOR", "black")
    fg_color = settings.get("MENU_HEADING_COLOR", "yellow")

    # Update this widget if it’s a frame or label/text
    if isinstance(frame, (tk.Frame, tk.Label, tk.Text)):
        frame.configure(bg=bg_color)
        if isinstance(frame, (tk.Label, tk.Text)):
            frame.configure(fg=fg_color)
        # For Text, also update cursor
        if isinstance(frame, tk.Text):
            frame.config(insertbackground=fg_color)

    # Recurse into children
    for child in frame.winfo_children():
        # Skip buttons
        if isinstance(child, tk.Button):
            continue
        refresh_menu_colors(child)

    help_text.config(insertbackground="white", fg="white")
    controller_timer_label.config(fg=settings.get("TEXT_COLOR"))

def send_help_message():
    message = help_text.get("1.0", tk.END).strip()
    if message:
        show_help_message(message,font=settings.get("HELP_FONT", ""),
                        fg=settings.get("TEXT_COLOR", ""),
                        bg=settings.get("BACKGROUND_COLOR", ""),
                        sound=settings.get("HELP_TRACK", ""))
        help_text.delete("1.0", tk.END)

# --- Initialization ---
root = tk.Tk()
root.title("Escape Room Controller")
root.geometry("900x700")
# Load saved settings
settings = load_settings()
MENU_BACKGROUND_COLOR = settings.get("MENU_BACKGROUND_COLOR", "black")
MENU_HEADING_COLOR = settings.get("MENU_HEADING_COLOR", "red")

root.configure(bg=MENU_BACKGROUND_COLOR)

monitors = get_monitors()
selected_monitor = tk.StringVar(value=settings.get("MONITOR", monitors[0].name))

# --- Frames ---
control_frame = tk.Frame(root, bg=settings.get("MENU_BACKGROUND_COLOR", "black"))
control_frame.pack(fill="both", expand=True)

settings_frame = tk.Frame(root, bg=settings.get("MENU_BACKGROUND_COLOR", "black"))

# --- Navigation ---
def show_settings():
    control_frame.pack_forget()
    settings_frame.pack(fill="both", expand=True)

def cancel_settings():
    settings_frame.pack_forget()
    control_frame.pack(fill="both", expand=True)

# --- SETTINGS TOGGLE BUTTON ---
settings_btn_control = tk.Button(
    control_frame,
    text="⚙️ Settings",
    font=("Arial", 12, "bold"),
    bg="gray20",
    fg="white",
    activebackground="gray35",
    command=lambda: show_settings()
)
settings_btn_control.pack(anchor="ne", padx=10, pady=10)

settings_btn_settings = tk.Button(
    settings_frame,
    text="⚙️ Settings",
    font=("Arial", 12, "bold"),
    bg="gray20",
    fg="white",
    activebackground="gray35",
    command=lambda: cancel_settings()
)
settings_btn_settings.pack(anchor="ne", padx=10, pady=10)


# --- SETTINGS PANEL ---
video_entry = labeled_entry_with_browse(settings_frame,
    "Video Path:", settings.get("VIDEO_PATH", ""), (("MP4 files", "*.mp4"),)
)
help_entry = labeled_entry_with_browse(settings_frame,
    "Help Track:", settings.get("HELP_TRACK", ""), (("MP3 files", "*.mp3"),)
)
interval_entry = labeled_entry_with_browse(settings_frame,
    "Interval Track:", settings.get("INTERVAL_SOUND", ""), (("MP3 files", "*.mp3"),)
)
end_entry = labeled_entry_with_browse(settings_frame,
    "End Track:", settings.get("TIME_OVER_SOUND", ""), (("MP3 files", "*.mp3"),)
)

background_color_entry = labeled_entry(settings_frame, "Background Color:", settings.get("BACKGROUND_COLOR", ""), 10)
background_image_timer_entry = labeled_entry_with_browse(settings_frame,
    "Timer Image:", settings.get("BACKGROUND_IMAGE_TIMER", ""),
    (("Image Files", "*.png;*.jpg;*.jpeg;*.gif"), ("All files", "*.*"))
)

background_image_help_entry = labeled_entry_with_browse(settings_frame,
    "Help Image:", settings.get("BACKGROUND_IMAGE_HELP", ""),
    (("Image Files", "*.png;*.jpg;*.jpeg;*.gif"), ("All files", "*.*"))
)

text_color_entry = labeled_entry(settings_frame, "Text Color:", settings.get("TEXT_COLOR", ""), 10)
menu_background_color_entry = labeled_entry(settings_frame, "Menu Background:", MENU_BACKGROUND_COLOR, 10)
menu_heading_color_entry = labeled_entry(settings_frame, "Menu Heading:", MENU_HEADING_COLOR, 10)

timer_fontsize_entry = labeled_entry(settings_frame, "Timer Font Size:", settings.get("TIMER_FONT", "")[1], width=10)
timer_font_entry = labeled_entry(settings_frame, "Timer Font:", settings.get("TIMER_FONT", "")[0], width=20)
help_fontsize_entry = labeled_entry(settings_frame, "Help Font Size:", settings.get("HELP_FONT", "")[1], width=10)
help_font_entry = labeled_entry(settings_frame, "Help Font:", settings.get("HELP_FONT", "")[0], width=20)
timer_entry = labeled_entry(settings_frame, "Time (minutes):", settings.get("TIMER_MINUTES", ""), width=10)

# Monitor dropdown
monitor_frame = tk.Frame(settings_frame, bg=MENU_BACKGROUND_COLOR)
monitor_frame.pack(fill="x", pady=3, padx=10)
tk.Label(monitor_frame, text="Select Monitor:", bg=MENU_BACKGROUND_COLOR, fg="yellow").pack(side="left")
monitor_menu = tk.OptionMenu(monitor_frame, selected_monitor, *[m.name for m in monitors])
monitor_menu.pack(side="left", padx=5)

# Apply and cancel
btn_frame = tk.Frame(settings_frame, bg=MENU_BACKGROUND_COLOR)
btn_frame.pack(pady=10)
apply_btn = tk.Button(btn_frame, text="Apply Settings", command=apply_settings)
apply_btn.pack(side="left", padx=10)
cancel_btn = tk.Button(btn_frame, text="Cancel", command=cancel_settings)
cancel_btn.pack(side="left", padx=10)

# --- CONTROL CONTENT ---
timer_frame = tk.Frame(control_frame, bg=MENU_BACKGROUND_COLOR)
timer_frame.pack(pady=5)

video_heading = tk.Label(timer_frame, text="Video Control", font=("Arial", 18, "bold"), fg=MENU_HEADING_COLOR, bg=MENU_BACKGROUND_COLOR)
video_heading.pack(pady=(10, 10)) 

video_frame = tk.Frame(timer_frame, bg=MENU_BACKGROUND_COLOR)
video_frame.pack(pady=5)

play_btn = tk.Button(video_frame, text="Play Video", command=lambda: play_video(root, controller_timer_label))
play_btn.pack(side=tk.LEFT, padx=5)

stop_btn = tk.Button(video_frame, text="Stop Video", command=stop_video)
stop_btn.pack(side=tk.LEFT, padx=5)

timer_heading = tk.Label(timer_frame, text="Timer Control", font=("Arial", 18, "bold"), fg=MENU_HEADING_COLOR, bg=MENU_BACKGROUND_COLOR)
timer_heading.pack(pady=(10, 10)) 

controller_timer_label = tk.Label(timer_frame, text="", font=("Arial", 20), fg=settings.get("TEXT_COLOR", ""), bg=MENU_BACKGROUND_COLOR)
controller_timer_label.pack(pady=10)

pause_btn = tk.Button(control_frame, text="Pause/Resume", command=toggle_pause)
pause_btn.pack(pady=10)

reset_btn = tk.Button(control_frame, text="Close timer", command=close_timer)
reset_btn.pack(pady=10)

help_heading = tk.Label(control_frame, text="Send Help Message", font=("Arial", 18, "bold"), fg=MENU_HEADING_COLOR, bg=MENU_BACKGROUND_COLOR)
help_heading.pack(pady=(20, 0))

help_frame = tk.Frame(control_frame, bg=MENU_BACKGROUND_COLOR)
help_frame.pack(pady=5, fill="x")

help_text = tk.Text(help_frame, height=4, width=70, font=("Arial", 14), fg="white", bg=MENU_BACKGROUND_COLOR)
help_text.pack(side=tk.LEFT, padx=60, pady=5)

help_text.config(insertbackground="white", fg="white")

send_btn = tk.Button(control_frame, text="Send", command=send_help_message)
send_btn.pack(pady=10)

root.protocol("WM_DELETE_WINDOW", lambda: (stop_video(), root.destroy()))
root.mainloop()
