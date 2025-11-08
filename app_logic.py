import tkinter as tk
import os
from PIL import Image, ImageTk
from sound_handler import play_sound
from settings_manager import load_settings
from screeninfo import get_monitors

MONITOR = None
RUNNING = True
controller_timer_label = None
help_text = None


def get_selected_monitor():
    settings = load_settings()
    monitor_name = settings.get("MONITOR", "")
    monitors = get_monitors()
    return next((m for m in monitors if m.name == monitor_name), monitors[0])

def show_help_message(message):
    settings = load_settings()
    monitor = get_selected_monitor()
    bg_image_path = settings.get("BACKGROUND_IMAGE_HELP", "")
    help_win = tk.Toplevel()
    help_win.geometry(f"{monitor.width}x{monitor.height}+{monitor.x}+{monitor.y}")
    help_win.overrideredirect(True)
    
    if bg_image_path and os.path.exists(bg_image_path):
        image = Image.open(bg_image_path)
        image = image.resize((monitor.width, monitor.height))
        bg_image = ImageTk.PhotoImage(image)
        
        canvas = tk.Canvas(help_win, width=monitor.width, height=monitor.height, highlightthickness=0)
        canvas.pack(fill="both", expand=True)
        canvas.create_image(0, 0, anchor="nw", image=bg_image)
        
        # Add the text on top of the image
        _ = canvas.create_text(
            monitor.width // 2,
            monitor.height // 2,
            text=message,
            font=settings.get("HELP_FONT", "(\"Arial\", 14)"),
            fill=settings.get("TEXT_COLOR", "red"),
            width=1800,
            anchor="center"
        )
        
        # Keep reference to image to avoid garbage collection
        canvas.bg_image = bg_image

    else:
        help_win.configure(bg=bg)
        canvas = tk.Canvas(help_win, width=monitor.width, height=monitor.height, highlightthickness=0, bg=settings.get("BACKGROUND_COLOR", "black"))
        canvas.pack(fill="both", expand=True)
        _ = canvas.create_text(
            monitor.width // 2,
            monitor.height // 2,
            text=message,
            font=settings.get("HELP_FONT", "(\"Arial\", 14)"),
            fill=settings.get("TEXT_COLOR", "red"),
            width=1800,
            anchor="center"
        )

    play_sound(settings.get("HELP_TRACK", "red"))
    help_win.after(settings.get("HELP_DURATION", "20"), help_win.destroy)

def toggle_pause():
    global RUNNING
    RUNNING = not RUNNING

def close_timer():
    global timer_window
    if timer_window:
        timer_window.destroy()
        timer_window = None

def show_timer(controller_timer_label, duration_seconds=None):
    settings = load_settings()
    global timer_window, RUNNING
    bg = settings.get("BACKGROUND_COLOR")
    bg_image_path = settings.get("BACKGROUND_IMAGE_TIMER", "")
    monitor = get_selected_monitor()

    if duration_seconds is None:
        duration_seconds = settings.get("TIMER_MINUTES", "") * 60

    timer_window = tk.Toplevel()
    timer_window.overrideredirect(True)
    timer_window.geometry(f"{monitor.width}x{monitor.height}+{monitor.x}+{monitor.y}")

    canvas = tk.Canvas(timer_window, width=monitor.width, height=monitor.height, highlightthickness=0)
    canvas.pack(fill="both", expand=True)

    if bg_image_path and os.path.exists(bg_image_path):
        image = Image.open(bg_image_path)
        image = image.resize((monitor.width, monitor.height))
        bg_image = ImageTk.PhotoImage(image)
        canvas.bg_image = bg_image  # keep reference
        canvas.create_image(0, 0, anchor="nw", image=bg_image)
    else:
        canvas.configure(bg=settings.get("BACKGROUND_COLOR", "black"))

    # Draw the timer text on top of the canvas
    timer_text_id = canvas.create_text(
        monitor.width // 2,
        monitor.height // 2,
        text="",
        font=settings["TIMER_FONT"],
        fill=settings["TEXT_COLOR"]
    )
    def update():
        nonlocal duration_seconds
        minutes, seconds = divmod(duration_seconds, 60)
        interval_sound = "INTERVAL_SOUND"
        end_sound = "TIME_OVER_SOUND"
        #timer_label.config(text=f"{minutes:02}:{seconds:02}")
        canvas.itemconfig(timer_text_id, text=f"{minutes:02}:{seconds:02}")
        controller_timer_label.config(text=f"{minutes:02}:{seconds:02}")

        if RUNNING == True and duration_seconds > 0:
            duration_seconds -= 1
            if duration_seconds == 0:
                pass
            elif duration_seconds % 900 == 0:
                play_sound(interval_sound)
            timer_window.after(1000, update)
        elif RUNNING == False:
            timer_window.after(1000, update)
        else:
            timer_window.update_idletasks()
            play_sound(end_sound)
            return
    update()
