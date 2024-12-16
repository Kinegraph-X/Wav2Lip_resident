from args_parser import args
import os, platform, socket, cv2
import subprocess, time, json
from collections import namedtuple

from Thread_with_return_value import ThreadWithReturnValue
import requests
import record_audio
from hparams import hparams

from keyboard_listener import keyboard_listener
from deserializer import deserialize

server_path = "content/Wav2Lip_with_cache/output/"
media_folder = "media/"
outfile = hparams.test_video_file.split("/")[-1]
print(outfile)
req_args = namedtuple('req_args', ('url', 'params'))

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

start_time = 0

def remux_audio():
    output_path = hparams.output_video_path
    command = 'ffmpeg -nostdin -y -i {} -i {} -strict -2 -c:v copy {}'.format(hparams.local_audio_filename, 'temp/result.avi', output_path)
    print(command)
    subprocess.call(command, shell=platform.system() != 'Windows', stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
    # subprocess.call(command, shell=platform.system() != 'Windows', stderr=subprocess.STDOUT)
    print(f'Video file saved to {output_path}')

def handle_img_batch(outfile_writer, images):
    global start_time
    # reconstruct numpy array
    images = deserialize(images)
    for img in images:
        outfile_writer.write(img)
    print(f'Writing file took {time.perf_counter() - start_time}')

def poll_server(ngrok_url, outfile_writer):
    global start_time
    start_time = time.perf_counter()

    # threading requests may not be necessary, but let's keep that principle as an example in our codebase
    request_thread = ThreadWithReturnValue(target = requests.get, args = req_args(ngrok_url, {"next_batch" : 'True'}))
    request_thread.start()
    response = request_thread.join()

    content_type = response.headers.get('content-type').split(";")[0].lower()
    print(f'receiving response took {time.perf_counter() - start_time}')
    
    if content_type == 'text/html':
        print(content_type, response.content)
    if content_type == 'text/plain':
        # print(content_type, response.content)
        if response.content == b"processing_ended":
            print('received ended processing')
            outfile_writer.release()
            remux_audio()
            return 'break'
        elif response.content == b"long_polling_timeout":
            print('long_polling timeout')
            return 'continue'
    elif content_type == 'application/octet-stream':
        print('octet-stream returned')
        handle_img_batch(outfile_writer, response.content)

def send_messages():

    ngrok_url = args.ngrok_addr

    temp_videofile = 'temp/result.avi'
    if os.path.exists(temp_videofile):
        os.remove(temp_videofile)
    outfile_writer = cv2.VideoWriter(temp_videofile, cv2.VideoWriter_fourcc(*'FMP4'), hparams.fps, hparams.resolution)

    # small hack to allow local testing
    if (args.ngrok_addr == 'http://localhost:3000'):
        server_path = "output/"
    
    while True:
        return_value = poll_server(ngrok_url, outfile_writer)
        if return_value == 'break':
            break
        elif return_value == 'continue':
             continue


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

    data = {"processed_file": f"{media_folder}{outfile}"}
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
    
