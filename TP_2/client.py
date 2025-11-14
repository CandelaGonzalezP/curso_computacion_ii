"""
Cliente de prueba para el Servidor A (Async).
"""

import requests
import argparse
import sys
import json
from urllib.parse import urlparse
import os
import base64
from datetime import datetime

def save_artifacts(data: dict, save_screenshot: bool):
    """
    Guarda el JSON en 'outputs/' y el screenshot en 'screenshots/'.
    """
    try:
        os.makedirs('outputs', exist_ok=True)
    except OSError as e:
        print(f"Error al crear el directorio 'outputs': {e}", file=sys.stderr)
        return

    url = data.get('url', 'unknown_url')
    domain = urlparse(url).netloc.replace('www.', '').replace('.', '_')
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    filename_base = f"{domain}_{timestamp}"

    json_path = os.path.join('outputs', f"{filename_base}.json")
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
                
                png_path = os.path.join('screenshots', f"{filename_base}.png")
                
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
        description='Cliente de prueba para el TP2',
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
        help='Guardar el JSON de respuesta y el screenshot en la carpeta /outputs'
    )
    
    args = parser.parse_args()
    
    server_url_base = f"http://{args.server_host}:{args.server_port}"
    if ':' in args.server_host and args.server_host != "localhost":
        server_url_base = f"http://[{args.server_host}]:{args.server_port}"
        
    scrape_url = f"{server_url_base}/scrape"

    print(f"Contactando al servidor en: {scrape_url}")
    print(f"Solicitando scraping de: {args.url}\n")
    
    try:
        response = requests.get(scrape_url, params={'url': args.url}, timeout=60)
        response.raise_for_status()
        
        print("Respuesta recibida (Status 200 OK). Procesando...")
        data = response.json()
        
        if args.save:
            save_artifacts(data, save_screenshot=True)
        else:
            if data.get('processing_data', {}).get('screenshot'):
                data['processing_data']['screenshot'] = "[...Base64 omitido...]"
            if data.get('processing_data', {}).get('thumbnails'):
                data['processing_data']['thumbnails'] = f"[{len(data['processing_data']['thumbnails'])} thumbnails]"
            print(json.dumps(data, indent=2, ensure_ascii=False))

        print("\n¡Solicitud completada!")
        
    except requests.ConnectionError:
        print(f"Error: No se pudo conectar al servidor en {server_url_base}", file=sys.stderr)
        print("Asegúrate de que 'server_scraping.py' esté corriendo.", file=sys.stderr)
    except requests.Timeout:
        print("Error: Timeout esperando la respuesta del servidor (más de 60s).", file=sys.stderr)
    except requests.HTTPError as e:
        print(f"Error HTTP {e.response.status_code}: {e.response.text}", file=sys.stderr)
    except json.JSONDecodeError:
        print("Error: La respuesta del servidor no es un JSON válido.", file=sys.stderr)
        print(f"Respuesta recibida: {response.text[:200]}...")
    except Exception as e:
        print(f"Error inesperado: {e}", file=sys.stderr)

if __name__ == "__main__":
    main()