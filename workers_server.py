import socket, json, time



def start_server(message_queue):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(("localhost", 9999))
    server.listen(1)
    print("Server listening on port 9999...")

    conn, addr = server.accept()
    print(f"Connected by {addr}")

    while True:
        data = conn.recv(1024).decode('utf-8')
        if not len(data):
            time.sleep(0.1)
            continue
        if data == "EXIT":
            print("Exiting server...")
            break
        print(f"Received: {data}")
        message_queue.put(data)  # Pass the message to the queue
    conn.close()
