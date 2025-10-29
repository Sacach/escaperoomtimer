import json
import os
import time
import threading
import pygame
import subprocess
import tkinter as tk
import pygetwindow as gw
from screeninfo import get_monitors
from tkinter import filedialog

VLC_PATH= r"C:/Program Files/VideoLAN/VLC/vlc.exe"

TIMER_MINUTES = 60
FONT_SIZE_TIMER = 500
FONT_SIZE_HELP = 65
VIDEO_PATH = "isadora-video.mp4"
HELP_TRACK = "test_laugh.mp3"
INTERVAL_SOUND = "scream.mp3"
TIME_OVER_SOUND = "Rituaali.mp3"
TIMER_FONT = ("UnifrakturCook", FONT_SIZE_TIMER)
HELP_FONT = ("Rubik Distressed", FONT_SIZE_HELP)
BACKGROUND_COLOR = "black"
TEXT_COLOR = "red"
SETTINGS_FILE = "escaperoom_settings.json"



HELP_DURATION = 20000
DELAY_AFTER_VIDEO = 1
SOUND_ON_FINISH = True
RUNNING = True

timer_window = None
video = None

pygame.mixer.init()

monitors = get_monitors()

root = tk.Tk()
selected_monitor = tk.StringVar(value=monitors[0].name)

#print(monitors)

def load_settings():
    global VIDEO_PATH, HELP_TRACK, INTERVAL_SOUND
    global TIME_OVER_SOUND, TIMER_FONT, HELP_FONT
    global TIMER_MINUTES, MONITOR, TEXT_COLOR, BACKGROUND_COLOR

    if not os.path.exists(SETTINGS_FILE):
        #print("No saved settings found — using defaults.")
        return

    with open(SETTINGS_FILE, "r") as f:
        settings = json.load(f)

    VIDEO_PATH = settings.get("VIDEO_PATH", VIDEO_PATH)
    HELP_TRACK = settings.get("HELP_TRACK", HELP_TRACK)
    INTERVAL_SOUND = settings.get("INTERVAL_SOUND", INTERVAL_SOUND)
    TIME_OVER_SOUND = settings.get("TIME_OVER_SOUND", TIME_OVER_SOUND)
    TIMER_FONT = tuple(settings.get("TIMER_FONT", TIMER_FONT))
    HELP_FONT = tuple(settings.get("HELP_FONT", HELP_FONT))
    TIMER_MINUTES = int(settings.get("TIMER_MINUTES", TIMER_MINUTES))
    BACKGROUND_COLOR = settings.get("BACKGROUND_COLOR", BACKGROUND_COLOR)
    TEXT_COLOR = settings.get("TEXT_COLOR", TEXT_COLOR)

    # Monitor handling
    for m in monitors:
        if m.name == settings.get("MONITOR"):
            MONITOR = m
            selected_monitor.set(m.name)
            break
    #print("Settings loaded")

load_settings()

def fix_path(path):
    return path.replace("/", "\\")

def play_video():
    def target():
        global video

        video = subprocess.Popen([
            fix_path(VLC_PATH),
            fix_path(VIDEO_PATH),
            "--fullscreen",
            "--no-video-title-show",
            "--play-and-exit"
        ])

        time.sleep(2)
        windows = [w for w in gw.getAllTitles() if "VLC" in w]
        if windows:
            win = gw.getWindowsWithTitle(windows[0])[0]
            print(MONITOR)
            win.moveTo(MONITOR.x, MONITOR.y)
            win.resizeTo(MONITOR.width, MONITOR.height)
        
        video.wait()

        #print("Video finished!")
        root.after(0, show_timer)

    t = threading.Thread(target=target)
    t.daemon = True
    t.start()

def stop_video():
    global video
    if video:
        video.terminate()

def play_sound(filepath, duration_ms=None):
    def target():
        sound = pygame.mixer.Sound(filepath)
        channel = sound.play()
        if duration_ms:
            time.sleep(duration_ms / 1000)
            channel.stop()
        else:
            while channel.get_busy():
                time.sleep(0.05)
    threading.Thread(target=target, daemon=True).start()

