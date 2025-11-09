# server_processing.py

import socketserver
import multiprocessing
import concurrent.futures
import argparse
import os
import sys
import struct
import socket

from common.serialization import serialize_message, deserialize_message, HEADER_SIZE
from common.protocol import KEY_URL
from processor.screenshot import generate_screenshot 
from processor.performance import analyze_performance 
from processor.image_processor import generate_thumbnails

HEADER_FORMAT = '<I'

def perform_processing(url: str) -> dict:
    """Función ejecutada por cada worker en el ProcessPoolExecutor (CPU-bound)."""
    screenshot_b64 = generate_screenshot(url) 
    performance_data = analyze_performance(url) 
    thumbnails_b64 = generate_thumbnails(url)
    
    return {
        "screenshot": screenshot_b64,
        "performance": performance_data,
        "thumbnails": thumbnails_b64
    }

class ProcessingHandler(socketserver.BaseRequestHandler):
    """Maneja las conexiones TCP del Servidor A usando ThreadingMixIn."""
    executor: concurrent.futures.ProcessPoolExecutor = None 

    def handle(self):
        self.request.settimeout(5) 
        request_data = {}
        processing_result = {}
        url = "N/A"
        
        try:
            # 1. Recibir el encabezado (longitud)
            header = self.request.recv(HEADER_SIZE)
            if not header or len(header) < HEADER_SIZE:
                return 
            
            (data_len,) = struct.unpack(HEADER_FORMAT, header)

            # 2. Recibir el cuerpo del mensaje (JSON)
            buffer = b''
            bytes_recibidos = 0
            while bytes_recibidos < data_len:
                chunk = self.request.recv(min(4096, data_len - bytes_recibidos))
                if not chunk:
                    return 
                buffer += chunk
                bytes_recibidos += len(chunk)
            
            request_data = deserialize_message(header + buffer)
            url = request_data.get(KEY_URL, "N/A")
            
            if not url:
                print("Error: URL no recibida en la solicitud.")
                processing_result = {"status": "error", "message": "Missing URL in request"}
            else:
                print(f"Petición de procesamiento recibida para: {url} | Delegando a pool.")
                
                # 3. Ejecutar la tarea en el pool de procesos
                future = self.executor.submit(perform_processing, url)
                processing_result = future.result(timeout=60) 
            
        except concurrent.futures.TimeoutError:
            print(f"Error: Timeout de procesamiento para {url}")
            processing_result = {"status": "error", "message": "Processing Timeout (CPU bound)"}
        except socketserver.socket.timeout:
            print("Error: Timeout de lectura en socket (Servidor B)")
            processing_result = {"status": "error", "message": "Socket Read Timeout"}
        except Exception as e:
            print(f"Error al manejar/deserializar mensaje para {url}: {e}")
            processing_result = {"status": "error", "message": f"Server B execution error: {e.__class__.__name__}"}
        
        # 4. Enviar el resultado de vuelta al Servidor A
        response_bytes = serialize_message(processing_result)
        try:
            self.request.sendall(response_bytes)
            print(f"Resultado de procesamiento enviado para {url}")
        except Exception as e:
            print(f"Error al enviar respuesta al Servidor A para {url}: {e}")

def main():
    parser = argparse.ArgumentParser(description="Servidor de Procesamiento Distribuido")
    parser.add_argument("-i", "--ip", required=True, help="Dirección de escucha")
    parser.add_argument("-p", "--port", required=True, type=int, help="Puerto de escucha")
    parser.add_argument("-n", "--processes", type=int, default=os.cpu_count(),
                        help=f"Número de procesos en el pool (default: {os.cpu_count()})")

    args = parser.parse_args()

    num_processes = args.processes
    with concurrent.futures.ProcessPoolExecutor(max_workers=num_processes) as executor:
        ProcessingHandler.executor = executor
        
        class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
            allow_reuse_address = True 
            
            # Soportar IPv4/IPv6 indistintamente
            address_family = socket.AF_INET
            try:
                if socket.has_ipv6:
                    address_family = socket.AF_INET6
            except Exception:
                pass
                
        try:
            server = ThreadedTCPServer((args.ip, args.port), ProcessingHandler)
            print(f"Servidor de Procesamiento (B) escuchando en {server.server_address} | Procesos: {num_processes}...")
            server.serve_forever()
        except KeyboardInterrupt:
            print("\nApagando el Servidor de Procesamiento...")
        except Exception as e:
            print(f"Error al iniciar el servidor: {e}")
            
if __name__ == "__main__":
    main()