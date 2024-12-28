import keyboard
import threading
import time
import record_audio

from logger import logger

# A flag to control the processing
processing = False

# Function to start processing when the key is pressed
def start_processing(event):
    global processing
    if not processing:
        logger.info(f"{event.name} key pressed! Starting processing...")
        processing = True
        threading.Thread(target=record_audio.start_recording).start()  # Run the processing in a separate thread

# Function to stop processing when the key is released
def stop_processing(event):
    global processing
    if processing:
        logger.info(f"{event.name} key released! Stopping processing...")
        processing = False
        record_audio.stop_recording.set()

def keyboard_listener():
    # Listen for the specific key press and release events
    keyboard.on_press_key('f9', start_processing)
    keyboard.on_release_key('f9', stop_processing)

    # Keep the script running
    logger.info("Press and hold F9 to start processing, release to stop.")
    # keyboard.wait('esc')  # The script will exit when 'esc' is pressed