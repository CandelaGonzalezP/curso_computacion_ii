import socketserver
import socket
import threading
from threading import current_thread

class ManejadorThreading(socketserver.BaseRequestHandler):
    def handle(self):
        thread_name = current_thread().name
        print(f"[{thread_name}] Conexión de: {self.client_address}")
        
        while True:
            data = self.request.recv(1024)
            if not data:
                break
            
            print(f"[{thread_name}] Recibido: {data.decode()}")
            respuesta = f"[{thread_name}] Echo: {data.decode()}"
            self.request.sendall(respuesta.encode())
        
        print(f"[{thread_name}] Conexión cerrada")

class ServidorIPv6Threading(socketserver.ThreadingTCPServer):
    address_family = socket.AF_INET6
    allow_reuse_address = True

if __name__ == "__main__":
    HOST, PORT = "::", 9999
    
    servidor = ServidorIPv6Threading((HOST, PORT), ManejadorThreading)
    print(f"Servidor multi-hilo IPv6 en [{HOST}]:{PORT}")
    
    try:
        servidor.serve_forever()
    except KeyboardInterrupt:
        print("\nCerrando servidor...")
        servidor.shutdown()