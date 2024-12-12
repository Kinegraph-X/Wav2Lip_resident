import socket, json, time

time.sleep(6)
print("called")
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

if __name__ == "__main__":
    client.connect(("localhost", 9999))

    media_folder = "media/"
    outfile = "lipsynced_avatar.mp4"

    data = {"processed_file": f"{media_folder}{outfile}"}
    serialized_data = json.dumps(data).encode('utf-8')
    client.sendall(serialized_data)