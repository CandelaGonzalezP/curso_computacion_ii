
# processor/image_processor.py
"""Procesador de imágenes para generar thumbnails"""

import base64
import logging
from io import BytesIO
from typing import List
from urllib.parse import urljoin, urlparse
import requests
from bs4 import BeautifulSoup

try:
    from PIL import Image
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
    logging.warning("PIL not available, image processing will be disabled")

logger = logging.getLogger(__name__)


class ImageProcessor:
    """Procesador de imágenes para thumbnails"""
    
    def __init__(self, max_images: int = 5, thumb_size: tuple = (200, 200)):
        self.max_images = max_images
        self.thumb_size = thumb_size
        self.pil_available = PIL_AVAILABLE
        
    def process(self, url: str, html: str) -> List[str]:
        """
        Procesar imágenes y generar thumbnails
        
        Args:
            url: URL de la página
            html: Contenido HTML
            
        Returns:
            Lista de thumbnails en base64
        """
        if not self.pil_available:
            logger.warning("PIL not available, skipping image processing")
            return []
        
        try:
            # Extraer URLs de imágenes
            image_urls = self._extract_image_urls(html, url)
            
            if not image_urls:
                logger.info("No images found")
                return []
            
            # Limitar número de imágenes
            image_urls = image_urls[:self.max_images]
            
            thumbnails = []
            for img_url in image_urls:
                try:
                    thumbnail = self._create_thumbnail(img_url)
                    if thumbnail:
                        thumbnails.append(thumbnail)
                except Exception as e:
                    logger.warning(f"Error processing image {img_url}: {str(e)}")
                    continue
            
            logger.info(f"Generated {len(thumbnails)} thumbnails")
            return thumbnails
            
        except Exception as e:
            logger.error(f"Error in image processing: {str(e)}")
            return []
    
    def _extract_image_urls(self, html: str, base_url: str) -> List[str]:
        """Extraer URLs de imágenes del HTML"""
        soup = BeautifulSoup(html, 'lxml')
        image_urls = []
        seen = set()
        
        for img in soup.find_all('img'):
            src = img.get('src') or img.get('data-src')
            if not src:
                continue
            
            # Convertir a URL absoluta
            absolute_url = urljoin(base_url, src)
            
            # Filtrar por extensión y duplicados
            if absolute_url not in seen:
                parsed = urlparse(absolute_url)
                if parsed.scheme in ('http', 'https'):
                    # Filtrar por extensión común de imagen
                    if any(ext in parsed.path.lower() for ext in ['.jpg', '.jpeg', '.png', '.gif', '.webp']):
                        image_urls.append(absolute_url)
                        seen.add(absolute_url)
        
        return image_urls
    
    def _create_thumbnail(self, image_url: str) -> Optional[str]:
        """Crear thumbnail de una imagen"""
        try:
            # Descargar imagen con timeout
            response = requests.get(
                image_url,
                timeout=10,
                headers={'User-Agent': 'Mozilla/5.0'}
            )
            response.raise_for_status()
            
            # Verificar tamaño
            if len(response.content) > 5_000_000:  # 5MB
                logger.warning(f"Image too large: {image_url}")
                return None
            
            # Abrir imagen
            img = Image.open(BytesIO(response.content))
            
            # Convertir a RGB si es necesario
            if img.mode in ('RGBA', 'LA', 'P'):
                background = Image.new('RGB', img.size, (255, 255, 255))
                if img.mode == 'P':
                    img = img.convert('RGBA')
                background.paste(img, mask=img.split()[-1] if img.mode in ('RGBA', 'LA') else None)
                img = background
            
            # Crear thumbnail
            img.thumbnail(self.thumb_size, Image.Resampling.LANCZOS)
            
            # Convertir a base64
            buffer = BytesIO()
            img.save(buffer, format='JPEG', quality=85, optimize=True)
            thumbnail_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
            
            return thumbnail_base64
            
        except Exception as e:
            logger.debug(f"Error creating thumbnail for {image_url}: {str(e)}")
            return None
