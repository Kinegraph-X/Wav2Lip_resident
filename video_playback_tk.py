from workers_server import start_server
import queue, json
from hparams import hparams

from tkinter import Tk
from tkVideoPlayer import TkinterVideo
import threading, time
from audio_playback import extract_audio, play_audio, audio_processing_done


# Initialize global variables
reading_lipsync = False
current_video = "static"  # Tracks which video is being played
video_is_playing = True  # Flag to track whether video is actually playing

# Initialize the main Tkinter window
root = Tk()
root.title("Video Player")

# Initialize the video player widget
video_player = TkinterVideo(master=root, scaled=True)
video_player.pack(expand=True, fill="both")

# Paths to the videos
video_path = hparams.static_video_file_path  # Path to your main video file
new_video_path = None  # This will be updated when a message is received

# Load the initial video (looping)
video_player.load(video_path)
video_player.set_size((480, 270))

# Function to handle video end and restart logic
def on_video_ended(event):
    global reading_lipsync, current_video, video_is_playing

    if not video_is_playing:
        return  # Prevent callback from firing immediately after load

    print(f"Video ended. Current video: {current_video}, reading_lipsync: {reading_lipsync}")
    if reading_lipsync:
        # Switch back to the static video after lipsync ends
        video_is_playing = False

        # root.after(0, video_player.stop)
        
        root.after(0, lambda: video_player.load(video_path))
        current_video = "static"
        reading_lipsync = False
        root.after(0, start_video_playback)
    else:
        return
        # Restart the static video
        root.after(0, video_player.seek, 0)
        root.after(100, start_video_playback)

# video_player.bind("<<Ended>>", on_video_ended)

def log_video_ended(event):
    print("callback received for video ended")

# video_player.bind("<<Ended>>", log_video_ended)

# Resize window based on video size
def set_window_size():
    video_width = 480
    video_height = 270
    root.geometry(f"{video_width}x{video_height}+1400+100")

set_window_size()

# Thread-safe queue for communication between socket and main thread
message_queue = queue.Queue()

def process_queue():
    global reading_lipsync, new_video_path, current_video, video_is_playing

    if not message_queue.empty():
        try:
            current_threads = threading.enumerate()
            print(f'thread count is {len(current_threads)}')
            # A new video is received
            new_video_path = json.loads(message_queue.get())["processed_file"]
            print(f"Processing new video path: {new_video_path}")

            extract_audio(new_video_path, hparams.audio_only_path)

            while not audio_processing_done.is_set():
                time.sleep(1)

            # Load and play the new video on the main thread
            
            # video_player.stop()
            root.after(0, lambda: video_player.load(new_video_path))
            reading_lipsync = True
            current_video = "lipsync"
            video_is_playing = False
            root.after(0, lambda: start_video_playback())

            audio_processing_done.clear()
            time.sleep(1)
            # Start audio playback in a separate thread
            threading.Thread(target=play_audio, args=(hparams.audio_only_path,), daemon=True).start()
        except Exception as e:
            print(f"Error processing queue: {e}")
    # Schedule the next queue check
    root.after(100, process_queue)

def start_video_playback():
    global video_is_playing
    video_is_playing = True
    video_player.play()
    # print(video_player.current_duration())

# Start the server in a separate thread
socket_thread = threading.Thread(target=start_server, args=(message_queue,), daemon=True)
socket_thread.start()

# Start processing the queue and playing the video
video_player.play()  # Start playing the initial video_path
# root.after(100, start_video_playback)
root.after(100, process_queue)

# Start the Tkinter main loop
root.mainloop()
