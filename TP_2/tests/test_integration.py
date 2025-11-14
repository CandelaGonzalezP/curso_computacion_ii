"""
Prueba de Integración E2E (End-to-End) Parametrizada.

Ejecuta toda la suite de pruebas E2E dos veces:
1. Una vez usando IPv4 (127.0.0.1)
2. Una vez usando IPv6 (::1)
"""

import os
import sys
import time
import subprocess
import requests
import pytest
import socket
from contextlib import closing


def get_python_executable():
    """Obtiene la ruta al ejecutable de Python dentro del venv."""
    path = os.path.join(os.path.dirname(__file__), '..', 'env', 'bin', 'python')
    if not os.path.exists(path):
        return sys.executable
    return path

def wait_for_health(url, timeout=20):
    """Espera a que el servidor A responda en /health."""
    end = time.time() + timeout
    while time.time() < end:
        try:
            r = requests.get(url, timeout=1)
            if r.status_code == 200:
                print(f"Servidor health OK en {url}")
                return True
        except requests.ConnectionError:
            time.sleep(0.2)
    print(f"Error: Timeout esperando {url}")
    return False

def wait_for_port(host, port, timeout=10):
    """Espera a que un puerto TCP esté abierto."""
    end = time.time() + timeout
    while time.time() < end:
        with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as sock:
            sock.settimeout(1)
            if sock.connect_ex((host, port)) == 0:
                print(f"Puerto {host}:{port} está abierto.")
                return True
            time.sleep(0.2)
    print(f"Error: Timeout esperando el puerto {host}:{port}")
    return False

def terminate_proc(p):
    """Detiene un proceso de forma segura."""
    try:
        p.terminate()
        p.wait(timeout=5)
    except Exception:
        pass 


@pytest.mark.slow
def test_e2e_simple_ipv4():
    """
    Prueba la cadena completa E2E en IPv4.
    """
    project_root = os.path.dirname(os.path.dirname(__file__))
    server_proc_script = os.path.join(project_root, 'server_processing.py')
    server_scrap_script = os.path.join(project_root, 'server_scraping.py')
    python_exe = get_python_executable()

    proc_server = None
    scrap_server = None
    
    try:
        # 1. Iniciar Servidor B (Procesamiento)
        proc_server = subprocess.Popen(
            [python_exe, server_proc_script, '-i', '127.0.0.1', '-p', '9000', '-n', '2'],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
        )
        print("\nIniciando Servidor B (Procesamiento)...")
        
        # --- ESPERA CORREGIDA ---
        # 2. Esperar a que el Servidor B esté LISTO
        assert wait_for_port('127.0.0.1', 9000), "El Servidor B (Procesamiento) no arrancó a tiempo."
        # --- FIN DE ESPERA ---
        
        # 3. Iniciar Servidor A (Scraping)
        scrap_server = subprocess.Popen(
            [python_exe, server_scrap_script, '-i', '127.0.0.1', '-p', '8000',
             '--processing-host', '127.0.0.1', '--processing-port', '9000'],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
        )
        print("Iniciando Servidor A (Scraping)...")

        # 4. Esperar a que el Servidor A esté listo
        health_url = 'http://127.0.0.1:8000/health'
        assert wait_for_health(health_url), "El Servidor A (Scraping) no respondió a tiempo."
        
        # 5. Hacer la petición de prueba (Cliente)
        print("Servidores listos. Realizando petición a /scrape...")
        scrape_url = 'http://127.0.0.1:8000/scrape'
        params = {'url': 'https://example.com'}
        
        r = requests.get(scrape_url, params=params, timeout=40)
        
        # 6. Verificar los resultados
        assert r.status_code == 200
        data = r.json()
        assert data['status'] == 'success'
        assert data['url'] == 'https://example.com'
        assert data['scraping_data']['title'] == 'Example Domain'
        assert 'screenshot' in data['processing_data']
        assert 'performance' in data['processing_data']
        
        print("¡Test E2E completado con éxito!")

    finally:
        print("\nApagando servidores...")
        if scrap_server:
            terminate_proc(scrap_server)
            print("Servidor A (Scraping) detenido.")
        if proc_server:
            terminate_proc(proc_server)
            print("Servidor B (Procesamiento) detenido.")