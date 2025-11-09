# scraper/async_http.py

import aiohttp
import asyncio

# Requisito: Time-out de scraping (máximo 30 segundos)
SCRAPING_TIMEOUT = 30.0

async def fetch_url(session: aiohttp.ClientSession, url: str) -> str:
    """Realiza una petición GET asíncrona a la URL y devuelve el HTML."""
    try:
        # Uso de ClientTimeout para manejar el timeout de 30 segundos
        timeout = aiohttp.ClientTimeout(total=SCRAPING_TIMEOUT)
        # allow_redirects=True es una buena práctica
        async with session.get(url, timeout=timeout, allow_redirects=True) as response:
            
            # Requisito: Manejo de errores de red (códigos de estado HTTP)
            response.raise_for_status() 
            
            # Requisito: Límites de memoria para páginas muy grandes (ej. 10MB)
            content_length = response.headers.get('Content-Length')
            if content_length and int(content_length) > 10 * 1024 * 1024:
                 raise ValueError("Página demasiado grande (más de 10MB)")
                 
            # Devolver el contenido como texto (esperamos que sea HTML)
            return await response.text() 

    # Requisito: Manejo de Timeouts en scraping
    except asyncio.TimeoutError:
        raise ConnectionError(f"Error: Timeout después de {SCRAPING_TIMEOUT}s.")
    # Requisito: Manejo de errores de red (conexiones rechazadas, DNS fallido, etc.)
    except aiohttp.client_exceptions.ClientConnectorError as e:
        raise ConnectionError(f"Error de conexión (Conexión rechazada, DNS, etc.) al acceder a {url}: {e}")
    except aiohttp.client_exceptions.ClientResponseError as e:
        raise ConnectionError(f"Error de respuesta (HTTP {e.status}) al acceder a {url}.")
    except ValueError as e:
        raise ConnectionError(f"Error de contenido: {e}")
    except Exception as e:
        raise ConnectionError(f"Error desconocido al obtener {url}: {e.__class__.__name__}")