"""
Cliente HTTP asíncrono para hacer requests sin bloquear el event loop
"""

import aiohttp
import asyncio
import logging
from typing import Optional, Dict
from aiohttp import ClientSession, ClientTimeout, TCPConnector, ClientError

logger = logging.getLogger(__name__)


class AsyncHTTPClient:
    """Cliente HTTP asíncrono con manejo de errores robusto"""
    
    def __init__(self, timeout: Optional[ClientTimeout] = None,
                 connector: Optional[TCPConnector] = None):
        """
        Inicializa el cliente HTTP asíncrono
        
        Args:
            timeout: Configuración de timeouts
            connector: Configuración del conector TCP
        """
        self.timeout = timeout or ClientTimeout(total=30, connect=10, sock_read=20)
        self.connector = connector or TCPConnector(limit=100, limit_per_host=10)
        self.session: Optional[ClientSession] = None
        
        # Headers por defecto para simular navegador
        self.default_headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'es-ES,es;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }
        
    async def _ensure_session(self):
        """Asegura que existe una sesión activa"""
        if self.session is None or self.session.closed:
            self.session = ClientSession(
                timeout=self.timeout,
                connector=self.connector,
                headers=self.default_headers
            )
            
    async def fetch(self, url: str, max_size: int = 10 * 1024 * 1024) -> str:
        """
        Descarga el contenido HTML de una URL de forma asíncrona
        
        Args:
            url: URL a descargar
            max_size: Tamaño máximo en bytes (default: 10MB)
            
        Returns:
            Contenido HTML como string
            
        Raises:
            ClientError: Si hay error en la conexión
            asyncio.TimeoutError: Si se excede el timeout
            ValueError: Si el contenido es demasiado grande
        """
        await self._ensure_session()
        
        try:
            logger.info(f"Fetching: {url}")
            
            async with self.session.get(url, allow_redirects=True) as response:
                # Verificar status code
                if response.status >= 400:
                    raise ClientError(f"HTTP {response.status}: {url}")
                    
                # Verificar Content-Length si está disponible
                content_length = response.headers.get('Content-Length')
                if content_length and int(content_length) > max_size:
                    raise ValueError(f"Content too large: {content_length} bytes")
                    
                # Leer contenido con límite
                content = await response.text(encoding='utf-8', errors='ignore')
                
                # Verificar tamaño después de leer
                if len(content.encode('utf-8')) > max_size:
                    raise ValueError(f"Content too large after reading")
                    
                logger.info(f"Successfully fetched: {url} ({len(content)} chars)")
                return content
                
        except asyncio.TimeoutError:
            logger.error(f"Timeout fetching {url}")
            raise
        except ClientError as e:
            logger.error(f"Client error fetching {url}: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error fetching {url}: {str(e)}")
            raise
            
    async def fetch_binary(self, url: str, max_size: int = 10 * 1024 * 1024) -> bytes:
        """
        Descarga contenido binario (imágenes, etc.)
        
        Args:
            url: URL a descargar
            max_size: Tamaño máximo en bytes
            
        Returns:
            Contenido binario
        """
        await self._ensure_session()
        
        try:
            logger.debug(f"Fetching binary: {url}")
            
            async with self.session.get(url, allow_redirects=True) as response:
                if response.status >= 400:
                    raise ClientError(f"HTTP {response.status}: {url}")
                    
                # Verificar Content-Length
                content_length = response.headers.get('Content-Length')
                if content_length and int(content_length) > max_size:
                    raise ValueError(f"Content too large: {content_length} bytes")
                    
                # Leer contenido
                content = await response.read()
                
                if len(content) > max_size:
                    raise ValueError(f"Content too large: {len(content)} bytes")
                    
                return content
                
        except asyncio.TimeoutError:
            logger.error(f"Timeout fetching binary {url}")
            raise
        except ClientError as e:
            logger.error(f"Client error fetching binary {url}: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error fetching binary {url}: {str(e)}")
            raise
            
    async def head(self, url: str) -> Dict[str, str]:
        """
        Hace un HEAD request para obtener headers sin descargar contenido
        
        Args:
            url: URL a consultar
            
        Returns:
            Diccionario con headers de respuesta
        """
        await self._ensure_session()
        
        try:
            async with self.session.head(url, allow_redirects=True) as response:
                return dict(response.headers)
                
        except Exception as e:
            logger.error(f"Error en HEAD request {url}: {str(e)}")
            return {}
            
    async def fetch_multiple(self, urls: list, max_concurrent: int = 5) -> Dict[str, str]:
        """
        Descarga múltiples URLs concurrentemente con límite
        
        Args:
            urls: Lista de URLs a descargar
            max_concurrent: Máximo número de descargas concurrentes
            
        Returns:
            Diccionario {url: content}
        """
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def fetch_with_semaphore(url):
            async with semaphore:
                try:
                    content = await self.fetch(url)
                    return url, content
                except Exception as e:
                    logger.error(f"Error fetching {url}: {str(e)}")
                    return url, None
                    
        tasks = [fetch_with_semaphore(url) for url in urls]
        results = await asyncio.gather(*tasks)
        
        return {url: content for url, content in results if content is not None}
        
    async def close(self):
        """Cierra la sesión HTTP"""
        if self.session and not self.session.closed:
            await self.session.close()
            logger.info("HTTP client session closed")
            
    async def __aenter__(self):
        """Context manager entry"""
        await self._ensure_session()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        await self.close()