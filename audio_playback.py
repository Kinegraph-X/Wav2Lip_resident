import platform, threading
from hparams import hparams
import pygame
import subprocess

audio_processing_done = threading.Event()
pygame.mixer.init()

def extract_audio(video_path, output_audio_path):
    print('"Extracting Audio')
    command = [
        f"{hparams.ffmpeg_path}ffmpeg", "-y", "-i", video_path, "-f", "wav", '-ar', '48000', '-ac', '1', output_audio_path # "-vn", 
    ]
    subprocess.call(command, shell=platform.system() != 'Windows', stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
    audio_processing_done.set()

def play_audio(audio_path):
    pygame.mixer.music.load(audio_path)
    pygame.mixer.music.play()
    #pygame.mixer.quit()