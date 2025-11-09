#!/usr/bin/env python3
"""
Servidor de Scraping Web Asíncrono (Parte A)
Sistema distribuido de scraping con asyncio
"""

import asyncio
import argparse
import json
import socket
import struct
import pickle
from datetime import datetime
from aiohttp import web, ClientSession, ClientTimeout
from typing import Dict, Any, Optional
import logging

# Importaciones locales
from scraper.html_parser import HTMLParser
from scraper.metadata_extractor import MetadataExtractor
from scraper.async_http import AsyncHTTPClient
from common.protocol import Protocol
from common.serialization import Serializer

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ScrapingServer:
    """Servidor asíncrono de scraping web"""
    
    def __init__(self, ip: str, port: int, workers: int, processing_host: str, processing_port: int):
        self.ip = ip
        self.port = port
        self.workers = workers
        self.processing_host = processing_host
        self.processing_port = processing_port
        self.app = web.Application()
        self.setup_routes()
        self.html_parser = HTMLParser()
        self.metadata_extractor = MetadataExtractor()
        self.http_client = AsyncHTTPClient(max_connections=workers)
        self.semaphore = asyncio.Semaphore(workers)
        
    def setup_routes(self):
        """Configurar rutas del servidor"""
        self.app.router.add_get('/scrape', self.handle_scrape)
        self.app.router.add_post('/scrape', self.handle_scrape_post)
        self.app.router.add_get('/health', self.handle_health)
        
    async def handle_health(self, request: web.Request) -> web.Response:
        """Endpoint de health check"""
        return web.json_response({
            'status': 'healthy',
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'workers': self.workers
        })
    
    async def handle_scrape(self, request: web.Request) -> web.Response:
        """Handler para GET /scrape?url=..."""
        url = request.query.get('url')
        if not url:
            return web.json_response(
                {'error': 'URL parameter is required', 'status': 'error'},
                status=400
            )
        
        try:
            result = await self.process_scraping(url)
            return web.json_response(result)
        except Exception as e:
            logger.error(f"Error processing {url}: {str(e)}", exc_info=True)
            return web.json_response(
                {
                    'error': str(e),
                    'status': 'error',
                    'url': url,
                    'timestamp': datetime.utcnow().isoformat() + 'Z'
                },
                status=500
            )
    
    async def handle_scrape_post(self, request: web.Request) -> web.Response:
        """Handler para POST /scrape con JSON body"""
        try:
            data = await request.json()
            url = data.get('url')
            if not url:
                return web.json_response(
                    {'error': 'URL field is required', 'status': 'error'},
                    status=400
                )
            
            result = await self.process_scraping(url)
            return web.json_response(result)
        except json.JSONDecodeError:
            return web.json_response(
                {'error': 'Invalid JSON body', 'status': 'error'},
                status=400
            )
        except Exception as e:
            logger.error(f"Error in POST handler: {str(e)}", exc_info=True)
            return web.json_response(
                {'error': str(e), 'status': 'error'},
                status=500
            )
    
    async def process_scraping(self, url: str) -> Dict[str, Any]:
        """
        Procesar scraping de URL de forma asíncrona
        Coordina con el servidor de procesamiento de forma transparente
        """
        async with self.semaphore:
            logger.info(f"Starting scraping for: {url}")
            timestamp = datetime.utcnow().isoformat() + 'Z'
            
            # Paso 1: Realizar scraping asíncrono
            try:
                html_content = await self.http_client.fetch(url, timeout=30)
            except asyncio.TimeoutError:
                raise Exception(f"Timeout fetching URL: {url}")
            except Exception as e:
                raise Exception(f"Error fetching URL: {str(e)}")
            
            # Paso 2: Extraer información de forma asíncrona
            scraping_task = asyncio.create_task(self._extract_scraping_data(html_content, url))
            
            # Paso 3: Solicitar procesamiento al Servidor B (transparente para el cliente)
            processing_task = asyncio.create_task(self._request_processing(url, html_content))
            
            # Esperar ambas tareas de forma asíncrona
            try:
                scraping_data, processing_data = await asyncio.gather(
                    scraping_task,
                    processing_task,
                    return_exceptions=True
                )
            except Exception as e:
                logger.error(f"Error in async gather: {str(e)}")
                raise
            
            # Manejar errores en las tareas
            if isinstance(scraping_data, Exception):
                logger.error(f"Scraping error: {str(scraping_data)}")
                scraping_data = {'error': str(scraping_data)}
            
            if isinstance(processing_data, Exception):
                logger.warning(f"Processing error: {str(processing_data)}")
                processing_data = {'error': str(processing_data)}
            
            # Construir respuesta consolidada
            response = {
                'url': url,
                'timestamp': timestamp,
                'scraping_data': scraping_data,
                'processing_data': processing_data,
                'status': 'success' if not isinstance(scraping_data, dict) or 'error' not in scraping_data else 'partial'
            }
            
            logger.info(f"Completed scraping for: {url}")
            return response
    
    async def _extract_scraping_data(self, html: str, url: str) -> Dict[str, Any]:
        """Extraer datos de scraping de forma asíncrona"""
        # Ejecutar parsing en el executor para no bloquear el event loop
        loop = asyncio.get_event_loop()
        
        # Parsear HTML
        soup = await loop.run_in_executor(None, self.html_parser.parse, html)
        
        # Extraer información en paralelo
        tasks = [
            loop.run_in_executor(None, self.html_parser.extract_title, soup),
            loop.run_in_executor(None, self.html_parser.extract_links, soup, url),
            loop.run_in_executor(None, self.metadata_extractor.extract_meta_tags, soup),
            loop.run_in_executor(None, self.html_parser.count_images, soup),
            loop.run_in_executor(None, self.html_parser.extract_structure, soup)
        ]
        
        results = await asyncio.gather(*tasks)
        
        return {
            'title': results[0],
            'links': results[1],
            'meta_tags': results[2],
            'images_count': results[3],
            'structure': results[4]
        }
    
    async def _request_processing(self, url: str, html_content: str) -> Dict[str, Any]:
        """
        Comunicarse con el servidor de procesamiento de forma asíncrona
        Esta comunicación es transparente para el cliente
        """
        try:
            # Preparar datos para enviar
            request_data = {
                'url': url,
                'html': html_content[:50000],  # Limitar tamaño
                'operations': ['screenshot', 'performance', 'images']
            }
            
            # Serializar datos
            serialized_data = Serializer.serialize(request_data)
            
            # Conectar al servidor de procesamiento usando asyncio
            reader, writer = await asyncio.wait_for(
                asyncio.open_connection(self.processing_host, self.processing_port),
                timeout=5.0
            )
            
            try:
                # Enviar datos usando el protocolo
                await Protocol.send_async(writer, serialized_data)
                
                # Recibir respuesta (con timeout de 60 segundos para procesamiento)
                response_data = await asyncio.wait_for(
                    Protocol.receive_async(reader),
                    timeout=60.0
                )
                
                # Deserializar respuesta
                processing_result = Serializer.deserialize(response_data)
                
                return processing_result
                
            finally:
                writer.close()
                await writer.wait_closed()
                
        except asyncio.TimeoutError:
            logger.warning(f"Timeout connecting to processing server for {url}")
            return {
                'error': 'Processing server timeout',
                'screenshot': None,
                'performance': None,
                'thumbnails': []
            }
        except ConnectionRefusedError:
            logger.warning(f"Processing server unavailable for {url}")
            return {
                'error': 'Processing server unavailable',
                'screenshot': None,
                'performance': None,
                'thumbnails': []
            }
        except Exception as e:
            logger.error(f"Error communicating with processing server: {str(e)}")
            return {
                'error': f'Processing communication error: {str(e)}',
                'screenshot': None,
                'performance': None,
                'thumbnails': []
            }
    
    def run(self):
        """Iniciar servidor"""
        logger.info(f"Starting Scraping Server on {self.ip}:{self.port}")
        logger.info(f"Workers: {self.workers}")
        logger.info(f"Processing Server: {self.processing_host}:{self.processing_port}")
        
        # Soportar IPv4 e IPv6
        try:
            web.run_app(
                self.app,
                host=self.ip,
                port=self.port,
                access_log=logger
            )
        except OSError as e:
            logger.error(f"Error starting server: {e}")
            raise