def show_help_message(message, duration=HELP_DURATION):
    global help_win
    help_win = tk.Toplevel()

    help_win.geometry(f"{MONITOR.width}x{MONITOR.height}+{MONITOR.x}+{MONITOR.y}")
    help_win.overrideredirect(True)
    help_win.configure(bg=BACKGROUND_COLOR)
    
    help_label = tk.Label(help_win, text=message, wraplength=1900, font=HELP_FONT, fg=TEXT_COLOR, bg=BACKGROUND_COLOR)
    help_label.pack(expand=True)

    play_sound(HELP_TRACK, duration_ms=duration)
    help_win.after(duration, help_win.destroy)

def show_timer(duration_seconds=None):
    if duration_seconds is None:
        duration_seconds = TIMER_MINUTES * 60
    global timer_window, RUNNING
    if timer_window:
        timer_window.destroy()

    timer_window = tk.Toplevel(root)
    timer_window.configure(bg=BACKGROUND_COLOR)
    timer_window.overrideredirect(True)
    timer_window.geometry(f"{MONITOR.width}x{MONITOR.height}+{MONITOR.x}+{MONITOR.y}")

    timer_label = tk.Label(timer_window, text="", font=TIMER_FONT, fg=TEXT_COLOR, bg=BACKGROUND_COLOR)
    timer_label.pack(expand=True)

    def update():
        nonlocal duration_seconds
        minutes, seconds = divmod(duration_seconds, 60)
        timer_label.config(text=f"{minutes:02}:{seconds:02}")
        controller_timer_label.config(text=f"{minutes:02}:{seconds:02}")

        if RUNNING == True and duration_seconds > 0:
            duration_seconds -= 1
            if duration_seconds == 0:
                pass
            elif duration_seconds % 900 == 0:
                play_sound(INTERVAL_SOUND)
            timer_window.after(1000, update)
        elif RUNNING == False:
            timer_window.after(1000, update)
        else:
            timer_window.update_idletasks()
            play_sound(TIME_OVER_SOUND)
            return
    update()

def on_close():
    global video, timer_window
    if video:
        video.terminate()
        video = None
    if timer_window:
        timer_window.destroy()
        timer_window = None
    root.destroy()

def toggle_pause():
    global RUNNING
    RUNNING = not RUNNING

def send_help_message():
    message = help_text.get("1.0", tk.END).strip()
    if message:
        show_help_message(message)
        help_text.delete("1.0", tk.END)

def close_timer():
    global timer_window
    if timer_window:
        timer_window.destroy()
        timer_window = None

def apply_settings():
    global VIDEO_PATH, HELP_TRACK, INTERVAL_SOUND
    global TIME_OVER_SOUND, TIMER_FONT, HELP_FONT
    global TIMER_MINUTES, MONITOR, TEXT_COLOR, BACKGROUND_COLOR

    TIMER_MINUTES = int(timer_entry.get())
    VIDEO_PATH = video_entry.get()
    HELP_TRACK = help_entry.get()
    INTERVAL_SOUND = interval_entry.get()
    TIME_OVER_SOUND = end_entry.get()
    TIMER_FONT = (timer_font_entry.get(), int(timer_fontsize_entry.get()))
    HELP_FONT = (help_font_entry.get(), int(help_fontsize_entry.get()))
    TEXT_COLOR = text_color_entry.get()
    BACKGROUND_COLOR = background_color_entry.get()

    for m in monitors:
        if m.name == selected_monitor.get():
            MONITOR = m
            print(f"Switched to monitor: {MONITOR}")
            break

    save_settings()

    confirm_label = tk.Label(settings_frame, text="Settings applied!", fg="green", bg="black")
    confirm_label.pack()
    settings_frame.after(1500, confirm_label.destroy)

    # Return to controls after 2 seconds
    settings_frame.after(2000, lambda: (
        settings_frame.pack_forget(),
        control_frame.pack(fill="both", expand=True)
    ))

