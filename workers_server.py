import socket, json, time
from logger import logger


def start_server(message_queue):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(("localhost", 9999))
    server.listen(1)
    logger.info("Video Playback socket listening on port 9999...")

    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client.connect(("127.0.0.1", 65432))
        logger.info("Video Playback Connected to synchronization socket.")
    except Exception as e:
        logger.info(f"Video Playback Failed to connect to synchronization socket. {e}")
    client.sendall('PLAYBACK_READY'.encode('utf-8'))

    conn, addr = server.accept()
    logger.info(f"Video Playback Connected by Client")

    while True:
        try:
            data = conn.recv(1024).decode('utf-8')
            if not len(data):
                time.sleep(0.1)
                continue
            if data == "EXIT":
                logger.info("Exiting video playback socket...")
                break
            logger.info(f"video playback socket Received: {data}")
            message_queue.put(data)  # Pass the message to the queue
        except ConnectionResetError:
            pass
    conn.close()
