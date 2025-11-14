"""
Test de Integración E2E (Versión Sencilla - Bonus Track)
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
    path = os.path.join(os.path.dirname(__file__), '..', 'env', 'bin', 'python3')
    if not os.path.exists(path):
        path = os.path.join(os.path.dirname(__file__), '..', 'env', 'bin', 'python')
    if not os.path.exists(path):
        return sys.executable 
    return path

def wait_for_port(host, port, timeout=15):
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
def test_e2e_bonus_track_simple_ipv4():
    """
    Prueba la cadena completa E2E del Bonus Track en IPv4.
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
        assert wait_for_port('127.0.0.1', 9000), "Servidor B no arrancó a tiempo."
        
        # 2. Iniciar Servidor A (Scraping)
        scrap_server = subprocess.Popen(
            [python_exe, server_scrap_script, '-i', '127.0.0.1', '-p', '8000',
             '--processing-host', '127.0.0.1', '--processing-port', '9000'],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
        )
        print("Iniciando Servidor A (Scraping)...")
        assert wait_for_port('127.0.0.1', 8000, timeout=5), "Servidor A no arrancó a tiempo."
        
        # 3. Hacer la petición POST para iniciar la tarea
        print("Servidores listos. Realizando POST a /scrape...")
        scrape_url = 'http://127.0.0.1:8000/scrape'
        r_post = requests.post(scrape_url, data={'url': 'https://example.com'}, timeout=10)
        
        assert r_post.status_code == 202 
        task_data = r_post.json()
        task_id = task_data.get('task_id')
        assert task_id, "El servidor no devolvió un task_id"
        print(f"Tarea {task_id} creada.")

        # 4. Hacer Polling a /status
        status_url = f'http://127.0.0.1:8000/status/{task_id}'
        end = time.time() + 40 
        current_status = ""
        while time.time() < end:
            time.sleep(2)
            r_status = requests.get(status_url, timeout=10)
            status_data = r_status.json()
            current_status = status_data.get('status')
            print(f"Estado de la tarea: {current_status}...")
            if current_status == 'completed':
                break
            if current_status == 'failed':
                pytest.fail(f"La tarea {task_id} falló en el servidor.")
        
        assert current_status == 'completed', "La tarea no se completó a tiempo."
        
        # 5. Obtener el resultado
        print("Tarea completada. Obteniendo resultado de /result...")
        result_url = f'http://127.0.0.1:8000/result/{task_id}'
        r_result = requests.get(result_url, timeout=10)
        
        assert r_result.status_code == 200
        data = r_result.json()
        assert data['status'] == 'success'
        assert data['url'] == 'https://example.com'
        assert data['scraping_data']['title'] == 'Example Domain'
        assert 'screenshot' in data['processing_data']
        
        print("¡Test E2E (Bonus Track) completado con éxito!")

    finally:
        # 6. Apagar los servidores
        print("\nApagando servidores...")
        if scrap_server:
            terminate_proc(scrap_server)
            print("Servidor A (Scraping) detenido.")
        if proc_server:
            terminate_proc(proc_server)
            print("Servidor B (Procesamiento) detenido.")