import socket
import sys

SERVER_HOST = "::1" # Loopback IPv6
SERVER_PORT = 9998
CHUNK_SIZE = 1024

def cliente_ipv6():
    """Cliente que se conecta usando la familia AF_INET6 (IPv6)."""
    try:
        # 1. Crear socket IPv6
        sock = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
        print(f"Intentando conectar a [{SERVER_HOST}]:{SERVER_PORT} (IPv6)...")
        sock.connect((SERVER_HOST, SERVER_PORT))
        
        # 2. Recibir mensaje de bienvenida
        respuesta_inicial = sock.recv(CHUNK_SIZE).decode()
        print(f"Servidor dice: {respuesta_inicial.strip()}")

        # 3. Enviar y recibir datos (simulando transferencia)
        mensaje2 = "Datos de prueba desde IPv6."
        sock.sendall(mensaje2.encode())
        print(f"Enviado: '{mensaje2}'")
        
        eco = sock.recv(CHUNK_SIZE).decode()
        print(f"Recibido: '{eco.strip()}'")

        # 4. Cerrar conexión
        sock.close()
        print("[INFO] Conexión IPv6 cerrada.")

    except Exception as e:
        print(f"[ERROR IPv6]: {e}")

if __name__ == "__main__":
    cliente_ipv6()