def save_settings():
    settings = {
        "VIDEO_PATH": VIDEO_PATH,
        "HELP_TRACK": HELP_TRACK,
        "INTERVAL_SOUND": INTERVAL_SOUND,
        "TIME_OVER_SOUND": TIME_OVER_SOUND,
        "TIMER_FONT": TIMER_FONT,
        "HELP_FONT": HELP_FONT,
        "TIMER_MINUTES": TIMER_MINUTES,
        "BACKGROUND_COLOR" : BACKGROUND_COLOR,
        "TEXT_COLOR" : TEXT_COLOR,
        "MONITOR": selected_monitor.get()
    }
    with open(SETTINGS_FILE, "w") as f:
        json.dump(settings, f, indent=4)
    #print("Settings saved")

def browse_file(entry_widget, filetypes=(("All files", "*.*"),)):
    filename = filedialog.askopenfilename(filetypes=filetypes)
    if filename:
        entry_widget.delete(0, tk.END)
        entry_widget.insert(0, filename)


root.title("Escape Room Controller")
root.geometry("900x700")
root.protocol("WM_DELETE_WINDOW", on_close)

print(BACKGROUND_COLOR)
root.configure(bg=BACKGROUND_COLOR)

# --- SETTINGS TOGGLE BUTTON ---
toggle_btn = tk.Button(
    root,
    text="⚙️ Settings",
    font=("Arial", 12, "bold"),
    bg="gray20",
    fg="white",
    activebackground="gray35",
    command=lambda: show_settings()
)
toggle_btn.pack(anchor="ne", padx=15, pady=10)

# --- CONTROL FRAME ---
control_frame = tk.Frame(root, bg=BACKGROUND_COLOR)
control_frame.pack(fill="both", expand=True)

# --- SETTINGS FRAME ---
settings_frame = tk.Frame(root, bg=BACKGROUND_COLOR)
# no pack yet — hidden at start

def show_settings():
    control_frame.pack_forget()
    settings_frame.pack(fill="both", expand=True)

def cancel_settings():
    settings_frame.pack_forget()
    control_frame.pack(fill="both", expand=True)

# --- SETTINGS CONTENT ---
def labeled_entry(label_text, default_value="", width=50):
    frame = tk.Frame(settings_frame, bg="black")
    frame.pack(fill="x", pady=3, padx=10)

    # Label on the left — fixed width so all fields align
    label = tk.Label(frame, text=label_text, bg="black", fg="yellow", width=15, anchor="w")
    label.grid(row=0, column=0, sticky="w")

    # Entry field (or could be replaced by a dropdown later)
    entry = tk.Entry(frame, width=width)
    entry.insert(0, str(default_value))
    entry.grid(row=0, column=1, padx=5, sticky="w")

    # Allow entry column to expand when window resizes
    frame.grid_columnconfigure(1, weight=1)

    return entry

def labeled_entry_with_browse(label_text, default_value, filetypes):
    frame = tk.Frame(settings_frame, bg="black")
    frame.pack(fill="x", pady=3, padx=10)

    # Label on the left (fixed width)
    label = tk.Label(frame, text=label_text, bg="black", fg="yellow", width=15, anchor="w")
    label.grid(row=0, column=0, sticky="w")

    # Entry field in the middle (expands)
    entry = tk.Entry(frame, width=50)
    entry.insert(0, default_value)
    entry.grid(row=0, column=1, padx=5, sticky="we")

    # Browse button on the right
    tk.Button(frame, text="Browse",
              command=lambda: browse_file(entry, filetypes)).grid(row=0, column=2, padx=5)

    # Make column 1 (entry) expand with window
    frame.grid_columnconfigure(1, weight=1)

    return entry

# --- Now create all your fields ---
video_entry = labeled_entry_with_browse("Video Path:", VIDEO_PATH,
    (("MP4 files", "*.mp4"), ("All files", "*.*")))

