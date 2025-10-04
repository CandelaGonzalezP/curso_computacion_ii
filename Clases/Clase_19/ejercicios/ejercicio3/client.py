import socket
import sys
import os

# --- Configuración y Constantes ---
SERVER_HOST = "::1" # Loopback IPv6
SERVER_PORT = 9999
CHUNK_SIZE = 1024
DOWNLOAD_DIR = "downloads"

# Asegurar que el directorio de descargas exista
if not os.path.exists(DOWNLOAD_DIR):
    os.makedirs(DOWNLOAD_DIR)

def descargar_archivo(sock, nombre_archivo, file_size):
    """
    Recibe los datos del archivo en chunks y los guarda.
    """
    ruta_guardar = os.path.join(DOWNLOAD_DIR, f"DL_{nombre_archivo}")
    bytes_recibidos = 0
    
    print(f"Iniciando descarga de '{nombre_archivo}' ({file_size} bytes)...")
    
    try:
        with open(ruta_guardar, 'wb') as f:
            while bytes_recibidos < file_size:
                # Calcular cuántos bytes quedan por recibir
                bytes_a_recibir = min(CHUNK_SIZE, file_size - bytes_recibidos)
                
                # Recibir el chunk
                chunk = sock.recv(bytes_a_recibir)
                if not chunk:
                    break # Conexión cerrada prematuramente
                
                f.write(chunk)
                bytes_recibidos += len(chunk)
                
                # Imprimir progreso (opcional)
                sys.stdout.write(f"\rProgreso: {bytes_recibidos/file_size*100:.2f}% ({bytes_recibidos} / {file_size} bytes)")
                sys.stdout.flush()
                
        if bytes_recibidos == file_size:
            print(f"\n[ÉXITO] Archivo guardado en: {ruta_guardar}")
        else:
            print(f"\n[ALERTA] Descarga incompleta. Esperado: {file_size}, Recibido: {bytes_recibidos}")

    except Exception as e:
        print(f"\n[ERROR] Fallo al escribir el archivo: {e}")

def cliente_principal():
    """Bucle de conexión y comandos del cliente."""
    try:
        # 1. Crear el socket IPv6
        client_socket = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
        client_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        client_socket.connect((SERVER_HOST, SERVER_PORT))
        print(f"Conectado a [{SERVER_HOST}]:{SERVER_PORT}")
        
    except ConnectionRefusedError:
        print(f"[FATAL] Conexión rechazada. Servidor no activo.")
        return
    except Exception as e:
        print(f"[FATAL] Error de conexión: {e}")
        return

    # Bucle de comandos
    while True:
        try:
            # 1. Recibir mensajes iniciales/respuestas del servidor
            respuesta_inicial = client_socket.recv(CHUNK_SIZE).decode()
            if not respuesta_inicial:
                print("\n[INFO] Servidor cerró la conexión.")
                break
                
            print("\n" + respuesta_inicial.strip())
            
            # Verificar si la respuesta es una señal de inicio de transferencia (GET)
            if respuesta_inicial.startswith("OK"):
                # Protocolo: OK <tamaño_archivo>
                try:
                    # El nombre del archivo se obtiene del comando GET previo
                    _, file_size_str = respuesta_inicial.split()
                    file_size = int(file_size_str)
                    
                    # Inicializar last_filename
                    last_filename = None
                    
                    # El nombre del archivo es la última solicitud GET
                    # (Esto requiere un manejo cuidadoso del estado, pero para un chat simple funciona)
                    if last_filename is not None:
                        descargar_archivo(client_socket, last_filename, file_size)
                    else:
                        print("ERROR: No se recuerda el nombre del archivo solicitado.")
                    
                    continue # Vuelve al inicio para esperar la siguiente instrucción

                except ValueError:
                    print("ERROR de protocolo: Respuesta OK inválida.")
                    continue
            
            # 2. Solicitar y enviar comando
            comando_usuario = input("Comando (LIST/GET <nombre>/QUIT): ")
            if not comando_usuario:
                continue

            comando_usuario = comando_usuario.strip()
            
            if comando_usuario.upper() == "QUIT":
                client_socket.sendall(b"QUIT")
                break
                
            if comando_usuario.upper().startswith("GET "):
                # Guardar el nombre del archivo solicitado para usarlo en la función de descarga
                last_filename = comando_usuario.split()[1] 

            client_socket.sendall(comando_usuario.encode())

        except Exception as e:
            print(f"\n[ERROR] Fallo en el cliente: {e}")
            break

    client_socket.close()

if __name__ == "__main__":
    cliente_principal()