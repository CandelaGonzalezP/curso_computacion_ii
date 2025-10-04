import socket
import sys

# --- Configuración y Constantes ---
SERVER_HOST = "::1" # Loopback IPv6
SERVER_PORT = 9997
CHUNK_SIZE = 1024

def cliente_calculadora():
    """Bucle de conexión e interacción del cliente."""
    try:
        # 1. Crear el socket IPv6
        client_socket = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
        client_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
        # 2. Conectar al servidor
        print(f"Intentando conectar a [{SERVER_HOST}]:{SERVER_PORT}...")
        client_socket.connect((SERVER_HOST, SERVER_PORT))
        
    except ConnectionRefusedError:
        print(f"[ERROR] Conexión rechazada. Asegúrate de que el servidor esté corriendo en [{SERVER_HOST}]:{SERVER_PORT}.")
        return
    except Exception as e:
        print(f"[ERROR] Fallo al conectar: {e}")
        return

    # Bucle de interacción
    while True:
        try:
            # 3. Recibir mensaje inicial/respuesta anterior
            respuesta = client_socket.recv(CHUNK_SIZE).decode()
            if not respuesta:
                print("\n[INFO] Servidor cerró la conexión.")
                break
                
            print(respuesta.strip())

            # 4. Solicitar expresión al usuario
            expresion_usuario = input("\nIngresa expresión o QUIT: ")
            
            if not expresion_usuario:
                continue

            if expresion_usuario.upper() == "QUIT":
                client_socket.sendall(b"QUIT")
                break
                
            # 5. Enviar expresión
            client_socket.sendall(expresion_usuario.encode())

        except EOFError:
            print("\n[INFO] Comando de fin de archivo. Cerrando.")
            break
        except Exception as e:
            print(f"\n[ERROR] Fallo en el cliente durante la comunicación: {e}")
            break

    client_socket.close()
    print("Cliente terminado.")

if __name__ == "__main__":
    cliente_calculadora()