"""
Prueba de Integración E2E (End-to-End) Parametrizada.

Ejecuta toda la suite de pruebas E2E dos veces:
1. Una vez usando IPv4 (127.0.0.1)
2. Una vez usando IPv6 (::1)

Esto valida el requisito del enunciado de soportar ambos protocolos.
"""

import pytest
import pytest_asyncio
import asyncio
import aiohttp
import multiprocessing
import socket
import time
from contextlib import closing
import os

from server_processing import ProcessingTCPServer, TaskHandler, run_task
from server_scraping import init_app
from common import ProtocolError


def find_free_port():
    """Encuentra un puerto libre en el sistema."""
    with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as s:
        s.bind(('', 0))
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        return s.getsockname()[1]


@pytest.fixture(scope="module", params=["ipv4", "ipv6"])
def ip_config(request):
    """
    Proporciona configuraciones de host para IPv4 e IPv6.
    Devuelve: (familia_socket, host_proc, host_scrape, host_cliente_url)
    """
    if request.param == "ipv4":
        if not socket.has_dualstack_ipv6():
             yield (socket.AF_INET, "127.0.0.1", "127.0.0.1", "127.0.0.1")
        else:
             yield (socket.AF_INET, "127.0.0.1", "::", "127.0.0.1")
    elif request.param == "ipv6":
        if not socket.has_dualstack_ipv6():
            pytest.skip("El sistema no soporta Sockets Dual-Stack (IPv6)")
            return
        yield (socket.AF_INET6, "::1", "::", "[::1]") 
    else:
        pytest.fail("Parámetro de IP desconocido")


@pytest.fixture(scope="module")
def processing_server_port():
    return find_free_port()

@pytest.fixture(scope="module")
def scraping_server_port():
    return find_free_port()

@pytest.fixture(scope="module")
def mp_pool():
    ctx = multiprocessing.get_context('spawn')
    pool = ctx.Pool(processes=2)
    yield pool
    pool.close()
    pool.join()

def run_processing_server(host, port, pool, family):
    """Target para el proceso del Servidor B."""
    try:
        import server_processing
        server_processing.mp_pool = pool
        
        ProcessingTCPServer.address_family = family
        server_address = (host, port)
        
        if host == '::':
             addr_info = socket.getaddrinfo(host, port, family, socket.SOCK_STREAM, 0, socket.AI_PASSIVE)
             server_address = addr_info[0][4]

        with ProcessingTCPServer(server_address, TaskHandler, pool) as server:
            server.serve_forever()
    except Exception as e:
        print(f"[Test-ProcServer] Error: {e}", flush=True)

@pytest.fixture(scope="module")
def processing_server(mp_pool, processing_server_port, ip_config):
    """Inicia el Servidor B (Processing) en un proceso separado."""
    family, host_proc, _, _ = ip_config
    
    ctx = multiprocessing.get_context('spawn')
    server_process = ctx.Process(
        target=run_processing_server, 
        args=(host_proc, processing_server_port, mp_pool, family),
        daemon=True
    )
    server_process.start()
    print(f"\n[Test] Servidor Procesamiento (PID {server_process.pid}) iniciando en {host_proc}:{processing_server_port} (Familia: {family})")
    
    end_time = time.time() + 10
    while time.time() < end_time:
        try:
            connect_host = host_proc if host_proc != "::" else "::1"
            with socket.create_connection((connect_host, processing_server_port), timeout=0.5):
                break
        except (OSError, ConnectionRefusedError):
            time.sleep(0.2)
    else:
        pytest.fail("No se pudo iniciar el servidor de procesamiento a tiempo")
    
    yield (host_proc, processing_server_port)
    
    print(f"[Test] Deteniendo Servidor Procesamiento (PID {server_process.pid})")
    server_process.terminate()
    server_process.join(timeout=1)

@pytest_asyncio.fixture(scope="module")
async def scraping_server(processing_server, scraping_server_port, ip_config):
    """Inicia el Servidor A (AsyncIO) en el event loop del test."""
    _, host_proc, host_scrape, _ = ip_config
    host_proc_conn = host_proc if host_proc != "::" else "::1" 
        
    class MockArgs:
        ip = host_scrape
        port = scraping_server_port
        processing_host = host_proc_conn
        processing_port = processing_server[1]
        workers = 1

    app = await init_app(MockArgs())
    runner = aiohttp.web.AppRunner(app)
    await runner.setup()
    site = aiohttp.web.TCPSite(runner, host_scrape, scraping_server_port)
    await site.start()
    print(f"[Test] Servidor AsyncIO iniciado en {host_scrape}:{scraping_server_port}")
    
    yield (host_scrape, scraping_server_port)
    
    print("[Test] Deteniendo Servidor AsyncIO...")
    await runner.cleanup()


@pytest.mark.asyncio
async def test_e2e_health(scraping_server, scraping_server_port, ip_config):
    """Prueba que el endpoint /health funciona en IPv4 y IPv6."""
    _, _, _, host_cliente_url = ip_config
    
    server_url = f"http://{host_cliente_url}:{scraping_server_port}"
    print(f"\n[TestE2E] Probando /health en {server_url}")

    async with aiohttp.ClientSession() as session:
        async with session.get(f"{server_url}/health") as resp:
            assert resp.status == 200
            data = await resp.json()
            assert data['status'] == 'healthy'

@pytest.mark.asyncio
async def test_e2e_scrape_python_org(scraping_server, scraping_server_port, ip_config):
    """Prueba la cadena completa E2E con una URL real (python.org)."""
    target_url = "https://www.python.org" 
    _, _, _, host_cliente_url = ip_config
    
    server_url = f"http://{host_cliente_url}:{scraping_server_port}"
    print(f"\n[TestE2E] Probando /scrape en {server_url} para {target_url}")
    
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{server_url}/scrape", params={'url': target_url}, timeout=60) as resp:
            data = await resp.json()
            assert resp.status == 200
            assert data['status'] == 'success'
            assert data['url'] == target_url
            
            assert "Welcome to Python.org" in data['scraping_data']['title']
            assert len(data['scraping_data']['links']) > 10
            
            processing = data['processing_data']
            assert 'error' not in str(processing['screenshot'])
            assert 'error' not in str(processing['performance'])
            assert isinstance(processing['screenshot'], str) and len(processing['screenshot']) > 1000
            assert processing['performance']['load_time_ms'] > 0
            assert len(processing['thumbnails']) > 0

@pytest.mark.asyncio
async def test_e2e_scrape_url_invalida(scraping_server, scraping_server_port, ip_config):
    """Prueba que el servidor maneja una URL inaccesible (debe devolver 502)."""
    target_url = "https://dominio-que-no-existe-12345.com" 
    _, _, _, host_cliente_url = ip_config
    
    server_url = f"http://{host_cliente_url}:{scraping_server_port}"
    print(f"\n[TestE2E] Probando URL inválida en {server_url}")

    async with aiohttp.ClientSession() as session:
        async with session.get(f"{server_url}/scrape", params={'url': target_url}, timeout=60) as resp:
            assert resp.status == 502
            data = await resp.json()
            assert data['status'] == 'failed'
            assert 'error' in data
            assert 'No se pudo conectar' in data['error']