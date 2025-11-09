#!/usr/bin/env python3
"""
Servidor de Procesamiento Distribuido (Parte B)
Sistema con multiprocessing para tareas CPU-bound
"""

import argparse
import socket
import socketserver
import multiprocessing as mp
from multiprocessing import Pool, Queue, Manager
from concurrent.futures import ProcessPoolExecutor
import logging
import os
import sys
from typing import Dict, Any, Optional

# Importaciones locales
from processor.screenshot import ScreenshotGenerator
from processor.performance import PerformanceAnalyzer
from processor.image_processor import ImageProcessor
from common.protocol import Protocol
from common.serialization import Serializer

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - [%(processName)s] - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ProcessingRequestHandler(socketserver.BaseRequestHandler):
    """Handler para procesar solicitudes de procesamiento"""
    
    def handle(self):
        """Manejar solicitud entrante"""
        logger.info(f"Connection from {self.client_address}")
        
        try:
            # Recibir datos usando el protocolo
            data = Protocol.receive_sync(self.request)
            
            if not data:
                logger.warning("No data received")
                return
            
            # Deserializar solicitud
            request_data = Serializer.deserialize(data)
            logger.info(f"Processing request for URL: {request_data.get('url', 'unknown')}")
            
            # Procesar solicitud usando el pool de procesos
            result = self.server.process_request_data(request_data)
            
            # Serializar resultado
            response_data = Serializer.serialize(result)
            
            # Enviar respuesta
            Protocol.send_sync(self.request, response_data)
            
            logger.info(f"Request processed successfully for {request_data.get('url')}")
            
        except Exception as e:
            logger.error(f"Error handling request: {str(e)}", exc_info=True)
            try:
                # Enviar error al cliente
                error_response = {
                    'error': str(e),
                    'screenshot': None,
                    'performance': None,
                    'thumbnails': []
                }
                response_data = Serializer.serialize(error_response)
                Protocol.send_sync(self.request, response_data)
            except:
                pass


