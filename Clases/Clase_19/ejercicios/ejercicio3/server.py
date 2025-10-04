import socket
import socketserver
import threading
import sys
import os

# --- Configuración y Constantes ---
# El directorio donde se encuentran los archivos para compartir
SHARED_DIR = "shared_files" 
CHUNK_SIZE = 1024 # Tamaño del trozo para enviar archivos

# Asegurar que el directorio compartido exista
if not os.path.exists(SHARED_DIR):
    os.makedirs(SHARED_DIR)
    print(f"[INFO] Creado directorio: {SHARED_DIR}")
    # Opcional: crea un archivo de prueba si no existe
    if not os.path.exists(os.path.join(SHARED_DIR, "test.txt")):
        with open(os.path.join(SHARED_DIR, "test.txt"), "w") as f:
            f.write("Este es un archivo de prueba para descargar.\n")

class ManejadorArchivos(socketserver.BaseRequestHandler):
    """Maneja las solicitudes de cada cliente en un hilo separado."""
    
    def setup(self):
        # Desempaqueta solo la IP y el puerto (los dos primeros valores de la tupla IPv6)
        self.ip, self.puerto, _, _ = self.client_address 
        self.client_info = f"[{self.ip}]:{self.puerto}"
        print(f"[*] Nueva conexión desde: {self.client_info}")

    def handle(self):
        """Bucle principal de manejo de comandos."""
        
        # Enviar mensaje de bienvenida
        self.request.sendall(b"Conectado al Servidor de Archivos IPv6. Escribe 'LIST' o 'GET <nombre_archivo>'.\n")

        while True:
            try:
                # Recibir el comando del cliente
                data = self.request.recv(CHUNK_SIZE).decode().strip()
                if not data:
                    break # Cliente se desconectó
                
                print(f"[{self.client_info}] COMANDO: {data}")
                partes = data.split()
                comando = partes[0].upper()

                if comando == "LIST":
                    self._listar_archivos()
                elif comando == "GET" and len(partes) > 1:
                    nombre_archivo = partes[1]
                    self._enviar_archivo(nombre_archivo)
                elif comando == "QUIT":
                    break
                else:
                    self.request.sendall(b"Comando no reconocido. Usa LIST o GET.\n")
                    
            except ConnectionResetError:
                break
            except Exception as e:
                print(f"[ERROR en {self.client_info}]: {e}")
                break

    def finish(self):
        """Se llama cuando la conexión termina."""
        print(f"[*] Conexión cerrada con: {self.client_info}")

    # --- Métodos de Comando ---

    def _listar_archivos(self):
        """Envía al cliente la lista de archivos disponibles."""
        try:
            archivos = [f for f in os.listdir(SHARED_DIR) if os.path.isfile(os.path.join(SHARED_DIR, f))]
            if not archivos:
                respuesta = "No hay archivos disponibles.\n"
            else:
                respuesta = "\nArchivos disponibles:\n" + "\n".join(archivos) + "\n"
            self.request.sendall(respuesta.encode())
        except Exception as e:
            error_msg = f"Error al listar archivos: {e}\n"
            self.request.sendall(error_msg.encode())

    def _enviar_archivo(self, nombre_archivo):
        """
        Envía un archivo al cliente en trozos (chunks).
        Este es el paso crítico para manejar archivos grandes eficientemente.
        """
        ruta_completa = os.path.join(SHARED_DIR, nombre_archivo)
        
        if not os.path.exists(ruta_completa) or not os.path.isfile(ruta_completa):
            self.request.sendall(f"ERROR: Archivo '{nombre_archivo}' no encontrado o no es válido.\n".encode())
            return
            
        try:
            # 1. Informar al cliente que la transferencia comenzará
            file_size = os.path.getsize(ruta_completa)
            # Protocolo: OK <tamaño_archivo>
            self.request.sendall(f"OK {file_size}\n".encode()) 

            # 2. Abrir y enviar el archivo en chunks
            with open(ruta_completa, 'rb') as f:
                bytes_enviados = 0
                while bytes_enviados < file_size:
                    # Leer un chunk de datos
                    bytes_leidos = f.read(CHUNK_SIZE) 
                    if not bytes_leidos:
                        break # Fin del archivo
                    
                    # Enviar el chunk
                    self.request.sendall(bytes_leidos)
                    bytes_enviados += len(bytes_leidos)
                    
            print(f"[{self.client_info}] Transferencia completa: {nombre_archivo} ({bytes_enviados} bytes)")
            
        except PermissionError:
            self.request.sendall(b"ERROR: Permiso denegado para leer el archivo.\n")
        except Exception as e:
            print(f"[ERROR de transferencia]: {e}")
            self.request.sendall(b"ERROR: Fallo durante la transferencia del archivo.\n")


class ServidorArchivosIPv6(socketserver.ThreadingTCPServer):
    """Clase de servidor que utiliza IPv6 y Threads."""
    address_family = socket.AF_INET6
    allow_reuse_address = True 

# --- Ejecución Principal del Servidor ---
if __name__ == "__main__":
    HOST, PORT = "::", 9999
    
    print("--- Servidor de Archivos IPv6 ---")
    print(f"Compartiendo archivos desde el directorio: {os.path.abspath(SHARED_DIR)}")
    
    try:
        servidor = ServidorArchivosIPv6((HOST, PORT), ManejadorArchivos)
        
        server_thread = threading.Thread(target=servidor.serve_forever, daemon=True)
        server_thread.start()
        
        print(f"Servidor iniciado: Escuchando en [{HOST}]:{PORT}")
        print("Presiona Ctrl+C para detener el servidor.")

        while True:
            # Mantener el hilo principal activo hasta la interrupción
            import time
            time.sleep(1) 

    except KeyboardInterrupt:
        print("\n[INFO] Deteniendo servidor...")
        servidor.shutdown()
        servidor.server_close()
        sys.exit(0)
    except Exception as e:
        print(f"[FATAL] Error al iniciar el servidor: {e}")