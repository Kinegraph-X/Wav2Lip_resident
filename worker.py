
import socket
import subprocess, time, json
import record_audio
import argparse

from keyboard_listener import keyboard_listener

parser = argparse.ArgumentParser(description='Worker which records an audio file from the mic, sneds it to a Google Notebook and retrieve the result of the computation')
parser.add_argument('--ngrok_addr', type=str, 
					help='A Ngrok tunnel may have been started from that Public URL',
                    required=False,
                    default='http://localhost:3000'
                    )
args = parser.parse_args()

server_path = "/content/Wav2Lip_with_cache/output/"
media_folder = "media/"
outfile = "lipsynced_avatar.mp4"

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

def send_messages():
    
    ngrok_url = args.ngrok_addr

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

    data = {"processed_file": f"media/{outfile}"}
    serialized_data = json.dumps(data).encode('utf-8')
    client.sendall(serialized_data)

    """

    # Simulate sending messages
    time.sleep(5)
    client.sendall(b"processed_video.mp4")
    print("Sent 'processed_video.mp4'.")

    time.sleep(5)
    client.sendall(b"another_video.mp4")
    print("Sent 'another_video.mp4'.")

    time.sleep(5)
    client.sendall(b"EXIT")
    print("Sent 'EXIT'.")
    """

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

    try:
        client.connect(("localhost", 9999))
        print("Connected to server.")
    except KeyboardInterrupt:
        client.close()

    listen_indefinitely()
    