def parse_arguments():
    """Parsear argumentos de línea de comandos"""
    parser = argparse.ArgumentParser(
        description='Servidor de Scraping Web Asíncrono',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos:
  %(prog)s -i 127.0.0.1 -p 8000
  %(prog)s -i ::1 -p 8000 -w 8
  %(prog)s -i 0.0.0.0 -p 8000 -w 4 --processing-host 127.0.0.1 --processing-port 9000
        """
    )
    
    parser.add_argument(
        '-i', '--ip',
        required=True,
        help='Dirección de escucha (soporta IPv4/IPv6)'
    )
    
    parser.add_argument(
        '-p', '--port',
        required=True,
        type=int,
        help='Puerto de escucha'
    )
    
    parser.add_argument(
        '-w', '--workers',
        type=int,
        default=4,
        help='Número de workers (default: 4)'
    )
    
    parser.add_argument(
        '--processing-host',
        default='127.0.0.1',
        help='IP del servidor de procesamiento (default: 127.0.0.1)'
    )
    
    parser.add_argument(
        '--processing-port',
        type=int,
        default=9000,
        help='Puerto del servidor de procesamiento (default: 9000)'
    )
    
    return parser.parse_args()


def main():
    """Función principal"""
    args = parse_arguments()
    
    server = ScrapingServer(
        ip=args.ip,
        port=args.port,
        workers=args.workers,
        processing_host=args.processing_host,
        processing_port=args.processing_port
    )
    
    try:
        server.run()
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Server error: {e}", exc_info=True)
        return 1
    
    return 0


if __name__ == '__main__':
    exit(main())