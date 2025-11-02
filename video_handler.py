import subprocess
import threading
import time
import pygetwindow as gw
from settings_manager import load_settings
from app_logic import show_timer, get_selected_monitor

VLC_PATH = "C:/Program Files/VideoLAN/VLC/vlc.exe"
video = None

def fix_path(path):
    return path.replace("/", "\\")

def play_video(root, controller_timer_label, video_path = None):
    settings = load_settings()
    video_path = settings.get("VIDEO_PATH", "")
    monitor = get_selected_monitor()
    print("vhandler", monitor)

    def target():
        global video
        video = subprocess.Popen([
            fix_path(VLC_PATH),
            fix_path(video_path),
            "--fullscreen",
            "--no-video-title-show",
            "--play-and-exit"
        ])
        time.sleep(2)
        windows = [w for w in gw.getAllTitles() if "VLC" in w]
        if windows:
            win = gw.getWindowsWithTitle(windows[0])[0]
            win.moveTo(monitor.x, monitor.y)
            win.resizeTo(monitor.width, monitor.height)
        video.wait()
        root.after(0, lambda: show_timer(controller_timer_label))
    threading.Thread(target=target, daemon=True).start()

def stop_video():
    global video
    if video:
        video.terminate()