help_entry = labeled_entry_with_browse("Help Track:", HELP_TRACK,
    (("MP3 files", "*.mp3"), ("All files", "*.*")))

interval_entry = labeled_entry_with_browse("Interval Track:", INTERVAL_SOUND,
    (("MP3 files", "*.mp3"), ("All files", "*.*")))

end_entry = labeled_entry_with_browse("End Track:", TIME_OVER_SOUND,
    (("MP3 files", "*.mp3"), ("All files", "*.*")))

timer_fontsize_entry = labeled_entry("Timer Font Size:", TIMER_FONT[1], width=10)
timer_font_entry = labeled_entry("Timer Font:", TIMER_FONT[0], width=20)
help_fontsize_entry = labeled_entry("Help Font Size:", HELP_FONT[1], width=10)
help_font_entry = labeled_entry("Help Font:", HELP_FONT[0], width=20)
text_color_entry = labeled_entry("Text color:", TEXT_COLOR, width=10)
background_color_entry = labeled_entry("Background color:", BACKGROUND_COLOR, width=10)

timer_entry = labeled_entry("Time (minutes):", TIMER_MINUTES, width=10)

# Monitor dropdown
monitor_frame = tk.Frame(settings_frame, bg="black")
monitor_frame.pack(fill="x", pady=3, padx=10)
tk.Label(monitor_frame, text="Select Monitor:", bg="black", fg="yellow").pack(side="left")
monitor_menu = tk.OptionMenu(monitor_frame, selected_monitor, *[m.name for m in monitors])
monitor_menu.pack(side="left", padx=5)

# Apply + Cancel buttons
btn_frame = tk.Frame(settings_frame, bg="black")
btn_frame.pack(pady=10)
apply_btn = tk.Button(btn_frame, text="Apply Settings", command=apply_settings)
apply_btn.pack(side="left", padx=10)
cancel_btn = tk.Button(btn_frame, text="Cancel", command=cancel_settings)
cancel_btn.pack(side="left", padx=10)

# --- CONTROL CONTENT ---
timer_frame = tk.Frame(control_frame, bg="black")
timer_frame.pack(pady=5)

video_heading = tk.Label(timer_frame, text="Video Control", font=("Arial", 18, "bold"), fg="green", bg="black")
video_heading.pack(pady=(10, 10)) 

video_frame = tk.Frame(timer_frame, bg="black")
video_frame.pack(pady=5)

play_btn = tk.Button(video_frame, text="Play Video", command=play_video)
play_btn.pack(side=tk.LEFT, padx=5)

stop_btn = tk.Button(video_frame, text="Stop Video", command=stop_video)
stop_btn.pack(side=tk.LEFT, padx=5)

timer_heading = tk.Label(timer_frame, text="Timer Control", font=("Arial", 18, "bold"), fg="green", bg="black")
timer_heading.pack(pady=(10, 10)) 

controller_timer_label = tk.Label(timer_frame, text="", font=("Arial", 20), fg=TEXT_COLOR, bg="black")
controller_timer_label.pack(pady=10)

pause_btn = tk.Button(control_frame, text="Pause/Resume", command=toggle_pause)
pause_btn.pack(pady=10)

reset_btn = tk.Button(control_frame, text="Close timer", command=close_timer)
reset_btn.pack(pady=10)

help_heading = tk.Label(control_frame, text="Send Help Message", font=("Arial", 18, "bold"), fg="green", bg="black")
help_heading.pack(pady=(20, 0))

help_frame = tk.Frame(control_frame, bg="black")
help_frame.pack(pady=5, fill="x")

help_text = tk.Text(help_frame, height=4, width=70, font=("Arial", 14), fg="white", bg="black")
help_text.pack(side=tk.LEFT, padx=60, pady=5)

help_text.config(insertbackground="white")

send_btn = tk.Button(control_frame, text="Send", command=send_help_message)
send_btn.pack(pady=10)

root.mainloop()