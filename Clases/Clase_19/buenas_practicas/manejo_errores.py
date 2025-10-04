import socket

try:
    sock = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
    sock.connect(('::1', 8080))
except socket.gaierror as e:
    print(f"Error de resolución de dirección: {e}")
except socket.error as e:
    print(f"Error de socket: {e}")
except Exception as e:
    print(f"Error inesperado: {e}")
finally:
    sock.close()