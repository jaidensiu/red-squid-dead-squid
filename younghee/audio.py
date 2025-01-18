import pygame

class Audio:
    def __init__(self):
        pygame.mixer.init()

    def play_audio(self, file_path):
        sound = pygame.mixer.music.load(file_path)
        sound.play()
        pygame.time.wait(int(sound.get_length() * 1000))  # Wait for the sound to finish

