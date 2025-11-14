"""
Módulo de Análisis de Rendimiento (SRP: Solo analiza performance).
"""

import requests
import time
from bs4 import BeautifulSoup
from typing import Dict, Any
from urllib.parse import urlparse, urljoin

from common import ProcessingError, TaskTimeoutError

def analyze_performance(url: str) -> Dict[str, Any]:
    """
    Calcula tiempo de carga, tamaño y número de requests (estimado).
    """
    try:
        start_time = time.time()
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=30) # Timeout 30s
        response.raise_for_status()
        
        load_time_ms = (time.time() - start_time) * 1000
        total_size_kb = len(response.content) / 1024
        
        soup = BeautifulSoup(response.content, 'lxml')
        base_domain = urlparse(url).netloc
        
        def is_internal(resource_url):
            if not resource_url:
                return False
            abs_url = urljoin(url, resource_url)
            return urlparse(abs_url).netloc == base_domain

        js_count = len([s['src'] for s in soup.find_all('script', src=True) if is_internal(s.get('src'))])
        css_count = len([c['href'] for c in soup.find_all('link', rel='stylesheet', href=True) if is_internal(c.get('href'))])
        img_count = len([i['src'] for i in soup.find_all('img', src=True) if is_internal(i.get('src'))])
        
        num_requests = 1 + js_count + css_count + img_count

        return {
            "load_time_ms": round(load_time_ms, 2),
            "total_size_kb": round(total_size_kb, 2),
            "num_requests": num_requests
        }

    except requests.Timeout as e:
        print(f"Error en Requests: Timeout al analizar performance de {url}")
        raise TaskTimeoutError(f"Timeout en análisis de performance para {url}") from e
    
    except requests.RequestException as e:
        print(f"Error en Requests al analizar performance de {url}: {e}")
        raise ProcessingError(f"Error de red en performance: {e}") from e

    except Exception as e:
        print(f"Error inesperado en Performance: {e}")
        raise ProcessingError(f"Error inesperado en Performance: {e}") from e