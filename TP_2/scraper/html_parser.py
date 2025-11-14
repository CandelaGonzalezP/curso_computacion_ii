"""
Funciones de parsing de HTML ( SRP: Solo parsea HTML).
Extrae: Título, Links, Estructura H1-H6, Conteo de Imágenes
y URLs de imágenes para el procesador.
"""

from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from typing import Dict, Any, List, Set
import re

def parse_basic_data(html: str, base_url: str) -> Dict[str, Any]:
    """
    Extrae título, links, conteo de imágenes y estructura de headers.
    """
    soup = BeautifulSoup(html, 'lxml')
    
    title = _extract_title(soup)
    links = _extract_links(soup, base_url)
    images_count = _count_images(soup)
    structure = _extract_structure(soup)
    
    image_urls_for_processing = _extract_image_urls(soup, base_url, limit=5) 

    return {
        "title": title,
        "links": links,
        "images_count": images_count,
        "structure": structure,
        "image_urls_for_processing": image_urls_for_processing
    }

def _extract_title(soup: BeautifulSoup) -> str:
    """Extrae el título, con fallback a H1."""
    if soup.title and soup.title.string:
        return soup.title.string.strip()
    if soup.h1 and soup.h1.string:
        return soup.h1.string.strip()
    
    meta_title = soup.find('meta', property='og:title')
    if meta_title and meta_title.get('content'):
        return meta_title['content'].strip()
        
    return "Sin Título"

def _extract_links(soup: BeautifulSoup, base_url: str) -> List[str]:
    """Extrae todos los enlaces HTTP/HTTPS absolutos y únicos."""
    links: Set[str] = set()
    for tag in soup.find_all('a', href=True):
        href = tag['href']
        if not href or href.startswith(('#', 'mailto:', 'tel:', 'javascript:')):
            continue
        
        try:
            abs_url = urljoin(base_url, href)
            parsed_url = urlparse(abs_url)
            if parsed_url.scheme in ['http', 'https'] and parsed_url.netloc:
                links.add(abs_url)
        except Exception:
            continue 
    return list(links)

def _count_images(soup: BeautifulSoup) -> int:
    """Cuenta <img> tags (ignorando data:) y CSS background-images simples."""
    
    img_tags = soup.find_all('img', src=True)
    img_tags_count = 0
    for tag in img_tags:
        if not tag.get('src', '').strip().startswith('data:image'):
            img_tags_count += 1
    
    css_images_count = 0
    style_tags = soup.find_all('style')
    for style in style_tags:
        if style.string:
            css_images_count += len(re.findall(r'url\(["\']?.*?\.(?:jpg|jpeg|png|gif|webp)', style.string, re.IGNORECASE))
    
    styled_elements = soup.find_all(style=re.compile(r'background-image', re.IGNORECASE))
    css_images_count += len(styled_elements)
    
    return img_tags_count + css_images_count

def _extract_structure(soup: BeautifulSoup) -> Dict[str, int]:
    """Cuenta headers H1-H6."""
    structure = {}
    for i in range(1, 7):
        tag_name = f'h{i}'
        structure[tag_name] = len(soup.find_all(tag_name))
    return structure

def _extract_image_urls(soup: BeautifulSoup, base_url: str, limit: int) -> List[str]:
    """Extrae URLs de imágenes para procesar."""
    image_urls: Set[str] = set()
    for tag in soup.find_all('img', src=True):
        src = tag['src']
        if not src or src.startswith('data:image'): 
            continue
            
        try:
            abs_url = urljoin(base_url, src)
            parsed_url = urlparse(abs_url)
            if parsed_url.scheme in ['http', 'https'] and parsed_url.netloc:
                image_urls.add(abs_url)
                if len(image_urls) >= limit:
                    break
        except Exception:
            continue
    return list(image_urls)