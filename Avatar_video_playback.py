# nuitka-project: --product-name=Avatar_video_playback
# nuitka-project: --product-version=1.0.0
# nuitka-project: --file-description="An AI powered talking avatar (video playback module)"
# nuitka-project: --copyright="Kinegraphx"
# nuitka-project: --windows-console-mode=disable

# nuitka-project: --include-data-files=media/Avatar_generic*=media/
# nuitka-project: --include-data-files=media/Avatar_Small_Local.mp4=media/
# nuitka-project: --include-data-dir="C:\Production_Tools\python 3.11.9\tcl\tcl8.6=tcl\tcl8.6"
# nuitka-project: --include-data-dir="C:\Production_Tools\python 3.11.9\tcl\tk8.6=tcl\tk8.6"


import threading, queue, json, time
from find_ressource import resource_path
from hparams import hparams
from args_parser import args
from video_playback_file_list import video_files
from workers_server import start_server
from vlc_player import VideoPlayer


# Paths to the videos
# video_path = hparams.static_video_file_path

video_path = hparams.media_folder + video_files[args.avatar_type + '_video_file_path']

video_player = VideoPlayer(resource_path(video_path))

# Thread-safe queue for communication between socket and main thread
message_queue = queue.Queue()

def process_queue():

    if not message_queue.empty():
        try:
            # A new video is received
            new_video_path = json.loads(message_queue.get())["processed_file"]
            print(f"Processing new video path: {new_video_path}")

            video_player.switch_to_video(resource_path(new_video_path))

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

if __name__ == "__main__":
    # Start the server in a separate thread
    socket_thread = threading.Thread(target=start_server, args=(message_queue,), daemon=True) 
    socket_thread.start()

    # TkInter is blocking, so also start listening to the server in a separate thread
    socket_thread = threading.Thread(target=loop_on_processing_queue, daemon=True)
    socket_thread.start()

    start_video_playback()

    socket_thread.join()