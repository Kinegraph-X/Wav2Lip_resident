from args_parser import args
import os, platform, socket, cv2
import atexit
import subprocess, time, json
from collections import namedtuple

from utils.socket_utils import close_client_socket
from Thread_with_return_value import ThreadWithReturnValue

import requests
from urllib3.exceptions import MaxRetryError
session = requests.Session()

import record_audio
from hparams import hparams

from keyboard_listener import keyboard_listener
from deserializer import deserialize

from logger import logger

outfile_writer = None
server_path = "content/Wav2Lip_with_cache/output/"
media_folder = hparams.media_folder
temp_videofile = hparams.temp_video_file

output_path = hparams.output_video_path
outfile = output_path.split("/")[-1]

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

start_time = 0

def remux_audio():
    command = 'ffmpeg -nostdin -y -i {} -i {} -strict -2 -c:v copy {}'.format(hparams.local_audio_filename, temp_videofile, output_path)
    print(command)
    subprocess.call(command, shell=platform.system() != 'Windows', stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
    # subprocess.call(command, shell=platform.system() != 'Windows', stderr=subprocess.STDOUT)
    logger.debug(f'Video file saved to {output_path}')

def handle_img_batch(images):
    global start_time, outfile_writer
    start_time = time.perf_counter()
    try:
        # reconstruct numpy array
        images = deserialize(images)
        if not outfile_writer:
            outfile_writer = cv2.VideoWriter(temp_videofile, cv2.VideoWriter_fourcc(*'mp4v'), hparams.fps, (images.shape[2], images.shape[1]))
        for img in images:
            outfile_writer.write(img)
        logger.debug(f'Writing file took {time.perf_counter() - start_time}')
    except Exception as e:
        print(e)

def poll_server(ngrok_url):
    logger.debug('polling server')
    global start_time, outfile_writer
    start_time = time.perf_counter()

    # threading requests may not be necessary, but let's keep that principle as an example in our codebase
    request_thread = ThreadWithReturnValue(target = session.get, args = (ngrok_url,), kwargs = {"params" : {"next_batch" : 'True'}})
    try:
        request_thread.start()
        response = request_thread.join()
    except (ConnectionRefusedError, requests.exceptions.ConnectionError, MaxRetryError) as e:
        logger.error(f"Polling connection failed: The server did not respond")
        return 'break'
    except Exception as e:
        logger.error(f"An unexpected error occurred while polling the server: {str(e)}")
        return 'break'
    else:
        content_type = response.headers.get('content-type').split(";")[0].lower()  

    logger.debug(f'receiving response took {time.perf_counter() - start_time}')
    
    if content_type == 'text/html':
        logger.error(content_type, response.content)
    if content_type == 'text/plain':
        if response.content == b"processing_ended":
            logger.info('received "ended processing"')
            outfile_writer.release()
            remux_audio()
            return 'break'
        elif response.content == b"long_polling_timeout":
            logger.info('long_polling timeout')
            return 'continue'
    elif content_type == 'application/octet-stream':
        logger.info('octet-stream returned')
        handle_img_batch(response.content)
        return 'continue'

def send_messages():
    global outfile_writer

    ngrok_url = args.ngrok_addr

    if os.path.exists(temp_videofile):
        os.remove(temp_videofile)
    
    while True:
        return_value = poll_server(ngrok_url)
        if return_value == 'break':
            outfile_writer = None
            break
        elif return_value == 'continue':
             continue
    
    logger.info('transmission ended')

    data = {"processed_file": f"{output_path}"}
    serialized_data = json.dumps(data).encode('utf-8')
    try:
        client.sendall(serialized_data)
    except:
        pass

def listen_indefinitely():
    try:
        while True:
            while not record_audio.stop_recording.is_set():
                time.sleep(1)

            record_audio.stop_recording.clear()
            send_messages()

    except Exception as e:
        logger.error(f'Unknown error in the client worker : {e}')
    except KeyboardInterrupt:
        record_audio.stop_recording.clear()


# Register the cleanup function to run on script termination
atexit.register(lambda : close_client_socket(client))


if __name__ == "__main__":
    keyboard_listener()
    # """
    try:
        client.connect(("localhost", 9999))
        logger.info("Connected to video playback socket.")
    except KeyboardInterrupt:
        close_client_socket()
    except (ConnectionResetError, ConnectionRefusedError):
        logger.error("Connection refused : Unable to connect to video playback socket.")
    except Exception as e:
        logger.error(f"Failed to connect to video playback socket: {e}")
        close_client_socket(client)
    # """
    listen_indefinitely()
    
