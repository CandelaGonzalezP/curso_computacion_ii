"""
Cliente de prueba para el Servidor A (Async).
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
        description='Cliente de prueba para el TP2 (CORREGIDO)',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos de uso:

  # MODO TRADICIONAL (requisito obligatorio - transparencia total)
  python client.py -u https://www.python.org --save
  
  # MODO ASÍNCRONO (Bonus Track - con task IDs)
  python client.py -u https://www.python.org --async --save
  
  # Consultar estado de tarea
  python client.py --status <task_id>
  
  # Descargar resultado de tarea
  python client.py --result <task_id> --save
        """
    )
    
    parser.add_argument(
        '-u', '--url', type=str,
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
    
    parser.add_argument(
        '--async', action='store_true', dest='async_mode',
        help='[BONUS] Usar modo asíncrono con task ID'
    )
    parser.add_argument(
        '--status', type=str, metavar='TASK_ID',
        help='[BONUS] Consultar el estado de una tarea específica'
    )
    parser.add_argument(
        '--result', type=str, metavar='TASK_ID',
        help='[BONUS] Descargar el resultado de una tarea completada'
    )
    
    args = parser.parse_args()
    
    server_url_base = f"http://{args.server_host}:{args.server_port}"
    if ':' in args.server_host and args.server_host != "localhost":
        server_url_base = f"http://[{args.server_host}]:{args.server_port}"
    

    if args.status:
        status_url = f"{server_url_base}/status/{args.status}"
        print(f"🔍 Consultando estado de tarea: {args.status}\n")
        try:
            response = requests.get(status_url, timeout=10)
            response.raise_for_status()
            status_data = response.json()
            print(json.dumps(status_data, indent=2))
        except requests.HTTPError as e:
            if e.response.status_code == 404:
                print(f"❌ Tarea no encontrada: {args.status}", file=sys.stderr)
            else:
                print(f"Error HTTP {e.response.status_code}: {e.response.text}", file=sys.stderr)
        except requests.RequestException as e:
            print(f"Error de conexión: {e}", file=sys.stderr)
        return

    if args.result:
        result_url = f"{server_url_base}/result/{args.result}"
        print(f"📥 Descargando resultado de tarea: {args.result}\n")
        try:
            response = requests.get(result_url, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if args.save:
                save_artifacts(data, save_screenshot=True)
            else:
                if data.get('processing_data', {}).get('screenshot'):
                    data['processing_data']['screenshot'] = "[...Base64 omitido...]"
                if data.get('processing_data', {}).get('thumbnails'):
                    data['processing_data']['thumbnails'] = f"[{len(data['processing_data']['thumbnails'])} thumbnails]"
                print(json.dumps(data, indent=2, ensure_ascii=False))
            
        except requests.HTTPError as e:
            if e.response.status_code == 404:
                print(f"❌ Tarea no encontrada: {args.result}", file=sys.stderr)
            elif e.response.status_code == 202:
                print(f"⚠️  La tarea aún no está completada.", file=sys.stderr)
            else:
                print(f"Error HTTP {e.response.status_code}: {e.response.text}", file=sys.stderr)
        except requests.RequestException as e:
            print(f"Error de conexión: {e}", file=sys.stderr)
        return

    if not args.url:
        parser.error("Se requiere -u/--url (o usar --status/--result)")
    

    if args.async_mode:
        scrape_async_url = f"{server_url_base}/scrape/async"
        
        print(f"🚀 Enviando solicitud ASÍNCRONA a: {scrape_async_url}")
        print(f"   URL a scrapear: {args.url}\n")
        
        try:
            response = requests.post(scrape_async_url, data={'url': args.url}, timeout=10)
            response.raise_for_status()
            task_data = response.json()
            
            task_id = task_data.get('task_id')
            print(f"✅ Tarea creada exitosamente!")
            print(f"   Task ID: {task_id}\n")
            
            status_url = f"{server_url_base}/status/{task_id}"
            result_url = f"{server_url_base}/result/{task_id}"
            
            print("⏳ Esperando a que la tarea se complete...")
            max_wait = 60  
            elapsed = 0
            
            while elapsed < max_wait:
                time.sleep(2)
                elapsed += 2
                
                status_resp = requests.get(status_url, timeout=10)
                status_data = status_resp.json()
                current_status = status_data.get('status')
                
                print(f"   [{elapsed}s] Estado: {current_status}")
                
                if current_status == 'completed':
                    print("\n✅ Tarea completada! Descargando resultados...\n")
                    result_resp = requests.get(result_url, timeout=10)
                    result_resp.raise_for_status()
                    data = result_resp.json()
                    
                    if args.save:
                        save_artifacts(data, save_screenshot=True)
                    else:
                        if data.get('processing_data', {}).get('screenshot'):
                            data['processing_data']['screenshot'] = "[...Base64 omitido...]"
                        if data.get('processing_data', {}).get('thumbnails'):
                            data['processing_data']['thumbnails'] = f"[{len(data['processing_data']['thumbnails'])} thumbnails]"
                        print(json.dumps(data, indent=2, ensure_ascii=False))
                    
                    print("\n¡Solicitud completada!")
                    return
                
                elif current_status == 'failed':
                    print(f"\n❌ La tarea falló.")
                    return
            
            print(f"\n⏰ Timeout: La tarea no se completó en {max_wait} segundos.")
            print(f"   Usa: python client.py --status {task_id}")
        
        except requests.RequestException as e:
            print(f"Error de conexión: {e}", file=sys.stderr)
        
        return
    

    scrape_url = f"{server_url_base}/scrape"

    print(f"📡 Contactando al servidor en: {scrape_url}")
    print(f"   Solicitando scraping de: {args.url}")
    print(f"   Modo: SÍNCRONO (transparencia total)\n")
    
    try:
        response = requests.get(scrape_url, params={'url': args.url}, timeout=60)
        response.raise_for_status()
        
        print("✅ Respuesta recibida (Status 200 OK). Procesando...")
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