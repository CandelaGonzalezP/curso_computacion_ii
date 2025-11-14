"""
Cliente de prueba simple para el Servidor A (Async).
"""

import requests
import argparse
import sys
import json
import time
from urllib.parse import urlparse
import os
import base64
from datetime import datetime

def save_artifacts(data: dict, save_screenshot: bool):
    """Guarda el JSON en 'outputs/' y el screenshot en 'screenshots/'."""
    try:
        os.makedirs('outputs', exist_ok=True)
    except OSError as e:
        print(f"Error al crear el directorio 'outputs': {e}", file=sys.stderr)
        return

    url = data.get('url', 'unknown_url')
    domain = urlparse(url).netloc.replace('www.', '').replace('.', '_')
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    base_filename = os.path.join('outputs', f"{domain}_{timestamp}")

    json_path = f"{base_filename}.json"
    try:
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"Resultados JSON completos guardados en: {json_path}")
    except IOError as e:
        print(f"Error al guardar JSON {json_path}: {e}", file=sys.stderr)

    if save_screenshot:
        try:
            os.makedirs('screenshots', exist_ok=True)
        except OSError as e:
            print(f"Error al crear el directorio 'screenshots': {e}", file=sys.stderr)
        
        try:
            b64_data = data.get('processing_data', {}).get('screenshot')
            if b64_data and isinstance(b64_data, str):
                png_data = base64.b64decode(b64_data)
                png_path = os.path.join('screenshots', f"{domain}_{timestamp}.png")
                
                with open(png_path, 'wb') as f:
                    f.write(png_data)
                print(f"Screenshot guardado en: {png_path}")
            else:
                print("No se encontró screenshot (o hubo un error) en la respuesta.")
        except (base64.binascii.Error, IOError, TypeError) as e:
            print(f"Error al decodificar o guardar screenshot: {e}", file=sys.stderr)
        except OSError as e:
            print(f"Error de sistema de archivos al guardar screenshot: {e}", file=sys.stderr)

def main():
    parser = argparse.ArgumentParser(
        description='Cliente de prueba para el TP2 (con Bonus Track)',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        '-u', '--url', type=str, required=True,
        help='URL completa a scrapear (ej: https://www.python.org)'
    )
    parser.add_argument(
        '--server_host', type=str, default='localhost',
        help='Host del Servidor A (default: localhost)'
    )
    parser.add_argument(
        '--server_port', type=int, default=8000,
        help='Puerto del Servidor A (default: 8000)'
    )
    parser.add_argument(
        '--save', action='store_true',
        help='Guardar el JSON de respuesta y el screenshot'
    )
    
    args = parser.parse_args()
    
    server_url_base = f"http://{args.server_host}:{args.server_port}"
    if ':' in args.server_host and args.server_host != "localhost":
        server_url_base = f"http://[{args.server_host}]:{args.server_port}"
        
    scrape_url = f"{server_url_base}/scrape"
    status_url = f"{server_url_base}/status"
    result_url = f"{server_url_base}/result"

    print(f"Contactando al servidor en: {scrape_url}")
    print(f"Solicitando scraping de: {args.url}\n")
    
    try:
        response = requests.post(scrape_url, data={'url': args.url}, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        task_id = data.get('task_id')
        
        if not task_id:
            print("Error: El servidor no devolvió un task_id.", file=sys.stderr)
            return
            
        print(f"Tarea creada con ID: {task_id}")
        
        while True:
            time.sleep(3)
            
            status_check_url = f"{status_url}/{task_id}"
            status_resp = requests.get(status_check_url, timeout=10)
            status_data = status_resp.json()
            
            current_status = status_data.get('status')
            print(f"Estado de la tarea: {current_status}...")
            
            if current_status == 'completed':
                break
            if current_status == 'failed':
                print(f"Error: La tarea {task_id} falló en el servidor.", file=sys.stderr)
                break
        
        print("Obteniendo resultado final...")
        final_result_url = f"{result_url}/{task_id}"
        result_resp = requests.get(final_result_url, timeout=10)
        result_resp.raise_for_status() 
        
        final_data = result_resp.json()
        
        if args.save:
            save_artifacts(final_data, save_screenshot=True)
        else:
            if final_data.get('processing_data', {}).get('screenshot'):
                final_data['processing_data']['screenshot'] = "[...Base64 omitido...]"
            print(json.dumps(final_data, indent=2, ensure_ascii=False))

        print("\n¡Solicitud completada!")
        
    except requests.ConnectionError:
        print(f"Error: No se pudo conectar al servidor en {server_url_base}", file=sys.stderr)
    except requests.Timeout:
        print("Error: Timeout esperando la respuesta del servidor.", file=sys.stderr)
    except requests.HTTPError as e:
        print(f"Error HTTP {e.response.status_code}: {e.response.text}", file=sys.stderr)
    except Exception as e:
        print(f"Error inesperado: {e}", file=sys.stderr)

if __name__ == "__main__":
    main()