"""
Parte B: Servidor de Procesamiento con Multiprocessing y SocketServer.
"""

import socketserver
import multiprocessing
import argparse
import sys
import socket
from typing import Tuple, Dict, Any

from common.protocol import (
    ProtocolHandler, 
    TASK_SCREENSHOT, TASK_PERFORMANCE, TASK_IMAGES,
    RESP_SUCCESS, RESP_ERROR
)
from common import ProcessingError, TaskTimeoutError, ProtocolError

from processor import screenshot, performance, image_processor

mp_pool = None

TASK_MAP = {
    TASK_SCREENSHOT: screenshot.take_screenshot,
    TASK_PERFORMANCE: performance.analyze_performance,
    TASK_IMAGES: image_processor.process_images,
}

def run_task(msg_type: int, payload: Dict[str, Any]) -> Any:
    """
    Función única que el Pool ejecuta.
    """
    task_func = TASK_MAP.get(msg_type)
    if not task_func:
        raise ValueError(f"Tipo de tarea desconocido: {msg_type}")

    if msg_type == TASK_IMAGES:
        return task_func(payload.get('image_urls', []))
    else:
        url = payload.get('url')
        if not url:
            raise ValueError("Payload no contiene 'url'")
        return task_func(url)


class TaskHandler(socketserver.BaseRequestHandler):
    """
    Handler para cada conexión de socket. Se ejecuta en un HILO separado.
    """
    
    def handle(self):
        print(f"[ProcServer] Conexión recibida de {self.client_address}")
        proto = ProtocolHandler()
        
        try:
            msg_type, payload = proto.sync_read_message(self.request)
            
            print(f"[ProcServer] Tarea {msg_type} recibida para: {payload.get('url')}")
            
            result = mp_pool.apply(run_task, args=(msg_type, payload))
            
            print(f"[ProcServer] Tarea {msg_type} completada. Enviando respuesta.")
            proto.sync_send_message(self.request, RESP_SUCCESS, {"data": result})

        except (ProcessingError, TaskTimeoutError, ValueError) as e:
            print(f"[ProcServer] Error de Tarea: {e}")
            self._send_error(proto, f"Error de Tarea: {e}")
        
        except ProtocolError as e:
            print(f"[ProcServer] Error de Protocolo: {e}")
        
        except Exception as e:
            print(f"[ProcServer] Error interno inesperado: {e}")
            self._send_error(proto, f"Error interno del servidor: {e}")
        
        print(f"[ProcServer] Conexión cerrada con {self.client_address}")

    def _send_error(self, proto: ProtocolHandler, error_msg: str):
        """Intenta enviar un mensaje de error al cliente si es posible."""
        try:
            proto.sync_send_message(self.request, RESP_ERROR, {"error": error_msg})
        except Exception as se:
            print(f"[ProcServer] No se pudo enviar mensaje de error (conexión cerrada?): {se}")


class ProcessingTCPServer(socketserver.ThreadingTCPServer):
    allow_reuse_address = True
    
    def __init__(self, server_address: Tuple[str, int], RequestHandlerClass: Any, pool: multiprocessing.Pool):
        super().__init__(server_address, RequestHandlerClass)
        self.mp_pool = pool

    def server_close(self):
        print("[ProcServer] Cerrando pool de procesos...")
        self.mp_pool.close()
        self.mp_pool.join()
        super().server_close()


def parse_args():
    parser = argparse.ArgumentParser(
        description='Servidor de Procesamiento Distribuido (Parte B)',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument('-i', '--ip', type=str, required=True, help='Dirección de escucha (ej: 0.0.0.0 o ::)')
    parser.add_argument('-p', '--port', type=int, required=True, help='Puerto de escucha')
    parser.add_argument('-n', '--processes', type=int, default=None, help=f'Número de procesos en el pool (default: {multiprocessing.cpu_count()})')
    return parser.parse_args()


def main():
    global mp_pool 
    args = parse_args()
    
    try:
        addr_info = socket.getaddrinfo(args.ip, args.port, socket.AF_UNSPEC, socket.SOCK_STREAM, 0, socket.AI_PASSIVE)
        family = addr_info[0][0]
        server_address = addr_info[0][4]
    except socket.gaierror as e:
        print(f"Error resolviendo dirección {args.ip}: {e}")
        sys.exit(1)

    ProcessingTCPServer.address_family = family
    pool_size = args.processes or multiprocessing.cpu_count()
    
    try:
        multiprocessing.set_start_method('spawn', force=True)
    except RuntimeError:
        pass 
        
    mp_pool = multiprocessing.Pool(processes=pool_size)
    
    print("=" * 60)
    print("Servidor de Procesamiento (Parte B)")
    print(f"Iniciando en: {server_address} (Familia: {family})")
    print(f"Tamaño del Pool de Procesos: {pool_size}")
    print("=" * 60)
    
    try:
        with ProcessingTCPServer(server_address, TaskHandler, mp_pool) as server:
            server.serve_forever()
    except KeyboardInterrupt:
        print("\n[ProcServer] Apagando servidor...")
        server.shutdown()

if __name__ == "__main__":
    main()