from args_parser import args
from hparams import hparams
import requests
session = requests.Session()

from logger import logger

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



url = args.ngrok_addr
stop_recording = threading.Event()

wf = None
start_time = 0.
audio_queue = queue.Queue()  # Queue for audio chunks

def send_audio_chunks():
    
    # Thread to handle sending audio chunks to the server.
    while True:

        if not audio_queue.empty():

            item = audio_queue.get()  # Get audio from the queue # timeout = .25

            if item is None:  # Flush signal
                break
            audio_chunk, audio_chunk_idx = item

            headers = {
                "Content-Type": "application/octet-stream",
                "Connection": "keep-alive",
                "X-Audio-Filename": FILENAME.split('/')[-1],
                "Content-Length": str(len(audio_chunk)),
                "X-Audio-Chunk-Timestamp": str(audio_chunk_idx),
                "X-Sample-Rate": str(SAMPLE_RATE),
                "X-Channels": str(CHANNELS),
            }

            try:
                req_thread = threading.Thread(target = handle_request, args = (headers, audio_chunk))
                req_thread.start()

                logger.info(f"Audio chunks {audio_chunk_idx} sent successfully.")
            except:
                logger.info('POST Audio request failed : the server might not be running')

        time.sleep(.1)

def handle_request(headers, audio_chunk):
    response = session.post(url, data=audio_chunk, headers=headers)
    logger.info("server responded : " + response.content.decode('utf-8'))

def record_callback(indata, frames, timestamp, status):
    global wf, audio_chunk_idx
    logger.debug(f'frame received {len(indata)}')
    
    # Callback function to handle incoming audio data.
    if status:
        logger.error(f"Status: {status}", flush=True)  # Print warnings/errors from the stream

    audio_chunk = np.int16(indata * 32767).tobytes()

    # Write the audio data to the wave file
    wf.writeframes(audio_chunk)
    
    audio_queue.put((audio_chunk, audio_chunk_idx))
    audio_chunk_idx += 1

def start_recording():
    global audio_chunk_idx, session
    # Starts the recording indefinitely until stopped.
    audio_chunk_idx = 0
    logger.info("Recording... release key to stop.")

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
            "X-Avatar-Type" : args.avatar_type
        }
        try:
            response = session.post( url, data=None, headers=headers)
            logger.info("server responded : " + response.content.decode('utf-8'))
        except Exception as e:
            print(e.args)

        logger.info("Recording stopped.")
        wf.close()
