import pygame
import logging

# Set up basic configuration for logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    datefmt='%H:%M:%S')

class Audio:
    def __init__(self):
        try:
            pygame.mixer.init()
            logging.info("Audio player initialized")
        except Exception as e:
            logging.error(f"Error initializing audio player: {e}")

    def play_audio(self, file_path):
        try:
            sound = pygame.mixer.Sound(file_path)
            sound.play()
            pygame.time.wait(int(sound.get_length() * 1000))  # Wait for the sound to finish
        except Exception as e:
            logging.error(f"Error playing audio: {e}")

    def play_audio_without_wait(self, file_path):
        try:
            sound = pygame.mixer.Sound(file_path)
            sound.play()
        except Exception as e:
            logging.error(f"Error playing audio: {e}")

