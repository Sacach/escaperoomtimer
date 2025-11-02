import pygame
import threading
import time

pygame.mixer.init()

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
