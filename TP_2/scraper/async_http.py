"""
Módulo Cliente HTTP Asíncrono (SRP: Solo maneja requests HTTP).
"""

import aiohttp
import asyncio
from typing import Optional, Tuple

from common import ScrapingError, TaskTimeoutError

class AsyncHTTPClient:
    """Wrapper para aiohttp.ClientSession con manejo de errores."""
    
    def __init__(self, timeout: int = 30):
        self.timeout = aiohttp.ClientTimeout(total=timeout)
        self.session: Optional[aiohttp.ClientSession] = None

    async def create_session(self):
        """Crea la aiohttp.ClientSession."""
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession(timeout=self.timeout)
            print("[AsyncHTTPClient] Sesión aiohttp creada.")

    async def close_session(self):
        """Cierra la aiohttp.ClientSession."""
        if self.session and not self.session.closed:
            await self.session.close()
            print("[AsyncHTTPClient] Sesión aiohttp cerrada.")

    async def fetch_html(self, url: str) -> Tuple[str, str]:
        """
        Obtiene el contenido HTML de una URL de forma asíncrona.
        
        Devuelve:
            Tuple[str, str]: (contenido_html, url_final)
        """
        if not self.session:
            await self.create_session()
        
        try:
            async with self.session.get(url, allow_redirects=True) as response:
                response.raise_for_status()
                
                content_length = response.headers.get('Content-Length')
                if content_length and int(content_length) > 10 * 1024 * 1024: 
                    raise ValueError(f"Página demasiado grande: {content_length} bytes")

                html = await response.text(encoding='utf-8')
                return html, str(response.url)
        
        except aiohttp.ClientConnectorError as e:
            print(f"Error de conexión al scrapear {url}: {e}")
            raise ScrapingError(f"No se pudo conectar a {url} (DNS o error de conexión)") from e
        
        except aiohttp.ClientResponseError as e:
            print(f"Error HTTP {e.status} al scrapear {url}: {e.message}")
            raise ScrapingError(f"Error HTTP {e.status} en {url}") from e
        
        except asyncio.TimeoutError as e:
            print(f"Timeout (30s) al scrapear {url}")
            raise TaskTimeoutError(f"Timeout al scrapear {url}") from e
        
        except ValueError as e: 
            print(f"Error de valor para {url}: {e}")
            raise ScrapingError(f"Error al procesar {url}: {e}") from e
        
        except Exception as e:
            print(f"Error inesperado de aiohttp con {url}: {e}")
            raise ScrapingError(f"Error inesperado al scrapear {url}: {e}") from e