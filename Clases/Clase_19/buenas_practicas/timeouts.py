import socket

sock = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
sock.settimeout(5.0)  # Timeout de 5 segundos

try:
    sock.connect(('::1', 8080))
    sock.sendall(b"mensaje")
    data = sock.recv(1024)
except socket.timeout:
    print("La operación excedió el tiempo límite")
finally:
    sock.close()