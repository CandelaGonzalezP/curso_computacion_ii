"""
Módulo para parsear HTML y extraer información estructural
"""

from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from typing import List, Dict
import logging

logger = logging.getLogger(__name__)


class HTMLParser:
    """Parser de HTML utilizando BeautifulSoup"""
    
    def __init__(self):
        self.parser = 'lxml'  # Parser más rápido
        
    def _get_soup(self, html_content: str) -> BeautifulSoup:
        """Crea objeto BeautifulSoup"""
        return BeautifulSoup(html_content, self.parser)
        
    def extract_title(self, html_content: str) -> str:
        """Extrae el título de la página"""
        try:
            soup = self._get_soup(html_content)
            title_tag = soup.find('title')
            if title_tag:
                return title_tag.get_text(strip=True)
            
            # Fallback a meta tags
            og_title = soup.find('meta', property='og:title')
            if og_title and og_title.get('content'):
                return og_title['content']
                
            return "Sin título"
            
        except Exception as e:
            logger.error(f"Error extrayendo título: {str(e)}")
            return "Error"
            
    def extract_links(self, html_content: str, base_url: str = None, 
                     max_links: int = 100) -> List[str]:
        """
        Extrae todos los enlaces de la página
        
        Args:
            html_content: Contenido HTML
            base_url: URL base para resolver enlaces relativos
            max_links: Máximo número de enlaces a retornar
            
        Returns:
            Lista de URLs absolutas
        """
        try:
            soup = self._get_soup(html_content)
            links = []
            seen = set()
            
            for link in soup.find_all('a', href=True):
                href = link['href'].strip()
                
                # Ignorar anclas y javascript
                if href.startswith('#') or href.startswith('javascript:'):
                    continue
                    
                # Resolver URL absoluta
                if base_url:
                    absolute_url = urljoin(base_url, href)
                else:
                    absolute_url = href
                    
                # Evitar duplicados
                if absolute_url not in seen:
                    seen.add(absolute_url)
                    links.append(absolute_url)
                    
                    if len(links) >= max_links:
                        break
                        
            return links
            
        except Exception as e:
            logger.error(f"Error extrayendo enlaces: {str(e)}")
            return []
            
    def extract_structure(self, html_content: str) -> Dict[str, int]:
        """
        Extrae la estructura de headers (H1-H6)
        
        Returns:
            Diccionario con conteo de cada tipo de header
        """
        try:
            soup = self._get_soup(html_content)
            structure = {}
            
            for i in range(1, 7):
                tag_name = f'h{i}'
                count = len(soup.find_all(tag_name))
                if count > 0:
                    structure[tag_name] = count
                    
            return structure
            
        except Exception as e:
            logger.error(f"Error extrayendo estructura: {str(e)}")
            return {}
            
    def count_images(self, html_content: str) -> int:
        """Cuenta el número total de imágenes en la página"""
        try:
            soup = self._get_soup(html_content)
            
            # Contar tags <img>
            img_tags = len(soup.find_all('img'))
            
            # Contar imágenes de background en CSS inline (aproximación)
            style_tags = soup.find_all(style=True)
            bg_images = sum(1 for tag in style_tags 
                          if 'background-image' in tag.get('style', ''))
            
            return img_tags + bg_images
            
        except Exception as e:
            logger.error(f"Error contando imágenes: {str(e)}")
            return 0
            
    def extract_image_urls(self, html_content: str, base_url: str = None,
                          max_images: int = 10) -> List[str]:
        """
        Extrae URLs de imágenes principales de la página
        
        Args:
            html_content: Contenido HTML
            base_url: URL base para resolver URLs relativas
            max_images: Máximo número de imágenes a extraer
            
        Returns:
            Lista de URLs de imágenes
        """
        try:
            soup = self._get_soup(html_content)
            image_urls = []
            seen = set()
            
            # Buscar tags <img>
            for img in soup.find_all('img', src=True):
                src = img['src'].strip()
                
                # Ignorar imágenes base64 y muy pequeñas
                if src.startswith('data:'):
                    continue
                    
                # Resolver URL absoluta
                if base_url:
                    absolute_url = urljoin(base_url, src)
                else:
                    absolute_url = src
                    
                if absolute_url not in seen:
                    seen.add(absolute_url)
                    image_urls.append(absolute_url)
                    
                    if len(image_urls) >= max_images:
                        break
                        
            return image_urls
            
        except Exception as e:
            logger.error(f"Error extrayendo URLs de imágenes: {str(e)}")
            return []
            
    def extract_text_content(self, html_content: str, max_length: int = 5000) -> str:
        """
        Extrae el contenido de texto principal de la página
        
        Args:
            html_content: Contenido HTML
            max_length: Longitud máxima del texto
            
        Returns:
            Texto limpio de la página
        """
        try:
            soup = self._get_soup(html_content)
            
            # Remover scripts y estilos
            for script in soup(['script', 'style', 'meta', 'link']):
                script.decompose()
                
            # Extraer texto
            text = soup.get_text(separator=' ', strip=True)
            
            # Limpiar espacios múltiples
            text = ' '.join(text.split())
            
            # Limitar longitud
            if len(text) > max_length:
                text = text[:max_length] + '...'
                
            return text
            
        except Exception as e:
            logger.error(f"Error extrayendo texto: {str(e)}")
            return ""