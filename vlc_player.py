import time
import tkinter as tk
import vlc
from vlc import Instance

class VideoPlayer:
    is_first_play = True
    current_duration = 0

    def __init__(self, looping_video_path):
        self.root = tk.Tk()
        self.root.title("Ask Mini-E_B_U")

        self.looping_video_path = looping_video_path
        self.is_reading_lipsync = False

        # Create VLC instance and media player
        self.vlc_instance = Instance("--input-repeat=999999") # "--input-repeat=999999"
        self.media_player = self.vlc_instance.media_player_new()

        # Create a Tkinter canvas for video rendering
        self.canvas = tk.Canvas(self.root, width=480, height=270)
        self.canvas.pack(expand=True, fill="both") # 

        # Set VLC to render video in the Tkinter canvas
        self._set_video_output()

        # Bind VLC events
        self.media_player.event_manager().event_attach(
            vlc.EventType.MediaPlayerEndReached, self.on_video_end
        )
        
    def on_first_play(self):
        self.is_first_play = False
        self.root.mainloop()

    def _set_video_output(self):
        """Set up the VLC video output to use the Tkinter canvas."""
        window_id = self.canvas.winfo_id()
        self.media_player.set_hwnd(window_id)

    def play_video(self, video_path): # , loop=False
        """Load and play a video."""
        media = self.vlc_instance.media_new(video_path)
        
        self.media_player.set_media(media)
        lipsync_start_time = time.perf_counter()
        self.media_player.play()

        if self.is_first_play:
            self.on_first_play()
        
        # Hack cause we're not able to get the duration before playback has started
        time.sleep(1)
        self.current_duration = self.media_player.get_length() / 1000
        
        # Hack cause on_ended event isn't triggered when loop playback
        if self.is_reading_lipsync:
            while time.perf_counter() - lipsync_start_time < self.current_duration:
                time.sleep(0.001)
            # Resume playing the looping video
            self.is_reading_lipsync = False
            self.play_video(self.looping_video_path)

    def on_video_end(self, event):
        print("video_ended")
        """Callback for when a video ends."""
        if self.is_reading_lipsync:
            # Resume playing the looping video
            self.is_reading_lipsync = False
            self.play_video(self.looping_video_path) # , loop=True

    def switch_to_video(self, path):
        print(f"playing new video file : {path}")
        """Play the lipsynced video once."""
        self.is_reading_lipsync = True
        self.play_video(path)

    def start(self):
        print("play started")
        self.play_video(self.looping_video_path) # , loop=True
