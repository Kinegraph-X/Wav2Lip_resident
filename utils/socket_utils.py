from logger import logger

def close_client_socket(sock):
    if sock:
        if not is_socket_closed(sock):
            logger.info("Closing client socket...")
            sock.close()

def is_socket_closed(sock):
    try:
        # this will try to read bytes without blocking and also without removing them from buffer (peek only)
        data = sock.sendall(b'{}')
        if not data or len(data) == 0:
            return True
    except BlockingIOError:
        return False  # socket is open and reading from it would block
    except (ConnectionResetError, ConnectionRefusedError):
        return True  # socket was closed for some other reason
    except Exception as e:
        message = str(e)
        if (message[:16] == "[WinError 10057]"):
            return True
        logger.error(f"unexpected exception when checking if a socket is closed {str(e)}")
        return True
    return False