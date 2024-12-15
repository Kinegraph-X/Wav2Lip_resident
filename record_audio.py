from args_parser import args
from hparams import hparams
import requests, json, socket
session = requests.Session()
import http.client

distant_url = args.ngrok_addr.split(':')

if len(distant_url) < 3:
    port = None
else:
    port = distant_url[2]

distant_url = distant_url[1][2:]
# conn = http.client.HTTPConnection(f'{distant_url}', port)
# conn.connect()
# conn.set_debuglevel(1)
import queue
import sounddevice as sd
import wave
import numpy as np
import threading, time

# Configuration
SAMPLE_RATE = 32000  # Samples per second
CHANNELS = 1         # 1 for mono, 2 for stereo
FILENAME = hparams.local_audio_filename
BLOCK_SIZE = 8192

"""
import logging
logging.basicConfig()
logging.getLogger().setLevel(logging.DEBUG)
requests_log = logging.getLogger("requests")
requests_log.setLevel(logging.DEBUG)
requests_log.propagate = True
"""

url = args.ngrok_addr
stop_recording = threading.Event()

wf = None
start_time = 0.
audio_queue = queue.Queue()  # Queue for audio chunks

def send_audio_chunks():
    
    """Thread to handle sending audio chunks to the server."""
    while True:
        # print('loop')
        if not audio_queue.empty():
            # print('not empty')
            # try:
            item = audio_queue.get()  # Get audio from the queue # timeout = .25
            # print('got item')

            if item is None:  # Flush signal
                break
            audio_chunk, audio_chunk_idx = item
            # print(f"got chunk {audio_chunk_idx} {len(audio_chunk)}")

            headers = {
                "Content-Type": "application/octet-stream",
                "Connection": "keep-alive",
                "X-Audio-Filename": FILENAME.split('/')[-1],
                "Content-Length": str(len(audio_chunk)),
                "X-Audio-Chunk-Timestamp": str(audio_chunk_idx),
                "X-Sample-Rate": str(SAMPLE_RATE),
                "X-Channels": str(CHANNELS),
            }

            req_thread = threading.Thread(target = handle_request, args = (headers, audio_chunk))
            req_thread.start()
            # req_thread.join()
            # """
            # print('before request')
            # conn.request("POST", '/', body=audio_chunk, headers=headers)
            # conn.request("GET", "", headers=headers)
            # response = session.post(url, data=audio_chunk, headers=headers)
            # print('request sent')
            # response = conn.getresponse().read()
            # print(response.content)
            # audio_queue.task_done()
            # response.raise_for_status()
            # """
            """
            except Exception as e:
                print(f"Error sending chunk: {e}")
            """
            print(f"Audio chunks {audio_chunk_idx} sent successfully.")

        time.sleep(.1)

def handle_request(headers, audio_chunk):
    response = session.post(url, data=audio_chunk, headers=headers)
    # print('request sent')
    # response = conn.getresponse().read()
    print(response.content)

def record_callback(indata, frames, timestamp, status):
    global wf, audio_chunk_idx
    print(f'frame received {len(indata)}')
    
    """Callback function to handle incoming audio data."""
    if status:
        print(f"Status: {status}", flush=True)  # Print warnings/errors from the stream

    audio_chunk = np.int16(indata * 32767).tobytes()

    # Write the audio data to the wave file
    wf.writeframes(audio_chunk)
    
    audio_queue.put((audio_chunk, audio_chunk_idx))
    audio_chunk_idx += 1

def start_recording():
    global audio_chunk_idx, session
    """Starts the recording indefinitely until stopped."""
    audio_chunk_idx = 0
    print("Recording... release key to stop.")

    global wf
    # Open the WAV file for writing
    wf = wave.open(FILENAME, 'w')
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(2)  # 16-bit PCM
    wf.setframerate(SAMPLE_RATE)

    # Start the thread to send audio chunks
    sender_thread = threading.Thread(target=send_audio_chunks, daemon=True)
    sender_thread.start()

    try:
        # """
        # Start the input stream with the callback
        with sd.InputStream(
            samplerate=SAMPLE_RATE,
            channels=CHANNELS,
            blocksize = BLOCK_SIZE,
            callback=record_callback
        ):
            stop_recording.wait()  # Wait until the event is set
    finally:
        # Ensure all chunks are processed before sending EOF
        audio_queue.put(None)
        sender_thread.join()  # Wait for the sending thread to finish

        headers = {
            "Content-Type": "application/octet-stream",
            "Connection": "keep-alive",
            "X-Audio-Filename": FILENAME.split('/')[-1],
            "X-Audio-Chunk-Timestamp": 'EOF',
            "X-Sample-Rate": str(SAMPLE_RATE),
            "X-Channels": str(CHANNELS),
        }
        # """
        try:
            response = session.post( url, data=None, headers=headers)
            print(response.content)
            # conn.request("POST", url, body=None, headers=headers)
            # response = conn.getresponse().read()
        except Exception as e:
            print(e.args)
        # """

        print("Recording stopped.")
        # """
        wf.close()
