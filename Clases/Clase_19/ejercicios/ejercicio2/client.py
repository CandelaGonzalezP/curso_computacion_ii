import socket
import threading
import sys
import time

# Configuración del cliente
SERVER_HOST = "::1" # Loopback IPv6
SERVER_PORT = 9999
NOMBRE_CLIENTE = ""

def recibir_mensajes(cliente_socket):
    """
    Función que se ejecuta en un hilo separado para escuchar constantemente
    los mensajes entrantes del servidor.
    """
    while True:
        try:
            # Espera datos del servidor
            data = cliente_socket.recv(1024)
            if not data:
                print("\n[INFO] Desconexión del servidor. Presiona Enter para salir.")
                break
            
            # Imprime el mensaje recibido
            mensaje = data.decode().strip()
            sys.stdout.write('\r' + ' ' * 80 + '\r') # Limpiar la línea de entrada
            print(mensaje)
            sys.stdout.write(f"Tú: ") # Mostrar de nuevo el prompt de entrada
            sys.stdout.flush()
            
        except OSError:
            # Ocurre si el socket es cerrado externamente (ej: al salir)
            break
        except Exception as e:
            print(f"\n[ERROR de recepción]: {e}")
            break

def enviar_mensajes(cliente_socket):
    """
    Bucle principal para leer la entrada del usuario y enviar mensajes al servidor.
    """
    print(f"\nConectado. Escribe y presiona Enter para enviar.")
    while True:
        try:
            # Leer el mensaje del usuario (bloqueante)
            mensaje = input("Tú: ")
            
            if mensaje.lower() in ('/quit', '/exit'):
                print("[INFO] Cerrando conexión...")
                cliente_socket.close()
                break

            if mensaje.strip():
                # Enviar el mensaje al servidor
                cliente_socket.sendall(mensaje.encode())
                
        except EOFError:
            print("\n[INFO] Comando de fin de archivo. Cerrando conexión.")
            cliente_socket.close()
            break
        except Exception as e:
            print(f"[ERROR de envío]: {e}")
            break


if __name__ == "__main__":
    
    # 1. Crear el socket IPv6
    try:
        client_socket = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
        client_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    except Exception as e:
        print(f"[FATAL] Error al crear socket IPv6: {e}")
        sys.exit(1)
    
    # 2. Conectar al servidor
    try:
        server_address = (SERVER_HOST, SERVER_PORT)
        print(f"Intentando conectar a [{SERVER_HOST}]:{SERVER_PORT}...")
        client_socket.connect(server_address)
        
    except ConnectionRefusedError:
        print(f"[FATAL] Conexión rechazada. Asegúrate de que el servidor esté corriendo en [{SERVER_HOST}]:{SERVER_PORT}.")
        sys.exit(1)
    except socket.gaierror as e:
        print(f"[FATAL] Error de dirección: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"[FATAL] Error de conexión: {e}")
        sys.exit(1)


    # 3. Iniciar el hilo de recepción
    recibir_hilo = threading.Thread(
        target=recibir_mensajes, 
        args=(client_socket,), 
        daemon=True
    )
    recibir_hilo.start()

    # 4. Iniciar el bucle principal de envío (en el hilo principal)
    enviar_mensajes(client_socket)

    # Esperar un poco para que el hilo de recepción termine
    time.sleep(0.5)
    print("Cliente terminado.")