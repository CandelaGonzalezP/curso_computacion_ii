import socket
import sys

SERVER_HOST = "127.0.0.1" # Loopback IPv4
SERVER_PORT = 9998
CHUNK_SIZE = 1024

def cliente_ipv4():
    """Cliente que se conecta usando la familia AF_INET (IPv4)."""
    try:
        # 1. Crear socket IPv4
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print(f"Intentando conectar a {SERVER_HOST}:{SERVER_PORT} (IPv4)...")
        sock.connect((SERVER_HOST, SERVER_PORT))
        
        # 2. Recibir mensaje de bienvenida
        respuesta_inicial = sock.recv(CHUNK_SIZE).decode()
        print(f"Servidor dice: {respuesta_inicial.strip()}")

        # 3. Enviar y recibir datos (simulando transferencia)
        mensaje1 = "Mensaje de prueba desde IPv4."
        sock.sendall(mensaje1.encode())
        print(f"Enviado: '{mensaje1}'")
        
        eco = sock.recv(CHUNK_SIZE).decode()
        print(f"Recibido: '{eco.strip()}'")

        # 4. Cerrar conexión
        sock.close()
        print("[INFO] Conexión IPv4 cerrada.")

    except Exception as e:
        print(f"[ERROR IPv4]: {e}")

if __name__ == "__main__":
    cliente_ipv4()