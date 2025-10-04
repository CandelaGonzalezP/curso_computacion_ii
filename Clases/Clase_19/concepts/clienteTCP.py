import socket

# Crear socket IPv6
client_socket = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)

# Conectar al servidor
server_address = ('::1', 8080)
client_socket.connect(server_address)

# Enviar mensaje
message = "Hola desde el cliente IPv6"
client_socket.sendall(message.encode())

# Recibir respuesta
response = client_socket.recv(1024)
print(f"Respuesta del servidor: {response.decode()}")

client_socket.close()