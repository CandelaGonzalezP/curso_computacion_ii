# server_scraping.py

import aiohttp.web
import asyncio
import argparse
import sys
import socket
import datetime
from urllib.parse import urlparse

# Importaciones de módulos internos
from common.serialization import serialize_message, deserialize_message, HEADER_SIZE
from common.protocol import create_scraping_request, create_scraping_response
from scraper.async_http import fetch_url, SCRAPING_TIMEOUT
from scraper.html_parser import extract_links_and_structure
from scraper.metadata_extractor import extract_meta_tags

# --- CONFIGURACIÓN DEFAULTS ---
# Estas variables son solo defaults si no se pasan argumentos.
DEFAULT_PROCESSING_SERVER_IP = '127.0.0.1' 
DEFAULT_PROCESSING_SERVER_PORT = 9000       

# --- FUNCIONES CENTRALES DE SCRAPING Y COORDINACIÓN ---

async def perform_scraping(url: str, session: aiohttp.ClientSession) -> dict:
    """Función principal de scraping I/O (Requisito 1 y 2)."""
    try:
        html_content = await fetch_url(session, url)
    except ConnectionError as e:
        raise e 

    data = extract_links_and_structure(html_content)
    metadata = extract_meta_tags(html_content)
    
    return {
        "title": data["title"],
        "links": data["links"],
        "meta_tags": metadata,
        "structure": data["structure"],
        "images_count": data["images_count"]
    }

# --- FUNCIÓN DE COMUNICACIÓN CORREGIDA ---
# Ahora recibe IP y Puerto como argumentos, eliminando la necesidad de 'global'.
async def communicate_with_processor(url: str, proc_ip: str, proc_port: int) -> dict:
    """Comunica asíncronamente con el Servidor B (multiprocessing)."""
    try:
        reader, writer = await asyncio.open_connection(
            proc_ip, proc_port # <--- Usa los argumentos pasados
        )

        request_msg = create_scraping_request(url)
        request_bytes = serialize_message(request_msg)
        
        writer.write(request_bytes)
        await writer.drain() 

        # 2. Recibir respuesta (Manejo de errores de comunicación)
        header = await asyncio.wait_for(reader.readexactly(HEADER_SIZE), timeout=10)
        import struct
        (data_len,) = struct.unpack('<I', header)

        buffer = await asyncio.wait_for(reader.readexactly(data_len), timeout=SCRAPING_TIMEOUT + 10)
        
        response_data = deserialize_message(header + buffer)
        writer.close()
        await writer.wait_closed()
        
        return response_data

    except asyncio.TimeoutError:
        return {"status": "error", "message": "Processor communication/processing timeout"}
    except ConnectionRefusedError:
        return {"status": "error", "message": "Processor server is down or refused connection"}
    except Exception as e:
        return {"status": "error", "message": f"Processor communication error: {e.__class__.__name__}: {e}"}

# --- HANDLER PRINCIPAL AIOHTTP ---

async def scrape_handler(request):
    """Handler para la ruta GET /scrape."""
    url = request.query.get('url')
    
    if not url:
        return aiohttp.web.json_response({"status": "error", "message": "Missing 'url' parameter"}, status=400)
    
    parsed_url = urlparse(url)
    if not parsed_url.scheme or not parsed_url.netloc:
         return aiohttp.web.json_response({"status": "error", "message": "Invalid or incomplete URL"}, status=400)

    # Obtener configuración del Servidor B desde el objeto app
    proc_ip = request.app['proc_ip']
    proc_port = request.app['proc_port']

    print(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] Petición de cliente recibida para: {url}")
    
    session = request.app['client_session']
    scraping_data = {}
    processing_data = {}
    status = "success"
    
    try:
        # 1. Realizar Scraping I/O (async)
        scraping_data = await perform_scraping(url, session)
        
        # 2. Coordinar con Servidor B para procesamiento (Pasando IP/Puerto)
        processing_data = await communicate_with_processor(url, proc_ip, proc_port)
        
        if processing_data.get('status') == 'error':
            status = "partial_success_processor_failed"
            print(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] Servidor B falló: {processing_data.get('message')}")
            
    except ConnectionError as e:
        status = "error (scraping failed)"
        scraping_data = {"error": str(e)}
        processing_data = {"error": "Processing not attempted"}
        print(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] Error de Scraping/Red: {e}")
        
    except Exception as e:
        status = "fatal_error_A"
        print(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] Error inesperado en el servidor A: {e.__class__.__name__}: {e}")

    # 3. Consolidar y devolver respuesta
    final_response = create_scraping_response(url, scraping_data, processing_data, status)
    print(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] Respuesta consolidada enviada para {url}")
    return aiohttp.web.json_response(final_response)

# --- ARRANQUE DEL SERVIDOR Y GESTIÓN DE CONFIGURACIÓN ---

# La función init_app ahora recibe los valores de la CLI.
async def init_app(proc_ip, proc_port): # <-- ¡QUITAMOS 'loop' aquí!
    # app = aiohttp.web.Application(loop=loop) <-- Eliminamos loop=loop
    app = aiohttp.web.Application() 
    
    # app['client_session'] = aiohttp.ClientSession(loop=loop) <-- Eliminamos loop=loop
    app['client_session'] = aiohttp.ClientSession()
    
    # Almacenar la configuración del Servidor B en el objeto app
    app['proc_ip'] = proc_ip
    app['proc_port'] = proc_port

    app.router.add_get('/scrape', scrape_handler)
    return app

async def cleanup_app(app):
    await app['client_session'].close()

def main():
    parser = argparse.ArgumentParser(description="Servidor de Scraping Web Asíncrono")
    parser.add_argument("-i", "--ip", required=True, help="Dirección de escucha (soporta IPv4/IPv6)")
    parser.add_argument("-p", "--port", required=True, type=int, help="Puerto de escucha")
    parser.add_argument("-w", "--workers", type=int, default=4, help="Número de workers (default: 4)")
    
    # Usar los defaults globales para argparse
    parser.add_argument("--proc-ip", default=DEFAULT_PROCESSING_SERVER_IP, help="IP del Servidor B")
    parser.add_argument("--proc-port", type=int, default=DEFAULT_PROCESSING_SERVER_PORT, help="Puerto del Servidor B")

    args = parser.parse_args()

    # Obtenemos los valores de la CLI
    proc_ip = args.proc_ip
    proc_port = args.proc_port

    # Detección de familia IP para el mensaje (no funcionalmente crítico para aiohttp.web.run_app)
    try:
        # Intenta crear un socket IPv6 para verificar su disponibilidad
        socket.socket(socket.AF_INET6, socket.SOCK_STREAM).close()
        family_name = 'IPv6'
    except Exception:
        family_name = 'IPv4'
    
    print(f"Servidor A escuchando en {args.ip}:{args.port} | Familia: {family_name} | Workers: {args.workers}")
    
    # --- BLOQUE CRÍTICO CORREGIDO: Usamos aiohttp.web.run_app directamente ---
    # Eliminamos: loop = asyncio.get_event_loop()
    # Eliminamos: app = loop.run_until_complete(...)
    
    aiohttp.web.run_app(
        # Pasamos el awaitable init_app() directamente. aiohttp se encarga del loop.
        init_app(proc_ip, proc_port), 
        host=args.ip, 
        port=args.port, 
        handle_signals=True,
        access_log=None,
        reuse_port=True,
        workers=args.workers,
    )

if __name__ == "__main__":
    main()