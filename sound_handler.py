import pygame
import threading
import time
from settings_manager import load_settings

pygame.mixer.init()

def play_sound(track, duration_ms=None):
    settings = load_settings()
    filepath = settings.get(track)
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
