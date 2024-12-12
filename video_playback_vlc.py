import threading, queue, json, time
from workers_server import start_server
from hparams import hparams

from vlc_player import VideoPlayer

# Initialize global variables
reading_lipsync = False
current_video = "static"  # Tracks which video is being played

# Paths to the videos
video_path = hparams.static_video_file_path  # Path to your main video file

video_player = VideoPlayer(video_path)

# Thread-safe queue for communication between socket and main thread
message_queue = queue.Queue()

def process_queue():
    global reading_lipsync, current_video

    if not message_queue.empty():
        try:
            current_threads = threading.enumerate()
            print(f'thread count is {len(current_threads)}')
            # A new video is received
            new_video_path = json.loads(message_queue.get())["processed_file"]
            print(f"Processing new video path: {new_video_path}")

            reading_lipsync = True
            current_video = "lipsync"
            video_player.switch_to_video(new_video_path)

        except Exception as e:
            print(f"Error processing queue: {e}")

def start_video_playback():
    video_player.start()

def loop_on_processing_queue():
    try:
        while True:
            time.sleep(0.1)
            process_queue()
    except KeyboardInterrupt:
        print("Exited")

# Start the server in a separate thread
socket_thread = threading.Thread(target=start_server, args=(message_queue,), daemon=True)
socket_thread.start()

# TkInter is blocking, so also start listening to the server in a separate thread
threading.Thread(target=loop_on_processing_queue, daemon=True).start()

start_video_playback()