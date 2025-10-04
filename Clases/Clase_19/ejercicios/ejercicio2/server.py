import socket
import socketserver
import threading
import sys
import time

# Lista global para almacenar los sockets de todos los clientes conectados
# Se utiliza un Lock para asegurar que el acceso a la lista sea seguro en entornos multihilo.
CLIENTES = []
CLIENTES_LOCK = threading.Lock()

class ManejadorCliente(socketserver.BaseRequestHandler):
    """
    Manejador para cada conexión de cliente. Cada instancia se ejecuta en su propio hilo.
    """
    
    def setup(self):
        """Se llama una vez que se establece la conexión."""
        
        # Desempaqueta solo la IP y el puerto (los dos primeros valores).
        # Se ignoran Flowinfo y Scope ID, que son específicos de IPv6.
        self.ip, self.puerto, _, _ = self.client_address 
        
        self.socket = self.request
        self.nombre = f"Cliente-{self.ip}:{self.puerto}"
        
        # Agregar el nuevo cliente a la lista global
        with CLIENTES_LOCK:
            CLIENTES.append(self.socket)
        
        print(f"[*] Nueva conexión: {self.nombre}")
        self._transmitir_mensaje_a_todos(f"--- {self.nombre} se ha unido al chat. ---".encode())


    def handle(self):
        """El bucle principal de manejo de la conexión."""
        while True:
            try:
                # Recibir datos del cliente
                data = self.socket.recv(1024)
                if not data:
                    break # Conexión cerrada por el cliente
                
                mensaje_recibido = data.decode().strip()
                mensaje_completo = f"[{self.nombre}]: {mensaje_recibido}"
                print(f"[RECV] {mensaje_completo}")
                
                # Transmitir el mensaje a todos los demás clientes
                self._transmitir_mensaje_a_todos(mensaje_completo.encode())
                
            except ConnectionResetError:
                break # Cliente desconectado abruptamente
            except Exception as e:
                print(f"[ERROR en {self.nombre}]: {e}")
                break

    def finish(self):
        """Se llama cuando la conexión del cliente termina."""
        # Eliminar el cliente de la lista global
        with CLIENTES_LOCK:
            if self.socket in CLIENTES:
                CLIENTES.remove(self.socket)
        
        mensaje_desconexion = f"--- {self.nombre} ha salido del chat. ---"
        print(f"[*] Conexión cerrada: {self.nombre}")
        self._transmitir_mensaje_a_todos(mensaje_desconexion.encode())
        
    def _transmitir_mensaje_a_todos(self, mensaje_bytes):
        """
        Envía un mensaje a todos los clientes conectados, excepto al remitente.
        """
        with CLIENTES_LOCK:
            clientes_activos = list(CLIENTES)
        
        for client_socket in clientes_activos:
            if client_socket != self.socket: # No enviar al remitente
                try:
                    # Anteponer el nombre del remitente al mensaje para el cliente
                    client_socket.sendall(mensaje_bytes + b'\n')
                except:
                    # Si falla el envío, el cliente está caído o cerrado. Se manejará en el próximo loop de handle.
                    print(f"[ALERTA] No se pudo enviar a un cliente.")


class ServidorChatIPv6(socketserver.ThreadingTCPServer):
    """
    Clase de servidor que utiliza IPv6 y Threads para concurrencia.
    """
    address_family = socket.AF_INET6
    # Permite reutilizar la dirección para reinicios rápidos
    allow_reuse_address = True 

# Configuración del servidor
HOST, PORT = "::", 9999 # '::' escucha en todas las interfaces IPv6

if __name__ == "__main__":
    print("--- Servidor de Chat IPv6 ---")
    
    try:
        # Crea el servidor con el host, puerto y el manejador de clientes
        servidor = ServidorChatIPv6((HOST, PORT), ManejadorCliente)
        
        # Inicia el servidor en un hilo separado para poder manejar la interrupción
        server_thread = threading.Thread(target=servidor.serve_forever, daemon=True)
        server_thread.start()
        
        print(f"Servidor iniciado: Escuchando en [{HOST}]:{PORT}")
        print("Presiona Ctrl+C para detener el servidor.")

        # Mantener el hilo principal activo
        while True:
            time.sleep(1) 

    except KeyboardInterrupt:
        print("\n[INFO] Deteniendo servidores...")
        servidor.shutdown()
        servidor.server_close()
        sys.exit(0)
    except Exception as e:
        print(f"[FATAL] Error al iniciar el servidor: {e}")