class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    """Servidor TCP con threading para manejar múltiples conexiones"""
    
    allow_reuse_address = True
    daemon_threads = True
    
    def __init__(self, server_address, RequestHandlerClass, num_processes):
        super().__init__(server_address, RequestHandlerClass)
        self.num_processes = num_processes
        
        # Crear pool de procesos
        logger.info(f"Creating process pool with {num_processes} workers")
        self.executor = ProcessPoolExecutor(max_workers=num_processes)
        
        # Inicializar componentes en el proceso principal
        self.screenshot_gen = ScreenshotGenerator()
        self.performance_analyzer = PerformanceAnalyzer()
        self.image_processor = ImageProcessor()
        
    def process_request_data(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Procesar datos de solicitud usando el pool de procesos
        Ejecuta operaciones CPU-bound en procesos separados
        """
        url = request_data.get('url')
        html = request_data.get('html', '')
        operations = request_data.get('operations', [])
        
        logger.info(f"Starting parallel processing for {url}")
        
        # Crear tareas para el pool de procesos
        futures = {}
        
        if 'screenshot' in operations:
            futures['screenshot'] = self.executor.submit(
                process_screenshot,
                url
            )
        
        if 'performance' in operations:
            futures['performance'] = self.executor.submit(
                process_performance,
                url,
                html
            )
        
        if 'images' in operations:
            futures['images'] = self.executor.submit(
                process_images,
                url,
                html
            )
        
        # Recolectar resultados
        results = {
            'screenshot': None,
            'performance': None,
            'thumbnails': []
        }
        
        for operation, future in futures.items():
            try:
                result = future.result(timeout=45)  # Timeout por operación
                
                if operation == 'screenshot':
                    results['screenshot'] = result
                elif operation == 'performance':
                    results['performance'] = result
                elif operation == 'images':
                    results['thumbnails'] = result
                    
            except Exception as e:
                logger.error(f"Error in {operation} processing: {str(e)}")
                if operation == 'performance':
                    results['performance'] = {
                        'error': str(e),
                        'load_time_ms': 0,
                        'total_size_kb': 0,
                        'num_requests': 0
                    }
        
        logger.info(f"Completed parallel processing for {url}")
        return results
    
    def shutdown(self):
        """Apagar servidor y pool de procesos"""
        logger.info("Shutting down server...")
        self.executor.shutdown(wait=True)
        super().shutdown()


# Funciones worker para ejecutar en procesos separados
def process_screenshot(url: str) -> Optional[str]:
    """
    Generar screenshot de la página
    Ejecutado en proceso separado (CPU-bound)
    """
    try:
        from processor.screenshot import ScreenshotGenerator
        generator = ScreenshotGenerator()
        screenshot_data = generator.capture(url)
        return screenshot_data
    except Exception as e:
        logger.error(f"Screenshot error: {str(e)}")
        return None


def process_performance(url: str, html: str) -> Dict[str, Any]:
    """
    Analizar rendimiento de la página
    Ejecutado en proceso separado (CPU-bound)
    """
    try:
        from processor.performance import PerformanceAnalyzer
        analyzer = PerformanceAnalyzer()
        performance_data = analyzer.analyze(url, html)
        return performance_data
    except Exception as e:
        logger.error(f"Performance analysis error: {str(e)}")
        return {
            'error': str(e),
            'load_time_ms': 0,
            'total_size_kb': 0,
            'num_requests': 0
        }


def process_images(url: str, html: str) -> list:
    """
    Procesar imágenes y generar thumbnails
    Ejecutado en proceso separado (CPU-bound)
    """
    try:
        from processor.image_processor import ImageProcessor
        processor = ImageProcessor()
        thumbnails = processor.process(url, html)
        return thumbnails
    except Exception as e:
        logger.error(f"Image processing error: {str(e)}")
        return []


class ProcessingServer:
    """Servidor de procesamiento principal"""
    
    def __init__(self, ip: str, port: int, num_processes: int):
        self.ip = ip
        self.port = port
        self.num_processes = num_processes
        self.server = None
        
    def run(self):
        """Iniciar servidor"""
        logger.info(f"Starting Processing Server on {self.ip}:{self.port}")
        logger.info(f"Process pool size: {self.num_processes}")
        
        try:
            # Determinar familia de dirección (IPv4 o IPv6)
            try:
                socket.inet_pton(socket.AF_INET6, self.ip)
                socketserver.TCPServer.address_family = socket.AF_INET6
                logger.info("Using IPv6")
            except socket.error:
                socketserver.TCPServer.address_family = socket.AF_INET
                logger.info("Using IPv4")
            
            # Crear servidor
            self.server = ThreadedTCPServer(
                (self.ip, self.port),
                ProcessingRequestHandler,
                self.num_processes
            )
            
            logger.info("Server ready to accept connections")
            
            # Servir forever
            self.server.serve_forever()
            
        except OSError as e:
            logger.error(f"Error starting server: {e}")
            raise
        except KeyboardInterrupt:
            logger.info("Server interrupted by user")
        finally:
            if self.server:
                self.server.shutdown()
                self.server.server_close()


def parse_arguments():
    """Parsear argumentos de línea de comandos"""
    parser = argparse.ArgumentParser(
        description='Servidor de Procesamiento Distribuido',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos:
  %(prog)s -i 127.0.0.1 -p 9000
  %(prog)s -i ::1 -p 9000 -n 8
  %(prog)s -i 0.0.0.0 -p 9000
        """
    )
    
    parser.add_argument(
        '-i', '--ip',
        required=True,
        help='Dirección de escucha'
    )
    
    parser.add_argument(
        '-p', '--port',
        required=True,
        type=int,
        help='Puerto de escucha'
    )
    
    parser.add_argument(
        '-n', '--processes',
        type=int,
        default=mp.cpu_count(),
        help=f'Número de procesos en el pool (default: {mp.cpu_count()})'
    )
    
    return parser.parse_args()


def main():
    """Función principal"""
    # Necesario para multiprocessing en Windows
    mp.set_start_method('spawn', force=True)
    
    args = parse_arguments()
    
    server = ProcessingServer(
        ip=args.ip,
        port=args.port,
        num_processes=args.num_processes
    )
    
    try:
        server.run()
    except Exception as e:
        logger.error(f"Server error: {e}", exc_info=True)
        return 1
    
    return 0


if __name__ == '__main__':
    exit(main())