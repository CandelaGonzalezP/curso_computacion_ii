#!/usr/bin/env python3
"""
ipv6_echo_server.py
Servidor echo IPv6 en el puerto 8888 que devuelve los mensajes en MAYÚSCULAS.
Acepta múltiples mensajes por conexión. Comando "QUIT" (insensible a mayúsculas)
cierra la conexión del cliente.
"""

import socket
import threading

HOST = '::'        # escuchar en todas las interfaces IPv6
PORT = 8888
BUFFER_SIZE = 1024

def handle_client(conn: socket.socket, addr):
    """Maneja la comunicación con un cliente (mantiene la conexión abierta)."""
    print(f"[+] Conexión desde {addr}")
    try:
        with conn:
            while True:
                data = conn.recv(BUFFER_SIZE)
                if not data:
                    # cliente cerró la conexión
                    print(f"[-] Cliente {addr} desconectó")
                    break

                # Decodificar con tolerancia a errores
                message = data.decode('utf-8', errors='replace')
                # Quitar saltos de línea al final para procesar el comando
                stripped = message.rstrip('\r\n')

                print(f"[>] Recibido de {addr}: {repr(stripped)}")

                # Comando QUIT (insensible a mayúsculas) cierra la conexión
                if stripped.upper() == 'QUIT':
                    # opcional: responder antes de cerrar
                    conn.sendall(b'BYE\n')
                    print(f"[i] Cierre por comando QUIT desde {addr}")
                    break

                # Responder con mayúsculas (añadimos newline para claridad)
                response = stripped.upper() + '\n'
                conn.sendall(response.encode('utf-8'))

    except Exception as e:
        print(f"[!] Error con {addr}: {e}")

def main():
    server_sock = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
    # Reusar dirección
    server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    # Asegurar que sea IPv6-only (evita direcciones IPv4-mapeadas)
    try:
        server_sock.setsockopt(socket.IPPROTO_IPV6, socket.IPV6_V6ONLY, 1)
    except (AttributeError, OSError):
        # En algunas plataformas esta opción puede no estar disponible o no necesitarse
        pass

    server_sock.bind((HOST, PORT))
    server_sock.listen(5)
    print(f"Servidor IPv6 escuchando en [{HOST}]:{PORT}")

    try:
        while True:
            conn, addr = server_sock.accept()
            # Lanzar hilo para manejar cada cliente simultáneamente
            t = threading.Thread(target=handle_client, args=(conn, addr), daemon=True)
            t.start()
    except KeyboardInterrupt:
        print("\n[!] Interrupción por teclado. Cerrando servidor...")
    finally:
        server_sock.close()

if __name__ == '__main__':
    main()
