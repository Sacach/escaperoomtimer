import tkinter as tk
import time
import threading
import cv2
import os
import sys
import msvcrt
from ffpyplayer.player import MediaPlayer
from screeninfo import get_monitors

TIMER_MINUTES = 60
FONT_SIZE = 500
VIDEO_PATH = "isadora-video.mp4"
LAUGH_TRACK = "test_laugh.mp3"
SCREAM = "scream.mp3"
RITUAL = "Rituaali.mp3"
HELP_FILE = "ohjeet.txt"
HELP_DURATION = 20000
DELAY_AFTER_VIDEO = 1
SOUND_ON_FINISH = True
RUNNING = True

root = tk.Tk()

monitors = get_monitors()
if len(monitors) > 1:
    monitor = monitors[1]
else:
    monitor = monitors[0]
x = monitor.x
y = monitor.y
root.geometry(f"{1920}x{1080}+{x}+{y}")
root.configure(bg='black')
root.overrideredirect(True) 
TIMER = tk.Label(root, text="", font=("UnifrakturCook", FONT_SIZE), fg="red", bg="black")
TIMER.pack(expand=True)

def play_video_and_start_timer():
    capture = cv2.VideoCapture(VIDEO_PATH)
    player = MediaPlayer(VIDEO_PATH)
    if not capture.isOpened():
        print("Videoa ei voitu avata.")
        return
    cv2.namedWindow("Video", cv2.WND_PROP_FULLSCREEN)
    cv2.setWindowProperty("Video", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

    paused = False

    while True:
        if not paused:
            ret, frame = capture.read()
            if not ret:
                break
            _, _ = player.get_frame()
            cv2.imshow("Video", frame)

        key = cv2.waitKey(25) & 0xFF
        if key == ord('q'):
            break
        elif key == ord(' '):
            paused = not paused
            player.set_pause(paused) 
            if paused:
                print("Paused")
            else:
                print("Unpaused")
    player.close_player()
    capture.release()
    cv2.destroyAllWindows()
    show_timer()

def show_help_message(message, duration=HELP_DURATION):
    help_win = tk.Toplevel()
    x = monitor.x
    y = monitor.y
    help_win.geometry(f"{1920}x{1080}+{x}+{y}")
    help_win.overrideredirect(True)
    help_win.configure(bg='black')
    
    help_label = tk.Label(help_win, text=message, wraplength=1900, font=("Rubik Distressed", 65), fg="red", bg="black")
    help_label.pack(expand=True)

    help_win.after(duration, help_win.destroy)

def show_timer(duration_seconds=TIMER_MINUTES*60):

    def update():
        global RUNNING
        nonlocal duration_seconds
        minutes, seconds = divmod(duration_seconds, 60)
        TIMER.config(text=f"{minutes:02}:{seconds:02}")

        sys.stdout.write(f"\r{minutes:02}:{seconds:02}")
        sys.stdout.flush()
        if RUNNING == True and duration_seconds > 0:
            duration_seconds -= 1
            if duration_seconds == 0:
                pass
            elif duration_seconds % 900 == 0:
                player = MediaPlayer(SCREAM)
                time.sleep(0.7)
                player.close_player()
            root.after(1000, update)
        elif RUNNING == False:
            root.after(1000, update)
        else:
            root.update_idletasks()
            player = MediaPlayer(RITUAL)
            time.sleep(18)
            player.close_player()
            return

    def monitor_help():
        global RUNNING
        last_msg = ""

        while True:
            try:
                with open(HELP_FILE, "r", encoding="utf-8") as f:
                    msg = f.read().strip()
                if msg and msg != last_msg:
                    last_msg = msg
                    if msg.lower() == "stop":
                        RUNNING = False
                        with open(HELP_FILE, "w", encoding="utf-8") as f:
                            f.write("")
                    else:
                        root.after(0, lambda: show_help_message(msg))
                        player = MediaPlayer(LAUGH_TRACK)
                        _, _ = player.get_frame()
                        with open(HELP_FILE, "w", encoding="utf-8") as f:
                            f.write("")
                        time.sleep(20)
                        player.close_player()
            except:
                pass
            time.sleep(1)

    def exit_on_q(event):
        root.destroy()
    update()
    root.bind("q", exit_on_q)
    threading.Thread(target=monitor_help, daemon=True).start()

    root.mainloop()

play_video_and_start_timer()
