from args_parser import args
import os, platform, socket, cv2
import subprocess, time, json
from collections import namedtuple

from Thread_with_return_value import ThreadWithReturnValue
import requests
session = requests.Session()
import record_audio
from hparams import hparams

from keyboard_listener import keyboard_listener
from deserializer import deserialize

outfile_writer = None
server_path = "content/Wav2Lip_with_cache/output/"
media_folder = hparams.media_folder
temp_videofile = hparams.temp_video_file

output_path = hparams.output_video_path
outfile = output_path.split("/")[-1]

# kept for archive (interesting syntax)
# req_args = namedtuple('req_args', ('url', 'params'))

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

start_time = 0

def remux_audio():
    command = 'ffmpeg -nostdin -y -i {} -i {} -strict -2 -c:v copy {}'.format(hparams.local_audio_filename, temp_videofile, output_path)
    print(command)
    subprocess.call(command, shell=platform.system() != 'Windows', stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
    # subprocess.call(command, shell=platform.system() != 'Windows', stderr=subprocess.STDOUT)
    print(f'Video file saved to {output_path}')

def handle_img_batch(images):
    global start_time, outfile_writer
    start_time = time.perf_counter()

    # reconstruct numpy array
    images = deserialize(images)
    if not outfile_writer:
         outfile_writer = cv2.VideoWriter(temp_videofile, cv2.VideoWriter_fourcc(*'mp4v'), hparams.fps, (images.shape[2], images.shape[1]))
    for img in images:
        outfile_writer.write(img)
    print(f'Writing file took {time.perf_counter() - start_time}')

def poll_server(ngrok_url):
    global start_time, outfile_writer
    start_time = time.perf_counter()

    # threading requests may not be necessary, but let's keep that principle as an example in our codebase
    request_thread = ThreadWithReturnValue(target = session.get, args = (ngrok_url,), kwargs = {"params" : {"next_batch" : 'True'}})
    request_thread.start()
    response = request_thread.join()

    content_type = response.headers.get('content-type').split(";")[0].lower()
    print(f'receiving response took {time.perf_counter() - start_time}')
    
    if content_type == 'text/html':
        print(content_type, response.content)
    if content_type == 'text/plain':
        # print(content_type, response.content)
        if response.content == b"processing_ended":
            print('received "ended processing"')
            outfile_writer.release()
            remux_audio()
            return 'break'
        elif response.content == b"long_polling_timeout":
            print('long_polling timeout')
            return 'continue'
    elif content_type == 'application/octet-stream':
        print('octet-stream returned')
        handle_img_batch(response.content)

def send_messages():
    global outfile_writer

    ngrok_url = args.ngrok_addr

    if os.path.exists(temp_videofile):
        os.remove(temp_videofile)
    
    # """
    while True:
        return_value = poll_server(ngrok_url)
        if return_value == 'break':
            outfile_writer = None
            break
        elif return_value == 'continue':
             continue
    # """
    
    print('transmission ended')

    # Old strategy, before streaming upload of the audio: re-implement if you wish
    """
    command = (f'Invoke-WebRequest \
                -Uri "{ngrok_url}" \
                -Method POST \
                -Form @{{"file" = Get-Item "{record_audio.FILENAME}"}}')
    
    subprocess.call([
        "pwsh", 
        "-Command",
        command])
    
    command = (f'Invoke-WebRequest \
                -Uri "{ngrok_url}/{server_path}{outfile}" \
                -Method GET \
                -Headers @{{"ngrok-skip-browser-warning" = "true"}} \
                -OutFile {media_folder}{outfile}')
    
    subprocess.call([
        "pwsh", 
        "-Command",
        command])
    """

    data = {"processed_file": f"{output_path}"}
    serialized_data = json.dumps(data).encode('utf-8')
    client.sendall(serialized_data)

def listen_indefinitely():
    try:
        while not record_audio.stop_recording.is_set():
            time.sleep(1)

        record_audio.stop_recording.clear()
        send_messages()
        listen_indefinitely()

    except KeyboardInterrupt:
        record_audio.stop_recording.clear()

if __name__ == "__main__":
    keyboard_listener()
    # """
    try:
        client.connect(("localhost", 9999))
        print("Connected to server.")
    except KeyboardInterrupt:
        client.close()
    # """
    listen_indefinitely()
    
