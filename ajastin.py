import tkinter as tk
import time
import vlc
import threading
import cv2
import os
import sys
import msvcrt
import pygame
from screeninfo import get_monitors
import keyboard
import subprocess
import pygetwindow as gw
from tkinter import filedialog

TIMER_MINUTES = 60
FONT_SIZE_TIMER = 500
FONT_SIZE_HELP = 65
VLC_PATH= r"C:/Program Files/VideoLAN/VLC/vlc.exe"
VIDEO_PATH = "escaperoomtimer/isadora-video.mp4"
HELP_TRACK = "escaperoomtimer/test_laugh.mp3"
INTERVAL_SOUND = "escaperoomtimer/scream.mp3"
TIME_OVER_SOUND = "escaperoomtimer/Rituaali.mp3"
HELP_FILE = "escaperoomtimer/ohjeet.txt"
TIMER_FONT = ("UnifrakturCook", FONT_SIZE_TIMER)
HELP_FONT = ("Rubik Distressed", FONT_SIZE_HELP)

HELP_DURATION = 20000
DELAY_AFTER_VIDEO = 1
SOUND_ON_FINISH = True
RUNNING = True

timer_window = None
video = None

pygame.mixer.init()

monitors = get_monitors()

if len(monitors) > 1:
    monitor = monitors[1]
else:
    monitor = monitors[0]

print(monitors)

def play_video():
    def target():
        global video
        video = subprocess.Popen([
            VLC_PATH,
            VIDEO_PATH,
            "--fullscreen",
            "--no-video-title-show",
            "--play-and-exit"
        ])
        time.sleep(2)
        windows = [w for w in gw.getAllTitles() if "VLC" in w]
        if windows:
            win = gw.getWindowsWithTitle(windows[0])[0]
            print(monitor)
            win.moveTo(monitor.x, monitor.y)
            win.resizeTo(monitor.width, monitor.height)
        
        video.wait()

        print("Video finished!")
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

    help_win.geometry(f"{monitor.width}x{monitor.height}+{monitor.x}+{monitor.y}")
    help_win.overrideredirect(True)
    help_win.configure(bg='black')
    
    help_label = tk.Label(help_win, text=message, wraplength=1900, font=HELP_FONT, fg="red", bg="black")
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
    timer_window.configure(bg='black')
    timer_window.overrideredirect(True)
    timer_window.geometry(f"{monitor.width}x{monitor.height}+{monitor.x}+{monitor.y}")

    timer_label = tk.Label(timer_window, text="", font=TIMER_FONT, fg="red", bg="black")
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
    global VIDEO_PATH, HELP_TRACK, INTERVAL_SOUND, TIME_OVER_SOUND, TIMER_FONT, HELP_FONT, TIMER_MINUTES


    TIMER_MINUTES = int(timer_entry.get())
    VIDEO_PATH = video_entry.get()
    HELP_TRACK = help_entry.get()
    INTERVAL_SOUND = interval_entry.get()
    TIME_OVER_SOUND = end_entry.get()
    TIMER_FONT = (timer_font_entry.get(), int(timer_fontsize_entry.get()))
    HELP_FONT = (help_font_entry.get(), int(help_fontsize_entry.get()))

def browse_file(entry_widget, filetypes=(("All files", "*.*"),)):
    filename = filedialog.askopenfilename(filetypes=filetypes)
    if filename:
        entry_widget.delete(0, tk.END)
        entry_widget.insert(0, filename)

def apply_monitor():
    global monitor
    for m in monitors:
        if m.name == selected_monitor.get():
            monitor = m
            print(f"Switched to monitor: {monitor}")
            break

root = tk.Tk()

selected_monitor = tk.StringVar(value=monitors[0].name)

root.title("Escape Room Controller")

root.geometry(f"{800}x{950}")

root.protocol("WM_DELETE_WINDOW", on_close)
root.configure(bg='black')

settings_heading = tk.Label(root, text="Settings", font=("Arial", 18, "bold"), fg="green", bg="black")
settings_heading.pack(pady=(20, 0))

settings_frame = tk.Frame(root, bg="black")
settings_frame.pack(pady=5, fill="x")

# Video
tk.Label(settings_frame, text="Video Path:", bg="black", fg="yellow").grid(row=0, column=0, sticky="w")
video_entry = tk.Entry(settings_frame, width=70)
video_entry.insert(0, VIDEO_PATH)
video_entry.grid(row=0, column=1, padx=5, pady=2)
video_browse = tk.Button(settings_frame, text="Browse", command=lambda: browse_file(video_entry, (("MP4 files","*.mp4"),("All files","*.*"))))
video_browse.grid(row=0, column=2, padx=5, pady=5)

# Help Track
tk.Label(settings_frame, text="Help Track:", bg="black", fg="yellow").grid(row=1, column=0, sticky="w")
help_entry = tk.Entry(settings_frame, width=70)
help_entry.insert(0, HELP_TRACK)
help_entry.grid(row=1, column=1, padx=5, pady=2)
help_browse = tk.Button(settings_frame, text="Browse", command=lambda: browse_file(help_entry, (("MP3 files","*.mp3"),("All files","*.*"))))
help_browse.grid(row=1, column=2, padx=5, pady=5)

