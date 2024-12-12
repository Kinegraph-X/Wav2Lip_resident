import sounddevice as sd
import wave
import numpy as np
import threading

# Configuration
SAMPLE_RATE = 16000  # Samples per second
CHANNELS = 1         # 1 for mono, 2 for stereo
FILENAME = "recordings/output.wav"

stop_recording = threading.Event()

def record_callback(indata, frames, time, status):
    """Callback function to handle incoming audio data."""
    if status:
        print(f"Status: {status}", flush=True)  # Print warnings/errors from the stream
    # Write the audio data to the wave file
    wf.writeframes(np.int16(indata * 32767).tobytes())

def start_recording():
    """Starts the recording indefinitely until stopped."""
    print("Recording... releas key to stop.")

    # Open the WAV file for writing
    global wf
    wf = wave.open(FILENAME, 'w')
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(2)  # 16-bit PCM
    wf.setframerate(SAMPLE_RATE)

    # Start the input stream with the callback
    with sd.InputStream(
        samplerate=SAMPLE_RATE,
        channels=CHANNELS,
        callback=record_callback
    ):
        stop_recording.wait()  # Wait until the event is set

    print("Recording stopped.")
    wf.close()

"""
def stop_on_input():
    # Stops recording on user input.
    # input()  # Wait for the user to press Enter
    stop_recording.set()  # Signal the recording thread to stop

if __name__ == "__main__":
    # Start recording in a separate thread
    record_thread = threading.Thread(target=start_recording)
    record_thread.start()

    # Wait for the stop event
    # stop_on_input()

    # Ensure all threads are cleanly joined
    record_thread.join()
    print(f"Audio saved as {FILENAME}")
"""