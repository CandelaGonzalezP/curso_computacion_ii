# client.py

import requests
import argparse
import json
import time

def test_scrape_request(server_url: str, url_to_scrape: str):
    """Envía una solicitud al Servidor A y muestra la respuesta."""
    try:
        full_url = f"{server_url}/scrape?url={url_to_scrape}"
        print(f"-> Solicitando scraping de: {url_to_scrape}")
        start_time = time.time()
        
        response = requests.get(full_url, timeout=45) 
        elapsed = time.time() - start_time
        response.raise_for_status() 
        
        data = response.json()
        
        print("\n--- Respuesta JSON Consolidada ---")
        print(json.dumps(data, indent=2))
        
        print(f"\n✅ Estado Final: {data.get('status', 'N/A')}")
        print(f"Tiempo total de respuesta: {elapsed:.2f} segundos")
        print(f"Título Extraído: {data.get('scraping_data', {}).get('title', 'N/A')}")
        print(f"Tiempo de Carga (simulado): {data.get('processing_data', {}).get('performance', {}).get('load_time_ms', 'N/A')} ms")
        
    except requests.exceptions.Timeout:
        print(f"\n❌ ERROR: Timeout al conectar con {server_url} o durante el procesamiento (T > 45s).")
    except requests.exceptions.RequestException as e:
        print(f"\n❌ ERROR de Solicitud HTTP: {e}")
        try:
            print(f"Cuerpo de error del servidor: {response.text}")
        except:
            pass
    except json.JSONDecodeError:
        print("\n❌ ERROR: Respuesta no es un JSON válido.")
    except Exception as e:
        print(f"\n❌ ERROR Inesperado: {e.__class__.__name__}: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Cliente de Prueba del Sistema de Scraping")
    parser.add_argument("--server", default="http://127.0.0.1:8080", 
                        help="URL base del Servidor A (Ej: http://127.0.0.1:8080)")
    parser.add_argument("--url", default="https://example.com", 
                        help="URL a scrapear")

    args = parser.parse_args()
    test_scrape_request(args.server, args.url)