# Interval sound
tk.Label(settings_frame, text="Interval Track:", bg="black", fg="yellow").grid(row=2, column=0, sticky="w")
interval_entry = tk.Entry(settings_frame, width=70)
interval_entry.insert(0, INTERVAL_SOUND)
interval_entry.grid(row=2, column=1, padx=5, pady=2)
interval_browse = tk.Button(settings_frame, text="Browse", command=lambda: browse_file(interval_entry, (("MP3 files","*.mp3"),("All files","*.*"))))
interval_browse.grid(row=2, column=2, padx=5, pady=5)

# End sound
tk.Label(settings_frame, text="End Track:", bg="black", fg="yellow").grid(row=3, column=0, sticky="w")
end_entry = tk.Entry(settings_frame, width=70)
end_entry.insert(0, TIME_OVER_SOUND)
end_entry.grid(row=3, column=1, padx=5, pady=2)
end_browse = tk.Button(settings_frame, text="Browse", command=lambda: browse_file(end_entry, (("MP3 files","*.mp3"),("All files","*.*"))))
end_browse.grid(row=3, column=2, padx=5, pady=5)

# Timer Font 
tk.Label(settings_frame, text="Timer Font Size:", bg="black", fg="yellow").grid(row=4, column=0, sticky="w")
timer_fontsize_entry = tk.Entry(settings_frame, width=10)
timer_fontsize_entry.insert(0, str(TIMER_FONT[1]))
timer_fontsize_entry.grid(row=4, column=1, sticky="w", padx=5, pady=2)

tk.Label(settings_frame, text="Timer Font:", bg="black", fg="yellow").grid(row=5, column=0, sticky="w")
timer_font_entry = tk.Entry(settings_frame, width=20)
timer_font_entry.insert(0, str(TIMER_FONT[0]))
timer_font_entry.grid(row=6, column=1, sticky="w", padx=5, pady=2)

# Help Font
tk.Label(settings_frame, text="Help Font Size:", bg="black", fg="yellow").grid(row=6, column=0, sticky="w")
help_fontsize_entry = tk.Entry(settings_frame, width=10)
help_fontsize_entry.insert(0, str(HELP_FONT[1]))
help_fontsize_entry.grid(row=5, column=1, sticky="w", padx=5, pady=2)

tk.Label(settings_frame, text="Help Font:", bg="black", fg="yellow").grid(row=7, column=0, sticky="w")
help_font_entry = tk.Entry(settings_frame, width=20)
help_font_entry.insert(0, str(HELP_FONT[0]))
help_font_entry.grid(row=7, column=1, sticky="w", padx=5, pady=2)

# Time
tk.Label(settings_frame, text="Timer amount (minutes):", bg="black", fg="yellow").grid(row=8, column=0, sticky="w")
timer_entry = tk.Entry(settings_frame, width=20)
timer_entry.insert(0, str(TIMER_MINUTES))
timer_entry.grid(row=8, column=1, sticky="w", padx=5, pady=2)

apply_btn = tk.Button(settings_frame, text="Apply Settings", command=apply_settings)
apply_btn.grid(row=9, column=0, columnspan=2, pady=10)


monitor_frame = tk.Frame(root, bg="black")
monitor_frame.pack(pady=5, fill="x")

monitor_label = tk.Label(monitor_frame, text="Select Monitor:", bg="black", fg="yellow")
monitor_label.grid(row=0, column=1, sticky="w", padx=5, pady=2)

monitor_menu = tk.OptionMenu(monitor_frame, selected_monitor, *[m.name for m in monitors])
monitor_menu.grid(row=0, column=2, sticky="w", padx=5, pady=2)

apply_btn = tk.Button(monitor_frame, text="Apply Monitor", command=apply_monitor)
apply_btn.grid(row=0, column=3, sticky="w", padx=5, pady=2)

video_heading = tk.Label(root, text="Video Control", font=("Arial", 18, "bold"), fg="green", bg="black")
video_heading.pack(pady=(10, 0)) 

video_frame = tk.Frame(root, bg="black")
video_frame.pack(pady=5)

play_btn = tk.Button(video_frame, text="Play Video", command=play_video)
play_btn.pack(side=tk.LEFT, padx=5)

stop_btn = tk.Button(video_frame, text="Stop Video", command=stop_video)
stop_btn.pack(side=tk.LEFT, padx=5)

timer_heading = tk.Label(root, text="Timer Control", font=("Arial", 18, "bold"), fg="green", bg="black")
timer_heading.pack(pady=(20, 0))

timer_frame = tk.Frame(root, bg="black")
timer_frame.pack(pady=5)

controller_timer_label = tk.Label(timer_frame, text="", font=("Arial", 20), fg="red", bg="black")
controller_timer_label.pack(pady=10)

pause_btn = tk.Button(timer_window, text="Pause/Resume", command=toggle_pause)
pause_btn.pack(pady=10)

reset_btn = tk.Button(timer_window, text="Close timer", command=close_timer)
reset_btn.pack(pady=10)

help_heading = tk.Label(root, text="Send Help Message", font=("Arial", 18, "bold"), fg="green", bg="black")
help_heading.pack(pady=(20, 0))

help_frame = tk.Frame(root, bg="black")
help_frame.pack(pady=5, fill="x")

help_text = tk.Text(help_frame, height=4, width=70, font=("Arial", 14), fg="white", bg="black")
help_text.pack(side=tk.LEFT, padx=5, pady=5)

send_btn = tk.Button(text="Send", command=send_help_message)
send_btn.pack(pady=10)

root.mainloop()