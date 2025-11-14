"""
Parte A: Servidor de Scraping Web Asíncrono (aiohttp).
"""

import asyncio
import argparse
import sys
import socket
import uuid
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


async def on_startup(app: web.Application):
    """Señal que se ejecuta cuando el servidor arranca."""
    print("[AsyncServer] Servidor arrancando...")
    http_client = AsyncHTTPClient(timeout=30)
    await http_client.create_session()
    app['http_client'] = http_client
    app['tasks_db'] = {}  
    print("[AsyncServer] Cliente HTTP (aiohttp) y DB de tareas listos.")

async def on_cleanup(app: web.Application):
    """Señal que se ejecuta cuando el servidor se apaga."""
    print("[AsyncServer] Servidor apagándose...")
    if 'http_client' in app:
        await app['http_client'].close_session()
        print("[AsyncServer] Cliente HTTP (aiohttp) cerrado.")


class ScrapingCoordinator:
    """Maneja la lógica de scraping y coordinación."""
    
    def __init__(self, proc_host: str, proc_port: int):
        self.proc_host = proc_host
        self.proc_port = proc_port
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
                error_msg = resp_payload.get('error', 'Error desconocido del Servidor B')
                print(f"[AsyncServer] Error reportado por Servidor B: {error_msg}")
                return {"error": error_msg}

        except (asyncio.TimeoutError, ConnectionRefusedError, ProtocolError) as e:
            print(f"[AsyncServer] Error de comunicación con Servidor B: {e}")
            raise ProtocolError(f"Error de comunicación con Servidor B: {e}") from e
        
        finally:
            if writer:
                writer.close()
                await writer.wait_closed()

    async def _perform_full_scraping(self, http_client: AsyncHTTPClient, url: str) -> Dict[str, Any]:
        """
        REQUISITO OBLIGATORIO: Función que hace scraping completo y devuelve resultado consolidado.
        Esta es la lógica core que cumple con "Parte C: Transparencia para el Cliente".
        """
        html, final_url = await http_client.fetch_html(url)
        
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
        
        return final_json

    
    async def handle_scrape_sync(self, request: web.Request) -> web.Response:
        """
        REQUISITO OBLIGATORIO (Parte C): GET /scrape?url=...
        
        El cliente hace UNA SOLA petición y recibe el resultado completo.
        Toda la coordinación con Servidor B es transparente.
        """
        url = request.query.get('url')
        if not url:
            return web.json_response(
                {'error': 'URL parameter is required', 'status': 'failed'},
                status=400
            )
            
        print(f"[AsyncServer] Petición SÍNCRONA de scraping para: {url}")
        
        try:
            http_client = request.app['http_client']
            result = await self._perform_full_scraping(http_client, url)
            return web.json_response(result, status=200)

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
    
    async def _run_scraping_task_background(self, app: web.Application, task_id: str, url: str):
        """
        BONUS TRACK: Función de background para tareas asíncronas.
        """
        tasks_db = app['tasks_db']
        http_client = app['http_client']
        
        try:
            tasks_db[task_id]['status'] = 'scraping'
            result = await self._perform_full_scraping(http_client, url)
            
            tasks_db[task_id]['result'] = result
            tasks_db[task_id]['status'] = 'completed'
            print(f"[AsyncServer] Tarea {task_id} completada.")

        except (ScrapingError, TaskTimeoutError, ProtocolError, Exception) as e:
            print(f"[AsyncServer] Tarea {task_id} falló: {e}")
            tasks_db[task_id]['status'] = 'failed'
            tasks_db[task_id]['result'] = {'error': str(e), 'status': 'failed'}

    async def handle_scrape_async(self, request: web.Request) -> web.Response:
        """
        BONUS TRACK: POST /scrape/async
        Devuelve task_id inmediatamente para consulta posterior.
        """
        data = await request.post()
        url = data.get('url')
        if not url:
            return web.json_response(
                {'error': 'URL parameter is required in POST data'},
                status=400
            )
            
        task_id = uuid.uuid4().hex
        app = request.app
        app['tasks_db'][task_id] = {
            "status": "pending",
            "result": None,
            "url": url
        }
        
        asyncio.create_task(self._run_scraping_task_background(app, task_id, url))
        
        print(f"[AsyncServer] Tarea ASÍNCRONA {task_id} creada para: {url}")
        
        return web.json_response(
            {"status": "pending", "task_id": task_id},
            status=202
        )

    async def handle_status(self, request: web.Request) -> web.Response:
        """BONUS TRACK: GET /status/{task_id}"""
        task_id = request.match_info.get('task_id')
        task = request.app['tasks_db'].get(task_id)
        
        if not task:
            return web.json_response({'error': 'Task ID not found'}, status=404)
        
        return web.json_response({'task_id': task_id, 'status': task['status']})

    async def handle_result(self, request: web.Request) -> web.Response:
        """BONUS TRACK: GET /result/{task_id}"""
        task_id = request.match_info.get('task_id')
        task = request.app['tasks_db'].get(task_id)
        
        if not task:
            return web.json_response({'error': 'Task ID not found'}, status=404)
            
        if task['status'] == 'completed':
            return web.json_response(task['result'])
        elif task['status'] == 'failed':
            return web.json_response(task['result'], status=500)
        else:
            return web.json_response(
                {'status': task['status'], 'message': 'Task is not yet complete.'},
                status=202 
            )

    async def handle_health(self, request: web.Request) -> web.Response:
        """Health check endpoint."""
        return web.json_response({"status": "healthy", "service": "ScrapingServer"})


def parse_args():
    parser = argparse.ArgumentParser(
        description='Servidor de Scraping Web Asíncrono (Parte A - COMPLETO)',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument('-i', '--ip', type=str, required=True, help='Dirección de escucha')
    parser.add_argument('-p', '--port', type=int, required=True, help='Puerto de escucha')
    parser.add_argument('-w', '--workers', type=int, default=1, help='Número de workers')
    parser.add_argument('--processing-host', type=str, default='127.0.0.1', help='Host del servidor de procesamiento')
    parser.add_argument('--processing-port', type=int, default=9000, help='Puerto del servidor de procesamiento')
    return parser.parse_args()

async def init_app(args: argparse.Namespace) -> web.Application:
    """Crea e inicializa la App aiohttp."""
    app = web.Application()
    
    coordinator = ScrapingCoordinator(
        args.processing_host, 
        args.processing_port 
    )
    
    app.router.add_get('/scrape', coordinator.handle_scrape_sync)
    app.router.add_get('/health', coordinator.handle_health)
    
    app.router.add_post('/scrape/async', coordinator.handle_scrape_async)
    app.router.add_get('/status/{task_id}', coordinator.handle_status)
    app.router.add_get('/result/{task_id}', coordinator.handle_result)
    
    app.on_startup.append(on_startup)
    app.on_cleanup.append(on_cleanup)
    
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
    print(" GET /scrape?url=... (transparencia total)")
    print(" POST /scrape/async (sistema de cola)")
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