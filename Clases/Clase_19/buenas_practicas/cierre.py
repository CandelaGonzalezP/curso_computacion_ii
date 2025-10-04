import socket

sock = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
try:
    # ... operaciones con el socket ...
    sock.shutdown(socket.SHUT_RDWR)
except socket.error:
    pass
finally:
    sock.close()