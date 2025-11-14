"""
Parte A: Servidor de Scraping Web Asíncrono (aiohttp).
"""

import asyncio
import argparse
import sys
import socket
from datetime import datetime
from typing import Dict, Any, Optional

from aiohttp import web

from common.protocol import (
    ProtocolHandler, TASK_SCREENSHOT, TASK_PERFORMANCE, TASK_IMAGES,
    RESP_SUCCESS, RESP_ERROR
)
from common import ScrapingError, TaskTimeoutError, ProtocolError

from scraper.async_http import AsyncHTTPClient 
from scraper.html_parser import parse_basic_data
from scraper.metadata_extractor import extract_metadata

class ScrapingCoordinator:
    """Maneja la lógica de scraping y coordinación."""
    
    def __init__(self, proc_host: str, proc_port: int, http_client: AsyncHTTPClient):
        self.proc_host = proc_host
        self.proc_port = proc_port
        self.http_client = http_client
        self.proto = ProtocolHandler()
        print(f"[AsyncServer] Coordinador listo. Procesador en: {proc_host}:{proc_port}")

    async def _request_processing(self, task_type: int, payload: Dict[str, Any]) -> Optional[Any]:
        """Función genérica para enviar una tarea al Servidor B."""
        writer = None
        try:
            reader, writer = await asyncio.wait_for(
                asyncio.open_connection(self.proc_host, self.proc_port),
                timeout=10.0
            )
            
            await self.proto.async_send_message(writer, task_type, payload)
            
            msg_type, resp_payload = await asyncio.wait_for(
                self.proto.async_read_message(reader),
                timeout=35.0
            )
            
            if msg_type == RESP_SUCCESS:
                return resp_payload.get('data')
            else:
                print(f"[AsyncServer] Error reportado por Servidor B: {resp_payload.get('error')}")
                return {"error": resp_payload.get('error')}

        except (asyncio.TimeoutError, ConnectionRefusedError, ProtocolError) as e:
            print(f"[AsyncServer] Error de comunicación con Servidor B: {e}")
            raise ProtocolError(f"Error de comunicación con Servidor B: {e}") from e
        
        finally:
            if writer:
                writer.close()
                await writer.wait_closed()

    async def handle_scrape(self, request: web.Request) -> web.Response:
        """Handler principal de aiohttp para /scrape."""
        url = request.query.get('url')
        if not url:
            return web.json_response(
                {'error': 'URL parameter is required', 'status': 'failed'},
                status=400
            )
            
        print(f"[AsyncServer] Petición de scraping recibida para: {url}")
        
        try:
            html, final_url = await self.http_client.fetch_html(url)
            
            loop = asyncio.get_running_loop()
            scrape_data = await loop.run_in_executor(
                None, parse_basic_data, html, final_url
            )
            meta_data = await loop.run_in_executor(
                None, extract_metadata, html
            )
            
            img_urls = scrape_data.pop("image_urls_for_processing", [])
            payload_base = {"url": final_url}
            payload_images = {"url": final_url, "image_urls": img_urls}

            task_screenshot = self._request_processing(TASK_SCREENSHOT, payload_base)
            task_performance = self._request_processing(TASK_PERFORMANCE, payload_base)
            task_images = self._request_processing(TASK_IMAGES, payload_images)
            
            results = await asyncio.gather(
                task_screenshot, task_performance, task_images
            )
            
            final_json = {
                "url": final_url,
                "timestamp": datetime.now().isoformat(),
                "scraping_data": {
                    "title": scrape_data.get("title"),
                    "links": scrape_data.get("links"),
                    "meta_tags": meta_data,
                    "structure": scrape_data.get("structure"),
                    "images_count": scrape_data.get("images_count")
                },
                "processing_data": {
                    "screenshot": results[0],
                    "performance": results[1],
                    "thumbnails": results[2] or []
                },
                "status": "success"
            }
            
            return web.json_response(final_json, status=200)

        except (ScrapingError, TaskTimeoutError) as e:
            print(f"[AsyncServer] Error de Scraping para {url}: {e}")
            return web.json_response(
                {'error': f'Error al procesar la URL {url}: {e}', 'status': 'failed'},
                status=502 
            )
            
        except ProtocolError as e:
            print(f"[AsyncServer] Error de comunicación interna: {e}")
            return web.json_response(
                {'error': 'Error interno de comunicación entre servidores', 'status': 'failed'},
                status=503 
            )

        except Exception as e:
            print(f"[AsyncServer] Error interno inesperado: {e}")
            return web.json_response(
                {'error': f'Error interno del servidor: {e}', 'status': 'failed'},
                status=500 
            )

    async def handle_health(self, request: web.Request) -> web.Response:
        """Handler para Health Check."""
        return web.json_response({"status": "healthy", "service": "ScrapingServer"})


def parse_args():
    parser = argparse.ArgumentParser(
        description='Servidor de Scraping Web Asíncrono (Parte A)',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument('-i', '--ip', type=str, required=True, help='Dirección de escucha (ej: 0.0.0.0 para IPv4, :: para IPv6/Dual)')
    parser.add_argument('-p', '--port', type=int, required=True, help='Puerto de escucha')
    parser.add_argument('-w', '--workers', type=int, default=1, help='Número de workers (default: 1, aiohttp es concurrente por sí mismo)')
    parser.add_argument('--processing-host', type=str, default='127.0.0.1', help='Host del servidor de procesamiento (default: 127.0.0.1)')
    parser.add_argument('--processing-port', type=int, default=9000, help='Puerto del servidor de procesamiento (default: 9000)')
    return parser.parse_args()

async def init_app(args: argparse.Namespace) -> web.Application:
    """Crea e inicializa la App aiohttp."""
    app = web.Application()
    
    http_client = AsyncHTTPClient(timeout=30)
    await http_client.create_session()
    
    coordinator = ScrapingCoordinator(
        args.processing_host, 
        args.processing_port, 
        http_client
    )
    
    app.router.add_get('/scrape', coordinator.handle_scrape)
    app.router.add_get('/health', coordinator.handle_health)
    
    async def _cleanup(app_instance):
        print("[AsyncServer] Cerrando sesión HTTP del cliente...")
        await http_client.close_session()
        
    app.on_cleanup.append(_cleanup)
    
    return app

def main():
    args = parse_args()

    if args.ip == '::':
        print("[AsyncServer] Escuchando en modo Dual-Stack (IPv4 e IPv6) en [::]")
    elif '.' in args.ip:
        print(f"[AsyncServer] Escuchando en modo IPv4 en {args.ip}")
    elif ':' in args.ip:
         print(f"[AsyncServer] Escuchando en modo IPv6 en [{args.ip}]")
         
    print(f"[AsyncServer] Puerto: {args.port}, Workers: {args.workers}")
    print("=" * 60)
    
    try:
        web.run_app(
            init_app(args),
            host=args.ip,
            port=args.port,
        )
    except KeyboardInterrupt:
        print("\n[AsyncServer] Apagando servidor...")
    except OSError as e:
        if "Address already in use" in str(e):
            print(f"Error: La dirección {args.ip}:{args.port} ya está en uso.")
        else:
            print(f"Error de OS: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()